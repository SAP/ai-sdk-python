import unittest

from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.azure_content_filter import AzureContentSafetyInput, AzureContentSafetyOutput
from gen_ai_hub.orchestration_v2.models.content_filtering import FilteringModuleConfig, InputFiltering, OutputFiltering
from gen_ai_hub.orchestration_v2.models.content_filter import AzureContentSafetyInputFilterConfig, AzureContentSafetyOutputFilterConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig


class TestOrchestrationConfigV2(unittest.TestCase):

    def setUp(self):
        self.template = Template(
            template=[UserMessage(content="Hello, World!")]
        )
        self.llm = LLMModelDetails(name="gpt-4o-mini")
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template,
                                                            model=self.llm)

    def test_minimal_config(self):
        module_config = ModuleConfig(prompt_templating=self.prompt_template)
        config = OrchestrationConfig(modules=module_config)

        json_data = config.model_dump()
        self.assertEqual(
            json_data["modules"]["prompt_templating"]["prompt"],
            self.template.model_dump(),
        )
        self.assertEqual(
            json_data["modules"]["prompt_templating"]["model"], self.llm.model_dump()
        )
        self.assertNotIn("filtering_module_config", json_data["modules"])

    def test_input_filtering(self):
        input_filtering = InputFiltering(filters=[
                AzureContentSafetyInputFilterConfig(config=AzureContentSafetyInput(hate=0))
            ])
        content_filter_config = FilteringModuleConfig(
            input= input_filtering
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        json_data = config.model_dump()
        self.assertEqual(
            json_data["modules"]["filtering"]["input"],
            input_filtering.model_dump(),
        )

    def test_output_filtering(self):
        output_filtering = OutputFiltering(filters=[
            AzureContentSafetyOutputFilterConfig(config=AzureContentSafetyOutput(hate=0))
        ])
        content_filter_config = FilteringModuleConfig(
            output=output_filtering
        )
        module_config = ModuleConfig(prompt_templating=self.prompt_template, filtering=content_filter_config)
        config = OrchestrationConfig(modules=module_config)
        json_data = config.model_dump()
        self.assertEqual(
            json_data["modules"]["filtering"]["output"],
            output_filtering.model_dump(),
        )
