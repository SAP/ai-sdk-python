import unittest

from gen_ai_hub.orchestration.models.data_masking import DataMasking
from gen_ai_hub.orchestration.models.sap_data_privacy_integration import SAPDataPrivacyIntegration, MaskingMethod, \
    ProfileEntity


class TestDataMasking(unittest.TestCase):

    def test_sap_data_privacy_integration(self):
        data_masking = DataMasking(
            providers=[
                SAPDataPrivacyIntegration(
                    method=MaskingMethod.PSEUDONYMIZATION,
                    entities=[ProfileEntity.EMAIL],
                    allowlist=["SAP"]
                )
            ]
        )

        expected_dict = {
            "masking_providers": [
                {
                    "type": "sap_data_privacy_integration",
                    "method": "pseudonymization",
                    "entities": [
                        {
                            "type": "profile-email"
                        }
                    ],
                    "allowlist": ["SAP"],
                    "mask_grounding_input": {
                        "enabled": False
                    }
                }
            ]
        }

        self.assertEqual(data_masking.to_dict(), expected_dict)
