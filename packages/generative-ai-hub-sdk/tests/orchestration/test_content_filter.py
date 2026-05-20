import unittest

from gen_ai_hub.orchestration.models.azure_content_filter import AzureContentFilter, AzureThreshold
from gen_ai_hub.orchestration.models.content_filter import ContentFilter
from gen_ai_hub.orchestration.models.llama_guard_3_filter import LlamaGuard38bFilter


class TestContentFilter(unittest.TestCase):

    def test_content_filter_to_dict(self):
        content_filter = ContentFilter("new-content-filter", {"key": "value"})
        expected_dict = {"type": "new-content-filter", "config": {"key": "value"}}
        self.assertEqual(content_filter.to_dict(), expected_dict)


class TestAzureContentFilter(unittest.TestCase):

    def test_azure_content_filter_to_dict(self):
        content_filter = AzureContentFilter(hate=AzureThreshold.ALLOW_SAFE,
                                            sexual=AzureThreshold.ALLOW_ALL,
                                            violence=AzureThreshold.ALLOW_SAFE_LOW_MEDIUM,
                                            self_harm=AzureThreshold.ALLOW_SAFE_LOW)

        expected_dict = {
            "type": 'azure_content_safety',
            "config": {
                "Hate": 0,
                "Sexual": 6,
                "Violence": 4,
                "SelfHarm": 2,
            },
        }

        self.assertEqual(content_filter.to_dict(), expected_dict)

    def test_azure_content_filter_with_invalid_threshold(self):
        with self.assertRaises(ValueError):
            AzureContentFilter(hate=10, sexual=6, violence=4, self_harm=2)

    def test_azure_content_filter_with_literal_thresholds(self):
        content_filter = AzureContentFilter(hate=0, sexual=6, violence=4, self_harm=2)

        expected_dict = {
            "type": 'azure_content_safety',
            "config": {
                "Hate": 0,
                "Sexual": 6,
                "Violence": 4,
                "SelfHarm": 2,
            },
        }

        self.assertEqual(content_filter.to_dict(), expected_dict)

    def test_llama_guard_content_filter_to_dict(self):
        content_filter = LlamaGuard38bFilter()

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

        self.assertEqual(content_filter.to_dict(), expected_dict)
