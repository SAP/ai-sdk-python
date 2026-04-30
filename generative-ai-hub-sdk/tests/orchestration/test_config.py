import unittest

from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.content_filter import ContentFilter
from gen_ai_hub.orchestration.models.content_filtering import InputFiltering, OutputFiltering, ContentFiltering
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import Message, Role
from gen_ai_hub.orchestration.models.template import Template


class TestOrchestrationConfig(unittest.TestCase):

    def setUp(self):
        self.template = Template(
            messages=[Message(role=Role.USER, content="Hello, World!")]
        )
        self.llm = LLM(name="gpt-4o-mini")

    def test_minimal_config(self):
        config = OrchestrationConfig(template=self.template, llm=self.llm)

        json_data = config.to_dict()
        self.assertEqual(
            json_data["module_configurations"]["templating_module_config"],
            self.template.to_dict(),
        )
        self.assertEqual(
            json_data["module_configurations"]["llm_module_config"], self.llm.to_dict()
        )
        self.assertNotIn("filtering_module_config", json_data["module_configurations"])

    def test_input_filtering(self):
        input_filter = ContentFilter("new-content-filter", {"key": "value"})
        config = OrchestrationConfig(
            template=self.template, llm=self.llm,
            filtering=ContentFiltering(input_filtering=InputFiltering(filters=[input_filter]))
        )
        json_data = config.to_dict()
        self.assertEqual(
            json_data["module_configurations"]["filtering_module_config"]["input"]["filters"][0],
            input_filter.to_dict(),
        )

    def test_output_filtering(self):
        output_filter = ContentFilter("new-content-filter", {"key": "value"})
        config = OrchestrationConfig(
            template=self.template, llm=self.llm,
            filtering=ContentFiltering(output_filtering=OutputFiltering(filters=[output_filter]))
        )
        json_data = config.to_dict()
        self.assertEqual(
            json_data["module_configurations"]["filtering_module_config"]["output"]["filters"][0],
            output_filter.to_dict(),
        )
