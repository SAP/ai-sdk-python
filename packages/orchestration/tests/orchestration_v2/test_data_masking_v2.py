import unittest

from gen_ai_hub.orchestration_v2.models.data_masking import (MaskingModuleConfig, MaskingProviderConfig, MaskingMethod,
                                                             DPIStandardEntity, ProfileEntity)



class TestDataMasking(unittest.TestCase):

    def test_sap_data_privacy_integration_providers(self):
        data_masking = MaskingModuleConfig(
            providers=[MaskingProviderConfig(
                method=MaskingMethod.ANONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.ADDRESS),
                          DPIStandardEntity(type=ProfileEntity.EMAIL),
                          DPIStandardEntity(type=ProfileEntity.PHONE),
                          DPIStandardEntity(type=ProfileEntity.PERSON), ]
            )]
        )

        expected_dict = {
            'providers':
                [
                    {
                        'type': 'sap_data_privacy_integration',
                        'method': 'anonymization',
                        'entities': [
                            {'type': 'profile-address'},
                            {'type': 'profile-email'},
                            {'type': 'profile-phone'},
                            {'type': 'profile-person'}
                        ]
                    }
                ]
        }

        self.assertEqual(data_masking.model_dump(), expected_dict)

    def test_sap_data_privacy_integration_masking_providers(self):
        data_masking = MaskingModuleConfig(
            masking_providers=[MaskingProviderConfig(
                method=MaskingMethod.ANONYMIZATION,
                entities=[DPIStandardEntity(type=ProfileEntity.ADDRESS),
                          DPIStandardEntity(type=ProfileEntity.EMAIL),
                          DPIStandardEntity(type=ProfileEntity.PHONE),
                          DPIStandardEntity(type=ProfileEntity.PERSON), ]
            )]
        )

        expected_dict = {
            'masking_providers':
                [
                    {
                        'type': 'sap_data_privacy_integration',
                        'method': 'anonymization',
                        'entities': [
                            {'type': 'profile-address'},
                            {'type': 'profile-email'},
                            {'type': 'profile-phone'},
                            {'type': 'profile-person'}
                        ]
                    }
                ]
        }

        self.assertEqual(data_masking.model_dump(), expected_dict)

    def test_maskin_module_config_error(self):
        with self.assertRaises(ValueError):
            MaskingModuleConfig()

        with self.assertRaises(ValueError):
            MaskingModuleConfig(
                masking_providers=[MaskingProviderConfig(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[DPIStandardEntity(type=ProfileEntity.ADDRESS),
                              DPIStandardEntity(type=ProfileEntity.EMAIL),
                              DPIStandardEntity(type=ProfileEntity.PHONE),
                              DPIStandardEntity(type=ProfileEntity.PERSON), ]
                )],
                providers=[MaskingProviderConfig(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[DPIStandardEntity(type=ProfileEntity.ADDRESS),
                              DPIStandardEntity(type=ProfileEntity.EMAIL),
                    ]
                )]
            )
