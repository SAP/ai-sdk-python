"""Orchestration flow for uploading datasets, registering AI Core configurations, and launching optimization jobs."""
import json
import os
import uuid
from pathlib import Path

from ai_api_client_sdk.models.artifact import Artifact
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

from gen_ai_hub.evaluations._internal._models import _AWSObjectStoreData
from gen_ai_hub.evaluations.constants import (
    AI_PROTOCOL_PREFIX,
    AWS_OSS_PATH_PREFIX_URL_KEY,
    DATASET_FOLDER_KEY,
    DEFAULT_KEY,
)
from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.helpers.logging import get_logger
from gen_ai_hub.evaluations.utils.aicore_utils import (
    generate_random_id,
    register_aicore_execution,
    upload_file_to_aws_s3,
)
from gen_ai_hub.evaluations.utils.oss_secret_utils import fetch_object_store_secret_by_name
from gen_ai_hub.optimizations.constants import OPTIMIZATIONS_ARTIFACT_KEY, OPTIMIZATIONS_SCENARIO_ID
from gen_ai_hub.optimizations.models.optimization_config import PromptOptimizationConfig
from gen_ai_hub.optimizations.models.optimization_run import OptimizationRun
from gen_ai_hub.optimizations.utils import register_optimization_aicore_configuration

logger = get_logger()


def _upload_optimization_dataset(
    dataset_data,
    dataset_type: str,
    object_store_credentials: _AWSObjectStoreData,
    ai_core_client: AICoreV2Client,
    resource_group: str,
    error_collector: ValidationCollector,
):
    """Upload dataset to S3 and register an optimization artifact. Returns (artifact_id, dataset_file_key)."""
    object_store_secret = fetch_object_store_secret_by_name(
        ai_core_client, DEFAULT_KEY, resource_group, error_collector
    )
    error_collector.raise_if_errors()

    bare_folder_id = generate_random_id()
    path_prefix = object_store_secret.metadata.get(AWS_OSS_PATH_PREFIX_URL_KEY)
    s3_root = os.path.join(path_prefix, bare_folder_id) if path_prefix else bare_folder_id

    dataset_file_name = f"{generate_random_id()[:7]}.{dataset_type}"
    dataset_file_key = os.path.join(DATASET_FOLDER_KEY, dataset_file_name)
    s3_file_key = os.path.join(s3_root, dataset_file_key)

    uploaded = upload_file_to_aws_s3(
        object_store_credentials,
        object_store_secret.metadata,
        dataset_data,
        s3_file_key,
        dataset_type,
        error_collector,
    )
    if not uploaded:
        error_collector.add_error(
            ErrorCode.FILE_UPLOAD_ERROR,
            f"Error uploading optimization dataset to object store at {s3_file_key}",
        )
        error_collector.raise_if_errors()

    artifact_url = os.path.join(AI_PROTOCOL_PREFIX, DEFAULT_KEY, bare_folder_id)
    try:
        response = ai_core_client.artifact.create(
            name=OPTIMIZATIONS_ARTIFACT_KEY + "-" + generate_random_id()[:7],
            kind=Artifact.Kind.OTHER,
            url=artifact_url,
            scenario_id=OPTIMIZATIONS_SCENARIO_ID,
            resource_group=resource_group,
        )
        logger.info("Optimization artifact created: %s", response.id)
        return response.id, dataset_file_key
    except Exception as err:
        error_collector.add_error(
            ErrorCode.ARTIFACT_CREATION_FAILURE,
            f"Error creating optimization artifact: {err}",
        )
        error_collector.raise_if_errors()
        return None, None


def optimization_job_flow(
    optimization_config: PromptOptimizationConfig,
    object_store_credentials: _AWSObjectStoreData,
    ai_core_client: AICoreV2Client,
    resource_group: str,
    error_collector: ValidationCollector,
    proxy_client=None,
) -> OptimizationRun:
    """Upload the dataset, register AI Core configuration and execution, and return an OptimizationRun."""
    if optimization_config.artifact_id:
        aicore_artifact_id = optimization_config.artifact_id
        dataset_file_key = optimization_config.dataset
        logger.info("Reusing existing artifact %s for optimization", aicore_artifact_id)
    else:
        dataset_path = optimization_config.dataset_path
        dataset_type = Path(dataset_path).suffix.lstrip(".")
        with open(dataset_path, "r", encoding="utf-8") as file:
            dataset_data = json.load(file)

        aicore_artifact_id, dataset_file_key = _upload_optimization_dataset(
            dataset_data,
            dataset_type,
            object_store_credentials,
            ai_core_client,
            resource_group,
            error_collector,
        )
        logger.info("Uploaded dataset and registered artifact %s", aicore_artifact_id)

    aicore_configuration_id = register_optimization_aicore_configuration(
        aicore_artifact_id,
        ai_core_client,
        resource_group,
        optimization_config,
        dataset_file_key,
        error_collector,
    )
    logger.info("AI Core configuration ID: %s", aicore_configuration_id)

    if not aicore_configuration_id:
        error_collector.add_error(
            ErrorCode.CONFIGURATION_CREATION_FAILURE,
            "Error while creating the optimization aicore configuration, so terminating the optimize function. "
            "Please look into the error and try again",
        )
    error_collector.raise_if_errors()

    aicore_execution_id = register_aicore_execution(
        ai_core_client,
        aicore_configuration_id,
        resource_group,
        error_collector,
    )
    logger.info("AI Core execution ID: %s", aicore_execution_id)
    logger.info("Dataset file key: %s", dataset_file_key)

    if not aicore_execution_id:
        error_collector.add_error(
            ErrorCode.EXECUTION_CREATION_FAILURE,
            "Error while creating the optimization aicore execution, so terminating the optimize function. "
            "Please look into the error and try again",
        )
    error_collector.raise_if_errors()

    return OptimizationRun(
        run_id=uuid.uuid4().hex,
        execution_id=aicore_execution_id,
        configuration_id=aicore_configuration_id,
        artifact_id=aicore_artifact_id,
        ai_core_client=ai_core_client,
        resource_group=resource_group,
        proxy_client=proxy_client,
        target_prompt_mapping=optimization_config.target_prompt_mapping,
    )
