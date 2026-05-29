import unittest
from unittest.mock import patch, MagicMock

from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.constants import (
    ALL_METRICS_COLUMN_MAPPING_KEY,
    CONTENT_FILTER_ON_INPUT_METRIC_ID,
    CONTENT_FILTER_ON_OUTPUT_METRIC_ID,
)
from gen_ai_hub.evaluations._internal._models import _EvaluationConfigData
from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode

from gen_ai_hub.evaluations.utils.validation_utils import (
    validate_metrics,
    validate_orchestration_url_across_configs,
    validate_orchestration_url,
    validate_orchestration_configuration,
    validate_input_config,
    validate_variable_mapping_of_prompts,
    validate_variable_mapping_of_metrics,
    remove_filter_metrics_if_provider_not_supported,
    validate_filtered_models,
    _validate_allowed_models,
    _validate_denied_models,
    _is_model_version_allowed,
    _is_model_version_denied,
    fetch_and_validate_orchestration_config,
    validate_variable_mapping_with_input_config,
    validate_config_data_collection,
    validate_merged_config_data,
)

from gen_ai_hub.evaluations.utils.orch_config_utils import (
    validate_if_all_grounding_input_params_present_in_prompt_variables,
)

class TestValidateMetrics(unittest.TestCase):

    def test_metrics_empty_list(self):
        collector = ValidationCollector()
        metrics = []
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        validate_metrics(metrics, [], orchestration_config_data, collector)

        with self.assertRaisesRegex(
            RuntimeError,
            "Metrics list cannot be empty. Atleast one metric needs to be provided",
        ):
            collector.raise_if_errors()

    def test_metrics_not_empty_but_one_metric_is_empty_string(self):
        collector = ValidationCollector()
        metrics = ["bleu", "", "bert_score"]
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        validate_metrics(metrics, [], orchestration_config_data, collector)

        with self.assertRaisesRegex(
            RuntimeError,
            "Metric name cannot be empty. Please provide a valid metric name",
        ):
            collector.raise_if_errors()

    def test_metrics_list_with_empty_metric_name(self):
        collector = ValidationCollector()
        metrics = [""]
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        validate_metrics(metrics, [], orchestration_config_data, collector)

        with self.assertRaisesRegex(
            RuntimeError,
            "Metric name cannot be empty. Please provide a valid metric name",
        ):
            collector.raise_if_errors()

    def test_metrics_list_with_missing_metric_name(self):
        collector = ValidationCollector()
        metrics = ["bleu", "f1/score", "bert_score"]
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        validate_metrics(metrics, [], orchestration_config_data, collector)

        with self.assertRaisesRegex(
            RuntimeError,
            "f1/score is neither a system supported metric nor provided in metric templates",
        ):
            collector.raise_if_errors()

    def test_metrics_valid_system_supported_metrics(self):
        collector = ValidationCollector()
        metrics = ["BERT Score", "BLEU"]
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        validate_metrics(metrics, [], orchestration_config_data, collector)

        # Should not raise
        collector.raise_if_errors()

    def test_metrics_valid_custom_metrics(self):
        collector = ValidationCollector()
        metrics = ["custom_metric_1", "custom_metric_2"]
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        metric_templates = [
            {
                "id": "custom_metric_1",
                "name": "groundedness",
                "spec": {
                    "promptType": "free-form",
                    "configuration": {
                        "modelConfiguration": {
                            "name": "gpt-4o",
                            "version": "2024-08-06",
                            "parameters": [],
                        },
                        "promptConfiguration": {
                            "systemPrompt": "system prompt",
                            "userPrompt": "user prompt",
                            "dataType": "numeric",
                        },
                    },
                },
            },
            {
                "id": "custom_metric_2",
                "name": "custom_metric_1",
                "spec": {
                    "promptType": "free-form",
                    "configuration": {
                        "modelConfiguration": {
                            "name": "gpt-4o",
                            "version": "2024-08-06",
                            "parameters": [],
                        },
                        "promptConfiguration": {
                            "systemPrompt": "system prompt",
                            "userPrompt": "user prompt",
                            "dataType": "numeric",
                        },
                    },
                },
            },
        ]

        validate_metrics(metrics, metric_templates, orchestration_config_data, collector)

        # Should not raise
        collector.raise_if_errors()

    def test_metrics_list_with_rag_flag_enabled(self):
        collector = ValidationCollector()
        metrics = ["BLEU", "BERT Score"]
        orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]

        validate_metrics(metrics, [], orchestration_config_data, collector)

        # Should not raise
        collector.raise_if_errors()





class TestValidateOrchestrationUrl(unittest.TestCase):

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.update_test_orch_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.extract_deployment_id")
    def test_valid_orch_url(
        self,
        mock_extract_deployment_id,
        mock_fetch_deployment_config,
        mock_fetch_and_validate,
        mock_select_model,
        mock_update_test_config,
        mock_call_orch_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "cfg-123"

        mock_extract_deployment_id.return_value = "deployment-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_config.return_value = {"test": "config"}

        evaluation_config_data = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url(
            evaluation_config_data,
            "https://host/v2/inference/deployments/valid/",
            mock_ai_core_client,
            "resource-group",
            collector,
        )

        collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.extract_deployment_id")
    def test_invalid_status_raises_validation_error(
        self,
        mock_extract_deployment_id,
        mock_fetch_deployment_config,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.DEAD
        mock_deployment_config.configuration_id = "cfg-123"

        mock_extract_deployment_id.return_value = "deployment-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config

        evaluation_config_data = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url(
            evaluation_config_data,
            "https://host/v2/inference/deployments/invalid/",
            mock_ai_core_client,
            "resource-group",
            collector,
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "Deployment status is.*expected 'RUNNING'",
        ):
            collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.update_test_orch_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.extract_deployment_id")
    def test_json_decode_error_handled(
        self,
        mock_extract_deployment_id,
        mock_fetch_deployment_config,
        mock_fetch_and_validate,
        mock_select_model,
        mock_update_test_config,
        mock_call_orch_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "cfg-123"

        mock_extract_deployment_id.return_value = "deployment-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_config.return_value = {"test": "config"}

        def side_effect(*args, **kwargs):
            error_collector = args[4] if len(args) > 4 else kwargs.get("error_collector")
            error_collector.add_error(
                ErrorCode.INVALID_ORCHESTRATION_CONFIG_ERROR,
                "Error occurred: Expecting value",
            )

        mock_call_orch_service.side_effect = side_effect

        evaluation_config_data = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url(
            evaluation_config_data,
            "https://host/v2/inference/deployments/jsondecode/",
            mock_ai_core_client,
            "resource-group",
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_orchestration_url")
    def test_validate_orch_url_across_configs_single_item(
        self,
        mock_validate_orch_url,
    ):
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        config = _EvaluationConfigData(
            orch_config_data=[{"modules": {}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url_across_configs(
            accumulated_config_data=config,
            orchestration_url="https://host/v2/inference/deployments/valid/",
            ai_core_client=mock_ai_core_client,
            resource_group="resource-group",
            error_collector=collector,
        )

        mock_validate_orch_url.assert_called_once_with(
            config,
            "https://host/v2/inference/deployments/valid/",
            mock_ai_core_client,
            "resource-group",
            collector,
            None,
        )

    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_orchestration_url")
    def test_validate_orch_url_across_configs_list(
        self,
        mock_validate_orch_url,
    ):
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        config1 = _EvaluationConfigData(
            orch_config_data=[{"modules": {}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        config2 = _EvaluationConfigData(
            orch_config_data=[{"modules": {}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url_across_configs(
            accumulated_config_data=[config1, config2],
            orchestration_url="https://host/v2/inference/deployments/valid/",
            ai_core_client=mock_ai_core_client,
            resource_group="resource-group",
            error_collector=collector,
        )

        self.assertEqual(mock_validate_orch_url.call_count, 2)

        mock_validate_orch_url.assert_any_call(
            config1,
            "https://host/v2/inference/deployments/valid/",
            mock_ai_core_client,
            "resource-group",
            collector,
            None,
        )

        mock_validate_orch_url.assert_any_call(
            config2,
            "https://host/v2/inference/deployments/valid/",
            mock_ai_core_client,
            "resource-group",
            collector,
            None,
        )

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.update_test_orch_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.extract_deployment_id")
    def test_retry_exception_handled_as_success(
        self,
        mock_extract_deployment_id,
        mock_fetch_deployment_config,
        mock_fetch_and_validate,
        mock_select_model,
        mock_update_test_config,
        mock_call_orch_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "cfg-123"

        mock_extract_deployment_id.return_value = "deployment-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_config.return_value = {"test": "config"}
        mock_call_orch_service.return_value = None

        evaluation_config_data = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url(
            evaluation_config_data,
            "https://host/v2/inference/deployments/retry/",
            mock_ai_core_client,
            "resource-group",
            collector,
        )

        collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.update_test_orch_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.extract_deployment_id")
    def test_unexpected_exception_raises_validation_error(
        self,
        mock_extract_deployment_id,
        mock_fetch_deployment_config,
        mock_fetch_and_validate,
        mock_select_model,
        mock_update_test_config,
        mock_call_orch_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client

        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)

        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "cfg-123"

        mock_extract_deployment_id.return_value = "deployment-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_config.return_value = {"test": "config"}

        def side_effect(*args, **kwargs):
            error_collector = args[4] if len(args) > 4 else kwargs.get("error_collector")
            error_collector.add_error(
                ErrorCode.INVALID_ORCHESTRATION_CONFIG_ERROR,
                "Error occurred: Unexpected error",
            )

        mock_call_orch_service.side_effect = side_effect

        evaluation_config_data = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_orchestration_url(
            evaluation_config_data,
            "https://host/v2/inference/deployments/unexpected/",
            mock_ai_core_client,
            "resource-group",
            collector,
        )

        with self.assertRaisesRegex(RuntimeError, "Unexpected error"):
            collector.raise_if_errors()





class TestValidateConfigDataCollection(unittest.TestCase):

    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_merged_config_data")
    def test_validate_config_data_collection_single_item(self, mock_validate_merged):
        """Test validate_config_data_collection with single _EvaluationConfigData"""
        collector = ValidationCollector()

        config = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_config_data_collection(config, collector)

        mock_validate_merged.assert_called_once_with(config, collector)

    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_merged_config_data")
    def test_validate_config_data_collection_list(self, mock_validate_merged):
        """Test validate_config_data_collection with list"""
        collector = ValidationCollector()

        config1 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        config2 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-3"}}}}],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )

        validate_config_data_collection([config1, config2], collector)

        self.assertEqual(mock_validate_merged.call_count, 2)
        mock_validate_merged.assert_any_call(config1, collector)
        mock_validate_merged.assert_any_call(config2, collector)


class TestValidateMergedConfigData(unittest.TestCase):

    @patch("gen_ai_hub.evaluations.utils.validation_utils.handle_reference_missing_rows")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.handle_language_match")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.handle_json_schema_match")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.handle_missing_dependent_variables_in_dataset")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_variable_mapping_with_input_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_input_config")
    def test_validate_merged_config_data(
        self,
        mock_validate_input_config,
        mock_validate_variable_mapping,
        mock_handle_missing_dependent,
        mock_handle_json_schema,
        mock_handle_language,
        mock_handle_reference,
    ):
        """Test validate_merged_config_data calls all validation functions"""

        collector = ValidationCollector()

        config = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={"row1": {"input": "test"}},
            metric_templates=[{"id": "metric1", "name": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping={"prompt/input": "data/input"},
        )

        validate_merged_config_data(config, collector)

        mock_validate_input_config.assert_called_once_with(
            config.orch_config_data,
            config.metrics_list,
            config.metric_templates,
            collector,
        )

        mock_validate_variable_mapping.assert_called_once_with(
            config.orch_config_data,
            config.dataset_data,
            config.variable_mapping,
            config.metrics_list,
            config.metric_templates,
            collector,
        )

        mock_handle_missing_dependent.assert_called_once_with(
            config.dataset_data,
            config.metrics_list,
            config.metric_templates,
            config.variable_mapping,
            collector,
        )

        mock_handle_json_schema.assert_called_once_with(
            config.metrics_list,
            config.dataset_data,
            config.variable_mapping,
            collector,
        )

        mock_handle_language.assert_called_once_with(
            config.metrics_list,
            config.dataset_data,
            config.variable_mapping,
            collector,
        )

        mock_handle_reference.assert_called_once_with(
            config.dataset_data,
            config.variable_mapping,
            config.metrics_list,
            collector,
        )



class TestValidateOrchestrationConfiguration(unittest.TestCase):

    def test_missing_modules(self):
        collector = ValidationCollector()
        orchestration_config_data = [{}]

        with self.assertRaisesRegex(RuntimeError, "modules is mandatory"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_missing_llm_module_config_or_templating_module_config(self):
        collector = ValidationCollector()
        orchestration_config_data = [{"modules": {"prompt_templating": {}}}]

        with self.assertRaisesRegex(RuntimeError, "Missing inside here configuration"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_missing_model_name_in_llm_module_config(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {},
                    "prompt": {"template": [{"content": "some content", "role": "user"}]},
                }
            }
        }]

        with self.assertRaisesRegex(RuntimeError, "Missing configuration for.*name"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_template_ref_not_supported(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {"template_ref": "uuid"},
                }
            }
        }]

        with self.assertRaisesRegex(RuntimeError, "template_ref inside prompt is not yet supported"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_empty_template_list(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {"template": []},
                }
            }
        }]

        with self.assertRaisesRegex(RuntimeError, "template list cannot be empty"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_missing_content_in_template(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {"template": [{}]},
                }
            }
        }]

        with self.assertRaisesRegex(RuntimeError, "Each template must be a dictionary"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_image_url_not_supported(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {
                        "template": [{
                            "role": "user",
                            "content": [{
                                "type": "image_url",
                                "image_url": {"url": "https://image.com"}
                            }]
                        }]
                    }
                }
            }
        }]

        with self.assertRaisesRegex(RuntimeError, "image_url is not supported"):
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

    def test_positive_case(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {
                        "template": [{
                            "content": "Prompt {{?var1}} {{?var2}}",
                            "role": "user",
                        }]
                    }
                }
            }
        }]

        validate_orchestration_configuration(orchestration_config_data, collector)
        collector.raise_if_errors()  # Should not raise

    def test_grounding_output_missing(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [{"role": "user", "content": "Test {{?otherVar}}"}]
                    },
                    "model": {"name": "gpt-4"}
                },
                "grounding": {
                    "config": {"placeholders": {"output": "groundingResult"}}
                },
            }
        }]

        with self.assertRaises(RuntimeError) as context:
            validate_orchestration_configuration(orchestration_config_data, collector)
            collector.raise_if_errors()

        self.assertIn(ErrorCode.INVALID_GROUNDING_CONFIGURATION.value, str(context.exception))
        self.assertIn("groundingResult", str(context.exception))

    def test_content_filter_supported_provider(self):
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {"template": [{"role": "user", "content": "Hello"}]},
                    "model": {"name": "gpt-4"},
                },
                "filtering": {
                    "input": {"filters": [{"type": "azure_content_safety"}]},
                    "output": {"filters": [{"type": "azure_content_safety"}]},
                },
            }
        }]

        metrics = [
            CONTENT_FILTER_ON_INPUT_METRIC_ID,
            CONTENT_FILTER_ON_OUTPUT_METRIC_ID,
            "other_metric"
        ]

        collector = ValidationCollector()

        remove_filter_metrics_if_provider_not_supported(
            orchestration_config_data, metrics, collector
        )

        self.assertEqual(len(metrics), 3)

    def test_content_filter_unsupported_provider(self):
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {"template": [{"role": "user", "content": "Hello"}]},
                    "model": {"name": "gpt-4"},
                },
                "filtering": {
                    "input": {"filters": [{"type": "unsupported_provider"}]},
                    "output": {"filters": [{"type": "unsupported_provider"}]},
                },
            }
        }]

        metrics = [
            CONTENT_FILTER_ON_INPUT_METRIC_ID,
            CONTENT_FILTER_ON_OUTPUT_METRIC_ID,
            "other_metric_1",
            "other_metric_2",
        ]

        collector = ValidationCollector()

        remove_filter_metrics_if_provider_not_supported(
            orchestration_config_data, metrics, collector
        )

        self.assertNotIn(CONTENT_FILTER_ON_INPUT_METRIC_ID, metrics)
        self.assertNotIn(CONTENT_FILTER_ON_OUTPUT_METRIC_ID, metrics)
        self.assertIn("other_metric_1", metrics)
        self.assertIn("other_metric_2", metrics)
        self.assertEqual(len(metrics), 2)


class TestValidateInputParameters(unittest.TestCase):

    def test_empty_metrics(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {"template": [{"content": "text", "role": "user"}]},
                }
            }
        }]

        with self.assertRaisesRegex(RuntimeError, "Metrics list cannot be empty"):
            validate_input_config(orchestration_config_data, [], [], collector)
            collector.raise_if_errors()

    def test_valid_input_parameters(self):
        collector = ValidationCollector()
        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "latest"},
                    "prompt": {"template": [{"content": "text", "role": "user"}]},
                }
            }
        }]

        metrics = ["bert_score"]

        metric_templates = [{
            "id": "bert_score",
            "name": "BERT Score",
            "evaluation_method": "computed",
        }]

        validate_input_config(
            orchestration_config_data,
            metrics,
            metric_templates,
            collector,
        )

        collector.raise_if_errors()  # Should not raise


class TestValidateVariableMappingOfMetrics(unittest.TestCase):

    def test_valid_all_metrics_reference_mapping(self):
        collector = ValidationCollector()
        metrics = ["bleu", "bert_score"]
        template_vars_data = [{"reference": "value1", "column1": "value2"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/reference"
        }

        validate_variable_mapping_of_metrics(
            metrics,
            [],
            template_vars_data,
            variable_mapping,
            collector,
        )

        collector.raise_if_errors()

    def test_invalid_all_metrics_reference_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"reference-key": "value1", "column1": "value2"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/invalid_column"
        }

        validate_variable_mapping_of_metrics(
            metrics,
            [],
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_valid_individual_metrics_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"reference": "value1", "json_schema": "value2"}]
        variable_mapping = {
            "metric1/reference": "data/reference",
            "metric2/json_schema": "data/json_schema",
        }

        metric_templates = [
            {
                "id": "metric1",
                "name": "Metric 1",
                "additionalProperties": {"variables": ["reference"]},
            },
            {
                "id": "metric2",
                "name": "Metric 2",
                "additionalProperties": {"variables": ["json_schema"]},
            },
        ]

        validate_variable_mapping_of_metrics(
            metrics,
            metric_templates,
            template_vars_data,
            variable_mapping,
            collector,
        )

        collector.raise_if_errors()

    def test_invalid_individual_metrics_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"reference": "value1", "json_schema": "value2"}]
        variable_mapping = {
            "metric1/invalid_key": "data/reference",
            "metric2/json_schema": "data/invalid_column",
        }

        validate_variable_mapping_of_metrics(
            metrics,
            [],
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_missing_dataset_column_for_all_metrics(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"column1": "value1"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/reference"
        }

        validate_variable_mapping_of_metrics(
            metrics,
            [],
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_missing_dataset_column_for_individual_metrics(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"column1": "value1"}]
        variable_mapping = {
            "metric1/reference": "data/reference",
            "metric2/json_schema": "data/json_schema",
        }

        validate_variable_mapping_of_metrics(
            metrics,
            [],
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()


class TestValidateVariableMappingOfPrompts(unittest.TestCase):

    def test_valid_variable_mapping(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "This is a prompt with {{?var1}} and {{?var2}}.", "role": "user"}
                    ]
                }
            }}
        }]

        template_vars_data = [{"var1": "value1", "var2": "value2"}]
        variable_mapping = {
            "prompt/var1": "data/var1",
            "prompt/var2": "data/var2",
        }

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            template_vars_data,
            variable_mapping,
            collector,
        )

        collector.raise_if_errors()

    def test_missing_variable_in_mapping_and_dataset(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "This is a prompt with {{?var1}} and {{?var2}}.", "role": "user"}
                    ]
                }
            }}
        }]

        template_vars_data = [{"var1": "value1"}]
        variable_mapping = {"prompt/var1": "data/var1"}

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_system_defined_variable_in_prompt(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "This is a prompt with {{?prompt}}", "role": "user"}
                    ]
                }
            }}
        }]

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            [{"var1": "value1"}],
            {},
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_variable_in_dataset_but_not_in_mapping(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "This is a prompt with {{?var1}} and {{?var2}}.", "role": "user"}
                    ]
                }
            }}
        }]

        template_vars_data = [{"var1": "value1", "var2": "value2"}]
        variable_mapping = {"prompt/var1": "data/var1"}

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            template_vars_data,
            variable_mapping,
            collector,
        )

        collector.raise_if_errors()

    def test_variable_in_mapping_but_not_in_dataset(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "This is a prompt with {{?var1}} and {{?var2}}.", "role": "user"}
                    ]
                }
            }}
        }]

        template_vars_data = [{"var1": "value1"}]
        variable_mapping = {
            "prompt/var1": "data/var1",
            "prompt/var2": "data/var2",
        }

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_variable_with_defaults_skipped_validation(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "Write about {{?topic}} in {{?sentiment}} way", "role": "user"}
                    ],
                    "defaults": {"topic": "apple"},
                }
            }}
        }]

        template_vars_data = [{"sentiment": "positive"}]
        variable_mapping = {"prompt/sentiment": "data/sentiment"}

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            template_vars_data,
            variable_mapping,
            collector,
        )

        collector.raise_if_errors()

    def test_variable_without_defaults_requires_validation(self):
        collector = ValidationCollector()

        orchestration_config_data = [{
            "modules": {"prompt_templating": {
                "prompt": {
                    "template": [
                        {"content": "Write about {{?topic}} in {{?sentiment}} way", "role": "user"}
                    ],
                    "defaults": {"topic": "apple"},
                }
            }}
        }]

        template_vars_data = [{"topic": "banana"}]
        variable_mapping = {"prompt/topic": "data/topic"}

        validate_variable_mapping_of_prompts(
            orchestration_config_data,
            template_vars_data,
            variable_mapping,
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()




class TestValidateIfGroundingInputPresentInPromptVariables(unittest.TestCase):

    def test_missing_modules_key(self):
        orch_config = {}
        collector = ValidationCollector()

        validate_if_all_grounding_input_params_present_in_prompt_variables(
            orch_config, collector
        )

        self.assertFalse(collector.has_errors())

    def test_missing_grounding_module_config_key(self):
        orch_config = {"modules": {}}
        collector = ValidationCollector()

        validate_if_all_grounding_input_params_present_in_prompt_variables(
            orch_config, collector
        )

        self.assertFalse(collector.has_errors())

    def test_empty_input_params_list(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [{"content": "Test {{?var1}}", "role": "user"}]
                    }
                },
                "grounding": {"config": {"placeholders": {"input": []}}},
            }
        }

        collector = ValidationCollector()

        validate_if_all_grounding_input_params_present_in_prompt_variables(
            orch_config, collector
        )

        self.assertFalse(collector.has_errors())

    def test_valid_input_params(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [{"content": "Test {{?var1}} and {{?var2}}", "role": "user"}]
                    }
                },
                "grounding": {
                    "config": {"placeholders": {"input": ["var1", "var2"]}}
                },
            }
        }

        collector = ValidationCollector()

        validate_if_all_grounding_input_params_present_in_prompt_variables(
            orch_config, collector
        )

        self.assertFalse(collector.has_errors())

    def test_missing_input_params(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [{"content": "Test {{?var1}}", "role": "user"}]
                    }
                },
                "grounding": {
                    "config": {"placeholders": {"input": ["var1", "var2"]}}
                },
            }
        }

        collector = ValidationCollector()

        validate_if_all_grounding_input_params_present_in_prompt_variables(
            orch_config, collector
        )

        errors = collector.errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], ErrorCode.INVALID_GROUNDING_CONFIGURATION.value)
        self.assertIn("var2", errors[0][1])



class TestValidateFilteredModels(unittest.TestCase):

    def setUp(self):
        self.valid_run_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "4.0"}
                }
            }
        }]

    def test_allow_filter_allows_valid_model(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = '[{"modelName": "gpt-4", "modelVersions": ["4.0"]}]'

        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "allow"

        collector = ValidationCollector()

        validate_filtered_models([param1, param2], self.valid_run_data, collector)
        collector.raise_if_errors()

    def test_deny_filter_blocks_invalid_model(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = '[{"modelName": "gpt-4", "modelVersions": ["4.0"]}]'

        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "deny"

        collector = ValidationCollector()

        validate_filtered_models([param1, param2], self.valid_run_data, collector)

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_invalid_filter_type_adds_error(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = '[{"modelName": "gpt-4", "modelVersions": ["4.0"]}]'

        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "invalid"

        collector = ValidationCollector()

        validate_filtered_models([param1, param2], self.valid_run_data, collector)

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_no_model_filter_list_skips_filtering(self):
        collector = ValidationCollector()
        validate_filtered_models([], self.valid_run_data, collector)
        collector.raise_if_errors()

    def test_validate_allow_filter_blocks_unknown_model(self):
        collector = ValidationCollector()
        run_models = {"gpt-4": ["4.0"], "llama": ["7b"]}
        allowed_models = {"gpt-4": ["4.0"]}

        _validate_allowed_models(run_models, allowed_models, collector)

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_validate_deny_filter_allows_unlisted_models(self):
        collector = ValidationCollector()
        run_models = {"gpt-4": ["4.0"]}
        denied_models = {"llama": ["7b"]}

        _validate_denied_models(run_models, denied_models, collector)
        collector.raise_if_errors()

    def test_validate_deny_filter_blocks_if_listed(self):
        collector = ValidationCollector()
        run_models = {"gpt-4": ["4.0"]}
        denied_models = {"gpt-4": ["4.0"]}

        _validate_denied_models(run_models, denied_models, collector)

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_is_model_version_allowed_true(self):
        self.assertTrue(
            _is_model_version_allowed("gpt-4", "4.0", {"gpt-4": ["4.0", "4.1"]})
        )

    def test_is_model_version_allowed_false(self):
        self.assertFalse(
            _is_model_version_allowed("gpt-4", "3.5", {"gpt-4": ["4.0"]})
        )

    def test_is_model_version_denied_true(self):
        self.assertTrue(
            _is_model_version_denied("gpt-4", "4.0", {"gpt-4": ["4.0", "4.1"]})
        )

    def test_is_model_version_denied_false(self):
        self.assertFalse(
            _is_model_version_denied("gpt-4", "3.5", {"gpt-4": ["4.0"]})
        )



class TestFetchAndValidateOrchConfig(unittest.TestCase):

    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_configuration_by_id")
    def test_fetch_and_validate_valid_allowlist(self, mock_fetch):
        mock_config_response = MagicMock()

        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = '[{"modelName": "gpt-4", "modelVersions": ["4.0"]}]'

        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "allow"

        mock_config_response.parameter_bindings = [param1, param2]
        mock_fetch.return_value = mock_config_response

        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "4.0"}
                }
            }
        }]

        collector = ValidationCollector()

        fetch_and_validate_orchestration_config(
            MagicMock(), "config-123", orchestration_config_data, "rg", collector
        )

        collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_configuration_by_id")
    def test_fetch_and_validate_invalid_filter(self, mock_fetch):
        mock_config_response = MagicMock()

        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = '[{"modelName": "gpt-4", "modelVersions": ["4.0"]}]'

        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "unsupported"

        mock_config_response.parameter_bindings = [param1, param2]
        mock_fetch.return_value = mock_config_response

        orchestration_config_data = [{
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "4.0"}
                }
            }
        }]

        collector = ValidationCollector()

        fetch_and_validate_orchestration_config(
            MagicMock(), "config-xyz", orchestration_config_data, "rg", collector
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()



class TestValidateVariableMappingWithInputConfig(unittest.TestCase):

    def setUp(self):
        self.orchestration_config_data = [
            {"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}
        ]
        self.template_vars_data = [{"input": "Hello"}]
        self.variable_mapping = {"all_metrics/input": "input"}
        self.metrics = ["some.metric"]
        self.collector = ValidationCollector()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_variable_mapping_of_metrics")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_variable_mapping_of_prompts")
    def test_calls_all_validation_subfunctions(
        self,
        mock_validate_prompts,
        mock_validate_metrics,
    ):
        validate_variable_mapping_with_input_config(
            self.orchestration_config_data,
            self.template_vars_data,
            self.variable_mapping,
            self.metrics,
            [],
            self.collector,
        )

        mock_validate_prompts.assert_called_once()
        mock_validate_metrics.assert_called_once()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.validate_variable_mapping_of_prompts")
    def test_raises_if_any_child_fails(self, mock_validate_prompts):
        mock_validate_prompts.side_effect = RuntimeError("Prompt validation failed")

        with self.assertRaises(RuntimeError):
            validate_variable_mapping_with_input_config(
                self.orchestration_config_data,
                self.template_vars_data,
                self.variable_mapping,
                self.metrics,
                [],
                self.collector,
            )
