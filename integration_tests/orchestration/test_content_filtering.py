from gen_ai_hub.orchestration.exceptions import OrchestrationError
from gen_ai_hub.orchestration.models.azure_content_filter import AzureThreshold, AzureContentFilter
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.content_filter import (
    ContentFilter,
    ContentFilterProvider,
)
from gen_ai_hub.orchestration.models.content_filtering import InputFiltering, OutputFiltering, ContentFiltering
from gen_ai_hub.orchestration.models.llama_guard_3_filter import LlamaGuard38bFilter
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase


class TestContentFilter(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.llm = LLM(
            name="gpt-4o-mini",
            version="latest",
            parameters={"max_tokens": 50, "temperature": 0.0},
        )
        self.template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
            ]
        )
        self.service = OrchestrationService(
            api_url=self.api_url,
            config=OrchestrationConfig(
                template=self.template,
                llm=self.llm,
            ),
        )

    def test_invalid_filter_provider(self):
        content_filter = ContentFilter(provider="unknown", config={"key": "value"})

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            filtering=ContentFiltering(InputFiltering(filters=[content_filter]))
        )

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_azure_filter_with_invalid_config(self):
        content_filter = ContentFilter(
            provider=ContentFilterProvider.AZURE, config={"key": "value"}
        )

        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]))

        with self.assertRaises(OrchestrationError):
            self.service.run()

    def test_valid_input_filtering_with_azure(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_ALL,
                                            self_harm=AzureThreshold.ALLOW_ALL,
                                            violence=AzureThreshold.ALLOW_ALL,
                                            sexual=AzureThreshold.ALLOW_ALL)

        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]))

        response = self.service.run()

        self.assertIsNotNone(response.module_results.input_filtering)
        self.assertIsNone(response.module_results.output_filtering)
        self.assertIsNotNone(response.orchestration_result.model)

    def test_valid_output_filtering_with_azure(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        self.service.config.filtering = ContentFiltering(output_filtering=OutputFiltering(filters=[content_filter]))

        response = self.service.run()

        self.assertIsNone(response.module_results.input_filtering)
        self.assertIsNotNone(response.module_results.output_filtering)
        self.assertIsNotNone(response.orchestration_result.model)

    def test_valid_input_and_output_filtering(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]),
                                                         OutputFiltering(filters=[content_filter])
                                                        )

        response = self.service.run()

        self.assertIsNotNone(response.module_results.input_filtering)
        self.assertIsNotNone(response.module_results.output_filtering)
        self.assertIsNotNone(response.orchestration_result.model)

    def test_blocked_input_filtering_with_azure(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        self.service.config.template.messages.append(UserMessage("I hate you!."))
        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]))

        with self.assertRaises(OrchestrationError):
            self.service.run()

    def test_valid_input_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()

        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]))

        response = self.service.run()

        self.assertIsNotNone(response.module_results.input_filtering)
        self.assertIsNone(response.module_results.output_filtering)
        self.assertIsNotNone(response.orchestration_result.model)

    def test_valid_output_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()

        self.service.config.filtering = ContentFiltering(output_filtering=OutputFiltering(filters=[content_filter]))

        response = self.service.run()

        self.assertIsNone(response.module_results.input_filtering)
        self.assertIsNotNone(response.module_results.output_filtering)
        self.assertIsNotNone(response.orchestration_result.model)

    def test_valid_input_and_output_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()

        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]),
                                                         OutputFiltering(filters=[content_filter])
                                                        )

        response = self.service.run()

        self.assertIsNotNone(response.module_results.input_filtering)
        self.assertIsNotNone(response.module_results.output_filtering)
        self.assertIsNotNone(response.orchestration_result.model)

    def test_blocked_input_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter(elections=True)

        user_message = UserMessage("We need to manipulate the elections.")

        self.service.config.template.messages.append(user_message)
        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter]))

        with self.assertRaises(OrchestrationError):
            self.service.run()

    def test_blocked_input_filtering_with_azure_and_llama(self):
        content_filter_azure = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)
        content_filter_llama = LlamaGuard38bFilter(hate=True)

        self.service.config.template.messages.append(UserMessage("I hate you!."))
        self.service.config.filtering = ContentFiltering(InputFiltering(filters=[content_filter_azure, content_filter_llama]))

        with self.assertRaises(OrchestrationError):
            self.service.run()
