from sap_ai_sdk_orchestration.exceptions import OrchestrationError
from sap_ai_sdk_orchestration.models.azure_content_filter import (AzureContentSafetyOutput, AzureThreshold,
                                                                     AzureContentFilter)
from sap_ai_sdk_orchestration.models.config import OrchestrationConfig, ModuleConfig
from sap_ai_sdk_orchestration.models.content_filter import (AzureContentSafetyOutputFilterConfig, ContentFilter,
                                                               ContentFilterProvider)
from sap_ai_sdk_orchestration.models.content_filtering import FilteringModuleConfig, OutputFiltering
from sap_ai_sdk_orchestration.models.llm_model_details import LLMModelDetails
from sap_ai_sdk_orchestration.models.message import SystemMessage, UserMessage
from sap_ai_sdk_orchestration.models.response import StreamCompletionPostResponse
from sap_ai_sdk_orchestration.models.streaming import GlobalStreamOptions
from sap_ai_sdk_orchestration.models.template import Template, PromptTemplatingModuleConfig
from sap_ai_sdk_orchestration.service import OrchestrationService
from integration_tests.constants import CLAUDE_4_5_SONNET_TEST_MODEL
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestStreaming(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()

        self.template = Template(
            template=[
                SystemMessage(content="This is a system message."),
                UserMessage(content="Hello, {{?name}}!"),
            ],
            defaults={"name": "Integration Test"}
        )
        self.llm = LLMModelDetails(
            name="gpt-4o-mini",
            params={'temperature': 0.0}
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)

    def create_service(self, output_filtering=None, stream_options=None):
        content_filter_config = None
        if output_filtering:
            content_filter_config = FilteringModuleConfig(
                output=output_filtering
            )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config,
                                     stream=GlobalStreamOptions(enabled=True, **(stream_options or {})))

        return OrchestrationService(api_url=self.api_url, config=config)

    def test_streaming(self):
        service = self.create_service()

        number_of_chunks = 0
        response_stream = service.stream()
        for i, chunk in enumerate(response_stream):
            if i == 0:
                self.assertEqual(chunk.intermediate_results.templating[1].content, "Hello, Integration Test!")
                self.assertIsNone(chunk.intermediate_results.llm)
            else:
                self.assertIsNotNone(chunk.intermediate_results.llm)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")

    def test_streaming_returns_token_usage(self):
        self.llm = LLMModelDetails(name=CLAUDE_4_5_SONNET_TEST_MODEL)
        service = self.create_service()

        response_stream = service.stream()

        for chunk in response_stream:
            self.assertIsInstance(chunk, StreamCompletionPostResponse)
            if chunk.final_result.usage:
                self.assertGreater(chunk.final_result.usage.prompt_tokens, 0)
                self.assertGreater(chunk.final_result.usage.completion_tokens, 0)
                self.assertGreater(chunk.final_result.usage.total_tokens, 0)

    def test_streaming_with_stream_options(self, chunk_size=5):
        service = self.create_service(stream_options={'chunk_size': chunk_size})

        response_stream = service.stream()
        number_of_chunks = 0
        for chunk in response_stream:
            if chunk.final_result.choices:
                self.assertLessEqual(len(chunk.final_result.choices[0].delta.content.split()), chunk_size)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")

    def test_streaming_with_error_in_stream(self):
        template = Template(template=[UserMessage(content="Write a novel about maths")])
        llm = LLMModelDetails(name='gpt-4o-mini',
                              params={'temperature': 0.0, 'max_tokens': 100000}  # This will exceed the token limit
                              )
        prompt_template = PromptTemplatingModuleConfig(prompt=template, model=llm)
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config,
                                     stream=GlobalStreamOptions(enabled=True))
        service = OrchestrationService(
            api_url=self.api_url,
            config=config
        )

        with self.assertRaises(OrchestrationError):
            for _ in service.stream():
                pass

    def test_output_filtering_with_stream_options(self):
        output_filtering = OutputFiltering(
            filters=[
                AzureContentSafetyOutputFilterConfig(
                    config=AzureContentSafetyOutput(hate=AzureThreshold.ALLOW_ALL,
                                              self_harm=AzureThreshold.ALLOW_ALL,
                                              sexual=AzureThreshold.ALLOW_ALL,
                                              violence=AzureThreshold.ALLOW_ALL,
                                              )
                )
            ],
            stream_options={'overlap': 10}
        )

        service = self.create_service(output_filtering=output_filtering)
        response_stream = service.stream()

        number_of_chunks = 0
        for i, chunk in enumerate(response_stream):
            if i == 0:
                self.assertEqual(chunk.intermediate_results.templating[1].content, "Hello, Integration Test!")
                self.assertIsNone(chunk.intermediate_results.llm)
            elif i == 1:
                self.assertIsNotNone(chunk.intermediate_results.output_filtering)
                self.assertIsNotNone(chunk.intermediate_results.llm)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")

    def test_output_filtering_with_stream_options_backward_compatibility(self):
        output_filtering = OutputFiltering(
            filters=[
                ContentFilter(
                    type=ContentFilterProvider.AZURE,
                    config=AzureContentFilter(hate=AzureThreshold.ALLOW_ALL,
                                              self_harm=AzureThreshold.ALLOW_ALL,
                                              sexual=AzureThreshold.ALLOW_ALL,
                                              violence=AzureThreshold.ALLOW_ALL,
                                              )
                )
            ],
            stream_options={'overlap': 10}
        )

        service = self.create_service(output_filtering=output_filtering)
        response_stream = service.stream()

        number_of_chunks = 0
        for i, chunk in enumerate(response_stream):
            if i == 0:
                self.assertEqual(chunk.intermediate_results.templating[1].content, "Hello, Integration Test!")
                self.assertIsNone(chunk.intermediate_results.llm)
            elif i == 1:
                self.assertIsNotNone(chunk.intermediate_results.output_filtering)
                self.assertIsNotNone(chunk.intermediate_results.llm)
            number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")
