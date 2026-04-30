import unittest

from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from gen_ai_hub.orchestration.models.translation.sap_document_translation import SAPDocumentTranslation
from gen_ai_hub.orchestration.models.translation.translation import InputTranslationConfig, OutputTranslationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template
from gen_ai_hub.orchestration.service import OrchestrationService
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.template import TemplateValue



class TestTranslation(OrchestrationServiceTestBase):
    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLM(
            name="gpt-4o",
            parameters={
                'temperature': 0.0,
            }
        )
        self.template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ]
        )

    def test_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        input_config = InputTranslationConfig(source_language="en-US", target_language="de-DE")
        output_config = OutputTranslationConfig(source_language="de-DE", target_language="en-US")

        translation_module = SAPDocumentTranslation(
            input_translation_config=input_config,
            output_translation_config=output_config
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            translation=translation_module
        )

        response = self.service.run(config=config,
                                     template_values=[
                                         TemplateValue("user_query", "What is orchestration service?"),
                                     ])

        # Check the input translation output
        self.assertRegex(response.module_results.input_translation.data["translated_template"], "Was ist .* Orchestrierungsservice")
        # Check the output translation output
        self.assertIn("choices", response.module_results.output_translation.data)
        self.assertIn("orchestration", response.module_results.output_translation.data.get("choices")[0].get("message").get("content"))
        # Check the orchestration result
        self.assertIn("orchestration", response.orchestration_result.choices[0].message.content)

    def test_only_input_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        input_config = InputTranslationConfig(source_language="en-US", target_language="de-DE")

        translation_module = SAPDocumentTranslation(
            input_translation_config=input_config
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            translation=translation_module
        )

        response = self.service.run(config=config,
                                     template_values=[
                                         TemplateValue("user_query", "What is orchestration service?"),
                                     ])

        # Check the input translation output
        self.assertRegex(response.module_results.input_translation.data["translated_template"], "Was ist .* Orchestrierungsservice")
        # Check the output translation output
        self.assertIsNone(response.module_results.output_translation)
        # Check the orchestration result
        self.assertIn("Orchestrierungsservice", response.orchestration_result.choices[0].message.content)

    def test_only_output_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        output_config = OutputTranslationConfig(source_language="en-US", target_language="de-DE")

        translation_module = SAPDocumentTranslation(
            output_translation_config=output_config
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            translation=translation_module
        )

        response = self.service.run(config=config,
                                     template_values=[
                                         TemplateValue("user_query", "What is orchestration service?"),
                                     ])

        # Check the input translation output
        self.assertIsNone(response.module_results.input_translation)
        # Check the output translation output
        self.assertIn("choices", response.module_results.output_translation.data)
        self.assertIn("Orchestrierungsservice", response.module_results.output_translation.data.get("choices")[0].get("message").get("content"))
        # Check the orchestration result
        self.assertIn("Orchestrierungsservice", response.orchestration_result.choices[0].message.content)



