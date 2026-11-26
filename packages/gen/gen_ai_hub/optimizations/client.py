"""Client for submitting and managing prompt optimization jobs on generative AI Hub."""
from gen_ai_hub.evaluations._internal._models import _AWSObjectStoreData
from gen_ai_hub.evaluations.client import EvaluationClient
from gen_ai_hub.evaluations.constants import DEFAULT_KEY
from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.utils.oss_secret_utils import fetch_object_store_secret_by_name
from gen_ai_hub.optimizations.models.optimization_config import PromptOptimizationConfig
from gen_ai_hub.optimizations.models.optimization_run import OptimizationRun
from gen_ai_hub.optimizations.optimization_flow import optimization_job_flow
from gen_ai_hub.optimizations.utils import validate_optimization_config


class OptimizationClient(EvaluationClient):
    """Client for running prompt optimization jobs against a target metric on generative AI Hub."""

    def optimize(self, optimization_config: PromptOptimizationConfig) -> OptimizationRun:
        """Submit a prompt optimization job and return an OptimizationRun to track its progress."""
        error_collector = ValidationCollector()
        try:
            if self.default_object_store_secret_name is None:
                response = fetch_object_store_secret_by_name(
                    self.ai_core_client,
                    DEFAULT_KEY,
                    self.resource_group,
                    error_collector,
                )
                if response is None:
                    error_collector.add_error(
                        ErrorCode.MISSING_DEFAULT_OBJECT_STORE_SECRET_ERROR.value,
                        "Default Object Store secret is required to run optimize function. "
                        "Please use setup() function to create one!",
                    )

            error_collector.raise_if_errors()

            validate_optimization_config(
                optimization_config,
                self.ai_core_client,
                self.resource_group,
                error_collector,
            )
            error_collector.raise_if_errors()

            object_store_credentials = _AWSObjectStoreData(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            return optimization_job_flow(
                optimization_config,
                object_store_credentials,
                self.ai_core_client,
                self.resource_group,
                error_collector,
                proxy_client=self._gen_ai_hub_proxy_client,
            )
        except Exception as exc:
            error_collector.raise_if_errors()
            raise RuntimeError("Optimize function failed!") from exc
