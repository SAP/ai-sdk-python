"""OptimizationRun: tracks the lifecycle and results of a prompt optimization job."""
import logging

from ai_api_client_sdk.models.metric_resource import MetricResource
from ai_api_client_sdk.models.status import Status
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.tracking import Tracking

from gen_ai_hub.evaluations.constants import ADDITIONAL_INFO_KEY
from gen_ai_hub.evaluations.models.evaluation_run import EvaluationRun
from gen_ai_hub.optimizations.models.optimization_results import OptimizationResults
from gen_ai_hub.prompt_registry.client import PromptTemplateClient

logger = logging.getLogger(__name__)


class _OptimizationRunContext:
    def __init__(self, execution_id, configuration_id, artifact_id,
                 ai_core_client, resource_group, proxy_client, target_prompt_mapping):
        self.execution_id = execution_id
        self.configuration_id = configuration_id
        self.artifact_id = artifact_id
        self.ai_core_client = ai_core_client
        self.resource_group = resource_group
        self.proxy_client = proxy_client
        self.target_prompt_mapping = target_prompt_mapping


class OptimizationRun(EvaluationRun):
    """Tracks execution state and exposes results for a submitted prompt optimization job."""

    _STEP_ERROR_MESSAGES = {
        "optimize": "Optimization job failed in the optimization step.",
        "config": "Optimization job failed in Config Validation step.",
    }

    def __init__(
        self,
        run_id: str,
        execution_id: str,
        ai_core_client: AICoreV2Client,
        configuration_id: str = None,
        artifact_id: str = None,
        resource_group: str = None,
        proxy_client=None,
        target_prompt_mapping: dict = None,
    ):
        self.id = run_id
        self.status = Status.UNKNOWN
        self._run_context = _OptimizationRunContext(
            execution_id=execution_id,
            configuration_id=configuration_id,
            artifact_id=artifact_id,
            ai_core_client=ai_core_client,
            resource_group=resource_group,
            proxy_client=proxy_client,
            target_prompt_mapping=target_prompt_mapping or {},
        )

    def _enrich_failed_pods(self, failed_pods: list, workflow_lookup: dict) -> None:
        for pod in failed_pods:
            pod_name = pod.get("name", "")
            if not self._apply_step_level_message(pod, pod_name):
                self._apply_fallback_message(pod, pod_name, workflow_lookup)

    def _apply_fallback_message(self, pod: dict, pod_name: str, workflow_lookup: dict) -> None:
        suffix = pod_name.split("-")[-1]
        workflow = workflow_lookup.get(suffix)
        if not workflow:
            return
        message = workflow.get("message", "Unknown error")
        pod[ADDITIONAL_INFO_KEY] = f"Optimization job failed with error: {message}"

    def get_debug_info(self):
        """Return structured debug information about the execution status."""
        execution_status_response = self._execution_status_fetcher()
        current_status = execution_status_response.status
        status_details = getattr(execution_status_response, "status_details", None)

        if not status_details:
            return {
                "status": current_status,
                "details": (
                    "No specific details found. Please use get_debug_logs() "
                    "to get more information."
                ),
            }

        failed_pod_details = self._extract_failed_pods(status_details)
        workflow_lookup = self._build_workflow_lookup(status_details)
        self._enrich_failed_pods(failed_pod_details, workflow_lookup)

        return {"status": current_status, "details": failed_pod_details}

    def aggregations(self):
        """Fetch and return metric aggregations for the optimization run from the tracking service."""
        try:
            tracking_client = Tracking(
                base_url=self._run_context.ai_core_client.base_url,
                token_creator=self._run_context.ai_core_client.rest_client.get_token,
                resource_group=self._run_context.resource_group,
            )
            result = tracking_client.query(
                execution_ids=[self._run_context.execution_id],
                resource_group=self._run_context.resource_group,
            )
            path = f"/lm/metrics?tagFilters=evaluation.ai.sap.com/child-of={self._run_context.execution_id}"
            child_response = self._run_context.ai_core_client.rest_client.get(
                path=path,
                resource_group=self._run_context.resource_group,
            )
            child_resources = [
                MetricResource.from_dict(r)
                for r in child_response.get("resources", [])
            ]
            result.resources = (result.resources or []) + child_resources
            return result
        except Exception as err:
            logger.warning("Could not fetch aggregations for run %s: %s", self.id, err)
            return None

    def results(self) -> OptimizationResults:
        """Fetch and return the optimization results including metrics and optimized prompts."""
        execution_status = self._execution_status_fetcher().status
        if execution_status != Status.COMPLETED:
            if execution_status == Status.RUNNING:
                raise ValueError(
                    "Status of the run is Running. Use wait_for_completion() first."
                )
            raise ValueError(
                f"Cannot fetch results — run is not completed. Current status: {execution_status}"
            )

        metrics = self.aggregations()

        prompt_client = PromptTemplateClient(proxy_client=self._run_context.proxy_client)
        prompts = {}
        for resource in (metrics.resources if metrics is not None else []):
            tags = {t.name: t.value for t in (resource.tags or [])}
            if tags.get("evaluation.ai.sap.com/purpose") != "target":
                continue
            model = tags.get("evaluation.ai.sap.com/model")
            prompt_id = tags.get("evaluation.ai.sap.com/promptTemplateId")
            if not model or not prompt_id:
                continue
            try:
                prompts[model] = prompt_client.get_prompt_template_by_id(prompt_id)
            except Exception as err:
                logger.warning("Could not fetch prompt for model %s (id=%s): %s", model, prompt_id, err)

        if not prompts:
            for model, prompt_ref in self._run_context.target_prompt_mapping.items():
                try:
                    name, version = prompt_ref.rsplit(":", 1)
                    response = prompt_client.get_prompt_templates(
                        scenario="genai-optimizations", name=name, version=version
                    )
                    if response.resources:
                        prompts[model] = response.resources[0]
                except Exception as err:
                    logger.warning("Could not fetch prompt for model %s (ref=%s): %s", model, prompt_ref, err)

        return OptimizationResults(metrics=metrics, prompts=prompts)
