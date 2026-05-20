import unittest
from unittest.mock import MagicMock

from gen_ai_hub.evaluations.models.evaluation_config import EvaluationConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails as LLM
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplateSpec, PromptTemplate
from gen_ai_hub.evaluations.models.dataset_config import Dataset
from gen_ai_hub.evaluations.models.metric_config import MetricConfig, MetricRef
from gen_ai_hub.evaluations._internal._models import _EvaluationConfigData
from gen_ai_hub.evaluations.helpers.config_data import build_accumulated_config


class TestBuildAccumulatedConfig(unittest.TestCase):
    """Tests for build_accumulated_config function."""

    def test_single_execution_flow_with_same_dataset_and_metrics(self):
        """Test that configs with same dataset and metrics use single execution flow."""
        # Create evaluation config data with same dataset and metrics
        eval_config_data = [
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-4"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            ),
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-3.5"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            )
        ]

        # Create evaluation configs (all with llm, no orchestration_registry_reference)
        eval_configs = [
            EvaluationConfig(
                llm=LLM(name="gpt-4", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                llm=LLM(name="gpt-3.5", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]

        accumulated, single_exec, reusable = build_accumulated_config(
            eval_config_data, has_mixed_config_types=False
        )

        # Should use single execution flow
        self.assertTrue(single_exec)
        self.assertFalse(reusable)
        # Should return accumulated config, not list
        self.assertIsInstance(accumulated, _EvaluationConfigData)

    def test_multiple_execution_flow_with_different_datasets(self):
        """Test that configs with different datasets use multiple execution flow."""
        eval_config_data = [
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-4"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            ),
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-3.5"}],
                dataset_data=[{"x": 2}],  # Different dataset
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            )
        ]

        eval_configs = [
            EvaluationConfig(
                llm=LLM(name="gpt-4", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test1.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                llm=LLM(name="gpt-3.5", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test2.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]

        accumulated, single_exec, reusable = build_accumulated_config(
            eval_config_data, has_mixed_config_types=False
        )

        # Should NOT use single execution flow
        self.assertFalse(single_exec)
        self.assertFalse(reusable)
        # Should return list of configs
        self.assertIsInstance(accumulated, list)

    def test_mixed_config_types_prevents_single_execution(self):
        """Test that mixing llm+template and orchestration_registry configs prevents single execution."""
        eval_config_data = [
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-4"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            ),
            _EvaluationConfigData(
                orch_config_data=[{"registry": "some-uuid"}],
                dataset_data=[{"x": 1}],  # Same dataset
                dataset_type="csv",
                metrics_list=["metric1"],  # Same metrics
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            )
        ]

        # Mixed configs: one with llm, one with orchestration_registry_reference
        eval_configs = [
            EvaluationConfig(
                llm=LLM(name="gpt-4", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                orchestration_registry_reference="some-uuid",
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]

        accumulated, single_exec, reusable = build_accumulated_config(
            eval_config_data, has_mixed_config_types=True  # Mixed: llm + registry
        )

        # Should NOT use single execution flow due to mixed types
        self.assertFalse(single_exec)
        # Should enable artifact reuse (same dataset, even though mixed types)
        self.assertTrue(reusable)
        # Should return list of configs
        self.assertIsInstance(accumulated, list)

    def test_all_orchestration_registry_configs_allow_single_execution(self):
        """Test that all orchestration_registry configs can use single execution."""
        eval_config_data = [
            _EvaluationConfigData(
                orch_config_data=[{"registry": "uuid1"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            ),
            _EvaluationConfigData(
                orch_config_data=[{"registry": "uuid2"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            )
        ]

        # All configs with orchestration_registry_reference
        eval_configs = [
            EvaluationConfig(
                orchestration_registry_reference="uuid1",
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                orchestration_registry_reference="uuid2",
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]

        accumulated, single_exec, reusable = build_accumulated_config(
            eval_config_data, has_mixed_config_types=False
        )

        # Should use single execution flow
        self.assertTrue(single_exec)
        self.assertFalse(reusable)
        self.assertIsInstance(accumulated, _EvaluationConfigData)

    def test_reusable_artifact_with_same_dataset_different_metrics(self):
        """Test that configs with same dataset but different metrics enable artifact reuse."""
        eval_config_data = [
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-4"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            ),
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-3.5"}],
                dataset_data=[{"x": 1}],  # Same dataset
                dataset_type="csv",
                metrics_list=["metric2"],  # Different metrics
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            )
        ]

        eval_configs = [
            EvaluationConfig(
                llm=LLM(name="gpt-4", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                llm=LLM(name="gpt-3.5", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric2"))]
            )
        ]

        accumulated, single_exec, reusable = build_accumulated_config(
            eval_config_data, has_mixed_config_types=False
        )

        # Should NOT use single execution (different metrics)
        self.assertFalse(single_exec)
        # Should enable artifact reuse (same dataset)
        self.assertTrue(reusable)
        self.assertIsInstance(accumulated, list)

    def test_backwards_compatibility_without_evaluation_configs(self):
        """Test that function works without evaluation_configs parameter (backwards compatibility)."""
        eval_config_data = [
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-4"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            ),
            _EvaluationConfigData(
                orch_config_data=[{"model": "gpt-3.5"}],
                dataset_data=[{"x": 1}],
                dataset_type="csv",
                metrics_list=["metric1"],
                metric_templates=[],
                variable_mapping={},
                tags={},
                test_row_count=10,
                repetitions=1,
                debug_mode=False
            )
        ]

        # Call without evaluation_configs
        accumulated, single_exec, reusable = build_accumulated_config(
            eval_config_data
        )

        # Should still work and use single execution (no mixed type detection)
        self.assertTrue(single_exec)
        self.assertFalse(reusable)
        self.assertIsInstance(accumulated, _EvaluationConfigData)


if __name__ == '__main__':
    unittest.main()
