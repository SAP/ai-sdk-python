import unittest

from gen_ai_hub.orchestration_v2.models.azure_content_filter import (AzureContentSafetyInput, AzureContentSafetyOutput,
                                                                     AzureThreshold, AzureContentFilter)
from gen_ai_hub.orchestration_v2.models.content_filtering import InputFiltering
from gen_ai_hub.orchestration_v2.models.content_filter import (AzureContentSafetyInputFilterConfig,
AzureContentSafetyOutputFilterConfig, LlamaGuard38bFilterConfig, ContentFilter, ContentFilterProvider)
from gen_ai_hub.orchestration_v2.models.llama_guard_3_filter import LlamaGuard38bFilter


class TestContentFilters(unittest.TestCase):

    def test_azure_input_content_filter_to_dict(self):
        input_filtering = InputFiltering(filters=[
            AzureContentSafetyInputFilterConfig(config=AzureContentSafetyInput(
                hate=AzureThreshold.ALLOW_SAFE,
                sexual=AzureThreshold.ALLOW_ALL,
                violence=AzureThreshold.ALLOW_SAFE_LOW_MEDIUM,
                self_harm=AzureThreshold.ALLOW_SAFE_LOW
            ))
        ])

        expected_dict = {
            "filters": [
                {"config":
                    {
                    "hate": 0,
                    "sexual": 6,
                    "violence": 4,
                    "self_harm": 2,
                    "prompt_shield": False
                    },
                    "type": 'azure_content_safety'
                }],
        }

        self.assertEqual(input_filtering.model_dump(), expected_dict)

    def test_azure_input_content_filter_with_invalid_threshold(self):
        with self.assertRaises(ValueError):
            AzureContentSafetyInput(hate=10, sexual=6, violence=4, self_harm=2)

    def test_azure_input_content_filter_with_literal_thresholds(self):
        content_filter_config = AzureContentSafetyInput(hate=0, sexual=6, violence=4, self_harm=2)
        content_filter = AzureContentSafetyInputFilterConfig(config=content_filter_config)

        expected_dict = {
            "type": 'azure_content_safety',
            "config": {
                "hate": 0,
                "sexual": 6,
                "violence": 4,
                "self_harm": 2,
                "prompt_shield": False
            },
        }

        self.assertEqual(content_filter.model_dump(), expected_dict)

    def test_azure_output_content_filter_with_literal_thresholds(self):
        content_filter_config = AzureContentSafetyOutput(hate=0, sexual=6, violence=4, self_harm=2)
        content_filter = AzureContentSafetyOutputFilterConfig(config=content_filter_config)

        expected_dict = {
            "type": 'azure_content_safety',
            "config": {
                "hate": 0,
                "sexual": 6,
                "violence": 4,
                "self_harm": 2,
                "protected_material_code": False
            },
        }

        self.assertEqual(content_filter.model_dump(), expected_dict)

    def test_llama_guard_content_filter_to_dict(self):
        content_filter = LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter())

        expected_dict = {
            "type": 'llama_guard_3_8b',
            "config":{
                "violent_crimes": False,
                "non_violent_crimes": False,
                "sex_crimes": False,
                "child_exploitation": False,
                "defamation": False,
                "specialized_advice": False,
                "privacy": False,
                "intellectual_property": False,
                "indiscriminate_weapons": False,
                "hate": False,
                "self_harm": False,
                "sexual_content": False,
                "elections": False,
                "code_interpreter_abuse": False,
            }
        }

        self.assertEqual(content_filter.model_dump(), expected_dict)

class TestContentFiltersBackwardCompatibility(unittest.TestCase):
    def test_azure_content_filter_to_dict_bc(self):
        content_filter_config = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                                   sexual=AzureThreshold.ALLOW_ALL,
                                                   violence=AzureThreshold.ALLOW_SAFE_LOW_MEDIUM,
                                                   self_harm=AzureThreshold.ALLOW_SAFE_LOW)
        content_filter = ContentFilter(type=ContentFilterProvider.AZURE, config=content_filter_config)

        expected_dict = {
            "type": 'azure_content_safety',
            "config": {
                "hate": 0,
                "sexual": 6,
                "violence": 4,
                "self_harm": 2,
            },
        }

        self.assertEqual(content_filter.model_dump(), expected_dict)

    def test_llama_guard_content_filter_to_dict_backward_compatibility(self):
        content_filter = ContentFilter(type=ContentFilterProvider.LLAMA_GUARD_3_8B,
                                       config=LlamaGuard38bFilter())

        expected_dict = {
            "type": 'llama_guard_3_8b',
            "config": {
                "violent_crimes": False,
                "non_violent_crimes": False,
                "sex_crimes": False,
                "child_exploitation": False,
                "defamation": False,
                "specialized_advice": False,
                "privacy": False,
                "intellectual_property": False,
                "indiscriminate_weapons": False,
                "hate": False,
                "self_harm": False,
                "sexual_content": False,
                "elections": False,
                "code_interpreter_abuse": False,
            }
        }

        self.assertEqual(content_filter.model_dump(), expected_dict)
