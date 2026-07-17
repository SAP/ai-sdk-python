def test_flat_and_not_flat_import_evaluation():
    from gen_ai_hub.evaluations import EvaluationClient as evaluation_client_flat
    from gen_ai_hub.evaluations.client import EvaluationClient as evaluation_client
    assert evaluation_client_flat == evaluation_client

    from gen_ai_hub.evaluations import Dataset as dataset_flat
    from gen_ai_hub.evaluations.models.dataset_config import Dataset as dataset
    assert dataset_flat == dataset

    from gen_ai_hub.evaluations import MetricConfig as metric_config_flat
    from gen_ai_hub.evaluations.models.metric_config import MetricConfig as metric_config
    assert metric_config_flat == metric_config

    from gen_ai_hub.evaluations import MetricRef as metric_ref_flat
    from gen_ai_hub.evaluations.models.metric_config import MetricRef as metric_ref
    assert metric_ref_flat == metric_ref

    from gen_ai_hub.evaluations import EvaluationConfig as evaluation_config_flat
    from gen_ai_hub.evaluations.models.evaluation_config import EvaluationConfig as evaluation_config
    assert evaluation_config_flat == evaluation_config

    from gen_ai_hub.evaluations import ArtifactSource as artifact_source_flat
    from gen_ai_hub.evaluations.models.artifact_source import ArtifactSource as artifact_source
    assert artifact_source_flat == artifact_source

    from gen_ai_hub.evaluations import EvaluationRun as evaluation_run_flat
    from gen_ai_hub.evaluations.models.evaluation_run import EvaluationRun as evaluation_run
    assert evaluation_run_flat == evaluation_run
