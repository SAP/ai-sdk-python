import unittest

from gen_ai_hub.orchestration_v2.models.translation import (TranslationModuleConfig, SAPDocumentTranslationInput,
                                                            SAPDocumentTranslationOutput, InputTranslationConfig,
                                                            OutputTranslationConfig,
                                                            SAPDocumentTranslationApplyToSelector, TranslationConfig,
                                                            SAPDocumentTranslation)

class TestTranslation(unittest.TestCase):
    def test_translation_module_config(self):
        translation_config = TranslationModuleConfig(
            input=SAPDocumentTranslationInput(
                config=InputTranslationConfig(
                    source_language="en-US",
                    target_language="de-DE"
                )
            ),
            output=SAPDocumentTranslationOutput(
                config=OutputTranslationConfig(
                    source_language="de-DE",
                    target_language="fr-FR"
                )
            )
        )
        config_dict = translation_config.model_dump()
        self.assertEqual(config_dict["input"]["config"]["source_language"], "en-US")
        self.assertEqual(config_dict["input"]["config"]["target_language"], "de-DE")
        self.assertEqual(config_dict["input"]["type"], "sap_document_translation")
        self.assertEqual(config_dict["output"]["config"]["source_language"], "de-DE")
        self.assertEqual(config_dict["output"]["config"]["target_language"], "fr-FR")
        self.assertEqual(config_dict["output"]["type"], "sap_document_translation")


    def test_only_input_translation_module(self):
        translation_config = TranslationModuleConfig(
            input=SAPDocumentTranslationInput(
                config=InputTranslationConfig(
                    source_language="en-US",
                    apply_to=[SAPDocumentTranslationApplyToSelector(
                        category="placeholders",
                        items=["user_input"],
                        source_language="en-US"
                    )],
                    target_language="de-DE"
                ),
        ))
        config_dict = translation_config.model_dump()

        self.assertEqual(config_dict["input"]["type"], "sap_document_translation")
        self.assertEqual(config_dict["input"]["config"]["source_language"], "en-US")
        self.assertEqual(config_dict["input"]["config"]["target_language"], "de-DE")
        self.assertEqual(config_dict["input"]["config"]["apply_to"][0]["category"], "placeholders")
        self.assertEqual(config_dict["input"]["config"]["apply_to"][0]["items"], ["user_input"])
        self.assertEqual(config_dict["input"]["config"]["apply_to"][0]["source_language"], "en-US")

        self.assertIsNone(config_dict.get("output"), "Output translation module should be None.")

    def test_only_output_translation_module(self):
        translation_config = TranslationModuleConfig(
            output=SAPDocumentTranslationOutput(
                config=OutputTranslationConfig(
                    source_language="en-US",
                    target_language="de-DE"
                )
            ),
        )
        config_dict = translation_config.model_dump()

        self.assertEqual(config_dict["output"]["type"], "sap_document_translation")
        self.assertEqual(config_dict["output"]["config"]["source_language"], "en-US")
        self.assertEqual(config_dict["output"]["config"]["target_language"], "de-DE")

        self.assertIsNone(config_dict.get("intput"), "Output translation module should be None.")

    def test_only_output_translation_module_target_language_not_str(self):
        translation_config = TranslationModuleConfig(
            output=SAPDocumentTranslationOutput(
                config=OutputTranslationConfig(
                    source_language="en-US",
                    target_language=SAPDocumentTranslationApplyToSelector(
                        category="placeholders",
                        items=["user_input"],
                        source_language="en-US"
                    )
                )
            ),
        )
        config_dict = translation_config.model_dump()

        self.assertEqual(config_dict["output"]["type"], "sap_document_translation")
        self.assertEqual(config_dict["output"]["config"]["source_language"], "en-US")
        self.assertEqual(config_dict["output"]["config"]["target_language"]["category"], "placeholders")
        self.assertEqual(config_dict["output"]["config"]["target_language"]["items"], ["user_input"])
        self.assertEqual(config_dict["output"]["config"]["target_language"]["source_language"], "en-US")

        self.assertIsNone(config_dict.get("intput"), "Output translation module should be None.")

class TestTranslationBackwardCompatibility(unittest.TestCase):
    def test_translation_module_config_backward_compatibility(self):
        translation_config = TranslationModuleConfig(
            input=SAPDocumentTranslation(
                config=TranslationConfig(
                    source_language="en-US",
                    target_language="de-DE"
                )
            ),
            output=SAPDocumentTranslation(
                config=TranslationConfig(
                    source_language="de-DE",
                    target_language="fr-FR"
                )
            )
        )
        config_dict = translation_config.model_dump()
        self.assertEqual(config_dict["input"]["config"]["source_language"], "en-US")
        self.assertEqual(config_dict["input"]["config"]["target_language"], "de-DE")
        self.assertEqual(config_dict["input"]["type"], "sap_document_translation")
        self.assertEqual(config_dict["output"]["config"]["source_language"], "de-DE")
        self.assertEqual(config_dict["output"]["config"]["target_language"], "fr-FR")
        self.assertEqual(config_dict["output"]["type"], "sap_document_translation")
