"""Integration tests for the prompt optimization flow."""
import unittest

from gen_ai_hub.optimizations.models.optimization_config import PromptOptimizationConfig
from gen_ai_hub.optimizations.models.optimization_results import OptimizationResults
from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplate, PromptTemplateSpec
from integration_tests.optimizations.test_base import OptimizationClientTestBase

BASE_PROMPT_NAME = "sdktest-opt-base-prompt"
BASE_PROMPT_VERSION = "0.0.1"
BASE_PROMPT_SCENARIO = "genai-optimizations"
TARGET_MODEL = "gemini-2.5-pro:001"
TARGET_PROMPT_NAME = "sdktest-opt-target-prompt"
TARGET_PROMPT_MAPPING = {TARGET_MODEL: f"{TARGET_PROMPT_NAME}:0.0.1"}
OPTIMIZATION_METRIC = "JSON_Match"


class TestOptimizationFlow(OptimizationClientTestBase):
    """Integration tests for the optimization job flow."""

    @classmethod
    def setUpClass(cls):
        """Create base prompt template for tests."""
        super().setUpClass()
        cls.base_prompt_id = None
        cls.base_prompt_ref = None

    def setUp(self):
        """Set up client and create base prompt template before each test class run."""
        super().setUp()
        if self.__class__.base_prompt_id is None:
            try:
                prompt_client = PromptTemplateClient(
                    proxy_client=self.client._gen_ai_hub_proxy_client
                )
                spec = PromptTemplateSpec(
                    template=[
                        PromptTemplate(role="system", content="You are a helpful assistant"),
                        PromptTemplate(
                            role="user",
                            content=(
                                "Giving the following message --- {{?input}} --- "
                                "Extract and return a json with the following keys and values: "
                                "- 'urgency' as one of `high`, `medium`, `low` "
                                "- 'sentiment' as one of `negative`, `neutral`, `positive` "
                                "- 'categories' Create a dictionary with categories as keys and boolean values (True/False), "
                                "where the value indicates whether the category is one of the best matching support category tags from: "
                                "`emergency_repair_services`, `routine_maintenance_requests`, `quality_and_safety_concerns`, "
                                "`specialized_cleaning_services`, `general_inquiries`, `sustainability_and_environmental_practices`, "
                                "`training_and_support_requests`, `cleaning_services_scheduling`, `customer_feedback_and_complaints`, "
                                "`facility_management_issues` "
                                "Your complete message should be a valid json string that can be read directly and only contain "
                                "the keys mentioned in the list above. Never enclose it in ```json...```, no newlines, no unnecessary whitespaces."
                            ),
                        ),
                    ],
                    defaults={"input": ""},
                    additional_fields={
                        "modelParams": {"temperature": 0.7, "max_tokens": 100},
                        "modelGroup": "chat",
                    },
                )
                response = prompt_client.create_prompt_template(
                    name=BASE_PROMPT_NAME,
                    version=BASE_PROMPT_VERSION,
                    scenario=BASE_PROMPT_SCENARIO,
                    prompt_template_spec=spec,
                )
                self.__class__.base_prompt_id = response.id
                self.__class__.base_prompt_ref = f"{BASE_PROMPT_SCENARIO}/{BASE_PROMPT_NAME}:{BASE_PROMPT_VERSION}"
                self.__class__.prompt_client = prompt_client
                print(f"Base prompt template created: {self.__class__.base_prompt_id}")
            except Exception as err:
                self.fail(f"Failed to create base prompt template: {err}")

    @classmethod
    def tearDownClass(cls):
        """Delete the base prompt template created for tests."""
        if hasattr(cls, "prompt_client") and hasattr(cls, "base_prompt_id") and cls.base_prompt_id:
            try:
                cls.prompt_client.delete_prompt_template_by_id(cls.base_prompt_id)
                print(f"Base prompt template deleted: {cls.base_prompt_id}")
            except Exception as err:
                print(f"Warning: Could not delete prompt template {cls.base_prompt_id}: {err}")

    def test_optimize_wait_for_completion(self):
        """Test optimization job completes successfully and returns results."""
        config = PromptOptimizationConfig(
            dataset_path=self.dataset_path,
            target_prompt_mapping=TARGET_PROMPT_MAPPING,
            target_models=[TARGET_MODEL],
            base_prompt=self.base_prompt_ref,
            optimization_metric=OPTIMIZATION_METRIC,
            prototype_mode=True,
        )

        run = self.client.optimize(config)
        self.assertIsNotNone(run)

        run.wait_for_completion()

        debug_info = run.get_debug_info()
        current_status = run.get_current_status()
        self.assertEqual(
            current_status.name, "COMPLETED",
            f"Run did not complete. Status: {current_status}, Debug info: {debug_info}",
        )

        results = run.results()
        self.assertIsInstance(results, OptimizationResults)
        self.assertIsNotNone(results.metrics)
        self.assertTrue(
            len(results.metrics.resources or []) > 0,
            "Expected at least one metric resource in results",
        )


if __name__ == "__main__":
    unittest.main()
