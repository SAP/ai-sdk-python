from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError
from gen_ai_hub.orchestration_v2.models.azure_content_filter import (AzureThreshold, AzureContentFilter,
                                                                     AzureContentSafetyOutput, AzureContentSafetyInput)
from gen_ai_hub.orchestration_v2.models.llama_guard_3_filter import LlamaGuard38bFilter
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.content_filter import (
    AzureContentSafetyOutputFilterConfig, ContentFilter, ContentFilterProvider,
    AzureContentSafetyInputFilterConfig, LlamaGuard38bFilterConfig
)
from gen_ai_hub.orchestration_v2.models.content_filtering import (InputFiltering, OutputFiltering,
                                                                  FilteringModuleConfig)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase


class TestContentFilter(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.llm = LLMModelDetails(
            name="gpt-4o-mini",
            version="latest",
            params={"max_tokens": 50, "temperature": 0.0},
        )
        self.template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
            ]
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)
        self.service = OrchestrationService(
            api_url=self.api_url
        )

    def test_valid_input_filtering_with_azure(self):
        content_filter = AzureContentSafetyInput(hate=AzureThreshold.ALLOW_ALL,
                                            self_harm=AzureThreshold.ALLOW_ALL,
                                            violence=AzureThreshold.ALLOW_ALL,
                                            sexual=AzureThreshold.ALLOW_ALL,
                                            prompt_shield=True)

        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                AzureContentSafetyInputFilterConfig(config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNotNone(response.intermediate_results.input_filtering)
        self.assertIsNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_valid_output_filtering_with_azure(self):
        content_filter = AzureContentSafetyOutput(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        content_filter_config = FilteringModuleConfig(
            output=
            OutputFiltering(filters=[
                AzureContentSafetyOutputFilterConfig(config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNone(response.intermediate_results.input_filtering)
        self.assertIsNotNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_valid_input_and_output_filtering(self):
        content_filter_output = AzureContentSafetyOutput(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        content_filter_input = AzureContentSafetyInput(hate=AzureThreshold.ALLOW_ALL,
                                                 self_harm=AzureThreshold.ALLOW_ALL,
                                                 violence=AzureThreshold.ALLOW_ALL,
                                                 sexual=AzureThreshold.ALLOW_ALL,
                                                 prompt_shield=True)

        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                AzureContentSafetyInputFilterConfig(config=content_filter_input)
            ]),
            output=
            OutputFiltering(filters=[
                AzureContentSafetyOutputFilterConfig(config=content_filter_output)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNotNone(response.intermediate_results.input_filtering)
        self.assertIsNotNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_blocked_input_filtering_with_azure(self):
        content_filter = AzureContentSafetyInput(hate=AzureThreshold.ALLOW_SAFE,
                                                 self_harm=AzureThreshold.ALLOW_SAFE,
                                                 violence=AzureThreshold.ALLOW_SAFE,
                                                 sexual=AzureThreshold.ALLOW_SAFE)

        self.template.template.append(UserMessage(content="I hate you!."))
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                AzureContentSafetyInputFilterConfig(config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_valid_input_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()

        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                LlamaGuard38bFilterConfig(config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNotNone(response.intermediate_results.input_filtering)
        self.assertIsNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_valid_output_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()

        content_filter_config = FilteringModuleConfig(
            output=
            OutputFiltering(filters=[
                LlamaGuard38bFilterConfig(config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNone(response.intermediate_results.input_filtering)
        self.assertIsNotNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_valid_input_and_output_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                LlamaGuard38bFilterConfig(config=content_filter)
            ]),
            output=
            OutputFiltering(filters=[
                LlamaGuard38bFilterConfig(config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNotNone(response.intermediate_results.input_filtering)
        self.assertIsNotNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_blocked_input_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter(elections=True)
        self.template.template.append(UserMessage(content="We need to manipulate the elections."))
        content_filter_config = FilteringModuleConfig(
            input=InputFiltering(filters=[LlamaGuard38bFilterConfig(config=content_filter)])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)


    def test_blocked_input_filtering_with_azure_and_llama(self):
        content_filter_azure = AzureContentSafetyInput(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)
        content_filter_llama = LlamaGuard38bFilter(hate=True)
        self.template.template.append(UserMessage(content="I hate you!."))
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                AzureContentSafetyInputFilterConfig(config=content_filter_azure),
                LlamaGuard38bFilterConfig(config=content_filter_llama)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

class TestContentFilterBackwardCompatibility(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.llm = LLMModelDetails(
            name="gpt-4o-mini",
            version="latest",
            params={"max_tokens": 50, "temperature": 0.0},
        )
        self.template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
            ]
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)
        self.service = OrchestrationService(
            api_url=self.api_url
        )

    def test_valid_input_and_output_filtering(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.AZURE, config=content_filter)
            ]),
            output=
            OutputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.AZURE, config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNotNone(response.intermediate_results.input_filtering)
        self.assertIsNotNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_blocked_input_filtering_with_azure(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)

        self.template.template.append(UserMessage(content="I hate you!."))
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.AZURE, config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_valid_input_and_output_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter()
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.LLAMA_GUARD_3_8B, config=content_filter)
            ]),
            output=
            OutputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.LLAMA_GUARD_3_8B, config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIsNotNone(response.intermediate_results.input_filtering)
        self.assertIsNotNone(response.intermediate_results.output_filtering)
        self.assertIsNotNone(response.final_result.model)

    def test_blocked_input_filtering_with_llama_guard38b(self):
        content_filter = LlamaGuard38bFilter(elections=True)
        self.template.template.append(UserMessage(content="We need to manipulate the elections."))
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.LLAMA_GUARD_3_8B, config=content_filter)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)


    def test_blocked_input_filtering_with_azure_and_llama(self):
        content_filter_azure = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            self_harm=AzureThreshold.ALLOW_SAFE,
                                            violence=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_SAFE)
        content_filter_llama = LlamaGuard38bFilter(hate=True)
        self.template.template.append(UserMessage(content="I hate you!."))
        content_filter_config = FilteringModuleConfig(
            input=
            InputFiltering(filters=[
                ContentFilter(type=ContentFilterProvider.LLAMA_GUARD_3_8B, config=content_filter_llama),
                ContentFilter(type=ContentFilterProvider.AZURE, config=content_filter_azure)
            ])
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)