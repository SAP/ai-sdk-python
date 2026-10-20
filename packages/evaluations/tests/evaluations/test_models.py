import unittest
from pathlib import Path

from ai_api_client_sdk.models.artifact import Artifact
from gen_ai_hub.evaluations.models.artifact_source import ArtifactSource
from gen_ai_hub.evaluations.models.dataset_config import Dataset
from gen_ai_hub.evaluations.models.evaluation_config import EvaluationConfig
from gen_ai_hub.evaluations.models.metric_config import MetricConfig, MetricRef
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails as LLM
from gen_ai_hub.orchestration_v2.models.template_ref import TemplateRef, TemplateRefByID
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplateSpec


class TestArtifactSource(unittest.TestCase):
    """Unit tests for ArtifactSource model"""

    def test_artifact_source_with_artifact_object(self):
        artifact_obj = Artifact(
            id="abc123",
            name="test-artifact",
            url="ai://default/path",
            kind="dataset",
            scenario_id="scenario-123",
            created_at="2025-11-12T08:40:13Z",
            modified_at="2025-11-12T08:40:13Z",
        )

        src = ArtifactSource(
            file_type="csv",
            artifact=artifact_obj,
            path="folder/data.csv",
        )

        self.assertIs(src.artifact, artifact_obj)
        self.assertEqual(src.path, "folder/data.csv")
        self.assertEqual(src.file_type, "csv")

    def test_artifact_source_with_artifact_id_as_string(self):
        artifact_id = "xyz789"

        src = ArtifactSource(
            file_type="json",
            artifact=artifact_id,
            path="data/sample.json",
        )

        self.assertEqual(src.artifact, artifact_id)
        self.assertEqual(src.path, "data/sample.json")
        self.assertEqual(src.file_type, "json")

    def test_artifact_source_without_path(self):
        artifact_id = "id-no-path"

        src = ArtifactSource(
            file_type="jsonl",
            artifact=artifact_id,
            path=None,
        )

        self.assertEqual(src.artifact, artifact_id)
        self.assertIsNone(src.path)
        self.assertEqual(src.file_type, "jsonl")

    def test_artifact_source_invalid_file_type_is_accepted(self):
        src = ArtifactSource(
            file_type="txt",
            artifact="abc",
            path="data/file.txt",
        )

        self.assertEqual(src.file_type, "txt")


class TestDataset(unittest.TestCase):

    def test_dataset_with_path_string_json(self):
        ds = Dataset("data/sample.json")
        self.assertEqual(ds.file_type, "json")

    def test_dataset_with_path_string_csv(self):
        ds = Dataset("folder/file.csv")
        self.assertEqual(ds.file_type, "csv")

    def test_dataset_with_pathlib_path(self):
        ds = Dataset(Path("root/data.jsonl"))
        self.assertEqual(ds.file_type, "jsonl")

    def test_dataset_with_unsupported_extension(self):
        ds = Dataset("data/sample.unknown")
        self.assertIsNone(ds.file_type)

    def test_dataset_with_artifact_source_uses_file_type(self):
        artifact_src = ArtifactSource(
            file_type="csv",
            artifact="abc-123",
            path="dataset/data.csv",
        )

        ds = Dataset(artifact_src)

        self.assertEqual(ds.file_type, "csv")
        self.assertIs(ds.source, artifact_src)


class TestEvaluationConfig(unittest.TestCase):

    def setUp(self):
        self.dataset = Dataset("data/sample.json")
        self.metrics = [MetricConfig(reference=MetricRef(name="bert-score"))]

    def test_initialization_with_llm_and_template_string(self):
        llm = LLM(name="gpt-test", version="latest", params={"temperature": 0.7})

        cfg = EvaluationConfig(
            dataset_config=self.dataset,
            metrics=self.metrics,
            llm=llm,
            template="Write a caption about {{?topic}}"
        )

        self.assertIs(cfg.llm, llm)
        self.assertEqual(cfg.template, "Write a caption about {{?topic}}")
        self.assertIsNone(cfg.orchestration_registry_reference)

    def test_initialization_with_llm_and_template_ref(self):
        llm = LLM(name="gpt-test", version="latest", params={"temperature": 0.7})
        t_ref = TemplateRef(template_ref=TemplateRefByID(id="abc123"))

        cfg = EvaluationConfig(
            dataset_config=self.dataset,
            metrics=self.metrics,
            llm=llm,
            template=t_ref
        )

        self.assertIs(cfg.llm, llm)
        self.assertIs(cfg.template, t_ref)
        self.assertIsNone(cfg.orchestration_registry_reference)

    def test_initialization_with_llm_and_template_spec(self):
        template_spec = PromptTemplateSpec(
            template=[{"role": "user", "content": "Explain {{?concept}}"}],
            defaults={}
        )

        cfg = EvaluationConfig(
            dataset_config=self.dataset,
            metrics=self.metrics,
            llm=LLM(name="gpt-test"),
            template=template_spec,
            template_variable_mapping={"concept": "topic"}
        )

        self.assertIs(cfg.template, template_spec)
        self.assertEqual(cfg.template_variable_mapping, {"concept": "topic"})

    def test_initialization_with_orchestration_registry_reference(self):
        cfg = EvaluationConfig(
            dataset_config=self.dataset,
            metrics=self.metrics,
            orchestration_registry_reference="a1b2c3d4-1234-5678-9999-abcdefabcdef"
        )

        self.assertEqual(
            cfg.orchestration_registry_reference,
            "a1b2c3d4-1234-5678-9999-abcdefabcdef"
        )
        self.assertIsNone(cfg.llm)
        self.assertIsNone(cfg.template)

    def test_initialization_with_optional_parameters(self):
        cfg = EvaluationConfig(
            dataset_config=self.dataset,
            metrics=self.metrics,
            llm=LLM(name="gpt-test"),
            test_row_count=50,
            repetitions=3,
            tags={"team": "ai-core"},
            debug_mode=True
        )

        self.assertEqual(cfg.test_row_count, 50)
        self.assertEqual(cfg.repetitions, 3)
        self.assertEqual(cfg.tags, {"team": "ai-core"})
        self.assertTrue(cfg.debug_mode)
