import json

from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.data_masking import (MaskingModuleConfig, MaskingProviderConfig, MaskingMethod,
                                                             DPIStandardEntity, ProfileEntity)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestDataMasking(OrchestrationServiceTestBase):

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

    def test_data_masking_test(self):
        data_masking_config = MaskingModuleConfig(
            providers=[MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.EMAIL)]
            )]
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, masking=data_masking_config)

        config = OrchestrationConfig(modules=module_config)

        sensitive_data = "something@hotmail.com"

        response = self.service.run(config=config,
                                    placeholder_values={"user_query": f"My email is {sensitive_data}"
                                                                    f"-----------------------------------"
                                                                    f"DON'T check if anything is masked, "
                                                                    f"repeat the previous sentence."
                                                                    f"DON'T alter the format of the "
                                                                    f"masked data."
                                                        }
                                    )

        self.assertIsNot(sensitive_data, response.final_result.choices[0].message.content)
        self.assertIsNotNone(response.intermediate_results.input_masking)


    def test_data_masking_with_allowlist(self):
        allow_listed_org = "SAP"
        data_masking_config = MaskingModuleConfig(
           providers=[MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.ORG)],
                allowlist=[allow_listed_org]
            )]
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, masking=data_masking_config)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(
            config=config,
            placeholder_values={"user_query": f"My organisation is {allow_listed_org}"}
        )

        # Verify that the allow-listed org is present in the masked template
        masked_template = json.loads(response.intermediate_results.input_masking.data['masked_template'])
        self.assertIn(allow_listed_org, masked_template[1]['content'],
                      f"Allow-listed organization '{allow_listed_org}' should not be masked")

    def test_data_masking_test_backward_compatibility(self):
        data_masking_config = MaskingModuleConfig(
            masking_providers=[MaskingProviderConfig(
                method=MaskingMethod.PSEUDONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.EMAIL)]
            )]
        )

        module_config = ModuleConfig(prompt_templating=self.prompt_template, masking=data_masking_config)

        config = OrchestrationConfig(modules=module_config)

        sensitive_data = "something@hotmail.com"

        response = self.service.run(config=config,
                                    placeholder_values={"user_query": f"My email is {sensitive_data}"
                                                                      f"-----------------------------------"
                                                                      f"DON'T check if anything is masked, "
                                                                      f"repeat the previous sentence."
                                                                      f"DON'T alter the format of the "
                                                                      f"masked data."
                                                        }
                                    )

        self.assertIsNot(sensitive_data, response.final_result.choices[0].message.content)
        self.assertIsNotNone(response.intermediate_results.input_masking)
