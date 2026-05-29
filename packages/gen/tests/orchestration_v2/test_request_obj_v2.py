import unittest

from gen_ai_hub.orchestration_v2.models.config import (OrchestrationConfig, ModuleConfig,
CompletionRequestConfigurationReferenceByIdConfigRef,
CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.models.orchestration_request import CompletionPostRequest


class TestOrchestrationRequestV2(unittest.TestCase):

    def setUp(self):
        self.template = Template(
            template=[UserMessage(content="Hello, World!")]
        )
        self.llm = LLMModelDetails(name="gpt-4o-mini")
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template,
                                                            model=self.llm)
        self.module_config = ModuleConfig(prompt_templating=self.prompt_template)
        self.config = OrchestrationConfig(modules=self.module_config)
        self.config_ref_id = CompletionRequestConfigurationReferenceByIdConfigRef(id="1234567890")
        self.config_ref_name = CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef(
            name="test",
            version="1",
            scenario="test"
        )

    def test_with_config(self):

        request = CompletionPostRequest(config=self.config)
        json_request = request.model_dump()
        self.assertIsNone(json_request.get("config_ref"))

    def test_with_config_ref_by_id(self):

        request = CompletionPostRequest(config_ref=self.config_ref_id)
        json_request = request.model_dump()
        self.assertEqual(json_request["config_ref"]["id"], self.config_ref_id.id)
        self.assertIsNone(json_request.get("config"))

    def test_with_config_ref_by_scenario(self):
        request = CompletionPostRequest(config_ref=self.config_ref_name)
        json_request = request.model_dump()
        self.assertEqual(json_request["config_ref"]["name"], self.config_ref_name.name)
        self.assertEqual(json_request["config_ref"]["version"], self.config_ref_name.version)
        self.assertEqual(json_request["config_ref"]["scenario"], self.config_ref_name.scenario)
        self.assertIsNone(json_request.get("config"))

    def test_with_config_and_config_ref(self):
        with self.assertRaises(ValueError):
            CompletionPostRequest(config=self.config, config_ref=self.config_ref_id)

    def test_with_no_config_or_config_ref(self):
        with self.assertRaises(ValueError):
            CompletionPostRequest()