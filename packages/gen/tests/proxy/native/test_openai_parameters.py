"""Regression tests for parameter filtering at the OpenAI proxy boundary."""
import json
from datetime import datetime

import pytest
import respx
from httpx import Response
from pydantic import BaseModel

from gen_ai_hub.proxy.gen_ai_hub_proxy.client import Deployment
from gen_ai_hub.proxy.native.openai import AsyncOpenAI, OpenAI
from gen_ai_hub.proxy.native.openai.clients import (
    AsyncChatCompletions,
    AsyncResponses,
    ChatCompletions,
    Responses,
)
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from tests.mock import (
    OPENAI_RESPONSES_RESPONSE,
    OPENAI_RESPONSES_RESPONSE_PARSE,
    OPENAI_STRUCTRED_OUTPUTS_RESPONSE,
    get_mocked_ai_core_client,
)


class PersonName(BaseModel):
    first_name: str
    last_name: str


@pytest.fixture
def proxy_client():
    return get_mocked_ai_core_client(client_id='test-openai-parameters')


def add_deployment(proxy_client, model_name):
    deployment = Deployment(
        url=f'https://api.gen-ai.io/v2/inference/deployments/{model_name}',
        deployment_id=f'{model_name}-deployment',
        config_id=f'{model_name}-config',
        config_name=f'{model_name}-config',
        model_name=model_name,
        model_version='latest',
        created_at=datetime.now(),
    )
    proxy_client._deployments.append(deployment)
    return deployment


@pytest.mark.parametrize('resource_class', [
    ChatCompletions, AsyncChatCompletions, Responses, AsyncResponses,
])
@pytest.mark.parametrize('model_name,supported', [
    ('o1', False),
    ('o3-mini', False),
    ('gpt-5', False),
    ('gpt-5-mini', False),
    ('gpt-5-nano', False),
    ('gpt-5-2025-08-07', False),
    ('gpt-5.1', False),
    ('gpt-5.2-pro', False),
    ('gpt-5.6-sol', False),
    ('gpt-6', False),
    ('gpt-6-sol', False),
    ('gpt-6.1-sol', False),
    ('gpt-6-astra', True),
    ('gpt-6-astra-2026-09-24', True),
    ('cohere--command-a-reasoning', False),
    ('gpt-4o-mini', True),
    ('gpt-4.1', True),
    ('gpt-5-chat-latest', True),
    ('gpt-5.1-chat-latest', True),
    ('cohere--command-a', True),
    ('custom-model', True),
    ('gpt-50', True),
    ('gpt-60', True),
])
def test_supports_temperature(resource_class, model_name, supported):
    assert resource_class.supports_temperature(model_name) is supported


@pytest.mark.parametrize('resource_name', ['responses', 'chat.completions'])
@pytest.mark.parametrize('method', ['create', 'parse'])
@pytest.mark.parametrize('model_name,reasoning_effort,supported', [
    ('gpt-6.1-sol', None, False),
    ('gpt-5.2', 'high', False),
    ('gpt-5.2', 'none', True),
    ('gpt-6-sol', 'none', True),
    ('gpt-6-astra', None, True),
    ('gpt-6-astra', 'high', True),
    ('gpt-5', 'none', False),
    ('o3', 'none', False),
    ('gpt-4o-mini', None, True),
    ('gpt-5-chat-latest', None, True),
    ('cohere--command-a-reasoning', None, False),
])
@pytest.mark.parametrize('is_async', [False, True])
@pytest.mark.asyncio
async def test_request_parameter_filtering(
    proxy_client, resource_name, method, model_name, reasoning_effort, supported, is_async,
):
    deployment = add_deployment(proxy_client, model_name)
    client = (AsyncOpenAI if is_async else OpenAI)(proxy_client=proxy_client)
    is_responses = resource_name == 'responses'
    resource = client.responses if is_responses else client.chat.completions
    kwargs = {'deployment_id': deployment.deployment_id, 'temperature': 0, 'n': 1}
    if is_responses:
        kwargs['input'] = 'Tell me about John Doe.'
        kwargs['max_output_tokens'] = 128
        if reasoning_effort is not None:
            kwargs['reasoning'] = {'effort': reasoning_effort}
        response_body = OPENAI_RESPONSES_RESPONSE_PARSE
        if method == 'parse':
            kwargs['text_format'] = PersonName
    else:
        kwargs['messages'] = [{'role': 'user', 'content': 'Tell me about John Doe.'}]
        kwargs['max_completion_tokens'] = 128
        if reasoning_effort is not None:
            kwargs['reasoning_effort'] = reasoning_effort
        response_body = OPENAI_STRUCTRED_OUTPUTS_RESPONSE
        if method == 'parse':
            kwargs['response_format'] = PersonName

    with respx.mock:
        route = respx.post(deployment.prediction_url).mock(
            return_value=Response(200, json=response_body),
        )
        try:
            result = getattr(resource, method)(**kwargs)
            if is_async:
                result = await result
            assert result is not None
            payload = json.loads(route.calls.last.request.content)
            assert ('temperature' in payload) is supported
            if supported:
                assert payload['temperature'] == 0
            assert ('n' in payload) is (not is_responses and not model_name.startswith('cohere--'))
            token_parameter = 'max_output_tokens' if is_responses else 'max_completion_tokens'
            assert (token_parameter in payload) is (is_responses or not model_name.startswith('cohere--'))
            if reasoning_effort is not None:
                if is_responses:
                    assert payload['reasoning']['effort'] == reasoning_effort
                else:
                    assert payload['reasoning_effort'] == reasoning_effort
            if method == 'parse':
                parsed = result.output_parsed if is_responses else result.choices[0].message.parsed
                assert isinstance(parsed, PersonName)
        finally:
            if is_async:
                await client.close()
            else:
                client.close()


@pytest.mark.parametrize('is_async', [False, True])
@pytest.mark.asyncio
async def test_langchain_reasoning_model_with_tools(proxy_client, is_async):
    model_name = 'gpt-6.1-sol'
    deployment = add_deployment(proxy_client, model_name)
    llm = ChatOpenAI(proxy_client=proxy_client, proxy_model_name=model_name, temperature=0)
    tool = {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Get the weather in a city.',
            'parameters': {
                'type': 'object',
                'properties': {'city': {'type': 'string'}},
                'required': ['city'],
            },
        },
    }
    with respx.mock:
        route = respx.post(deployment.prediction_url).mock(
            return_value=Response(200, json=OPENAI_RESPONSES_RESPONSE),
        )
        try:
            bound = llm.bind_tools([tool])
            result = await bound.ainvoke('hello') if is_async else bound.invoke('hello')
            assert result.content
            payload = json.loads(route.calls.last.request.content)
            assert 'n' not in payload
            assert 'temperature' not in payload
            assert payload['tools'][0]['name'] == 'get_weather'
            assert 'input' in payload
        finally:
            llm.root_client.close()
            await llm.root_async_client.close()
