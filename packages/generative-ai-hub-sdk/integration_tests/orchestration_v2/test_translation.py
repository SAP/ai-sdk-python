from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from gen_ai_hub.orchestration_v2.models.translation import (TranslationModuleConfig, InputTranslationConfig,
                                                            OutputTranslationConfig, SAPDocumentTranslationInput,
                                                            SAPDocumentTranslationOutput,
                                                            SAPDocumentTranslationApplyToSelector,
                                                            TranslationConfig, SAPDocumentTranslation)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestTranslation(OrchestrationServiceTestBase):
    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o",
            params={
                'temperature': 0.0,
            }
        )
        self.template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ]
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)

    def test_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        input_config = SAPDocumentTranslationInput(
            config=InputTranslationConfig(
                source_language="en-US",
                target_language="de-DE"
            ))
        output_config = SAPDocumentTranslationOutput(
            config=OutputTranslationConfig(
                source_language="de-DE",
                target_language="en-US"
            ))

        translation_config = TranslationModuleConfig(
            input=input_config,
            output=output_config
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config,
                                     placeholder_values={"user_query": "What is orchestration service?"}
                                    )

        # Check the input translation output
        self.assertRegex(
            response.intermediate_results.input_translation.data["translated_template"],
            "Was ist .* Orchestrierungsservice")
        # Check the output translation output
        self.assertIn("choices", response.intermediate_results.output_translation.data)
        self.assertIn(
            "orchestration",
            response.intermediate_results.output_translation.data.get("choices")[0].get("message").get("content"))
        # Check the orchestration result
        self.assertIn("orchestration", response.final_result.choices[0].message.content)

    def test_only_input_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        input_config = SAPDocumentTranslationInput(
            config=InputTranslationConfig(
                source_language="en-US",
                target_language="de-DE"
            ))

        translation_config = TranslationModuleConfig(
            input=input_config
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config,
                                    placeholder_values={"user_query": "What is orchestration service?"}
                                    )

        # Check the input translation output
        self.assertRegex(
            response.intermediate_results.input_translation.data["translated_template"],
            "Was ist .* Orchestrierungsservice")
        # Check the output translation output
        self.assertIsNone(response.intermediate_results.output_translation)
        # Check the orchestration result
        self.assertIn("Orchestrierungsservice", response.final_result.choices[0].message.content)

    def test_only_output_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        output_config = SAPDocumentTranslationOutput(
            config=OutputTranslationConfig(
                source_language="en-US", target_language="de-DE"
            ))

        translation_config = TranslationModuleConfig(
            output=output_config
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config,
                                    placeholder_values={"user_query": "What is orchestration service?"}
                                    )

        # Check the input translation output
        self.assertIsNone(response.intermediate_results.input_translation)
        # Check the output translation output
        self.assertIn("choices", response.intermediate_results.output_translation.data)
        self.assertIn(
            "Orchestrierungsservice",
                    response.intermediate_results.output_translation.data.get("choices")[0].get("message").get("content"))
        # Check the orchestration result
        self.assertIn("Orchestrierungsservice", response.final_result.choices[0].message.content)

    def test_input_translation_apply_to_only_user_placeholder(self):
        input_config = SAPDocumentTranslationInput(
            config=InputTranslationConfig(
                target_language="de-DE",
                apply_to=[
                    SAPDocumentTranslationApplyToSelector(
                        category="placeholders",
                        items=["user_query"],
                        source_language="en-US",
                    )
                ],
            ),
        )
        translation_config = TranslationModuleConfig(input=input_config)
        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(
            config=config,
            placeholder_values={"user_query": "What is orchestration service?"},
        )

        translated = response.intermediate_results.input_translation.data["translated_placeholders"]["user_query"]

        self.assertRegex(translated, r"Was ist .*Orchestrierungsservice")

    def test_input_translation_translate_history(self):
        input_config = SAPDocumentTranslationInput(
            translate_messages_history=False,
            config=InputTranslationConfig(
                target_language="de-DE"),
            )
        translation_config = TranslationModuleConfig(input=input_config)
        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(
            config=config,
            placeholder_values={"user_query": "What is orchestration service?"},
            history=[UserMessage(content="Hello, World!")],
        )

        translated = response.intermediate_results.input_translation.data["translated_template"]

        self.assertRegex(translated, r"Was ist .*Orchestrierungsservice")
        self.assertNotIn(translated, "Welt")

    def test_output_translation_target_language_from_placeholder_selector(self):
        output_config = SAPDocumentTranslationOutput(
            config=OutputTranslationConfig(
                source_language="en-US",
                target_language=SAPDocumentTranslationApplyToSelector(
                    category="placeholders",
                    items=["target_lang"],
                    source_language="en-US",
                ),
            )
        )

        translation_config = TranslationModuleConfig(output=output_config)
        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        with self.assertRaises(OrchestrationError) as ctx:
            self.service.run(
                config=config,
                placeholder_values={
                    "user_query": "What is orchestration service?",
                    "target_lang": "de-DE",
                },
            )

        self.assertIn("is not present in translation.input.config.apply_to", str(ctx.exception))


@retry_on_429_or_503_class()
class TestTranslationBackwardCompatibility(OrchestrationServiceTestBase):
    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o",
            params={
                'temperature': 0.0,
            }
        )
        self.template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ]
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)

    def test_translation(self):
        """
        Run orchestration service with translation configuration.
        """

        input_config = SAPDocumentTranslation(
            config=TranslationConfig(
                source_language="en-US",
                target_language="de-DE"
            ))
        output_config = SAPDocumentTranslation(
            config=TranslationConfig(
                source_language="de-DE", target_language="en-US"
            ))

        translation_config = TranslationModuleConfig(
            input=input_config,
            output=output_config
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, translation=translation_config)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config,
                                     placeholder_values={"user_query": "What is orchestration service?"}
                                    )

        # Check the input translation output
        self.assertRegex(
            response.intermediate_results.input_translation.data["translated_template"],
            "Was ist .* Orchestrierungsservice")
        # Check the output translation output
        self.assertIn("choices", response.intermediate_results.output_translation.data)
        self.assertIn("orchestration",
                response.intermediate_results.output_translation.data.get("choices")[0].get("message").get("content"))
        # Check the orchestration result
        self.assertIn("orchestration", response.final_result.choices[0].message.content)
