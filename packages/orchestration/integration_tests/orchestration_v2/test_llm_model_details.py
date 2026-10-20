from parameterized import parameterized

from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestLLM(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
            ]
        )

    def test_invalid_llm_name(self):
        llm = LLMModelDetails(
            name="unknown-llm",
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=llm)
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)
        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_invalid_llm_version(self):
        llm = LLMModelDetails(
            name="gpt-4o-mini",
            version="unknown",
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=llm)
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_invalid_llm_parameters(self):
        llm = LLMModelDetails(
            name="gpt-4o-mini",
            params={
                "unknown_parameter": "value",
            },
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=llm)
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    @parameterized.expand(
        [
            "gpt-4o",
            "gpt-4o-mini",
            "gemini-2.5-flash",
        ]
    )
    def test_valid_llm(self, name="gpt-4o-mini"):
        llm = LLMModelDetails(
            name=name,
            params={
                'temperature': 0.0,
            }
        )

        prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=llm)
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertTrue(response.final_result.model.startswith(llm.name))
