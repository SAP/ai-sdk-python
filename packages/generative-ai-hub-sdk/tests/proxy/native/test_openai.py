import unittest
from unittest.mock import MagicMock
from pydantic import BaseModel

import openai
from openai.types import Completion, CreateEmbeddingResponse
from openai.types.chat import ChatCompletion, ChatCompletionUserMessageParam
from openai.types.responses import Response

from gen_ai_hub.proxy.native.openai import OpenAI, AsyncOpenAI
from gen_ai_hub.proxy.native.openai.clients import ChatCompletions, AsyncChatCompletions, Responses, AsyncResponses
from integration_tests.constants import OPENAI_GPT_4O_MINI_TEST_MODEL, NVIDIA_EMBEDDING_TEST_MODEL

from tests.mock import (
    get_mocked_ai_core_client,
    openai_chat_completion_mocker,
    openai_stream_completion_mocker,
    openai_embeddings_mocker, openai_structured_outputs_mocker,
    openai_responses_mocker, openai_responses_structured_outputs_mocker
)
from tests.proxy.langchain_.test_init_models import TestInitModels


class TestOpenAIModels(unittest.TestCase):

    def setUp(self) -> None:
        self.proxy_client = get_mocked_ai_core_client(client_id='testopenaiclient')
        self.messages = [{
            'role': 'system',
            'content': 'You are a helpful assistant.'
        }, {
            'role': 'user',
            'content': 'Say hi, in one word!'
        }]
        self.kwargs = {'model_name': OPENAI_GPT_4O_MINI_TEST_MODEL, 'messages': self.messages}

    def test_chat_stream_completion(self):
        deployment = self.proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL)
        with openai_stream_completion_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            chunks = openai_client.chat.completions.create(**self.kwargs)
            self.assertTrue(all('"object": "chat.completion.chunk"' in chunk for chunk in chunks))

    def test_chat_completion(self):
        deployment = self.proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL)
        with openai_chat_completion_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            response = openai_client.chat.completions.create(**self.kwargs)
            self.assertIsInstance(response, ChatCompletion)
            response = openai_client.with_raw_response.chat.completions.create(**self.kwargs)
            self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_completion(self):
        deployment = self.proxy_client.select_deployment(model_name='gpt-4-instruct')
        deployment.prediction_urls.register({'gpt-4-instruct':
                                                 '/completions'})  # Add it to test completion model
        with openai_chat_completion_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            kwargs = {'model_name': 'gpt-4-instruct', 'prompt': 'Say this is a test', 'max_tokens': 7, 'temperature': 0}
            response = openai_client.completions.create(**kwargs)
            self.assertIsInstance(response, Completion)
            response = openai_client.with_raw_response.completions.create(**kwargs)
            self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_completion_with_custom_model(self):
        model_name = 'test-custom-openai-model'
        custom_deployment = TestInitModels.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        with openai_chat_completion_mocker(f'{custom_deployment.url}/completions'):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            kwargs = {'model_name': model_name, 'prompt': 'Say this is a test', 'max_tokens': 7, 'temperature': 0}
            response = openai_client.completions.create(**kwargs)
            self.assertIsInstance(response, Completion)
            response = openai_client.with_raw_response.completions.create(**kwargs)
            self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_update_deployments_called_for_custom_model(self):
        model_name = 'test-custom-openai-model-2'
        custom_deployment = TestInitModels.create_deployment(model_name)
        deployments = TestInitModels.create_gen_ai_hub_deployments()
        deployments.append(custom_deployment)
        deployments_dict = {}
        for i in range(len(deployments)):
            deployments_dict[i] = deployments[i]
        self.proxy_client._get_scenario_deployments = MagicMock()
        self.proxy_client._get_scenario_deployments.return_value = deployments_dict
        with openai_chat_completion_mocker(f'{custom_deployment.url}/completions'):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            kwargs = {'model_name': model_name, 'prompt': 'Say this is a test', 'max_tokens': 7, 'temperature': 0}
            response = openai_client.completions.create(**kwargs)
            self.assertIsInstance(response, Completion)
            response = openai_client.with_raw_response.completions.create(**kwargs)
            self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)
        self.proxy_client._get_scenario_deployments.assert_called_once_with(
            self.proxy_client.foundational_model_scenarios[0])

    def test_embeddings(self):
        deployment = self.proxy_client.select_deployment(model_name='text-embedding-ada-002')
        with openai_embeddings_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            kwargs = {'model': 'text-embedding-ada-002', 'input': 'Your text string goes here'}
            response = openai_client.embeddings.create(**kwargs)
            self.assertIsInstance(response, CreateEmbeddingResponse)

    def test_nvidia_embeddings(self, model=NVIDIA_EMBEDDING_TEST_MODEL):
        input_type = ['query', 'passage']
        for it in input_type:
            deployment = self.proxy_client.select_deployment(model_name=model)
            with openai_embeddings_mocker(deployment.prediction_url):
                openai_client = OpenAI(proxy_client=self.proxy_client)
                kwargs = {'model': model, 'input': 'Your text string goes here',
                          'extra_body': {'input_type': it}}
                response = openai_client.embeddings.create(**kwargs)
                self.assertIsInstance(response, CreateEmbeddingResponse)

    def test_embeddings_with_custom_model(self):
        model_name = 'test-custom-openai-embedding-model'
        custom_deployment = TestInitModels.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        with openai_embeddings_mocker(custom_deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            kwargs = {'model': model_name, 'input': 'Your text string goes here'}
            response = openai_client.embeddings.create(**kwargs)
            self.assertIsInstance(response, CreateEmbeddingResponse)

        # region Tests for structured_outputs = response in json format
        """ Tests for structured outputs in OpenAI client
            https://platform.openai.com/docs/guides/structured-outputs
        """

    class PersonName(BaseModel):
        first_name: str
        last_name: str

    def test_openai_client_beta_attribute_set_to_self(self):
        """Test that OpenAI client beta attribute is set to self"""
        openai_client = OpenAI(proxy_client=self.proxy_client)

        # Verify beta attribute is set to self
        self.assertEqual(openai_client.beta, openai_client)
        self.assertIsNotNone(openai_client.beta)

        """Test that AsyncOpenAI client beta attribute is set to self"""
        async_openai_client = AsyncOpenAI(proxy_client=self.proxy_client)

        # Verify beta attribute is set to self
        self.assertEqual(async_openai_client.beta, async_openai_client)
        self.assertIsNotNone(async_openai_client.beta)

    def test_beta_client_enables_structured_output_access(self):
        """Test that beta client enables access to structured output features"""
        openai_client = OpenAI(proxy_client=self.proxy_client)

        # Verify beta client has the same chat completions interface as main client
        self.assertEqual(openai_client.beta.chat.completions, openai_client.chat.completions)

        # Verify beta parse method is accessible
        self.assertTrue(hasattr(openai_client.beta.chat.completions, 'parse'))
        self.assertTrue(callable(openai_client.beta.chat.completions.parse))

        """Test that async beta client enables access to structured output features"""
        async_openai_client = AsyncOpenAI(proxy_client=self.proxy_client)

        # Verify beta client has the same chat completions interface as main client
        self.assertEqual(async_openai_client.beta.chat.completions, async_openai_client.chat.completions)

        # Verify beta parse method is accessible
        self.assertTrue(hasattr(async_openai_client.beta.chat.completions, 'parse'))
        self.assertTrue(callable(async_openai_client.beta.chat.completions.parse))

    def test_chat_completions_parse_method_exists(self):
        """Test that the parse method exists on ChatCompletions"""
        openai_client = OpenAI(proxy_client=self.proxy_client)
        chat_completions = openai_client.chat.completions

        # Verify parse method exists and is callable
        self.assertTrue(hasattr(chat_completions, 'parse'))
        self.assertTrue(callable(chat_completions.parse))
        self.assertIsInstance(chat_completions, ChatCompletions)

        """Test that the async parse method exists on AsyncChatCompletions"""
        async_openai_client = AsyncOpenAI(proxy_client=self.proxy_client)
        async_chat_completions = async_openai_client.chat.completions

        # Verify async parse method exists and is callable
        self.assertTrue(hasattr(async_chat_completions, 'parse'))
        self.assertTrue(callable(async_chat_completions.parse))
        self.assertIsInstance(async_chat_completions, AsyncChatCompletions)

    def test_chat_completions_parse_with_response_format(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        """Test that parse method handles response_format parameter correctly"""

        deployment = self.proxy_client.select_deployment(model_name=model)
        with openai_structured_outputs_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            response = openai_client.chat.completions.parse(
                model=model,
                messages=ChatCompletionUserMessageParam(role="user", content="Tell me about John Doe."),
                response_format=self.PersonName
            )
            self.assertIsInstance(response, ChatCompletion)

    async def test_async_chat_completions_parse_with_response_format(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        """Test that async parse method works with a Pydantic model for structured output"""

        deployment = self.proxy_client.select_deployment(model_name=model)
        with openai_structured_outputs_mocker(deployment.prediction_url):
            openai_client = AsyncOpenAI(proxy_client=self.proxy_client)
            response = await openai_client.chat.completions.parse(
                model=model,
                messages=ChatCompletionUserMessageParam(role="user", content="Tell me about John Doe."),
                response_format=self.PersonName
            )
            self.assertIsInstance(response, ChatCompletion)

    # endregion

    def test_responses(self):
        deployment = self.proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL)
        with openai_responses_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            kwargs = {'model_name': OPENAI_GPT_4O_MINI_TEST_MODEL, 'input': 'Say this is a test'}
            response = openai_client.responses.create(**kwargs)
            self.assertIsInstance(response, Response)

    def test_responses_parse_method_exists(self):
        """Test that the parse method exists on Responses"""
        openai_client = OpenAI(proxy_client=self.proxy_client)
        responses = openai_client.responses

        # Verify parse method exists and is callable
        self.assertTrue(hasattr(responses, 'parse'))
        self.assertTrue(callable(responses.parse))
        self.assertIsInstance(responses, Responses)

        """Test that the async parse method exists on AsyncResponses"""
        async_openai_client = AsyncOpenAI(proxy_client=self.proxy_client)
        async_responses = async_openai_client.responses

        # Verify async parse method exists and is callable
        self.assertTrue(hasattr(async_responses, 'parse'))
        self.assertTrue(callable(async_responses.parse))
        self.assertIsInstance(async_responses, AsyncResponses)

    def test_responses_parse_with_text_format(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        """Test that parse method handles text_format parameter correctly"""

        deployment = self.proxy_client.select_deployment(model_name=model)
        with openai_responses_structured_outputs_mocker(deployment.prediction_url):
            openai_client = OpenAI(proxy_client=self.proxy_client)
            response = openai_client.responses.parse(
                model=model,
                input="Tell me about John Doe aged 30.",
                text_format=self.PersonName
            )
            self.assertIsInstance(response, Response)


class TestAsyncOpenAIModels(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.proxy_client = get_mocked_ai_core_client(client_id='testasyncopenaiclient')
        self.messages = [{
            'role': 'system',
            'content': 'You are a helpful assistant.'
        }, {
            'role': 'user',
            'content': 'Say hi, in one word!'
        }]
        self.kwargs = {'model_name': OPENAI_GPT_4O_MINI_TEST_MODEL, 'messages': self.messages}

    async def test_async_chat_completions(self):
        deployment = self.proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL)
        with openai_chat_completion_mocker(deployment.prediction_url):
            openai_client = AsyncOpenAI(proxy_client=self.proxy_client)
            response = await openai_client.chat.completions.create(**self.kwargs)
            self.assertIsInstance(response, ChatCompletion)
            response = await openai_client.with_raw_response.chat.completions.create(**self.kwargs)
            self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    async def test_async_nvidia_embeddings(self, model=NVIDIA_EMBEDDING_TEST_MODEL):
        deployment = self.proxy_client.select_deployment(model_name=model)
        with openai_embeddings_mocker(deployment.prediction_url):
            openai_client = AsyncOpenAI(proxy_client=self.proxy_client)
            kwargs = {'model': model, 'input': 'Your text string goes here',
                      'extra_body': {'input_type': 'query'}}
            response = await openai_client.embeddings.create(**kwargs)
            self.assertIsInstance(response, CreateEmbeddingResponse)

    async def test_async_responses(self):
        deployment = self.proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL)
        with openai_responses_mocker(deployment.prediction_url):
            openai_client = AsyncOpenAI(proxy_client=self.proxy_client)
            kwargs = {'model_name': OPENAI_GPT_4O_MINI_TEST_MODEL, 'input': 'Say this is a test'}
            response = await openai_client.responses.create(**kwargs)
            self.assertIsInstance(response, Response)
