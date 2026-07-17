from parameterized import parameterized

from gen_ai_hub.orchestration.exceptions import OrchestrationError
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage
from gen_ai_hub.orchestration.models.template import Template
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class

@retry_on_429_or_503_class()
class TestLLM(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
            ]
        )

    def test_invalid_llm_name(self):

        llm = LLM(
            name="unknown-llm",
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=llm,
        )

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_invalid_llm_version(self):

        llm = LLM(
            name="gpt-4o-mini",
            version="unknown",
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=llm,
        )

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_invalid_llm_parameters(self):

        llm = LLM(
            name="gpt-4o-mini",
            parameters={
                "unknown_parameter": "value",
            },
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=llm,
        )

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    @parameterized.expand(
        [
          #  "gpt-4",
            "gpt-4o",
            "gpt-4o-mini",
            "gemini-2.5-flash",
        ]
    )
    def test_valid_llm(self, name="gpt-4o-mini"):

        llm = LLM(
            name=name,
            parameters={
                'temperature': 0.0,
            }
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=llm,
        )

        response = self.service.run(config=config)

        self.assertTrue(response.orchestration_result.model.startswith(llm.name))


