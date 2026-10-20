"""
Integration tests for single execution flow in evaluations.
Tests evaluation with a single EvaluationConfig.
"""
import unittest
from gen_ai_hub.evaluations.models.evaluation_config import EvaluationConfig
from gen_ai_hub.evaluations.models.dataset_config import Dataset
from gen_ai_hub.evaluations.models.metric_config import MetricConfig, MetricRef
from gen_ai_hub.prompt_registry.models.prompt_template import (
    PromptTemplateSpec,
    PromptTemplate,
)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails as LLM
from .test_base import EvaluationClientTestBase


class TestSingleExecutionFlow(EvaluationClientTestBase):
    """Test single evaluation execution flow."""

    def test_evaluate_with_llm_and_template_spec(self):
        """Test evaluation with LLM and PromptTemplateSpec."""
        evaluation_config = EvaluationConfig(
            llm=LLM(name="gpt-4o", version="latest"),
            template=PromptTemplateSpec(
                template=[
                    PromptTemplate(
                        role="user",
                        content="Provide a concise and informative response to the following consumer health question: {{?question}}"
                    )
                ]
            ),
            template_variable_mapping={"question": "topic"},
            dataset_config=Dataset(self.dataset_path),
            metrics=[
                MetricConfig(
                    reference=MetricRef(id="3ea07c1f-5b10-4b12-bf46-6d429faf8010"),
                    variable_mapping={"reference": "ground_truth"},
                ),
            ],
        )
        evaluation_runs = self.client.evaluate(evaluation_config)
        
        self.assertIsNotNone(evaluation_runs)
        self.assertEqual(len(evaluation_runs), 1)
        
        run = evaluation_runs[0]
        run.wait_for_completion()
        
        results = run.results()
        metrics = results.metrics()
        
        expected_columns = {
            "submission_id",
            "run_id",
            "repetition_count",
            "metric",
            "aggregating_value",
            "metric_result",
            "error",
        }

        self.assertTrue(
            expected_columns.issubset(metrics.columns),
            f"Missing columns: {expected_columns - set(metrics.columns)}"
        )
        self.assertTrue(
            metrics["error"].isna().all(),
            f"Some metric rows contain errors:\n{metrics[metrics['error'].notna()]}"
        )


if __name__ == '__main__':
    unittest.main()
