"""Optimization-specific helpers: AI Core configuration registration and config validation."""
import json
import os

from ai_api_client_sdk.models.input_artifact_binding import InputArtifactBinding
from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.helpers.logging import get_logger
from gen_ai_hub.evaluations.utils.aicore_utils import generate_random_id
from gen_ai_hub.evaluations.utils.metric_client_utils import get_custom_metric_by_id
from gen_ai_hub.optimizations.constants import (
    OPTIMIZATIONS_CONFIG_PREFIX_KEY,
    OPTIMIZATIONS_SCENARIO_ID,
)

logger = get_logger()


def register_optimization_aicore_configuration(
    aicore_artifact_id: str,
    ai_core_client: AICoreV2Client,
    resource_group: str,
    optimization_config,
    dataset_file_key: str,
    error_collector: ValidationCollector,
):
    """Register an AI Core configuration for an optimization run and return the configuration ID."""
    try:
        target_models_str = ",".join(optimization_config.target_models)
        target_prompt_mapping_str = ",".join(
            f"{k}={v}" for k, v in optimization_config.target_prompt_mapping.items()
        )

        parameter_bindings_list = [
            ParameterBinding(key="basePrompt", value=optimization_config.base_prompt),
            ParameterBinding(key="baseModel", value=optimization_config.base_model or "none"),
            ParameterBinding(key="dataset", value=dataset_file_key),
            ParameterBinding(key="targetModels", value=target_models_str),
            ParameterBinding(key="targetPromptMapping", value=target_prompt_mapping_str),
            ParameterBinding(key="optimizationMetric", value=optimization_config.optimization_metric or "none"),
            ParameterBinding(key="customMetricId", value=optimization_config.custom_metric_id or "none"),
            ParameterBinding(key="includeFewShotExamples",
                             value=str(optimization_config.include_few_shot_examples).lower()),
            ParameterBinding(key="maximize", value=str(optimization_config.maximize).lower()),
            ParameterBinding(
                key="correctnessCutoff",
                value=str(optimization_config.correctness_cutoff) if optimization_config.correctness_cutoff else "none",
            ),
            ParameterBinding(key="promptTemplateScope", value=optimization_config.prompt_template_scope or "tenant"),
            ParameterBinding(key="prototypeMode", value=str(optimization_config.prototype_mode).lower()),
        ]
        train_cfg = optimization_config.train_dataset_config
        test_cfg = optimization_config.test_dataset_config
        train_path = (train_cfg.source.path if train_cfg and train_cfg.source else None) or "none"
        test_path = (test_cfg.source.path if test_cfg and test_cfg.source else None) or "none"
        parameter_bindings_list += [
            ParameterBinding(key="trainDataset", value=train_path),
            ParameterBinding(key="testDataset", value=test_path),
            ParameterBinding(key="fieldEvaluationMetrics", value=optimization_config.field_evaluation_metrics or "none"),
            ParameterBinding(key="modelParams", value=optimization_config.model_params or "none"),
            ParameterBinding(key="variableMapping", value=optimization_config.variable_mapping or "none"),
        ]

        configuration_name = OPTIMIZATIONS_CONFIG_PREFIX_KEY + generate_random_id()[:7]

        response = ai_core_client.configuration.create(
            name=configuration_name,
            scenario_id=OPTIMIZATIONS_SCENARIO_ID,
            executable_id="genai-optimizations",
            parameter_bindings=parameter_bindings_list,
            input_artifact_bindings=[
                InputArtifactBinding(key="prompt-data", artifact_id=aicore_artifact_id)
            ],
            resource_group=resource_group,
        )
        configuration_id = response.id
        logger.info("Optimization configuration id created is %s", configuration_id)
        return configuration_id
    except Exception as err:
        error_collector.add_error(
            ErrorCode.CONFIGURATION_CREATION_FAILURE,
            f"Error occurred while attempting to create optimization aicore configuration with error of {err}",
        )
        return None


def _validate_json_file(dataset_path: str, error_collector: ValidationCollector):
    try:
        with open(dataset_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not data:
            error_collector.add_error(
                ErrorCode.EMPTY_FILE_DATA_ERROR,
                f"Dataset file is empty: {dataset_path}",
            )
    except ValueError as err:
        error_collector.add_error(
            ErrorCode.INVALID_JSON_DECODING_ERROR,
            f"Dataset file is not valid JSON: {dataset_path} — {err}",
        )


def _validate_dataset_path(dataset_path: str, error_collector: ValidationCollector):
    if not os.path.exists(dataset_path):
        error_collector.add_error(
            ErrorCode.INVALID_FILE_PATH_ERROR,
            f"Dataset file not found: {dataset_path}",
        )
        return
    _, ext = os.path.splitext(dataset_path)
    if ext.lower() != ".json":
        error_collector.add_error(
            ErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
            f"Unsupported dataset file type '{ext}'. Only .json is supported for optimization.",
        )
    else:
        _validate_json_file(dataset_path, error_collector)


def _validate_target_prompt_mapping(optimization_config, error_collector: ValidationCollector):
    missing = set(optimization_config.target_models) - set(optimization_config.target_prompt_mapping.keys())
    if missing:
        error_collector.add_error(
            ErrorCode.INVALID_PARAMETER_VALUE_ERROR,
            f"target_prompt_mapping is missing entries for target_models: {sorted(missing)}",
        )


def _validate_custom_metric(optimization_config, ai_core_client, resource_group, error_collector):
    metric_info = get_custom_metric_by_id(
        optimization_config.custom_metric_id,
        ai_core_client,
        resource_group,
        error_collector,
    )
    if not metric_info:
        error_collector.add_error(
            ErrorCode.METRIC_SERVER_RESOLVE_ERROR,
            f"custom_metric_id '{optimization_config.custom_metric_id}' could not be resolved "
            "on the Metric Management Service.",
        )


def validate_optimization_config(
    optimization_config,
    ai_core_client: AICoreV2Client,
    resource_group: str,
    error_collector: ValidationCollector,
):
    """Validate the optimization configuration, including dataset path, target models, base prompt, and custom metric."""
    if optimization_config.dataset_path is not None:
        _validate_dataset_path(optimization_config.dataset_path, error_collector)

    if not optimization_config.target_models:
        error_collector.add_error(
            ErrorCode.INVALID_PARAMETER_VALUE_ERROR,
            "target_models must be a non-empty list.",
        )

    if not optimization_config.base_prompt or not optimization_config.base_prompt.strip():
        error_collector.add_error(
            ErrorCode.INVALID_PARAMETER_VALUE_ERROR,
            "base_prompt must be a non-empty string.",
        )

    if optimization_config.target_models and optimization_config.target_prompt_mapping:
        _validate_target_prompt_mapping(optimization_config, error_collector)

    if optimization_config.custom_metric_id:
        _validate_custom_metric(optimization_config, ai_core_client, resource_group, error_collector)
