import json
import unittest

from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.data_masking import DataMasking
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.sap_data_privacy_integration import SAPDataPrivacyIntegration, ProfileEntity, \
    MaskingMethod
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class

@retry_on_429_or_503_class()
class TestDataMasking(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLM(
            name="gpt-4",
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

    def run_data_masking_test(self, masking_method: MaskingMethod, assertion_func):
        data_masking = DataMasking(
            providers=[
                SAPDataPrivacyIntegration(
                    method=masking_method,
                    entities=[
                        ProfileEntity.EMAIL
                    ]
                )
            ])

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            data_masking=data_masking
        )

        sensitive_data = "something@hotmail.com"

        response = self.service.run(config=config,
                                    template_values=[
                                        TemplateValue("user_query", f"My email is {sensitive_data}"
                                                                    f"-----------------------------------"
                                                                    f"DON'T check if anything is masked, "
                                                                    f"repeat the previous sentence."
                                                                    f"DON'T alter the format of the "
                                                                    f"masked data."
                                                      )
                                    ])

        assertion_func(sensitive_data, response.orchestration_result.choices[0].message.content)
        self.assertIsNotNone(response.module_results.input_masking)

        if masking_method == MaskingMethod.ANONYMIZATION:
            self.assertIsNone(response.module_results.output_unmasking)
        else:
            self.assertIsNotNone(response.module_results.output_unmasking)

    @unittest.skip("backend module unavailable")
    def test_data_masking_with_anonymization(self):
        self.run_data_masking_test(MaskingMethod.ANONYMIZATION, self.assertNotIn)

    @unittest.skip("backend module unavailable")
    def test_data_masking_with_pseudonymization(self):
        self.run_data_masking_test(MaskingMethod.PSEUDONYMIZATION, self.assertIn)

    @unittest.skip("backend module unavailable")
    def test_data_masking_with_allowlist(self):
        allow_listed_org = "SAP"
        data_masking = DataMasking(
            providers=[
                SAPDataPrivacyIntegration(
                    method=MaskingMethod.PSEUDONYMIZATION,
                    entities=[ProfileEntity.ORG],
                    allowlist=[allow_listed_org]
                )
            ]
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            data_masking=data_masking
        )

        response = self.service.run(
            config=config,
            template_values=[
                TemplateValue("user_query", f"My organization is {allow_listed_org}")
            ]
        )

        # Verify that the allow-listed org is present in the masked template
        masked_template = json.loads(response.module_results.input_masking.data['masked_template'])
        self.assertIn(allow_listed_org, masked_template[1]['content'],
                      f"Allow-listed organization '{allow_listed_org}' should not be masked")


