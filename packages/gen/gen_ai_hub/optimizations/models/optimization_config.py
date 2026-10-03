"""PromptOptimizationConfig: configuration model for prompt optimization jobs."""
from typing import Dict, List, Optional


class PromptOptimizationConfig:
    """Configuration for a prompt optimization job.

    :param target_prompt_mapping: Maps each target model (``name:version``) to the output
        prompt name in the Prompt Registry.
    :param target_models: List of models to optimize for, e.g. ``["gpt-4o:2024-11-20"]``.
    :param base_prompt: Starting prompt template referenced as ``<scenario>/<name>:<version>``.
    :param optimization_metric: System-defined metric to optimize for (e.g. ``"JSON_Match"``).
        Mutually exclusive with ``custom_metric_id``.
    :param artifact_id: AI Core artifact ID of a pre-uploaded dataset. Mutually exclusive with ``dataset_path``.
    :param dataset: Relative file key within the artifact (required when using ``artifact_id``).
    :param dataset_path: Local path to a labelled JSON dataset. The SDK uploads it automatically.
        Mutually exclusive with ``artifact_id``.
    :param base_model: Reference model used internally during optimization.
    :param include_few_shot_examples: Whether to include few-shot examples in the optimized prompt
        (default: ``False``).
    :param custom_metric_id: ID of a custom metric to optimize for. Mutually exclusive with
        ``optimization_metric``.
    :param maximize: Whether higher metric scores are better (default: ``True``).
    :param correctness_cutoff: Score threshold for correctness classification.
    :param prompt_template_scope: Scope for the output prompt template — ``"tenant"`` or
        ``"resourcegroup"`` (default: ``"tenant"``).
    :param prototype_mode: Use as few as 3 samples for quick prototyping (default: ``False``).
    :param train_dataset_config: Optional training dataset config. Requires ``test_dataset_config``.
    :param test_dataset_config: Optional test dataset config. Required when ``train_dataset_config`` is provided.
    :param model_params: JSON string mapping model IDs to parameter dicts (e.g. ``temperature``, ``max_tokens``).
    :param variable_mapping: JSON string mapping prompt template variable names to dataset field names.
    :param field_evaluation_metrics: JSON string mapping response format field names to their evaluation metrics
        (e.g. ``'{"urgency": "ExactMatch", "sentiment": "LLMaaJ:Sem_Sim_1"}'``). Requires a ``response_format``
        to be defined in the base prompt template. Mutually exclusive with ``optimization_metric`` and ``custom_metric_id``.
    """

    def __init__(
        self,
        target_prompt_mapping: Dict[str, str],
        target_models: List[str],
        base_prompt: str,
        optimization_metric: Optional[str] = None,
        artifact_id: Optional[str] = None,
        dataset: Optional[str] = None,
        dataset_path: Optional[str] = None,
        base_model: Optional[str] = "none",
        include_few_shot_examples: Optional[bool] = False,
        custom_metric_id: Optional[str] = None,
        maximize: Optional[bool] = True,
        correctness_cutoff: Optional[float] = None,
        prompt_template_scope: Optional[str] = "tenant",
        prototype_mode: Optional[bool] = False,
        train_dataset_config=None,
        test_dataset_config=None,
        model_params: Optional[str] = None,
        variable_mapping: Optional[str] = None,
        field_evaluation_metrics: Optional[str] = None,
    ):
        self.artifact_id = artifact_id
        self.dataset = dataset
        self.dataset_path = dataset_path
        self.target_prompt_mapping = target_prompt_mapping
        self.target_models = target_models
        self.base_prompt = base_prompt
        self.optimization_metric = optimization_metric
        self.base_model = base_model
        self.include_few_shot_examples = include_few_shot_examples
        self.custom_metric_id = custom_metric_id
        self.maximize = maximize
        self.correctness_cutoff = correctness_cutoff
        self.prompt_template_scope = prompt_template_scope
        self.prototype_mode = prototype_mode
        self.train_dataset_config = train_dataset_config
        self.test_dataset_config = test_dataset_config
        self.model_params = model_params
        self.variable_mapping = variable_mapping
        self.field_evaluation_metrics = field_evaluation_metrics
        self._validate(
            artifact_id, dataset, dataset_path,
            optimization_metric, custom_metric_id,
            train_dataset_config, test_dataset_config,
            field_evaluation_metrics,
        )

    def _validate(self, artifact_id, dataset, dataset_path,
                  optimization_metric, custom_metric_id,
                  train_dataset_config, test_dataset_config,
                  field_evaluation_metrics=None):
        if artifact_id is None and dataset_path is None:
            raise ValueError("Either artifact_id or dataset_path must be provided.")
        if artifact_id is not None and dataset_path is not None:
            raise ValueError("Only one of artifact_id or dataset_path must be provided, not both.")
        if artifact_id is not None and dataset is None:
            raise ValueError("dataset (filename) must be provided when using artifact_id.")
        if train_dataset_config is not None and test_dataset_config is None:
            raise ValueError("test_dataset_config must be provided when train_dataset_config is provided.")
        if optimization_metric is None and custom_metric_id is None and field_evaluation_metrics is None:
            raise ValueError(
                "At least one of optimization_metric, custom_metric_id, or field_evaluation_metrics must be provided."
            )
        if optimization_metric is not None and custom_metric_id is not None:
            raise ValueError("Only one of optimization_metric or custom_metric_id must be provided, not both.")
