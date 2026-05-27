import unittest

from gen_ai_hub.orchestration.models.translation.translation import InputTranslationConfig, \
    InputTranslationModule, OutputTranslationConfig, OutputTranslationModule, TranslationType
from gen_ai_hub.orchestration.models.translation.sap_document_translation import SAPDocumentTranslation
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import Message, Role
from gen_ai_hub.orchestration.models.template import Template


class TestTranslation(unittest.TestCase):
    def test_input_translation_config(self):
        config = InputTranslationConfig(source_language="en-US", target_language="de-DE")
        config_dict = config.to_dict()
        self.assertEqual(config_dict["source_language"], "en-US")
        self.assertEqual(config_dict["target_language"], "de-DE")

    def test_input_translation_module(self):
        config = InputTranslationConfig(source_language="en-US", target_language="de-DE")
        translation_module = InputTranslationModule(type=TranslationType.SAP_DOCUMENT_TRANSLATION, config=config)
        module_dict = translation_module.to_dict()
        self.assertEqual(module_dict["type"], TranslationType.SAP_DOCUMENT_TRANSLATION)
        self.assertEqual(module_dict["config"]["source_language"], "en-US")
        self.assertEqual(module_dict["config"]["target_language"], "de-DE")

    def test_output_translation_config(self):
        config = OutputTranslationConfig(target_language="de-DE", source_language="en-US")
        config_dict = config.to_dict()
        self.assertEqual(config_dict["target_language"], "de-DE")
        self.assertEqual(config_dict["source_language"], "en-US")

    def test_output_translation_module(self):
        config = OutputTranslationConfig(target_language="de-DE", source_language="en-US")
        translation_module = OutputTranslationModule(type=TranslationType.SAP_DOCUMENT_TRANSLATION, config=config)
        module_dict = translation_module.to_dict()
        self.assertEqual(module_dict["type"], TranslationType.SAP_DOCUMENT_TRANSLATION)
        self.assertEqual(module_dict["config"]["target_language"], "de-DE")
        self.assertEqual(module_dict["config"]["source_language"], "en-US")

    def test_sap_docu_translation(self):
        input_config = InputTranslationConfig(source_language="en-US", target_language="de-DE")
        output_config = OutputTranslationConfig(target_language="de-DE", source_language="en-US")

        translation_module = SAPDocumentTranslation(
            input_translation_config=input_config,
            output_translation_config=output_config
        )
        template = Template(
            messages=[Message(role=Role.USER, content="Hello, World!")]
        )
        llm = LLM(name="gpt-4o-mini")

        config = OrchestrationConfig(
            template=template, llm=llm,
            translation= translation_module
        )

        conf_dict = config.to_dict()

        self.assertIn("module_configurations", conf_dict)
        self.assertIn("input_translation_module_config", conf_dict["module_configurations"])
        self.assertIn("output_translation_module_config", conf_dict["module_configurations"])

        input_translation_module_config = translation_module.input_translation.to_dict()
        output_translation_module_config = translation_module.input_translation.to_dict()

        self.assertEqual(input_translation_module_config["type"], TranslationType.SAP_DOCUMENT_TRANSLATION)
        self.assertEqual(input_translation_module_config["config"]["source_language"], "en-US")
        self.assertEqual(input_translation_module_config["config"]["target_language"], "de-DE")

        self.assertEqual(output_translation_module_config["type"], TranslationType.SAP_DOCUMENT_TRANSLATION)
        self.assertEqual(output_translation_module_config["config"]["target_language"], "de-DE")
        self.assertEqual(output_translation_module_config["config"]["source_language"], "en-US")

    def test_only_input_translation_module(self):
        input_config = InputTranslationConfig(source_language="en-US", target_language="de-DE")

        translation_module = SAPDocumentTranslation(
            input_translation_config=input_config)

        input_translation_module_config = translation_module.input_translation.to_dict()

        self.assertEqual(input_translation_module_config["type"], TranslationType.SAP_DOCUMENT_TRANSLATION)
        self.assertEqual(input_translation_module_config["config"]["source_language"], "en-US")
        self.assertEqual(input_translation_module_config["config"]["target_language"], "de-DE")

        self.assertIsNone(translation_module.output_translation, "Output translation module should be None.")

    def test_only_output_translation_module(self):
        output_config = OutputTranslationConfig(target_language="de-DE", source_language="en-US")

        translation_module = SAPDocumentTranslation(output_translation_config=output_config)

        output_translation_module_config = translation_module.output_translation.to_dict()

        self.assertEqual(output_translation_module_config["type"], TranslationType.SAP_DOCUMENT_TRANSLATION)
        self.assertEqual(output_translation_module_config["config"]["target_language"], "de-DE")
        self.assertEqual(output_translation_module_config["config"]["source_language"], "en-US")

        self.assertIsNone(translation_module.input_translation, "Input translation module should be None.")