import unittest
from unittest.mock import MagicMock, patch

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.models.evaluation_config import EvaluationConfig
from gen_ai_hub.evaluations.models.dataset_config import Dataset
from gen_ai_hub.evaluations.models.artifact_source import ArtifactSource
from gen_ai_hub.orchestration_v2.models.template_ref import TemplateRef, TemplateRefByID, TemplateRefByScenarioNameVersion
from gen_ai_hub.prompt_registry.models.prompt_template import (
    PromptTemplateSpec,
    PromptTemplate,
)

from gen_ai_hub.evaluations.utils.config_data_utils import (
    _fetch_template_by_guid,
    _register_prompt_template,
    _get_prompt_template_uuid_by_metadata,
    get_orch_config_data,
    get_dataset_data,
)

from gen_ai_hub.evaluations.exceptions.error_codes import ErrorCode


class TestConfigDataUtils(unittest.TestCase):

    def test_fetch_template_by_guid_success(self):
        collector = ValidationCollector()
        client = MagicMock()
        client.get_prompt_template_by_id.return_value.spec.template = ["template"]

        result = _fetch_template_by_guid(client, "uuid", collector)

        self.assertEqual(result, ["template"])

    def test_fetch_template_by_guid_exception(self):
        collector = ValidationCollector()
        client = MagicMock()
        client.get_prompt_template_by_id.side_effect = RuntimeError("boom")

        result = _fetch_template_by_guid(client, "uuid", collector)

        self.assertIsNone(result)
        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.generate_random_id",
        return_value="abcdef123"
    )
    def test_register_prompt_template_with_string(self, _):
        collector = ValidationCollector()
        client = MagicMock()
        client.create_prompt_template.return_value.id = "pt-123"

        template = [PromptTemplate(role="user", content="hello")]

        result = _register_prompt_template(template, client, collector)

        self.assertEqual(result, "pt-123")

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.generate_random_id",
        return_value="abcdef123"
    )
    def test_register_prompt_template_with_spec(self, _):
        collector = ValidationCollector()
        client = MagicMock()
        client.create_prompt_template.return_value.id = "pt-456"

        spec = PromptTemplateSpec(
            template=[PromptTemplate(role="user", content="hi")]
        )

        result = _register_prompt_template(spec, client, collector)

        self.assertEqual(result, "pt-456")

    def test_register_prompt_template_exception(self):
        collector = ValidationCollector()
        client = MagicMock()
        client.create_prompt_template.side_effect = RuntimeError("fail")

        result = _register_prompt_template("hello", client, collector)

        self.assertIsNone(result)
        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    def test_get_prompt_template_uuid_by_metadata_success(self):
        collector = ValidationCollector()
        client = MagicMock()

        response = MagicMock()
        response.resources = [MagicMock(id="uuid-123")]
        client.get_prompt_templates.return_value = response

        template_ref = TemplateRef(
            template_ref=TemplateRefByScenarioNameVersion(
                scenario="s",
                name="n",
                version="v",
            )
        )

        result = _get_prompt_template_uuid_by_metadata(
            client,
            template_ref,
            collector,
        )

        self.assertEqual(result, "uuid-123")

    def test_get_prompt_template_uuid_by_metadata_exception(self):
        collector = ValidationCollector()
        client = MagicMock()
        client.get_prompt_templates.side_effect = RuntimeError("fail")

        template_ref = TemplateRef(
            template_ref=TemplateRefByScenarioNameVersion(
                scenario="s",
                name="n",
                version="v",
            )
        )

        _get_prompt_template_uuid_by_metadata(client, template_ref, collector)

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.resolve_orchestration_config_v2",
        return_value=["orch"]
    )
    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.PromptTemplateClient"
    )
    def test_get_orch_config_data_template_string(self, mock_pt_client, _):
        collector = ValidationCollector()
        ai_client = MagicMock(spec=AICoreV2Client)
        proxy_client = MagicMock()

        mock_pt_client.return_value.create_prompt_template.return_value.id = "pt-123"

        evaluation_config = EvaluationConfig(
            llm="gpt-4",
            template="hello",
            dataset_config=Dataset(source="file.json"),
            metrics=[],
        )

        result = get_orch_config_data(
            evaluation_config,
            ai_client,
            proxy_client,
            collector,
        )

        self.assertEqual(result, ["orch"])

    def test_get_orch_config_data_invalid_llm_template_combo(self):
        collector = ValidationCollector()

        evaluation_config = EvaluationConfig(
            llm="gpt-4",
            template=None,
            dataset_config=Dataset(source="file.json"),
            metrics=[],
        )

        get_orch_config_data(
            evaluation_config,
            MagicMock(),
            MagicMock(),
            collector,
        )

        with self.assertRaises(RuntimeError):
            collector.raise_if_errors()

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.fetch_orchestration_config_from_registry",
        return_value=["registry"]
    )
    def test_get_orch_config_data_registry_reference(self, _):
        collector = ValidationCollector()

        evaluation_config = EvaluationConfig(
            orchestration_registry_reference="ref",
            dataset_config=Dataset(source="file.json"),
            metrics=[],
        )

        result = get_orch_config_data(
            evaluation_config,
            MagicMock(),
            MagicMock(),
            collector,
        )

        self.assertEqual(result, ["registry"])

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.resolve_artifact_path",
        return_value=["artifact"]
    )
    def test_get_dataset_data_artifact_source(self, _):
        collector = ValidationCollector()

        artifact_source = MagicMock(spec=ArtifactSource)
        dataset = Dataset(source=artifact_source)

        result = get_dataset_data(
            dataset,
            MagicMock(),
            {},
            "rg",
            collector,
        )

        self.assertEqual(result, ["artifact"])

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.load_config_file",
        return_value=[{"row": 1}]
    )
    def test_get_dataset_data_file_source(self, _):
        collector = ValidationCollector()

        dataset = Dataset(source="file.json")

        result = get_dataset_data(
            dataset,
            MagicMock(),
            {},
            "rg",
            collector,
        )

        self.assertEqual(result, [{"row": 1}])

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.resolve_orchestration_config_v2",
        return_value=["orch-config"]
    )
    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils._register_prompt_template",
        return_value="pt-123"
    )
    def test_get_orch_config_data_prompt_template_spec(
        self, mock_register, mock_resolve
    ):
        collector = ValidationCollector()

        template_spec = PromptTemplateSpec(
            template=[PromptTemplate(role="user", content="hello")]
        )

        evaluation_config = EvaluationConfig(
            llm="gpt-4",
            template=template_spec,
            dataset_config=Dataset(source="file.json"),
            metrics=[],
        )

        result = get_orch_config_data(
            evaluation_config,
            MagicMock(),
            MagicMock(),
            collector,
        )

        self.assertEqual(result, ["orch-config"])
        mock_register.assert_called_once()
        mock_resolve.assert_called_once()

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.resolve_orchestration_config_v2",
        return_value=["orch-config"]
    )
    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils._fetch_template_by_guid",
        return_value=[{"role": "user", "content": "hello"}]
    )
    def test_get_orch_config_data_template_ref_with_id(
        self, mock_fetch, mock_resolve
    ):
        collector = ValidationCollector()

        template_ref = TemplateRef(template_ref=TemplateRefByID(id="template-uuid"))

        evaluation_config = EvaluationConfig(
            llm="gpt-4",
            template=template_ref,
            dataset_config=Dataset(source="file.json"),
            metrics=[],
        )

        result = get_orch_config_data(
            evaluation_config,
            MagicMock(),
            MagicMock(),
            collector,
        )

        self.assertEqual(result, ["orch-config"])
        mock_fetch.assert_called_once()
        mock_resolve.assert_called_once()

    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.PROMPT_TEMPLATE_METADATA_FIELDS",
        ["non_existent_attr"]
    )
    @patch(
        "gen_ai_hub.evaluations.utils.config_data_utils.resolve_orchestration_config_v2",
        return_value=[]
    )
    def test_get_orch_config_data_invalid_template_ref(self, _):
        collector = ValidationCollector()

        llm = MagicMock()
        llm.name = "gpt-4"

        # Create a TemplateRef with an inner object that doesn't have the expected attributes
        # Using model_construct to bypass Pydantic validation
        mock_inner = MagicMock()
        del mock_inner.id  # Remove the id attribute
        del mock_inner.non_existent_attr  # Remove the patched metadata field
        template_ref = TemplateRef.model_construct(template_ref=mock_inner)

        evaluation_config = EvaluationConfig(
            llm=llm,
            template=template_ref,
            dataset_config=Dataset(source="file.json"),
            metrics=[],
        )

        result = get_orch_config_data(
            evaluation_config,
            MagicMock(),
            MagicMock(),
            collector,
        )

        self.assertEqual(result, [])

        with self.assertRaises(RuntimeError) as exc:
            collector.raise_if_errors()

        self.assertIn(
            ErrorCode.INVALID_TEMPLATE_REFERENCE_KEY.name,
            str(exc.exception)
        )
