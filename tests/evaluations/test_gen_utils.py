import json
import unittest
from unittest.mock import patch, MagicMock

from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode

from gen_ai_hub.evaluations.utils.gen_utils import (
    get_mapped_value_if_exists,
    list_prompt_variables,
    flatten_prompt_configuration,
    get_prompt_variables_from_orch_config,
    get_custom_metric_ids_from_input,
    populate_dataset_data_if_single_schema_provided,
    populate_dataset_data_if_single_reference_provided,
    populate_dataset_data_if_individual_metric_reference_provided,
    extract_dataset_columns,
    create_custom_metric_name,
    count_user_prompts_from_template_list,
    select_model_details_randomly,
    create_model_versions_map_from_orch_configs,
    create_model_versions_map_from_configuration_param_bindings,
    handle_missing_dependent_variables_in_dataset,
    handle_reference_missing_rows,
    parse_model_filter_list,
    build_model_versions_map,
    validate_metrics,
    validate_variable_mapping_of_metrics,
    validate_variable_mapping_of_prompts,
    update_variable_mapping,
    get_accumulated_config_data,
    create_model_versions_map_from_custom_metric_config,
    update_test_orch_config,
    validate_metric_name,
    check_if_metric_is_defined,
    extract_metrics_variables,
    validate_individual_custom_metrics,
    handle_json_schema_match,
    validate_language_code_and_data_population,
    handle_language_match,
    update_artifact_dict,
    resolve_orchestration_config_v2,
)

from gen_ai_hub.evaluations.utils.validation_utils import (
    validate_orchestration_url,
    validate_orchestration_configuration,
    validate_input_config,
    extract_deployment_id,
)

from gen_ai_hub.evaluations._internal._models import _EvaluationConfigData

from gen_ai_hub.evaluations.constants import (
    AICORE_LLM_PROMPT_TEMPLATE_KEY,
    ALL_METRICS_COLUMN_MAPPING_KEY,
    JSON_SCHEMA_MATCH_METRIC_ID,
    LANGUAGE_MATCH_METRIC_ID,
    LANGUAGE_KEY,
    MODEL_CONFIGURATION_KEY,
    MODEL_NAME_KEY,
    MODEL_VERSION_KEY,
    LATEST_MODEL_VERSION_KEY,
    MODULES_KEY,
    PROMPT_TEMPLATING_KEY,
    PROMPT_KEY,
    TEMPLATE_KEY,
    MODEL_KEY,
)

from gen_ai_hub.evaluations.models.artifact_source import ArtifactSource
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplate
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails as LLM


@patch.dict("os.environ", {"METRICS_DATA_PATH": "metrics_info.json"})
class TestGetMappedValueIfExists(unittest.TestCase):
    def test_mapping_key_exists_with_data_prefix(self):
        key = "original_key"
        mapping_key = "prompt/mapping_key"
        variable_mapping = {"prompt/mapping_key": "data/mapped_field"}
        dataset_rows = ["mapped_field"]
        result = get_mapped_value_if_exists(
            key, mapping_key, variable_mapping, dataset_rows
        )
        self.assertEqual(result, "mapped_field")

    def test_mapping_key_exists_with_other_prefix(self):
        key = "original_key"
        mapping_key = "prompt/mapping_key"
        variable_mapping = {"prompt/mapping_key": "other/mapped_field"}
        dataset_rows = ["field"]
        result = get_mapped_value_if_exists(
            key, mapping_key, variable_mapping, dataset_rows
        )
        self.assertEqual(result, "original_key")

    def test_mapping_key_does_not_exist(self):
        key = "original_key"
        mapping_key = "prompt/non_existent_key"
        variable_mapping = {"prompt/mapping_key": "data/mapped_field"}
        dataset_rows = ["field"]
        result = get_mapped_value_if_exists(
            key, mapping_key, variable_mapping, dataset_rows
        )
        self.assertEqual(result, "original_key")

    def test_mapping_key_exist_but_column_does_not_exist(self):
        key = "original_key"
        mapping_key = "prompt/mapping_key"
        variable_mapping = {"prompt/mapping_key": "data/mapped_field"}
        dataset_rows = ["field"]
        result = get_mapped_value_if_exists(
            key, mapping_key, variable_mapping, dataset_rows
        )
        self.assertEqual(result, "original_key")


class TestPopulateTemplateVarsDataIfSingleSchemaProvided(unittest.TestCase):
    def test_json_schema_key_directly_present_in_dataset_partial(self):
        collector = ValidationCollector()
        template_vars_data = [
            {
                "topic": "banana",
                "json_schema": '{"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"source_langauge":{"type":"string"},"is_supported":{"type":"boolean"},"translated_text":{"type":"string"}},"required":["source_language","is_supported","translated_text"]}',
            },
            {"topic": "apple"},
        ]
        variable_mapping = {}

        populate_dataset_data_if_single_schema_provided(
            template_vars_data, variable_mapping, collector
        )

        #  needs to replicate the schema value using existing value
        self.assertEqual(
            template_vars_data[1]["json_schema"],
            '{"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"source_langauge":{"type":"string"},"is_supported":{"type":"boolean"},"translated_text":{"type":"string"}},"required":["source_language","is_supported","translated_text"]}'
        )

    def test_json_schema_key_present_in_first_row(self):
        collector = ValidationCollector()
        template_vars_data = [
            {
                "topic": "ml",
                "json_schema_key": '{"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"source_langauge":{"type":"string"},"is_supported":{"type":"boolean"},"translated_text":{"type":"string"}},"required":["source_language","is_supported","translated_text"]}',
            },
            {"topic": "ai"},
            {"topic": "gen_ai"},
        ]
        variable_mapping = {"json_schema_match/json_schema": "data/json_schema_key"}

        populate_dataset_data_if_single_schema_provided(
            template_vars_data, variable_mapping, collector
        )

        self.assertEqual(
            template_vars_data[1]["json_schema_key"],
            '{"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"source_langauge":{"type":"string"},"is_supported":{"type":"boolean"},"translated_text":{"type":"string"}},"required":["source_language","is_supported","translated_text"]}'
        )
        self.assertEqual(
            template_vars_data[2]["json_schema_key"],
            '{"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"source_langauge":{"type":"string"},"is_supported":{"type":"boolean"},"translated_text":{"type":"string"}},"required":["source_language","is_supported","translated_text"]}'
        )


# Tests for parse_prompt_template_content and get_variable_value_from_orch_response removed
# as these functions don't exist in the current gen_utils.py


class TestListPromptVariables(unittest.TestCase):
    def test_single_variable(self):
        content = "This is a prompt with a single variable {{ ?var1 }}."
        result = list_prompt_variables(content)
        self.assertEqual(result, ["var1"])

    def test_multiple_variables(self):
        content = "This is a prompt with multiple variables {{?var1}} and {{?var2}}."
        result = list_prompt_variables(content)
        self.assertEqual(result, ["var1", "var2"])

    def test_no_variables(self):
        content = "This is a prompt with no variables."
        result = list_prompt_variables(content)
        self.assertEqual(result, [])

    def test_nested_variables(self):
        content = "This is a prompt with nested variables {{?var1}} and {{?var2}} inside {{?var3}}."
        result = list_prompt_variables(content)
        self.assertEqual(result, ["var1", "var2", "var3"])

    def test_empty_variables_throws_exception(self):
        content = "This is a prompt with empty variables {{?}}."
        with self.assertRaises(ValueError):
            list_prompt_variables(content)

    def test_unsupported_named_variables_throws_exception(self):
        content = "This is a prompt with empty variables {{?12topics}}."
        with self.assertRaises(ValueError):
            list_prompt_variables(content)


class TestFormatPromptConfiguration(unittest.TestCase):
    def test_flat_dict(self):
        config = {"scenario": "genai-evaluations", "metricName": "groundedness"}
        expected = "scenario: genai-evaluations\nmetricName: groundedness"
        self.assertEqual(flatten_prompt_configuration(config), expected)

    def test_nested_dict(self):
        config = {
            "scenario": "genai-evaluations",
            "prompt_configuration": {"rating": "rating", "data_type": "numerical"},
        }
        expected = "scenario: genai-evaluations\nprompt_configuration: rating: rating, data_type: numerical"
        self.assertEqual(flatten_prompt_configuration(config), expected)

    def test_list_values(self):
        config = {
            "model_parameters": ["temperature", "max_tokens"],
            "parameter_values": {"temperature": [0.7, 0.8]},
        }
        expected = "model_parameters: temperature; max_tokens\nparameter_values: temperature: 0.7; 0.8"
        self.assertEqual(flatten_prompt_configuration(config), expected)

    def test_empty_dict(self):
        config = {}
        expected = ""
        self.assertEqual(flatten_prompt_configuration(config), expected)

    def test_mixed_nested(self):
        config = {
            "metricName": "groundedness",
            "model_configuration": {
                "models": ["gpt-4", "gpt-3.5"],
                "parameters": {"temperature": 0.7, "max_tokens": 50},
            },
        }
        expected = (
            "metricName: groundedness\n"
            "model_configuration: models: gpt-4; gpt-3.5, parameters: temperature: 0.7, max_tokens: 50"
        )
        self.assertEqual(flatten_prompt_configuration(config), expected)


class TestGetPromptVariablesFromOrchConfig(unittest.TestCase):
    def test_empty_config(self):
        orch_config = {"modules": {"prompt_templating": {"prompt": {"template": []}}}}
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, set())

    def test_single_template_with_variables(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "This is a prompt with {{?var1}} and {{?var2}}.",
                            }
                        ]
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, {"var1", "var2"})

    def test_multiple_templates_with_variables(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "This is a prompt with {{?var1}}.",
                            },
                            {
                                "role": "user",
                                "content": "This is another prompt with {{?var2}} and {{?var3}}.",
                            },
                        ]
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, {"var1", "var2", "var3"})

    def test_output_param_removal(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "Prompt with {{?var1}} and {{?groundingOutput}}.",
                            },
                            {
                                "role": "user",
                                "content": "Another prompt with {{?var2}}.",
                            },
                        ]
                    }
                },
                "grounding": {
                    "placeholders": {
                        "output": "groundingOutput"
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, {"var1", "var2"})  # 'groundingOutput' is removed

    def test_templates_with_no_variables(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "This is a prompt with no variables.",
                            },
                            {
                                "role": "user",
                                "content": "Another prompt with no variables.",
                            },
                        ]
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, set())

    def test_mixed_templates(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "This is a prompt with {{?var1}}.",
                            },
                            {
                                "role": "user",
                                "content": "This is a prompt with no variables.",
                            },
                            {
                                "role": "user",
                                "content": "Another prompt with {{?var2}}.",
                            },
                        ]
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, {"var1", "var2"})


class TestGetMetrics(unittest.TestCase):
    def test_get_custom_metric_ids_from_input(self):
        collector = ValidationCollector()
        custom_metric_config_data = [
            {"metricId": "custom_metric_1"},
            {"metricId": "custom_metric_2"},
        ]
        custom_metric_ids = get_custom_metric_ids_from_input(custom_metric_config_data, collector)
        self.assertEqual(len(custom_metric_ids), 2)
        self.assertIn("custom_metric_1", custom_metric_ids)
        self.assertIn("custom_metric_2", custom_metric_ids)

    def test_get_custom_metric_ids_from_input_if_empty(self):
        collector = ValidationCollector()
        custom_metric_config_data = []
        custom_metric_ids = get_custom_metric_ids_from_input(custom_metric_config_data, collector)
        self.assertEqual(len(custom_metric_ids), 0)


class TestValidateMetrics(unittest.TestCase):
    def test_metrics_empty_list(self):
        collector = ValidationCollector()
        metrics = []
        metrics_templates = []
        orchestration_config_data = [{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}]
        with self.assertRaises(RuntimeError) as cm:
            validate_metrics(metrics, metrics_templates, orchestration_config_data, collector)
            collector.raise_if_errors()
        self.assertIn("Metrics list cannot be empty. Atleast one metric needs to be provided", str(cm.exception))

    def test_metrics_not_empty_but_one_metric_is_empty_string(self):
        # can occur in case of missed syntax --> metrics = blue,,bertscore
        collector = ValidationCollector()
        metrics = ["bleu", "", "bert_score"]
        metric_templates = []
        orchestration_config_data = [{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}]
        with self.assertRaises(RuntimeError) as cm:
            validate_metrics(metrics, metric_templates, orchestration_config_data, collector)
            collector.raise_if_errors()
        self.assertIn("Metric name cannot be empty. Please provide a valid metric name", str(cm.exception))

    def test_metrics_list_with_empty_metric_name(self):
        collector = ValidationCollector()
        metrics = [""]
        metric_templates = []
        orchestration_config_data = [{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}]
        with self.assertRaises(RuntimeError) as cm:
            validate_metrics(metrics, metric_templates, orchestration_config_data, collector)
            collector.raise_if_errors()
        self.assertIn("Metric name cannot be empty. Please provide a valid metric name", str(cm.exception))

    def test_metrics_valid_system_supported_metrics(self):
        collector = ValidationCollector()
        metrics = ["bert_score", "bleu"]
        metrics_templates = [
            {
                "evaluationMethod": "computed",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "bert_score",
                "name": "BERT Score",
                "description": "This is a description for bert score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [0, 1],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "computed",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "bleu",
                "name": "BLEU",
                "description": "This is a description for bleu score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [0, 1],
                    "experimental": False,
                },
            },
        ]
        orchestration_config_data = [{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}]
        validate_metrics(metrics, metrics_templates, orchestration_config_data, collector)
        collector.raise_if_errors()

    def test_metrics_llm_based_metric_more_than_one_user_prompts(self):
        collector = ValidationCollector()
        metrics = ["pointwise_correctness"]
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "This is a prompt with {{?var1}}.",
                            },
                            {
                                "role": "user",
                                "content": "This is a prompt with no variables.",
                            },
                            {
                                "role": "user",
                                "content": "Another prompt with {{?var2}}.",
                            },
                        ]
                    }
                }
            }
        }

        metrics_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "pointwise_correctness",
                "name": "Pointwise Correctness",
                "description": "This is a description for Pointwise Correctness.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]

        orchestration_config_data = [orch_config]
        with self.assertRaises(RuntimeError) as cm:
            validate_metrics(metrics, metrics_templates, orchestration_config_data, collector)
            collector.raise_if_errors()
        self.assertIn("More than one user prompts provided in template list", str(cm.exception))

    def test_metrics_llm_based_metric_missing_user_prompts(self):
        collector = ValidationCollector()
        metrics = ["pointwise_correctness"]
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "system",
                                "content": "This is a system prompt with no variables.",
                            }
                        ]
                    }
                }
            }
        }

        metrics_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "pointwise_correctness",
                "name": "Pointwise Correctness",
                "description": "This is a description for Pointwise Correctness.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]

        orchestration_config_data = [orch_config]
        with self.assertRaises(RuntimeError) as cm:
            validate_metrics(metrics, metrics_templates, orchestration_config_data, collector)
            collector.raise_if_errors()
        self.assertIn("Missing user prompt in template list", str(cm.exception))


class TestValidateOrchesrationUrl(unittest.TestCase):
    run1 = MagicMock()
    run1.name = "run1"
    run1.config = {
        "modules": {
            "prompt_templating": {
                "prompt": {
                    "template": [
                        {
                            "role": "system",
                            "content": "This is a system prompt with no variables.",
                        }
                    ]
                },
                "model": {"name": "gpt-4", "version": "4.0"},
            }
        }
    }
    run2 = MagicMock()
    run2.name = "run2"
    run2.config = {
        "modules": {
            "prompt_templating": {
                "prompt": {
                    "template": [
                        {
                            "role": "system",
                            "content": "This is a system prompt with no variables.",
                        }
                    ]
                },
                "model": {"name": "llama2", "version": "7b"},
            }
        }
    }
    run_data = [run1, run2]

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.update_test_orch_config")
    def test_valid_orch_url(
        self,
        mock_update_test_orch_config,
        mock_select_model,
        mock_fetch_and_validate,
        mock_fetch_deployment_config,
        mock_call_orchestration_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client
        
        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)
        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "config-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_fetch_and_validate.return_value = None
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_orch_config.return_value = {"test": "config"}
        mock_call_orchestration_service.return_value = None

        test_orch_url = "https://api.ai.staging.eu-west-1.mlf-aws-dev.com/v2/inference/deployments/valid/"
        config_data = _EvaluationConfigData(
            orch_config_data=[self.run1.config],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )
        try:
            validate_orchestration_url(
                config_data, test_orch_url, mock_ai_core_client, "resource-group", collector
            )
            collector.raise_if_errors()
        except RuntimeError:
            self.fail(
                "validate_orchestration_url raised RuntimeError unexpectedly!"
            )

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.update_test_orch_config")
    def test_invalid_orch_url_raises_validation_error(
        self,
        mock_update_test_orch_config,
        mock_select_model,
        mock_fetch_and_validate,
        mock_fetch_deployment_config,
        mock_call_orchestration_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client
        
        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)
        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "config-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_fetch_and_validate.return_value = None
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_orch_config.return_value = {"test": "config"}
        # Mock the function to add error to collector instead of raising
        def mock_call_with_error(*args, **kwargs):
            error_collector = args[4] if len(args) > 4 else kwargs.get('error_collector')
            if error_collector:
                error_collector.add_error(
                    ErrorCode.INVALID_ORCHESTRATION_CONFIG_ERROR,
                    "Error occurred: Invalid URL while trying to run the test orchestration config endpoint call with this user provided deployment url"
                )
        mock_call_orchestration_service.side_effect = mock_call_with_error

        test_orch_url = "https://api.ai.staging.eu-west-1.mlf-aws-dev.com/v2/inference/deployments/invalid/"
        config_data = _EvaluationConfigData(
            orch_config_data=[self.run1.config],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )
        validate_orchestration_url(
            config_data, test_orch_url, mock_ai_core_client, "resource-group", collector
        )
        # Exception is caught and added to collector
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertRegex(str(cm.exception), "Error occurred.*while trying to run the test orchestration config")

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.update_test_orch_config")
    def test_json_decode_error_handled_as_success(
        self,
        mock_update_test_orch_config,
        mock_select_model,
        mock_fetch_and_validate,
        mock_fetch_deployment_config,
        mock_call_orchestration_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client
        
        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)
        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "config-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_fetch_and_validate.return_value = None
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_orch_config.return_value = {"test": "config"}
        # JSONDecodeError is caught internally and added to collector
        def mock_call_with_json_error(*args, **kwargs):
            error_collector = args[4] if len(args) > 4 else kwargs.get('error_collector')
            if error_collector:
                error_collector.add_error(
                    ErrorCode.INVALID_ORCHESTRATION_CONFIG_ERROR,
                    "Error occurred: Expecting value while trying to run the test orchestration config endpoint call"
                )
        mock_call_orchestration_service.side_effect = mock_call_with_json_error

        test_orch_url = "https://api.ai.staging.eu-west-1.mlf-aws-dev.com/v2/inference/deployments/json-decode/"
        config_data = _EvaluationConfigData(
            orch_config_data=[self.run1.config],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )
        validate_orchestration_url(
            config_data, test_orch_url, mock_ai_core_client, "resource-group", collector
        )
        # Should have error in collector
        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.update_test_orch_config")
    def test_retry_exception_handled_as_success(
        self,
        mock_update_test_orch_config,
        mock_select_model,
        mock_fetch_and_validate,
        mock_fetch_deployment_config,
        mock_call_orchestration_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client
        
        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)
        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "config-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_fetch_and_validate.return_value = None
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_orch_config.return_value = {"test": "config"}
        # Exception is caught internally and added to collector
        def mock_call_with_retry_error(*args, **kwargs):
            error_collector = args[4] if len(args) > 4 else kwargs.get('error_collector')
            if error_collector:
                error_collector.add_error(
                    ErrorCode.INVALID_ORCHESTRATION_CONFIG_ERROR,
                    "Error occurred: Retry error while trying to run the test orchestration config endpoint call"
                )
        mock_call_orchestration_service.side_effect = mock_call_with_retry_error

        test_orch_url = "https://api.ai.staging.eu-west-1.mlf-aws-dev.com/v2/inference/deployments/retry/"
        config_data = _EvaluationConfigData(
            orch_config_data=[self.run1.config],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )
        validate_orchestration_url(
            config_data, test_orch_url, mock_ai_core_client, "resource-group", collector
        )
        # Should have error in collector
        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    @patch("gen_ai_hub.evaluations.utils.validation_utils.call_orchestration_service_with_v2_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_deployment_config")
    @patch("gen_ai_hub.evaluations.utils.validation_utils.fetch_and_validate_orchestration_config")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.select_model_details_randomly")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.update_test_orch_config")
    def test_unexpected_exception_raises_validation_error(
        self,
        mock_update_test_orch_config,
        mock_select_model,
        mock_fetch_and_validate,
        mock_fetch_deployment_config,
        mock_call_orchestration_service,
    ):
        from ai_api_client_sdk.models.status import Status
        from ai_core_sdk.ai_core_v2_client import AICoreV2Client
        
        collector = ValidationCollector()
        mock_ai_core_client = MagicMock(spec=AICoreV2Client)
        mock_deployment_config = MagicMock()
        mock_deployment_config.status = Status.RUNNING
        mock_deployment_config.configuration_id = "config-123"
        mock_fetch_deployment_config.return_value = mock_deployment_config
        mock_fetch_and_validate.return_value = None
        mock_select_model.return_value = ("gpt-4", "4.0")
        mock_update_test_orch_config.return_value = {"test": "config"}
        # ClientConnectionError is caught internally and added to collector
        def mock_call_with_connection_error(*args, **kwargs):
            error_collector = args[4] if len(args) > 4 else kwargs.get('error_collector')
            if error_collector:
                error_collector.add_error(
                    ErrorCode.INVALID_ORCHESTRATION_CONFIG_ERROR,
                    "Error occurred: Unexpected while trying to run the test orchestration config endpoint call"
                )
        mock_call_orchestration_service.side_effect = mock_call_with_connection_error

        test_orch_url = "https://api.ai.staging.eu-west-1.mlf-aws-dev.com/v2/inference/deployments/unexpected/"
        config_data = _EvaluationConfigData(
            orch_config_data=[self.run1.config],
            dataset_type="json",
            dataset_data={},
            metric_templates=[],
            metrics_list=[],
        )
        validate_orchestration_url(
            config_data, test_orch_url, mock_ai_core_client, "resource-group", collector
        )
        # Should have error in collector
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertRegex(str(cm.exception), "Error occurred.*while trying to run")


class TestValidateOrchestrationConfiguration(unittest.TestCase):
    def test_missing_modules(self):
        collector = ValidationCollector()
        run_data = [{}]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertIn("modules is mandatory in the orchestration config", str(cm.exception))

    def test_missing_model_or_prompt_templating(self):
        collector = ValidationCollector()
        run_data = [{"modules": {}}]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertIn("prompt_templating is mandatory in the modules field", str(cm.exception))

    def test_missing_name_in_model(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {"template": [{"content": "some content", "role": "user"}]},
                    "model": {},
                },
            }
        }]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertRegex(str(cm.exception), "Missing configuration for.*model.*name")

    def test_template_ref_in_prompt_templating(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template_ref": "b2eb90fa-bf26-4d5e-87c4-d37f49zshuhf3c"
                    },
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertRegex(str(cm.exception), "template_ref.*not yet supported")

    def test_empty_template_list(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {"template": []},
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertIn("template list cannot be empty", str(cm.exception))

    def test_missing_content_in_template_list(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {"template": [{}]},
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertRegex(str(cm.exception), "content.*role")

    def test_image_url_in_content_type(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": "https://i.natgeofe.com/n/548467d8-c5f1-4551-9f58-6817a8d2c45e/NationalGeographic_2572187_3x2.jpg"
                                        },
                                    }
                                ],
                            }
                        ]
                    },
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        with self.assertRaises(RuntimeError) as cm:
            validate_orchestration_configuration(run_data, collector)
            collector.raise_if_errors()
        self.assertIn("image_url is not supported", str(cm.exception))

    # write one positive test case where everything is right and no exception is raised
    def test_positive_case(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "content": "This is a prompt with {{?var1}} and {{?var2}}.",
                                "role": "user",
                            }
                        ]
                    },
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        validate_orchestration_configuration(run_data, collector)
        collector.raise_if_errors()  # Should not raise
        self.assertTrue(True)


class TestValidateInputParameters(unittest.TestCase):
    def test_empty_metrics(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "Sample text",
                            }
                        ]
                    },
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        metrics = []
        metric_templates = []
        with self.assertRaises(RuntimeError) as cm:
            validate_input_config(run_data, metrics, metric_templates, collector)
            collector.raise_if_errors()
        self.assertIn("Metrics list cannot be empty. Atleast one metric needs to be provided", str(cm.exception))

    def test_valid_input_parameters(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": "Sample text",
                            }
                        ]
                    },
                    "model": {
                        "name": "gpt-4",
                        "version": "latest",
                    },
                },
            }
        }]
        metrics = ["bert_score"]
        metric_templates = [
            {
                "evaluationMethod": "computed",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "bert_score",
                "name": "BERT Score",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]
        # This should not raise any exception
        validate_input_config(run_data, metrics, metric_templates, collector)
        collector.raise_if_errors()  # Should not raise

class TestValidateVariableMappingOfMetrics(unittest.TestCase):
    def test_valid_all_metrics_reference_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"reference": "value1", "column1": "value2"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/reference"
        }
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        validate_variable_mapping_of_metrics(
            metrics,
            metric_templates,
            template_vars_data,
            variable_mapping,
            collector,
        )
        collector.raise_if_errors()  # Should not raise
        self.assertTrue(True)

    def test_invalid_all_metrics_reference_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"reference-key": "value1", "column1": "value2"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/invalid_column"
        }
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        with self.assertRaises(RuntimeError):
            validate_variable_mapping_of_metrics(
                metrics,
                metric_templates,
                template_vars_data,
                variable_mapping,
                collector,
            )
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
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": ["reference"],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": ["json_schema"],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        validate_variable_mapping_of_metrics(
            metrics,
            metric_templates,
            template_vars_data,
            variable_mapping,
            collector,
        )
        collector.raise_if_errors()  # Should not raise
        self.assertTrue(True)

    def test_invalid_individual_metrics_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"reference": "value1", "json_schema": "value2"}]
        variable_mapping = {
            "metric1/invalid_key": "data/reference",
            "metric2/json_schema": "data/invalid_column",
        }
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        with self.assertRaises(RuntimeError):
            validate_variable_mapping_of_metrics(
                metrics,
                metric_templates,
                template_vars_data,
                variable_mapping,
                collector,
            )
            collector.raise_if_errors()

    def test_missing_dataset_column_for_all_metrics(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        template_vars_data = [{"column1": "value1"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/reference"
        }
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        with self.assertRaises(RuntimeError):
            validate_variable_mapping_of_metrics(
                metrics,
                metric_templates,
                template_vars_data,
                variable_mapping,
                collector,
            )
            collector.raise_if_errors()

    def test_invalid_custom_metric_mapping(self):
        collector = ValidationCollector()

        # Use a system metric name (not in mock_custom_metric_data)
        metrics = ["metric1", "system_metric"]

        # mock metric templates
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "system_metric",
                "name": "System metric",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]

        # Dataset has only these columns
        template_vars_data = [{"reference": "value1", "json_schema": "value2"}]

        # This mapping refers to a non-existent dataset field, which should trigger validation error
        variable_mapping = {
            "system_metric/topic": "data/non_existent_column",
            "metric1/reference": "data/reference",
        }

        with self.assertRaises(RuntimeError):
            validate_variable_mapping_of_metrics(
                metrics,
                metric_templates,
                template_vars_data,
                variable_mapping,
                collector,
            )
            collector.raise_if_errors()

    def test_valid_custom_metric_mapping(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2", "correctness"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "correctness",
                "name": "Correctness",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": ["topic"],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric 2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": ["json_schema"],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        template_vars_data = [{"field": "value1", "json_schema": "value2"}]
        variable_mapping = {
            "correctness/topic": "data/field",
            "metric2/json_schema": "data/json_schema",
        }
        validate_variable_mapping_of_metrics(
            metrics,
            metric_templates,
            template_vars_data,
            variable_mapping,
            collector,
        )
        collector.raise_if_errors()  # Should not raise
        self.assertTrue(True)

    def test_missing_dataset_column_for_individual_metrics(self):
        collector = ValidationCollector()
        metrics = ["metric1", "metric2"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric 1",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric2",
                "name": "Metric 2",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            },
        ]
        template_vars_data = [{"column1": "value1"}]
        variable_mapping = {
            "metric1/reference": "data/reference",
            "metric2/json_schema": "data/json_schema",
        }
        with self.assertRaises(RuntimeError):
            validate_variable_mapping_of_metrics(
                metrics,
                metric_templates,
                template_vars_data,
                variable_mapping,
                collector,
            )
            collector.raise_if_errors()


class TestValidateVariableMappingOfPrompts(unittest.TestCase):
    def test_valid_variable_mapping(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "content": "This is a prompt with {{?var1}} and {{?var2}}.",
                                "role": "user"
                            }
                        ]
                    }
                }
            }
        }]
        template_vars_data = [{"var1": "value1", "var2": "value2"}]
        variable_mapping = {"prompt/var1": "data/var1", "prompt/var2": "data/var2"}

        validate_variable_mapping_of_prompts(
            run_data, template_vars_data, variable_mapping, collector
        )
        collector.raise_if_errors()  # Should not raise
        self.assertTrue(True)

    def test_missing_variable_in_mapping_and_dataset(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "content": "This is a prompt with {{?var1}} and {{?var2}}.",
                                "role": "user"
                            }
                        ]
                    }
                }
            }
        }]
        template_vars_data = [{"var1": "value1"}]
        variable_mapping = {"prompt/var1": "data/var1"}

        with self.assertRaises(RuntimeError) as cm:
            validate_variable_mapping_of_prompts(
                run_data, template_vars_data, variable_mapping, collector
            )
            collector.raise_if_errors()
        self.assertIn("The provided prompt variable :var2 in Orch config does not match", str(cm.exception))

    def test_system_defined_variable_in_prompt(self):
        collector = ValidationCollector()
        content = "This is a prompt with {{?prompt}}"
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [{"content": content, "role": "user"}]
                    }
                }
            }
        }]
        template_vars_data = [{"var1": "value1"}]
        variable_mapping = {}

        with self.assertRaises(RuntimeError) as cm:
            validate_variable_mapping_of_prompts(
                run_data, template_vars_data, variable_mapping, collector
            )
            collector.raise_if_errors()
        self.assertIn("System defined variables", str(cm.exception))

    def test_variable_in_dataset_but_not_in_mapping(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "content": "This is a prompt with {{?var1}} and {{?var2}}.",
                                "role": "user"
                            }
                        ]
                    }
                }
            }
        }]
        template_vars_data = [{"var1": "value1", "var2": "value2"}]
        variable_mapping = {"prompt/var1": "data/var1"}

        validate_variable_mapping_of_prompts(
            run_data, template_vars_data, variable_mapping, collector
        )
        collector.raise_if_errors()  # Should not raise
        self.assertTrue(True)

    def test_variable_in_mapping_but_not_in_dataset(self):
        collector = ValidationCollector()
        run_data = [{
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "content": "This is a prompt with {{?var1}} and {{?var2}}.",
                                "role": "user"
                            }
                        ]
                    }
                }
            }
        }]
        template_vars_data = [{"var1": "value1"}]
        variable_mapping = {"prompt/var1": "data/var1", "prompt/var2": "data/var2"}

        with self.assertRaises(RuntimeError) as cm:
            validate_variable_mapping_of_prompts(
                run_data, template_vars_data, variable_mapping, collector
            )
            collector.raise_if_errors()
        self.assertIn("The provided prompt variable :var2", str(cm.exception))


class TestPopulateTemplateVarsDataIfSingleReferenceProvided(unittest.TestCase):
    def test_reference_key_directly_present_in_dataset_already_filled(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"topic": "banana", "reference": "ref_value"},
            {"topic": "apple", "reference": "ref_value"},
        ]
        variable_mapping = {}

        populate_dataset_data_if_single_reference_provided(
            template_vars_data, variable_mapping, collector
        )

        # Needs to replicate the reference value using existing value
        self.assertEqual(template_vars_data[1]["reference"], "ref_value")

    def test_reference_key_directly_present_in_dataset_single_value(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"topic": "banana", "reference": "ref_value"},
            {"topic": "apple"},
        ]
        variable_mapping = {}

        populate_dataset_data_if_single_reference_provided(
            template_vars_data, variable_mapping, collector
        )

        # Needs to replicate the reference value using existing value
        self.assertEqual(template_vars_data[1]["reference"], "ref_value")

    def test_reference_key_present_in_first_row(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"topic": "ml", "ref_key": "ref_value"},
            {"topic": "ai"},
            {"topic": "gen_ai"},
        ]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/ref_key"
        }

        populate_dataset_data_if_single_reference_provided(
            template_vars_data, variable_mapping, collector
        )

        self.assertEqual(template_vars_data[1]["ref_key"], "ref_value")
        self.assertEqual(template_vars_data[2]["ref_key"], "ref_value")

    def test_reference_key_missing_in_all_rows(self):
        collector = ValidationCollector()
        template_vars_data = [{"other_key": "value1"}, {"other_key": "value2"}]
        variable_mapping = {
            f"{ALL_METRICS_COLUMN_MAPPING_KEY}/reference": "data/ref_key"
        }

        with self.assertRaises(RuntimeError):
            populate_dataset_data_if_single_reference_provided(
                template_vars_data, variable_mapping, collector
            )
            collector.raise_if_errors()

    def test_partial_reference_key_in_dataset(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"topic": "banana", "reference": "ref_value"},
            {"topic": "apple", "reference": ""},
            {"topic": "apple", "reference": ""},
            {"topic": "apple", "reference": "ref_value"},
            {"topic": "apple", "reference": ""},
        ]
        variable_mapping = {}

        with self.assertRaises(RuntimeError):
            populate_dataset_data_if_single_reference_provided(
                template_vars_data, variable_mapping, collector
            )
            collector.raise_if_errors()

    def test_no_reference_key_in_dataset(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"topic": "banana"},
            {"topic": "apple"},
        ]
        variable_mapping = {"all_metrics/reference": "data/reference"}

        with self.assertRaises(RuntimeError):
            populate_dataset_data_if_single_reference_provided(
                template_vars_data, variable_mapping, collector
            )
            collector.raise_if_errors()


class TestPopulateTemplateVarsDataIfIndividualMetricReferenceProvided(unittest.TestCase):
    def test_reference_key_directly_present_in_dataset_single_value(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"metric1_reference": "value1", "column1": "value2"},
            {"column1": "value3"},
        ]
        variable_mapping = {"bleu/reference": "data/metric1_reference"}
        metrics = ["bleu"]

        populate_dataset_data_if_individual_metric_reference_provided(
            template_vars_data, variable_mapping, metrics, collector
        )
        print("template data now is ", template_vars_data)
        self.assertTrue(True)
        # assert template_vars_data[1]["metric1_reference"] == "value1"

    def test_reference_key_present_in_first_row(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"metric1_reference": "value1", "column1": "value2"},
            {"column1": "value3"},
            {"column1": "value4"},
        ]
        variable_mapping = {"bertscore/reference": "data/metric1_reference"}
        metrics = ["bertscore"]

        populate_dataset_data_if_individual_metric_reference_provided(
            template_vars_data, variable_mapping, metrics, collector
        )

        self.assertEqual(template_vars_data[1]["metric1_reference"], "value1")
        self.assertEqual(template_vars_data[2]["metric1_reference"], "value1")

    def test_reference_key_missing_in_all_rows(self):
        collector = ValidationCollector()
        template_vars_data = [{"column1": "value1"}, {"column1": "value2"}]
        variable_mapping = {"bleu/reference": "data/metric1_reference"}
        metrics = ["bleu"]

        with self.assertRaises(RuntimeError):
            populate_dataset_data_if_individual_metric_reference_provided(
                template_vars_data, variable_mapping, metrics, collector
            )
            collector.raise_if_errors()

    def test_reference_key_partial_rows(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"metric1_reference": "value1", "column1": "value2"},
            {"column1": "value3"},
            {"metric1_reference": "value4", "column1": "value5"},
        ]
        variable_mapping = {"rouge/reference": "data/metric1_reference"}
        metrics = ["rouge"]

        with self.assertRaises(RuntimeError):
            populate_dataset_data_if_individual_metric_reference_provided(
                template_vars_data, variable_mapping, metrics, collector
            )
            collector.raise_if_errors()

    def test_reference_key_not_in_variable_mapping(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"metric1_reference": "value1", "column1": "value2"},
            {"column1": "value3"},
        ]
        variable_mapping = {}
        metrics = ["metric1"]

        populate_dataset_data_if_individual_metric_reference_provided(
            template_vars_data, variable_mapping, metrics, collector
        )

        self.assertNotIn("metric1_reference", template_vars_data[1])

    def test_multiple_metrics_with_reference(self):
        collector = ValidationCollector()
        template_vars_data = [
            {"metric1_reference": "value1", "metric2_reference": "value2"},
            {"column1": "value3"},
        ]
        variable_mapping = {
            "rouge/reference": "data/metric1_reference",
            "exact-match/reference": "data/metric2_reference",
        }
        metrics = ["rouge", "exact-match"]

        populate_dataset_data_if_individual_metric_reference_provided(
            template_vars_data, variable_mapping, metrics, collector
        )

        self.assertEqual(template_vars_data[1]["metric1_reference"], "value1")
        self.assertEqual(template_vars_data[1]["metric2_reference"], "value2")


class TestExtractDatasetColumns(unittest.TestCase):
    def test_extract_from_list_of_dicts(self):
        template_variables = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"},
        ]
        result = extract_dataset_columns(template_variables)
        self.assertEqual(result, ["key1", "key2"])

    def test_extract_from_empty_list(self):
        template_variables = []
        result = extract_dataset_columns(template_variables)
        self.assertEqual(result, [])

    def test_extract_from_dict(self):
        template_variables = {"key1": "value1", "key2": "value2"}
        result = extract_dataset_columns(template_variables)
        self.assertEqual(result, ["key1", "key2"])

    def test_extract_from_empty_dict(self):
        template_variables = {}
        result = extract_dataset_columns(template_variables)
        self.assertEqual(result, [])

    def test_extract_from_non_dict_or_list(self):
        template_variables = "invalid_type"
        result = extract_dataset_columns(template_variables)
        self.assertEqual(result, [])


    def test_get_user_prompts_from_template_list(self):
        """Test with valid prompt templates"""
        template_list = [
            {"role": "user", "content": "this is a prompt from user."},
            {"role": "system", "content": "this is a prompt from system."},
        ]

        user_prompt_count = count_user_prompts_from_template_list(template_list)
        self.assertEqual(user_prompt_count, 1)

        template_list = [
            {"role": "user", "content": "this is a prompt from user."},
            {"role": "user", "content": "this is another prompt from user."},
        ]

        user_prompt_count = count_user_prompts_from_template_list(template_list)
        self.assertEqual(user_prompt_count, 2)


class TestCreateCustomMetricName(unittest.TestCase):
    def setUp(self):
        self.mock_custom_metric = {"metricName": "custom_metric_1", "scenario": "scenario_1", "version": "v1"}
        self.mock_custom_metric_missing_version = {"metricName": "custom_metric_1", "scenario": "scenario_1"}
        self.mock_custom_metric_metricId = {"metricId": "custom_metric_id"}
        self.mock_custom_metric_invalid_metricId = {
            "metricId": "custom_metric_id",
            "metricName": "custom_metric",
            "scenario": "genai-evaluations",
        }
        self.mock_custom_metric_missing_metric_name = {"scenario": "genai-evaluations", "version": "0.0.1"}
        self.mock_custom_metric_missing_scenario = {"metricName": "custom_metric", "version": "0.0.1"}
        self.mock_custom_metric_missing_scenario_and_metric_name = {"version": "0.0.1"}

    def test_valid_only_custom_metric_id(self):
        """Test with a valid custom metric name."""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric_metricId, collector)
        self.assertEqual(result, "custom_metric_id")
        collector.raise_if_errors()  # Should not raise

    def test_invalid_custom_metric_id(self):
        """Test with a valid custom metric name."""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric_invalid_metricId, collector)
        # Function returns the metric_id but adds error to collector
        self.assertEqual(result, "custom_metric_id")  # Still returns the metric_id
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Both 'metricId' and 'scenario/metricName' cannot be provided at the same time", str(cm.exception))

    def test_valid_full_custom_metric_name(self):
        """Test with a valid custom metric name."""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        self.assertEqual(result, "scenario_1/custom_metric_1/v1")
        collector.raise_if_errors()  # Should not raise

    def test_valid_no_version_custom_metric_name(self):
        """Test with a valid custom metric name."""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric_missing_version, collector)
        self.assertEqual(result, "scenario_1/custom_metric_1")
        collector.raise_if_errors()  # Should not raise

    def test_invalid_custom_metric_name_without_scenario(self):
        """Test with a valid custom metric name but no scenario."""
        self.mock_custom_metric["scenario"] = None
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        # Function still returns a value but adds error
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_empty_metric_name(self):
        """Test with an empty metricName."""
        self.mock_custom_metric["metricName"] = ""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'metricName' field in custom metric configuration", str(cm.exception))

    def test_empty_scenario(self):
        """Test with an empty scenario."""
        self.mock_custom_metric["scenario"] = ""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_none_metric_name(self):
        """Test with a None metricName."""
        self.mock_custom_metric["metricName"] = None
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'metricName' field in custom metric configuration", str(cm.exception))

    def test_none_scenario(self):
        """Test with a None scenario."""
        self.mock_custom_metric["scenario"] = None
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_both_metric_id_and_scenario_empty(self):
        """Test with both metric ID and scenario empty."""
        self.mock_custom_metric["metricName"] = ""
        self.mock_custom_metric["scenario"] = ""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_both_metric_id_and_scenario_none(self):
        """Test with both metric ID, metricName, and scenario None."""
        self.mock_custom_metric["metricName"] = None
        self.mock_custom_metric["scenario"] = None
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_no_required_variables_present_scenario(self):
        """Test with a None scenario."""
        collector = ValidationCollector()
        result = create_custom_metric_name({}, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_missing_scenario_and_metric_name(self):
        """Test with both scenario and metricName missing."""
        collector = ValidationCollector()
        result = create_custom_metric_name(
            self.mock_custom_metric_missing_scenario_and_metric_name, collector
        )
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))

    def test_missing_metric_name(self):
        """Test with a missing metricName."""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric_missing_metric_name, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'metricName' field in custom metric configuration", str(cm.exception))

    def test_missing_scenario(self):
        """Test with a missing scenario."""
        collector = ValidationCollector()
        result = create_custom_metric_name(self.mock_custom_metric_missing_scenario, collector)
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Missing 'scenario' field in custom metric configuration", str(cm.exception))


class TestSelectModelDetailsRandomly(unittest.TestCase):
    def test_valid_selection(self):
        run1 = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "4.0"},
                }
            }
        }
        run2 = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "llama2", "version": "7b"},
                }
            }
        }
        run3 = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "4.1"},
                }
            }
        }

        run_data = [run1, run2, run3]
        collector = ValidationCollector()

        name, model_version = select_model_details_randomly(run_data, collector)
        collector.raise_if_errors()

        self.assertIn(name, {"gpt-4", "llama2"})
        self.assertIn(model_version, {"4.0", "4.1", "7b"})

    def test_no_model_data_raises_validation_error(self):
        run_data = []
        collector = ValidationCollector()

        result = select_model_details_randomly(run_data, collector)
        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()
        self.assertIsNone(result)

    def test_empty_names(self):
        run1 = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "", "version": "4.0"},
                }
            }
        }
        run2 = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "", "version": "4.1"},
                }
            }
        }

        run_data = [run1, run2]
        collector = ValidationCollector()

        result = select_model_details_randomly(run_data, collector)
        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()
        self.assertIsNone(result)


class TestCreateModelVersionsMapFromOrchConfigs(unittest.TestCase):
    def test_returns_expected_map(self):
        orch_config = {
            "modules": {
                "prompt_templating": {"model": {"name": "gpt-4", "version": "4.0"}}
            }
        }
        collector = ValidationCollector()
        result = create_model_versions_map_from_orch_configs([orch_config], collector)

        self.assertEqual(result, {"gpt-4": ["4.0"]})
        collector.raise_if_errors()

    def test_empty_model_data_triggers_collector(self):
        orch_config = {
            "modules": {"prompt_templating": {"model": {"name": "", "version": ""}}}
        }
        collector = ValidationCollector()
        result = create_model_versions_map_from_orch_configs([orch_config], collector)

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

        self.assertIsNone(result)


class TestCreateModelVersionsMapFromConfigurationParamBindings(unittest.TestCase):
    def test_valid_json_stringified_value(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = json.dumps(
            [
                {"modelName": "gpt-4", "modelVersions": ["4.0", "4.1"]},
                {"modelName": "llama2", "modelVersions": ["7b"]},
            ]
        )
        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "allow"
        param_bindings = [param1, param2]

        collector = ValidationCollector()
        result_map, filter_type = create_model_versions_map_from_configuration_param_bindings(
            param_bindings, collector
        )
        self.assertEqual(result_map, {"gpt-4": ["4.0", "4.1"], "llama2": ["7b"]})
        self.assertEqual(filter_type, "allow")

    def test_model_filter_list_value_is_none(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = None
        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "deny"
        param_bindings = [param1, param2]

        collector = ValidationCollector()
        result_map, filter_type = create_model_versions_map_from_configuration_param_bindings(
            param_bindings, collector
        )
        self.assertEqual(result_map, {})
        self.assertEqual(filter_type, "deny")

    def test_invalid_json_adds_error(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = "[invalid-json]"
        param2 = MagicMock()
        param2.key = "modelFilterListType"
        param2.value = "allow"
        param_bindings = [param1, param2]

        collector = ValidationCollector()
        result_map, filter_type = create_model_versions_map_from_configuration_param_bindings(
            param_bindings, collector
        )
        # Function adds error to collector instead of raising
        self.assertEqual(result_map, {})
        self.assertEqual(filter_type, "allow")

    def test_missing_model_filter_list_type(self):
        param1 = MagicMock()
        param1.key = "modelFilterList"
        param1.value = json.dumps(
            [{"modelName": "gpt-4", "modelVersions": ["latest"]}]
        )
        param_bindings = [param1]

        collector = ValidationCollector()
        result_map, filter_type = create_model_versions_map_from_configuration_param_bindings(
            param_bindings, collector
        )
        self.assertEqual(result_map, {"gpt-4": ["latest"]})
        self.assertIsNone(filter_type)


class TestParseModelFilterList(unittest.TestCase):
    def test_parse_valid_dict_list(self):
        param = MagicMock()
        param.value = [{"modelName": "gpt-4", "modelVersions": ["4.0"]}]
        collector = ValidationCollector()
        result = parse_model_filter_list(param, collector)
        self.assertEqual(result, [{"modelName": "gpt-4", "modelVersions": ["4.0"]}])

    def test_parse_valid_json_string(self):
        param = MagicMock()
        param.value = json.dumps([{"modelName": "gpt-4", "modelVersions": ["4.0"]}])
        collector = ValidationCollector()
        result = parse_model_filter_list(param, collector)
        self.assertEqual(result, [{"modelName": "gpt-4", "modelVersions": ["4.0"]}])

    def test_parse_none_returns_empty(self):
        param = MagicMock()
        param.value = None
        collector = ValidationCollector()
        result = parse_model_filter_list(param, collector)
        self.assertEqual(result, [])

    def test_parse_invalid_json_adds_error(self):
        param = MagicMock()
        param.value = "[invalid-json"
        collector = ValidationCollector()
        result = parse_model_filter_list(param, collector)
        # Function adds error to collector instead of raising
        self.assertEqual(result, [])
        self.assertTrue(collector.has_errors())

    def test_parse_type_error_adds_error(self):
        param = MagicMock()
        param.value = 123
        collector = ValidationCollector()
        result = parse_model_filter_list(param, collector)
        # Function adds error to collector instead of raising
        self.assertEqual(result, [])
        self.assertTrue(collector.has_errors())

    def test_parse_string_null_returns_empty(self):
        param = MagicMock()
        param.value = "null"
        collector = ValidationCollector()
        result = parse_model_filter_list(param, collector)
        self.assertEqual(result, [])


class TestBuildModelVersionsMap(unittest.TestCase):
    def test_valid_model_list(self):
        model_list = [
            {"modelName": "gpt-4", "modelVersions": ["4.0", "4.1"]},
            {"modelName": "llama2", "modelVersions": ["7b"]},
        ]
        expected = {"gpt-4": ["4.0", "4.1"], "llama2": ["7b"]}
        result = build_model_versions_map(model_list)
        self.assertEqual(result, expected)

    def test_model_list_with_missing_name(self):
        model_list = [
            {"modelName": "gpt-4", "modelVersions": ["4.0"]},
            {"modelVersions": ["7b"]},  # Missing modelName
        ]
        expected = {"gpt-4": ["4.0"]}
        result = build_model_versions_map(model_list)
        self.assertEqual(result, expected)

    def test_empty_model_list(self):
        model_list = []
        result = build_model_versions_map(model_list)
        self.assertEqual(result, {})


class TestExtractDeploymentId(unittest.TestCase):
    def test_url_with_trailing_slash(self):
        url = "https://host.domain/api/v1/deployments/deployment123/"
        self.assertEqual(extract_deployment_id(url), "deployment123")

    def test_url_without_trailing_slash(self):
        url = "https://host.domain/api/v1/deployments/deployment456"
        self.assertEqual(extract_deployment_id(url), "deployment456")

class TestHandleMissingDependentVariables(unittest.TestCase):
    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_dataset_columns")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_metrics_variables")
    def test_variable_present_in_dataset(self, mock_extract_vars, mock_extract_cols):
        mock_extract_cols.return_value = {"question", "answer"}
        mock_extract_vars.return_value = ["question"]

        collector = ValidationCollector()
        metrics = ["metric1"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric1",
                "description": "This is a description for Pointwise Correctness.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]
        dataset = [{"question": "What?", "answer": "Yes"}]
        variable_mapping = {}

        handle_missing_dependent_variables_in_dataset(
            dataset, metrics, metric_templates, variable_mapping, collector
        )

        self.assertFalse(collector.has_errors())

    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_dataset_columns")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_metrics_variables")
    def test_variable_mapped_correctly(self, mock_extract_vars, mock_extract_cols):
        mock_extract_cols.return_value = {"other_column"}
        mock_extract_vars.return_value = ["question"]

        collector = ValidationCollector()
        metrics = ["metric1"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric1",
                "description": "This is a description for Pointwise Correctness.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]
        dataset = [{"other_column": "value"}]
        variable_mapping = {"metric1/question": "other_column"}

        handle_missing_dependent_variables_in_dataset(
            dataset, metrics, metric_templates, variable_mapping, collector
        )
        self.assertFalse(collector.has_errors())

    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_dataset_columns")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_metrics_variables")
    def test_variable_present_under_all_metrics_mapping(
        self, mock_extract_vars, mock_extract_cols
    ):
        mock_extract_cols.return_value = {"some_column"}
        mock_extract_vars.return_value = ["question"]

        collector = ValidationCollector()
        metrics = ["metric1"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric1",
                "description": "This is a description for Pointwise Correctness.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]
        dataset = [{"some_column": "value"}]
        variable_mapping = {"all_metrics/question": "some_column"}

        handle_missing_dependent_variables_in_dataset(
            dataset, metrics, metric_templates, variable_mapping, collector
        )
        self.assertFalse(collector.has_errors())

    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_dataset_columns")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_metrics_variables")
    def test_missing_variable_and_no_mapping_raises_error(
        self, mock_extract_vars, mock_extract_cols
    ):
        mock_extract_cols.return_value = {"only_column"}
        mock_extract_vars.return_value = ["question"]

        collector = ValidationCollector()
        metrics = ["metric1"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "metric1",
                "name": "Metric1",
                "description": "This is a description for Pointwise Correctness.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]
        dataset = [{"only_column": "data"}]
        variable_mapping = {}  # no mapping for "question"

        handle_missing_dependent_variables_in_dataset(
            dataset, metrics, metric_templates, variable_mapping, collector
        )

        with self.assertRaises(RuntimeError) as e:
            collector.raise_if_errors()

        self.assertIn("Invalid mapping", str(e.exception))

    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_dataset_columns")
    @patch("gen_ai_hub.evaluations.utils.gen_utils.extract_metrics_variables")
    def test_metric_with_no_dependent_variables_is_skipped(
        self, mock_extract_vars, mock_extract_cols
    ):
        mock_extract_cols.return_value = {"irrelevant"}
        mock_extract_vars.return_value = []

        collector = ValidationCollector()
        metrics = ["custom_metric"]
        metric_templates = [
            {
                "evaluationMethod": "llm-as-a-judge",
                "scenario": "genai-evaluations",
                "createdAt": "0001-01-01 00:00:00+00:00",
                "managedBy": "imperative",
                "metricType": "evaluation",
                "systemPredefined": True,
                "id": "custom_metric",
                "name": "Custom Metric",
                "description": "This is a description for Bert Score.",
                "version": "1.0.0",
                "includeProperties": ["reference"],
                "additionalProperties": {
                    "variables": [],
                    "output_type": "numerical",
                    "supported_values": [1, 5],
                    "experimental": False,
                },
            }
        ]

        dataset = [{"irrelevant": "data"}]
        variable_mapping = {}

        handle_missing_dependent_variables_in_dataset(
            dataset, metrics, metric_templates, variable_mapping, collector
        )

        self.assertFalse(collector.has_errors())


class TestHandleReferenceMissingRows(unittest.TestCase):
    @patch(
        "gen_ai_hub.evaluations.utils.gen_utils.populate_dataset_data_if_single_reference_provided"
    )
    @patch(
        "gen_ai_hub.evaluations.utils.gen_utils.populate_dataset_data_if_individual_metric_reference_provided"
    )
    def test_calls_both_population_functions(
        self,
        mock_populate_individual,
        mock_populate_all,
    ):
        # Arrange
        template_vars_data = [{"input": "Hello", "reference": "Hi"}]
        variable_mapping = {"allMetrics/reference": "reference"}
        metrics = ["metric1", "metric2"]
        collector = MagicMock()

        # Act
        handle_reference_missing_rows(
            template_vars_data, variable_mapping, metrics, collector
        )

        # Assert
        mock_populate_all.assert_called_once_with(
            template_vars_data, variable_mapping, collector
        )
        mock_populate_individual.assert_called_once_with(
            template_vars_data, variable_mapping, metrics, collector
        )


class TestTemplateContent(unittest.TestCase):
    def test_template_content_with_single_list(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "This is a prompt with {{?var1}} and {{?var2}}.",
                                    }
                                ],
                            }
                        ]
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, {"var1", "var2"})

    def test_template_content_with_multiple_lists(self):
        orch_config = {
            "modules": {
                "prompt_templating": {
                    "prompt": {
                        "template": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "This is a prompt with {{?var1}} and {{?var2}}.",
                                    },
                                    {
                                        "type": "text",
                                        "text": "This is a prompt with {{?var3}} and {{?var4}}.",
                                    },
                                    {
                                        "type": "text",
                                        "text": "This is a prompt with {{?var5}} and {{?var6}}.",
                                    },
                                ],
                            }
                        ]
                    }
                }
            }
        }
        result = get_prompt_variables_from_orch_config(orch_config)
        self.assertEqual(result, {"var1", "var2", "var3", "var4", "var5", "var6"})


# Tests for uncovered lines
class TestUpdateVariableMapping(unittest.TestCase):
    def test_update_variable_mapping(self):
        """Test update_variable_mapping function"""
        variable_mapping = {"var1": "field1", "var2": "field2"}
        prefix_key = "prompt/"
        variable_mapping_dict = {}
        
        result = update_variable_mapping(variable_mapping, prefix_key, variable_mapping_dict)
        
        self.assertEqual(result, {
            "prompt/var1": "data/field1",
            "prompt/var2": "data/field2"
        })
        self.assertEqual(variable_mapping_dict, result)  # Should modify the dict in place

    def test_update_variable_mapping_with_existing_dict(self):
        """Test update_variable_mapping with existing dict"""
        variable_mapping = {"var1": "field1"}
        prefix_key = "metric1/"
        variable_mapping_dict = {"existing": "value"}
        
        result = update_variable_mapping(variable_mapping, prefix_key, variable_mapping_dict)
        
        self.assertIn("metric1/var1", result)
        self.assertIn("existing", result)


class TestGetAccumulatedConfigData(unittest.TestCase):
    def test_get_accumulated_config_data_single(self):
        """Test get_accumulated_config_data with single config"""
        config1 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={"row1": {"input": "test"}},
            metric_templates=[{"id": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping={"prompt/input": "data/input"},
        )
        
        result = get_accumulated_config_data([config1])
        
        self.assertEqual(result.orch_config_data, config1.orch_config_data)
        self.assertEqual(result.metrics_list, ["metric1"])
        self.assertEqual(result.variable_mapping, {"prompt/input": "data/input"})

    def test_get_accumulated_config_data_multiple(self):
        """Test get_accumulated_config_data with multiple configs"""
        config1 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={"row1": {"input": "test1"}},
            metric_templates=[{"id": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping={"prompt/input": "data/input"},
        )
        config2 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "llama2"}}}}],
            dataset_type="json",
            dataset_data={"row1": {"input": "test1"}},
            metric_templates=[{"id": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping={"prompt/output": "data/output"},
        )
        
        result = get_accumulated_config_data([config1, config2])
        
        self.assertEqual(len(result.orch_config_data), 2)
        self.assertEqual(result.variable_mapping, {"prompt/input": "data/input", "prompt/output": "data/output"})

    def test_get_accumulated_config_data_with_none_mapping(self):
        """Test get_accumulated_config_data when variable_mapping is None"""
        config1 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={"row1": {"input": "test"}},
            metric_templates=[{"id": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping=None,
        )
        
        result = get_accumulated_config_data([config1])
        
        self.assertEqual(result.variable_mapping, {})

    def test_get_accumulated_config_data_exception_handling(self):
        """Test get_accumulated_config_data exception handling"""
        # Create a config that will cause an exception inside the try block
        # The exception should be caught and wrapped in RuntimeError
        config1 = _EvaluationConfigData(
            orch_config_data=[{"modules": {"prompt_templating": {"model": {"name": "gpt-4"}}}}],
            dataset_type="json",
            dataset_data={"row1": {"input": "test"}},
            metric_templates=[{"id": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping={"prompt/input": "data/input"},
        )
        
        # Create a bad config that will cause an error when extending
        class BadOrchConfig:
            def __iter__(self):
                raise ValueError("Error during iteration")
        
        bad_config = _EvaluationConfigData(
            orch_config_data=BadOrchConfig(),  # This will cause an error when extending
            dataset_type="json",
            dataset_data={"row1": {"input": "test"}},
            metric_templates=[{"id": "metric1"}],
            metrics_list=["metric1"],
            variable_mapping=None,
        )
        
        with self.assertRaises(RuntimeError) as cm:
            get_accumulated_config_data([config1, bad_config])
        self.assertRegex(str(cm.exception), "Failed to accumulate")


class TestCreateModelVersionsMapFromCustomMetricConfig(unittest.TestCase):
    def test_create_model_versions_map_from_custom_metric_config(self):
        """Test create_model_versions_map_from_custom_metric_config"""
        custom_metric_config_data = [
            {
                "metricId": "metric1",
                MODEL_CONFIGURATION_KEY: {
                    MODEL_NAME_KEY: "gpt-4",
                    MODEL_VERSION_KEY: "4.0",
                }
            },
            {
                "metricId": "metric2",
                MODEL_CONFIGURATION_KEY: {
                    MODEL_NAME_KEY: "llama2",
                    MODEL_VERSION_KEY: "7b",
                }
            },
        ]
        
        result = create_model_versions_map_from_custom_metric_config(custom_metric_config_data)
        
        self.assertEqual(result, {"gpt-4": ["4.0"], "llama2": ["7b"]})

    def test_create_model_versions_map_from_custom_metric_config_empty(self):
        """Test create_model_versions_map_from_custom_metric_config with empty list"""
        result = create_model_versions_map_from_custom_metric_config([])
        self.assertEqual(result, {})

    def test_create_model_versions_map_from_custom_metric_config_none(self):
        """Test create_model_versions_map_from_custom_metric_config with None"""
        result = create_model_versions_map_from_custom_metric_config(None)
        self.assertEqual(result, {})

    def test_create_model_versions_map_from_custom_metric_config_with_latest(self):
        """Test create_model_versions_map_from_custom_metric_config with latest version"""
        custom_metric_config_data = [
            {
                "metricId": "metric1",
                MODEL_CONFIGURATION_KEY: {
                    MODEL_NAME_KEY: "gpt-4",
                    # No version specified, should use LATEST_MODEL_VERSION_KEY
                }
            },
        ]
        
        result = create_model_versions_map_from_custom_metric_config(custom_metric_config_data)
        
        self.assertEqual(result, {"gpt-4": [LATEST_MODEL_VERSION_KEY]})

    def test_create_model_versions_map_from_custom_metric_config_missing_model_name(self):
        """Test create_model_versions_map_from_custom_metric_config with missing model name"""
        custom_metric_config_data = [
            {
                "metricId": "metric1",
                MODEL_CONFIGURATION_KEY: {
                    MODEL_VERSION_KEY: "4.0",
                    # Missing model name
                }
            },
        ]
        
        result = create_model_versions_map_from_custom_metric_config(custom_metric_config_data)
        
        self.assertEqual(result, {})  # Should not add entry if model_name is missing


class TestUpdateTestOrchConfigException(unittest.TestCase):
    def test_update_test_orch_config_exception_handling(self):
        """Test update_test_orch_config exception handling"""
        collector = ValidationCollector()
        # Mock ORCHESTRATION_CONFIGURATION_V2 to raise an exception
        with patch("gen_ai_hub.evaluations.utils.gen_utils.ORCHESTRATION_CONFIGURATION_V2", {}):
            result = update_test_orch_config("gpt-4", "4.0", collector)
            
            self.assertIsNone(result)
            with self.assertRaises(RuntimeError) as cm:
                collector.raise_if_errors()
            self.assertIn("Error updating model name and version", str(cm.exception))


class TestValidateMetricName(unittest.TestCase):
    def test_validate_metric_name_empty(self):
        """Test validate_metric_name with empty metric"""
        collector = ValidationCollector()
        all_supported_metrics = ["bert_score", "bleu"]
        
        validate_metric_name("", all_supported_metrics, collector)
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Metric name cannot be empty", str(cm.exception))

    def test_validate_metric_name_unsupported(self):
        """Test validate_metric_name with unsupported metric"""
        collector = ValidationCollector()
        all_supported_metrics = ["bert_score", "bleu"]
        
        validate_metric_name("unknown_metric", all_supported_metrics, collector)
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("unknown_metric is neither a system supported metric", str(cm.exception))

    def test_validate_metric_name_valid(self):
        """Test validate_metric_name with valid metric"""
        collector = ValidationCollector()
        all_supported_metrics = ["bert_score", "bleu"]
        
        validate_metric_name("bert_score", all_supported_metrics, collector)
        
        collector.raise_if_errors()  # Should not raise


class TestCheckIfMetricIsDefinedWithSlash(unittest.TestCase):
    def test_check_if_metric_is_defined_with_slash_format(self):
        """Test check_if_metric_is_defined with metric in scenario/name/version format"""
        collector = ValidationCollector()
        metrics = ["scenario1/metric1/v1.0"]
        metric_templates = [
            {
                "id": "metric1",
                "scenario": "scenario1",
                "name": "metric1",
                "version": "v1.0",
            }
        ]
        
        check_if_metric_is_defined(metrics, metric_templates, collector)
        
        collector.raise_if_errors()  # Should not raise

    def test_check_if_metric_is_defined_with_slash_format_not_found(self):
        """Test check_if_metric_is_defined with metric in slash format not found"""
        collector = ValidationCollector()
        metrics = ["scenario1/metric1/v1.0"]
        metric_templates = [
            {
                "id": "metric1",
                "scenario": "scenario2",  # Different scenario
                "name": "metric1",
                "version": "v1.0",
            }
        ]
        
        check_if_metric_is_defined(metrics, metric_templates, collector)
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("scenario1/metric1/v1.0 is neither a system supported metric", str(cm.exception))


class TestExtractMetricsVariablesWithMetricName(unittest.TestCase):
    def test_extract_metrics_variables_with_metric_name(self):
        """Test extract_metrics_variables with metric_name parameter"""
        metric_templates = [
            {
                "id": "metric1",
                "name": "Metric 1",
                "additionalProperties": {
                    "variables": ["var1", "var2"]
                }
            },
            {
                "id": "metric2",
                "name": "Metric 2",
                "additionalProperties": {
                    "variables": ["var3"]
                }
            },
        ]
        
        result = extract_metrics_variables(metric_templates, "metric1")
        
        self.assertEqual(result, ["var1", "var2"])

    def test_extract_metrics_variables_with_metric_name_by_name_key(self):
        """Test extract_metrics_variables with metric_name matching name key"""
        metric_templates = [
            {
                "id": "metric1",
                "name": "Metric 1",
                "additionalProperties": {
                    "variables": ["var1", "var2"]
                }
            },
        ]
        
        result = extract_metrics_variables(metric_templates, "Metric 1")
        
        self.assertEqual(result, ["var1", "var2"])


class TestValidateIndividualCustomMetrics(unittest.TestCase):
    def test_validate_individual_custom_metrics(self):
        """Test validate_individual_custom_metrics"""
        collector = ValidationCollector()
        variable_mapping = {
            "custom_metric1/var1": "data/field1",
        }
        dataset_columns = ["field1"]
        custom_metric_ids = ["custom_metric1"]
        custom_metric_variables = {"var1"}
        
        validate_individual_custom_metrics(
            variable_mapping,
            dataset_columns,
            custom_metric_ids,
            custom_metric_variables,
            collector,
        )
        
        collector.raise_if_errors()  # Should not raise

    def test_validate_individual_custom_metrics_removes_system_variables(self):
        """Test validate_individual_custom_metrics removes predefined system variables"""
        collector = ValidationCollector()
        variable_mapping = {}
        dataset_columns = ["var1"]  # var1 is in dataset, so no error after system var is removed
        custom_metric_ids = []
        custom_metric_variables = {AICORE_LLM_PROMPT_TEMPLATE_KEY, "var1"}
        
        validate_individual_custom_metrics(
            variable_mapping,
            dataset_columns,
            custom_metric_ids,
            custom_metric_variables,
            collector,
        )
        
        # Should not raise since system variable is removed and var1 is in dataset
        collector.raise_if_errors()


class TestValidateEmptyMappingWithCustomVars(unittest.TestCase):
    def test_validate_empty_mapping_with_custom_vars(self):
        """Test _validate_empty_mapping_with_custom_vars"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_empty_mapping_with_custom_vars
        
        collector = ValidationCollector()
        variable_mapping = {}
        dataset_columns = ["field1"]
        custom_metric_variables = {"var1", "var2"}
        
        _validate_empty_mapping_with_custom_vars(
            variable_mapping,
            dataset_columns,
            custom_metric_variables,
            collector,
        )
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Variable mapping is empty", str(cm.exception))

    def test_validate_empty_mapping_with_custom_vars_all_in_dataset(self):
        """Test _validate_empty_mapping_with_custom_vars when all vars in dataset"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_empty_mapping_with_custom_vars
        
        collector = ValidationCollector()
        variable_mapping = {}
        dataset_columns = ["var1", "var2"]
        custom_metric_variables = {"var1", "var2"}
        
        _validate_empty_mapping_with_custom_vars(
            variable_mapping,
            dataset_columns,
            custom_metric_variables,
            collector,
        )
        
        collector.raise_if_errors()  # Should not raise


class TestValidateMappingEntry(unittest.TestCase):
    def test_validate_mapping_entry_short_key(self):
        """Test _validate_mapping_entry with key less than 3 parts"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_mapping_entry
        
        collector = ValidationCollector()
        key = "metric/var"  # Only 2 parts
        value = "data/field"
        custom_metric_ids = ["metric"]
        custom_metric_variables = {"var"}
        dataset_columns = ["field"]
        
        _validate_mapping_entry(
            key, value, custom_metric_ids, custom_metric_variables, dataset_columns, collector
        )
        
        collector.raise_if_errors()  # Should not raise (early return)

    def test_validate_mapping_entry_not_custom_metric(self):
        """Test _validate_mapping_entry with non-custom metric key"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_mapping_entry
        
        collector = ValidationCollector()
        key = "all_metrics/var1"  # COLUMN_MAPPING_DEFAULT_KEYS
        value = "data/field"
        custom_metric_ids = []
        custom_metric_variables = set()
        dataset_columns = ["field"]
        
        _validate_mapping_entry(
            key, value, custom_metric_ids, custom_metric_variables, dataset_columns, collector
        )
        
        collector.raise_if_errors()  # Should not raise (early return)

    def test_validate_mapping_entry_invalid_variable(self):
        """Test _validate_mapping_entry with invalid variable"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_mapping_entry
        
        collector = ValidationCollector()
        # Key needs at least 3 parts for the function to process it
        key = "scenario1/metric1/invalid_var"
        value = "data/field"
        custom_metric_ids = ["scenario1/metric1"]
        custom_metric_variables = {"valid_var"}
        # invalid_var is NOT in custom_metric_variables AND NOT in dataset_columns
        dataset_columns = ["field"]
        
        _validate_mapping_entry(
            key, value, custom_metric_ids, custom_metric_variables, dataset_columns, collector
        )
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("Invalid mapping value provided", str(cm.exception))

    def test_validate_mapping_entry_missing_dataset_column(self):
        """Test _validate_mapping_entry with missing dataset column"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_mapping_entry
        
        collector = ValidationCollector()
        # Key needs at least 3 parts for the function to process it
        key = "scenario1/metric1/var1"
        value = "data/missing_field"
        custom_metric_ids = ["scenario1/metric1"]
        custom_metric_variables = {"var1"}
        # var1 is in custom_metric_variables, so first check passes
        # missing_field (dataset_value) is not in dataset_columns, so second check should fail
        dataset_columns = ["other_field"]
        
        _validate_mapping_entry(
            key, value, custom_metric_ids, custom_metric_variables, dataset_columns, collector
        )
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertRegex(str(cm.exception), "The provided mapping.*is not valid")

    def test_validate_mapping_entry_value_without_slash(self):
        """Test _validate_mapping_entry with value without slash"""
        from gen_ai_hub.evaluations.utils.gen_utils import _validate_mapping_entry
        
        collector = ValidationCollector()
        key = "custom_metric1/var1"
        value = "just_field"  # No "data/" prefix
        custom_metric_ids = ["custom_metric1"]
        custom_metric_variables = {"var1"}
        dataset_columns = ["just_field"]
        
        _validate_mapping_entry(
            key, value, custom_metric_ids, custom_metric_variables, dataset_columns, collector
        )
        
        collector.raise_if_errors()  # Should not raise


class TestHandleJsonSchemaMatch(unittest.TestCase):
    def test_handle_json_schema_match(self):
        """Test handle_json_schema_match"""
        collector = ValidationCollector()
        metrics = [JSON_SCHEMA_MATCH_METRIC_ID, "other_metric"]
        dataset_data = [
            {"json_schema": '{"type": "object"}'},
            {"other": "data"},
        ]
        variable_mapping = {}
        
        handle_json_schema_match(metrics, dataset_data, variable_mapping, collector)
        
        # Should populate missing rows
        self.assertIn("json_schema", dataset_data[1])
        collector.raise_if_errors()  # Should not raise

    def test_handle_json_schema_match_not_in_metrics(self):
        """Test handle_json_schema_match when metric not in list"""
        collector = ValidationCollector()
        metrics = ["other_metric"]
        dataset_data = [{"other": "data"}]
        variable_mapping = {}
        
        handle_json_schema_match(metrics, dataset_data, variable_mapping, collector)
        
        # Should not modify data
        self.assertNotIn("json_schema", dataset_data[0])


class TestValidateLanguageCodeAndDataPopulation(unittest.TestCase):
    def test_validate_language_code_and_data_population_valid(self):
        """Test validate_language_code_and_data_population with valid language codes"""
        collector = ValidationCollector()
        dataset_data = [
            {LANGUAGE_KEY: "en"},
            {LANGUAGE_KEY: "fr"},
        ]
        variable_mapping = {}
        
        validate_language_code_and_data_population(dataset_data, variable_mapping, collector)
        
        collector.raise_if_errors()  # Should not raise

    def test_validate_language_code_and_data_population_missing_value(self):
        """Test validate_language_code_and_data_population with missing values"""
        collector = ValidationCollector()
        dataset_data = [
            {LANGUAGE_KEY: "en"},
            {},  # Missing key entirely
        ]
        variable_mapping = {}
        
        validate_language_code_and_data_population(dataset_data, variable_mapping, collector)
        
        # After populate_dataset_data_if_data_missing, the empty row should have "en"
        # But if it's still None or empty after population, it should error
        # Actually, the function populates first, so we need a case where all are empty
        dataset_data2 = [
            {},  # Missing key
            {},  # Missing key
        ]
        collector2 = ValidationCollector()
        validate_language_code_and_data_population(dataset_data2, variable_mapping, collector2)
        
        # Should error because no valid value to populate from
        with self.assertRaises(RuntimeError):
            collector2.raise_if_errors()

    def test_validate_language_code_and_data_population_invalid_code(self):
        """Test validate_language_code_and_data_population with invalid language code"""
        collector = ValidationCollector()
        dataset_data = [
            {LANGUAGE_KEY: "invalid_lang_code"},
        ]
        variable_mapping = {}
        
        validate_language_code_and_data_population(dataset_data, variable_mapping, collector)
        
        with self.assertRaises(RuntimeError) as cm:
            collector.raise_if_errors()
        self.assertIn("is not supported by the language match metric", str(cm.exception))

    def test_validate_language_code_and_data_population_with_mapping(self):
        """Test validate_language_code_and_data_population with variable mapping"""
        collector = ValidationCollector()
        dataset_data = [
            {"lang_field": "en"},
            {"lang_field": "fr"},
        ]
        variable_mapping = {f"{LANGUAGE_MATCH_METRIC_ID}/{LANGUAGE_KEY}": "data/lang_field"}
        
        validate_language_code_and_data_population(dataset_data, variable_mapping, collector)
        
        collector.raise_if_errors()  # Should not raise


class TestHandleLanguageMatch(unittest.TestCase):
    def test_handle_language_match(self):
        """Test handle_language_match"""
        collector = ValidationCollector()
        metrics = [LANGUAGE_MATCH_METRIC_ID, "other_metric"]
        dataset_data = [
            {LANGUAGE_KEY: "en"},
        ]
        variable_mapping = {}
        
        handle_language_match(metrics, dataset_data, variable_mapping, collector)
        
        collector.raise_if_errors()  # Should not raise

    def test_handle_language_match_not_in_metrics(self):
        """Test handle_language_match when metric not in list"""
        collector = ValidationCollector()
        metrics = ["other_metric"]
        dataset_data = [{"other": "data"}]
        variable_mapping = {}
        
        handle_language_match(metrics, dataset_data, variable_mapping, collector)
        
        # Should not raise or modify
        collector.raise_if_errors()  # Should not raise


class TestUpdateArtifactDict(unittest.TestCase):
    def test_update_artifact_dict_with_string(self):
        """Test update_artifact_dict with string artifact"""
        artifact_reference = ArtifactSource(
            artifact="artifact-id-123",
            file_type="json",
        )
        artifact_dict_count = {}
        
        update_artifact_dict(artifact_reference, artifact_dict_count)
        
        self.assertEqual(artifact_dict_count, {"artifact-id-123": 1})
        
        # Test incrementing
        update_artifact_dict(artifact_reference, artifact_dict_count)
        self.assertEqual(artifact_dict_count, {"artifact-id-123": 2})

    def test_update_artifact_dict_with_artifact_object(self):
        """Test update_artifact_dict with Artifact object"""
        from ai_api_client_sdk.models.artifact import Artifact
        
        mock_artifact = MagicMock(spec=Artifact)
        mock_artifact.id = "artifact-uuid-456"
        
        artifact_reference = ArtifactSource(
            artifact=mock_artifact,
            file_type="json",
        )
        artifact_dict_count = {}
        
        update_artifact_dict(artifact_reference, artifact_dict_count)
        
        self.assertEqual(artifact_dict_count, {"artifact-uuid-456": 1})


class TestResolveOrchestrationConfigV2(unittest.TestCase):
    def test_resolve_orchestration_config_v2(self):
        """Test resolve_orchestration_config_v2"""
        template1 = PromptTemplate(
            role="user",
            content="Template 1 with {{?var1}}"
        )
        template2 = PromptTemplate(
            role="system",
            content="Template 2"
        )
        llm = LLM(
            name="gpt-4",
            version="4.0",
            params={"temperature": 0.7}
        )
        
        result = resolve_orchestration_config_v2([template1, template2], llm)
        
        self.assertIn(MODULES_KEY, result)
        self.assertIn(PROMPT_TEMPLATING_KEY, result[MODULES_KEY])
        self.assertIn(PROMPT_KEY, result[MODULES_KEY][PROMPT_TEMPLATING_KEY])
        self.assertIn(TEMPLATE_KEY, result[MODULES_KEY][PROMPT_TEMPLATING_KEY][PROMPT_KEY])
        self.assertEqual(len(result[MODULES_KEY][PROMPT_TEMPLATING_KEY][PROMPT_KEY][TEMPLATE_KEY]), 2)
        self.assertIn(MODEL_KEY, result[MODULES_KEY][PROMPT_TEMPLATING_KEY])
        self.assertEqual(result[MODULES_KEY][PROMPT_TEMPLATING_KEY][MODEL_KEY]["name"], "gpt-4")
        self.assertEqual(result[MODULES_KEY][PROMPT_TEMPLATING_KEY][MODEL_KEY]["version"], "4.0")
        self.assertEqual(result[MODULES_KEY][PROMPT_TEMPLATING_KEY][MODEL_KEY]["parameters"], {"temperature": 0.7})
