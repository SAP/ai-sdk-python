import unittest

from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails


class TestLLModelDetails(unittest.TestCase):

    def test_llm_with_no_parameters(self):
        llm = LLMModelDetails(name="gpt-4o-mini")
        json_data = llm.model_dump()
        self.assertEqual(json_data.get("params", {}), {})

    def test_llm_custom_parameters(self):
        params = {"temperature": 0.7, "max_tokens": 100}
        llm = LLMModelDetails(name="gpt-4o-mini", params=params)
        json_data = llm.model_dump()
        self.assertEqual(json_data["params"], params)

    def test_llm_json_serialization(self):
        llm = LLMModelDetails(name="gpt-4o-mini", version="v1", params={"temperature": 0.7})
        expected_dict = {
            "name": "gpt-4o-mini",
            "version": "v1",
            "params": {"temperature": 0.7},
            "max_retries": 2,
            "timeout": 600
        }
        json_data = llm.model_dump()
        self.assertEqual(json_data, expected_dict)

    def test_llm_model_details_with_unsupported_properties(self):
        with self.assertRaises(ValueError):
            LLMModelDetails(name="gpt-4o-mini", max_retries=10)

        with self.assertRaises(ValueError):
            LLMModelDetails(name="gpt-4o-mini", timeout=100000)
