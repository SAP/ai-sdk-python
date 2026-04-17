import unittest

from httpx import TimeoutException

from gen_ai_hub.orchestration.exceptions import OrchestrationError
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.response import OrchestrationResponse
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase


class AsyncLLMTest(OrchestrationServiceTestBase, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up common variables for asynchronous tests.
        # Replace the API URL with your actual test endpoint.
        self.service = OrchestrationService(api_url=self.api_url)
        self.config = OrchestrationConfig(
            llm=LLM(name="gpt-4o-mini", parameters={"temperature": 0.0}),
            template=Template(
                messages=[
                    SystemMessage("This is a system message."),
                    UserMessage("Hello, {{?name}}!"),
                ],
                defaults=[TemplateValue("name", "World")],
            ),
        )

    async def test_async_invalid_llm_name(self):
        """Test that an unknown LLM name causes an error asynchronously."""
        llm = LLM(name="unknown-llm")
        config = OrchestrationConfig(template=self.config.template, llm=llm)
        with self.assertRaises(OrchestrationError):
            await self.service.arun(config=config)

    async def test_async_invalid_llm_version(self):
        """Test that an invalid LLM version causes an error asynchronously."""
        llm = LLM(name="gpt-4o-mini", version="unknown")
        config = OrchestrationConfig(template=self.config.template, llm=llm)
        with self.assertRaises(OrchestrationError):
            await self.service.arun(config=config)

    async def test_async_valid_llm(self):
        """Test that a valid LLM returns a result asynchronously."""
        response = await self.service.arun(config=self.config)
        self.assertTrue(response.orchestration_result.model.startswith(self.config.llm.name))

    async def test_async_streaming(self):
        """Test asynchronous streaming mode returns at least one chunk."""
        service = OrchestrationService(api_url=self.api_url, config=self.config)
        chunks = []
        # astream() returns an asynchronous iterator.
        async for chunk in await service.astream():
            chunks.append(chunk)
        self.assertGreater(len(chunks), 0, "No streaming chunks were received.")

    async def test_async_streaming_with_invalid_options(self):
        """Test that passing invalid stream options raises an error asynchronously."""
        with self.assertRaises(OrchestrationError):
            # The invalid stream options should cause an error during the async call.
            async for _ in await self.service.astream(config=self.config, stream_options={'unknown': 10}):
                pass

    async def test_async_reuse_client(self):
        """
        ensures the client is reused and not closed when making multiple requests
        """
        service = OrchestrationService(api_url=self.api_url, config=self.config)
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
        config = OrchestrationConfig(
            template=Template(
                messages=[
                    SystemMessage("You are a famous professor for theoretical physics."),
                    UserMessage("Elaborate on the relativity theory."),
                ],
            ),
            llm=LLM(name="gpt-5-nano")
        )

        # First request - should time out
        with self.assertRaises(TimeoutException):
            await self.service.arun(config=config)

        # Second request - should succeed due to overwrite in request with higher timeout
        result = await self.service.arun(config=config, timeout=300)
        self.assertIsInstance(result, OrchestrationResponse)
