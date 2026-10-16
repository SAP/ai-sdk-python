def test_flat_and_not_flat_import_evaluation():
    from sap_ai_sdk_evaluations import EvaluationClient as evaluation_client_flat
    from sap_ai_sdk_evaluations.client import EvaluationClient as evaluation_client
    assert evaluation_client_flat == evaluation_client

    from sap_ai_sdk_evaluations import Dataset as dataset_flat
    from sap_ai_sdk_evaluations.models.dataset_config import Dataset as dataset
    assert dataset_flat == dataset

    from sap_ai_sdk_evaluations import MetricConfig as metric_config_flat
    from sap_ai_sdk_evaluations.models.metric_config import MetricConfig as metric_config
    assert metric_config_flat == metric_config

    from sap_ai_sdk_evaluations import MetricRef as metric_ref_flat
    from sap_ai_sdk_evaluations.models.metric_config import MetricRef as metric_ref
    assert metric_ref_flat == metric_ref

    from sap_ai_sdk_evaluations import EvaluationConfig as evaluation_config_flat
    from sap_ai_sdk_evaluations.models.evaluation_config import EvaluationConfig as evaluation_config
    assert evaluation_config_flat == evaluation_config

    from sap_ai_sdk_evaluations import ArtifactSource as artifact_source_flat
    from sap_ai_sdk_evaluations.models.artifact_source import ArtifactSource as artifact_source
    assert artifact_source_flat == artifact_source

    from sap_ai_sdk_evaluations import EvaluationRun as evaluation_run_flat
    from sap_ai_sdk_evaluations.models.evaluation_run import EvaluationRun as evaluation_run
    assert evaluation_run_flat == evaluation_run
