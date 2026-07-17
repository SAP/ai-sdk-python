import unittest
from typing import cast

from gen_ai_hub.orchestration.exceptions import OrchestrationError
from gen_ai_hub.orchestration.models.azure_content_filter import AzureContentFilter, AzureThreshold
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.content_filtering import OutputFiltering, ContentFiltering
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.response import OrchestrationResponseStreaming
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.constants import CLAUDE_4_5_SONNET_TEST_MODEL
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestStreaming(OrchestrationServiceTestBase):


    def setUp(self):
        super().setUp()

        self.template = Template(
            messages=[
                SystemMessage("This is a system message."),
                UserMessage("Hello, {{?name}}!"),
            ],
            defaults=[TemplateValue(name="name", value="Integration Test")],
        )
        self.llm = LLM(
            name="gpt-4o-mini",
            parameters={'temperature': 0.0}
        )

    def create_service(self, output_filtering=None, stream_options=None):
        filter_config = None
        if output_filtering:
            filter_config = ContentFiltering(output_filtering=output_filtering)
        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            filtering= filter_config,
        )

        if stream_options:
            config.stream_options = stream_options

        return OrchestrationService(api_url=self.api_url, config=config)

    def test_streaming(self):
        service = self.create_service()

        number_of_chunks = 0
        response_stream = service.stream()
        for i, chunk in enumerate(response_stream):
            chunk = cast(OrchestrationResponseStreaming, chunk)
            if i == 0:
                self.assertEqual(chunk.module_results.templating[1].content, "Hello, Integration Test!")
                self.assertIsNone(chunk.module_results.llm)
            else:
                self.assertIsNotNone(chunk.module_results.llm)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")

    @unittest.skip("Internal server error")
    def test_streaming_returns_token_usage(self):
        self.llm = LLM(name=CLAUDE_4_5_SONNET_TEST_MODEL)
        service = self.create_service()

        response_stream = service.stream()
        for chunk in enumerate(response_stream):
            response_streaming = cast(OrchestrationResponseStreaming, chunk)[1]
            if response_streaming.orchestration_result.usage:
                self.assertGreater(response_streaming.orchestration_result.usage.prompt_tokens, 0)
                self.assertGreater(response_streaming.orchestration_result.usage.completion_tokens, 0)
                self.assertGreater(response_streaming.orchestration_result.usage.total_tokens, 0)
                self.assertGreater(response_streaming.module_results.llm.usage.total_tokens, 0)

    def test_streaming_with_stream_options(self, chunk_size=5):
        service = self.create_service()

        response_stream = service.stream(stream_options={'chunk_size': chunk_size})
        number_of_chunks = 0
        for chunk in response_stream:
            if chunk.orchestration_result.choices:
                self.assertLessEqual(len(chunk.orchestration_result.choices[0].delta.content.split()), chunk_size)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")

    def test_streaming_with_invalid_stream_options(self):
        service = self.create_service()

        with self.assertRaises(OrchestrationError):
            for _ in service.stream(stream_options={'unknown': 10}):
                pass

    def test_streaming_with_error_in_stream(self):
        service = OrchestrationService(
            api_url=self.api_url,
            config=OrchestrationConfig(
                llm=LLM(
                    name='gpt-4o-mini',
                    parameters={'temperature': 0.0, 'max_tokens': 100000}  # This will exceed the token limit
                ),
                template=Template(messages=[UserMessage("Write a novel about maths")])
            )
        )

        with self.assertRaises(OrchestrationError):
            for _ in service.stream():
                pass

    def test_output_filtering_with_stream_options(self):
        output_filtering = OutputFiltering(
            filters=[
                AzureContentFilter(
                    hate=AzureThreshold.ALLOW_ALL,
                    self_harm=AzureThreshold.ALLOW_ALL,
                    sexual=AzureThreshold.ALLOW_ALL,
                    violence=AzureThreshold.ALLOW_ALL,
                )
            ],
            stream_options={'overlap': 10}
        )

        service = self.create_service(output_filtering=output_filtering)
        response_stream = service.stream()

        number_of_chunks = 0
        for i, chunk in enumerate(response_stream):
            chunk = cast(OrchestrationResponseStreaming, chunk)
            if i == 0:
                self.assertEqual(chunk.module_results.templating[1].content, "Hello, Integration Test!")
                self.assertIsNone(chunk.module_results.llm)
            elif i == 1:
                self.assertIsNotNone(chunk.module_results.output_filtering)
                self.assertIsNotNone(chunk.module_results.llm)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")

    def test_output_filtering_with_invalid_stream_options(self):
        output_filtering = OutputFiltering(
            filters=[
                AzureContentFilter(
                    hate=AzureThreshold.ALLOW_ALL,
                    self_harm=AzureThreshold.ALLOW_ALL,
                    sexual=AzureThreshold.ALLOW_ALL,
                    violence=AzureThreshold.ALLOW_ALL,
                )
            ],
            stream_options={'unknown': 10}
        )

        service = self.create_service(output_filtering)

        with self.assertRaises(OrchestrationError):
            for _ in service.stream():
                pass
