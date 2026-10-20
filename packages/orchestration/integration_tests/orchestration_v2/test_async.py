import unittest

from httpx import TimeoutException

from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError
from gen_ai_hub.orchestration_v2.models.config import (OrchestrationConfig, ModuleConfig,
CompletionRequestConfigurationReferenceByIdConfigRef,
CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.response import CompletionPostResponse
from gen_ai_hub.orchestration_v2.models.streaming import GlobalStreamOptions
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class AsyncLLMTest(OrchestrationServiceTestBase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up common variables for asynchronous tests.
        # Replace the API URL with your actual test endpoint.
        self.service = OrchestrationService(api_url=self.api_url)
        prompt_template = PromptTemplatingModuleConfig(
            model=LLMModelDetails(name="gpt-4o-mini", params={"temperature": 0.0}),
            prompt=Template(
                template=[
                    SystemMessage(content="This is a system message."),
                    UserMessage(content="Hello, {{?name}}!"),
                ],
                defaults={"name": "World"},
            ),
        )
        module_config = ModuleConfig(prompt_templating=prompt_template)
        self.config = OrchestrationConfig(modules=module_config)
        self.config_stream = OrchestrationConfig(modules=module_config, stream=GlobalStreamOptions(enabled=True))
        self.config_ref_id = CompletionRequestConfigurationReferenceByIdConfigRef(id="1234567890")
        self.config_ref_name = CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef(
            name="test",
            version="1",
            scenario="test"
        )

    async def test_async_invalid_llm_name(self):
        """Test that an unknown LLM name causes an error asynchronously."""
        llm = LLMModelDetails(name="unknown-llm")
        prompt_template = PromptTemplatingModuleConfig(
            model=llm,
            prompt=Template(
                template=[
                    SystemMessage(content="This is a system message."),
                    UserMessage(content="Hello, {{?name}}!"),
                ],
                defaults={"name": "World"},
            ),
        )
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)
        with self.assertRaises(OrchestrationError):
            await self.service.arun(config=config)

    async def test_async_invalid_llm_version(self):
        """Test that an invalid LLM version causes an error asynchronously."""
        llm = LLMModelDetails(name="gpt-4o-mini", version="unknown")
        prompt_template = PromptTemplatingModuleConfig(
            model=llm,
            prompt=Template(
                template=[
                    SystemMessage(content="This is a system message."),
                    UserMessage(content="Hello, {{?name}}!"),
                ],
                defaults={"name": "World"},
            ),
        )
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)
        with self.assertRaises(OrchestrationError):
            await self.service.arun(config=config)

    async def test_async_valid_llm(self):
        """Test that a valid LLM returns a result asynchronously."""
        response = await self.service.arun(config=self.config)
        self.assertTrue(response.final_result.model.startswith(self.config.modules.prompt_templating.model.name))

    async def test_async_streaming(self):
        """Test asynchronous streaming mode returns at least one chunk."""
        service = OrchestrationService(api_url=self.api_url, config=self.config_stream)
        chunks = []
        # astream() returns an asynchronous iterator.
        async for chunk in await service.astream():
            chunks.append(chunk)
        self.assertGreater(len(chunks), 0, "No streaming chunks were received.")

    async def test_async_reuse_client(self):
        """
        ensures the client is reused and not closed when making multiple requests
        """
        service = OrchestrationService(api_url=self.api_url, config=self.config_stream)
        reusable_client = service.async_client
        # First request
        chunks1 = []
        async for chunk in await service.astream():
            chunks1.append(chunk)
        self.assertFalse(reusable_client.is_closed)

        # Second request
        chunks2 = []
        async for chunk in await service.astream():
            chunks2.append(chunk)
        self.assertGreater(len(chunks2), 0, "No streaming chunks were received.")

        # ensure httpx client is reused
        self.assertEqual(reusable_client, service.async_client)

        await service.aclose_http_connection()
        self.assertTrue(reusable_client.is_closed)

    async def test_async_timeout_per_request(self):
        """
        set low default timeout for reusable client, which leads to a timeout.
        overwrite timeout with higher value via request and show that response is returned.
        """
        self.service = OrchestrationService(self.api_url, timeout=0.1)

        # First request - should time out
        with self.assertRaises(TimeoutException):
            await self.service.arun(config=self.config)

        # Second request - should succeed due to overwrite in request with higher timeout
        result = await self.service.arun(config=self.config, timeout=300)
        self.assertIsInstance(result, CompletionPostResponse)

    async def test_config_and_config_ref_provided_error_class_and_methode(self):
        service = OrchestrationService(api_url=self.api_url, config=self.config)
        with self.assertRaises(ValueError):
            await service.arun(config_ref=self.config_ref_name)

    async def test_config_and_config_ref_provided_error_methode(self):
        service = OrchestrationService(api_url=self.api_url)
        with self.assertRaises(ValueError):
            await service.arun(config=self.config, config_ref=self.config_ref_id)
