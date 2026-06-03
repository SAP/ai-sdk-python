import unittest

from gen_ai_hub.orchestration.models.llm import LLM


class TestLLM(unittest.TestCase):
    def test_llm_default_version(self):
        llm = LLM("gpt-4o-mini")
        json_data = llm.to_dict()
        self.assertEqual(json_data["model_version"], "latest")

    def test_llm_with_no_parameters(self):
        llm = LLM("gpt-4o-mini")
        json_data = llm.to_dict()
        self.assertEqual(json_data["model_params"], {})

    def test_llm_custom_parameters(self):
        params = {"temperature": 0.7, "max_tokens": 100}
        llm = LLM("gpt-4o-mini", parameters=params)
        json_data = llm.to_dict()
        self.assertEqual(json_data["model_params"], params)

    def test_llm_json_serialization(self):
        llm = LLM("gpt-4o-mini", "v1", {"temperature": 0.7})
        expected_dict = {
            "model_name": "gpt-4o-mini",
            "model_version": "v1",
            "model_params": {"temperature": 0.7},
        }
        json_data = llm.to_dict()
        self.assertEqual(json_data, expected_dict)
