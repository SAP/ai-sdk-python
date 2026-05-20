import unittest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

import gen_ai_hub.evaluations.client as module
from gen_ai_hub.evaluations.client import EvaluationClient, _has_mixed_config_types
from gen_ai_hub.evaluations.models.evaluation_config import EvaluationConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails as LLM
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplateSpec, PromptTemplate
from gen_ai_hub.evaluations.models.dataset_config import Dataset
from gen_ai_hub.evaluations.models.metric_config import MetricConfig, MetricRef
from gen_ai_hub.evaluations.constants import (
    DEFAULT_KEY,
    ORCHESTRATION_URL_SETUP_KEY,
    OBJECT_STORE_SECRET_EXISTS_MESSAGE,
    INPUT_SECRET_SETUP_KEY,
    DEFAULT_SECRET_SETUP_KEY,
)


class TestHasMixedConfigTypes(unittest.TestCase):
    """Tests for _has_mixed_config_types helper function."""

    def test_empty_list_returns_false(self):
        """Test that an empty list returns False."""
        self.assertFalse(_has_mixed_config_types([]))

    def test_single_config_returns_false(self):
        """Test that a single config returns False."""
        config = EvaluationConfig(
            llm=LLM(name="gpt-4", version="1.0"),
            template=PromptTemplateSpec(
                template=[PromptTemplate(role="user", content="test")]
            ),
            dataset_config=Dataset("test.csv"),
            metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
        )
        self.assertFalse(_has_mixed_config_types([config]))

    def test_all_llm_configs_returns_false(self):
        """Test that all llm configs return False."""
        configs = [
            EvaluationConfig(
                llm=LLM(name="gpt-4", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                llm=LLM(name="gpt-3.5", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test2")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]
        self.assertFalse(_has_mixed_config_types(configs))

    def test_all_registry_configs_returns_false(self):
        """Test that all orchestration_registry configs return False."""
        configs = [
            EvaluationConfig(
                orchestration_registry_reference="uuid1",
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                orchestration_registry_reference="uuid2",
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]
        self.assertFalse(_has_mixed_config_types(configs))

    def test_mixed_configs_returns_true(self):
        """Test that mixed llm and registry configs return True."""
        configs = [
            EvaluationConfig(
                llm=LLM(name="gpt-4", version="1.0"),
                template=PromptTemplateSpec(
                    template=[PromptTemplate(role="user", content="test")]
                ),
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            ),
            EvaluationConfig(
                orchestration_registry_reference="uuid1",
                dataset_config=Dataset("test.csv"),
                metrics=[MetricConfig(reference=MetricRef(name="metric1"))]
            )
        ]
        self.assertTrue(_has_mixed_config_types(configs))


class TestEvaluationClient(unittest.TestCase):

    def setUp(self):
        # Prevent real get_proxy_client side-effects
        patcher = patch(
            "gen_ai_hub.evaluations.client.get_proxy_client",
            autospec=True,
        )
        self.addCleanup(patcher.stop)
        self.mock_proxy = patcher.start()

        self.fake_ai_core = MagicMock()

    def test_init_with_client_passed_and_attrs_set(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            c = EvaluationClient(
                base_url="https://a",
                resource_group="rg",
                aws_access_key_id="AK",
                aws_secret_access_key="SK",
                ai_core_client=self.fake_ai_core,
            )

        self.assertEqual(c.base_url, "https://a")
        self.assertEqual(c.resource_group, "rg")
        self.assertIs(c.ai_core_client, self.fake_ai_core)
        self.assertEqual(c.aws_access_key_id, "AK")
        self.assertEqual(c.aws_secret_access_key, "SK")

    def test_init_missing_aws_raises(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            with self.assertRaises(ValueError):
                EvaluationClient(
                    base_url="x",
                    resource_group="rg",
                    ai_core_client=self.fake_ai_core,
                )

    def test_from_env_uses_fetch_credentials_and_constructs(self):
        fake_creds = {
            "base_url": "https://bv",
            "resource_group": "rg",
            "aws_access_key_id": "A",
            "aws_secret_access_key": "B",
        }

        with patch.object(module, "fetch_credentials", return_value=fake_creds), \
             patch("gen_ai_hub.evaluations.client.AICoreV2Client", autospec=True), \
             patch("gen_ai_hub.evaluations.client.get_proxy_client"):

            ec = EvaluationClient.from_env(profile_name="p")

        self.assertIsInstance(ec, EvaluationClient)
        self.assertEqual(ec.base_url, "https://bv")
        self.assertEqual(ec.resource_group, "rg")
        self.assertEqual(ec.aws_access_key_id, "A")

    def test_setup_input_secret_name_missing_raises(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        with self.assertRaises(ValueError):
            client.setup(
                input_secret_body={"type": "aws"},
                default_secret_body=None,
            )

    def test_setup_invalid_secret_type_raises(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        bad_body = {"name": "n", "type": "unsupported-type"}

        with self.assertRaises(ValueError):
            client.setup(input_secret_body=bad_body)

    def test_setup_secret_exists_replace_false_raises(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        resp_exists = SimpleNamespace(
            message=OBJECT_STORE_SECRET_EXISTS_MESSAGE
        )

        with patch(
            "gen_ai_hub.evaluations.client.create_aws_object_store_secret",
            return_value=resp_exists,
        ):
            with self.assertRaises(ValueError):
                client.setup(
                    input_secret_body={"name": "in", "type": "aws"},
                    replace_existing=False,
                )

    def test_setup_existing_config_and_running_deployment_reused(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group=DEFAULT_KEY,
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        cfg = MagicMock(id="cfg-1")
        deployment = SimpleNamespace(deployment_url="https://running")

        with patch(
            "gen_ai_hub.evaluations.client.get_orchestration_api_url",
            return_value="https://running",
        ):

            res = client.setup()

        self.assertEqual(
            res[ORCHESTRATION_URL_SETUP_KEY],
            "https://running",
        )
        self.assertEqual(client.orchestration_url, "https://running")

    def test_setup_existing_config_no_running_deployment_creates_new(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group=DEFAULT_KEY,
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        cfg = MagicMock(id="cfg-1")

        with patch(
            "gen_ai_hub.evaluations.client.get_orchestration_api_url",
            side_effect=ValueError("No deployment found"),
        ), patch(
            "gen_ai_hub.evaluations.client.create_llm_orchestration_deployment_url",
            return_value="https://new-orch",
        ):

            res = client.setup()

        self.assertEqual(
            res[ORCHESTRATION_URL_SETUP_KEY],
            "https://new-orch",
        )
        self.assertEqual(client.orchestration_url, "https://new-orch")

    def test_repr(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        repr_str = repr(client)
        self.assertIn("EvaluationClient", repr_str)
        self.assertIn("base_url", repr_str)

    def test_from_env_with_cert_url_conversion(self):
        fake_creds = {
            "base_url": "https://bv",
            "resource_group": "rg",
            "aws_access_key_id": "A",
            "aws_secret_access_key": "B",
            "cert_url": "https://cert-url",
        }

        with patch.object(module, "fetch_credentials", return_value=fake_creds), \
             patch("gen_ai_hub.evaluations.client.AICoreV2Client", autospec=True), \
             patch("gen_ai_hub.evaluations.client.get_proxy_client"):

            ec = EvaluationClient.from_env(profile_name="p")

        self.assertIsInstance(ec, EvaluationClient)
        # cert_url should have been converted to auth_url
        self.assertNotIn("cert_url", fake_creds)
        self.assertIn("auth_url", fake_creds)

    def test_setup_with_default_secret_body(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group=DEFAULT_KEY,
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        resp_success = SimpleNamespace(message="success")

        with patch(
            "gen_ai_hub.evaluations.client.create_aws_object_store_secret",
            return_value=resp_success,
        ), patch(
            "gen_ai_hub.evaluations.client.get_orchestration_api_url",
            return_value="https://running",
        ):
            res = client.setup(
                default_secret_body={"name": "default", "type": "S3"}
            )

        self.assertIn(DEFAULT_SECRET_SETUP_KEY, res)
        self.assertEqual(client.default_object_store_secret_name, "default")

    def test_setup_with_user_provided_orchestration_url(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
                orchestration_url="https://user-provided",
            )

        res = client.setup()

        self.assertEqual(res[ORCHESTRATION_URL_SETUP_KEY], "https://user-provided")
        self.assertEqual(client.orchestration_url, "https://user-provided")

    def test_setup_with_input_secret_body_success(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        resp_success = SimpleNamespace(message="created")

        with patch(
            "gen_ai_hub.evaluations.client.create_aws_object_store_secret",
            return_value=resp_success,
        ), patch(
            "gen_ai_hub.evaluations.client.create_llm_orchestration_deployment_url",
            return_value="https://new-deployment",
        ):
            res = client.setup(
                input_secret_body={"name": "in", "type": "S3"},
            )

        self.assertIn(INPUT_SECRET_SETUP_KEY, res)
        self.assertEqual(client.input_object_store_secret_name, "in")

    def test_setup_secret_creation_fails_raises_runtime_error(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        with patch(
            "gen_ai_hub.evaluations.client.create_aws_object_store_secret",
            side_effect=Exception("API Error"),
        ):
            with self.assertRaises(RuntimeError) as context:
                client.setup(
                    input_secret_body={"name": "in", "type": "S3"},
                )

            self.assertIn("Creation of in object store secret failed", str(context.exception))

    def test_setup_secret_exists_and_gets_replaced(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        resp_exists = SimpleNamespace(message=OBJECT_STORE_SECRET_EXISTS_MESSAGE)
        resp_success = SimpleNamespace(message="created")

        # Use a list to track calls and return different results
        responses = iter([resp_exists, resp_success])

        with patch(
            "gen_ai_hub.evaluations.client.create_aws_object_store_secret",
            side_effect=lambda *args, **kwargs: next(responses),
        ), patch(
            "gen_ai_hub.evaluations.client.delete_object_store_secret"
        ) as mock_delete, patch(
            "gen_ai_hub.evaluations.client.create_llm_orchestration_deployment_url",
            return_value="https://new-deployment",
        ):
            res = client.setup(
                input_secret_body={"name": "in", "type": "S3"},
                replace_existing=True,
            )

        self.assertIn(INPUT_SECRET_SETUP_KEY, res)
        mock_delete.assert_called_once()  # Verify delete was called

    def test_evaluate_missing_default_secret_raises(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        mock_config = MagicMock()

        with patch(
            "gen_ai_hub.evaluations.client.fetch_object_store_secret_by_name",
            return_value=None,
        ):
            with self.assertRaises(RuntimeError):
                client.evaluate([mock_config])

    def test_evaluate_missing_orchestration_url_raises(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )
            client.default_object_store_secret_name = "default"

        mock_config = MagicMock()

        with patch(
            "gen_ai_hub.evaluations.client.fetch_object_store_secret_by_name",
            return_value=MagicMock(),
        ):
            with self.assertRaises(RuntimeError):
                client.evaluate([mock_config])

    def test_resolve_orchestration_deployment_url_non_default_resource_group(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="non-default",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        with patch(
            "gen_ai_hub.evaluations.client.create_llm_orchestration_deployment_url",
            return_value="https://new-deployment",
        ):
            url = client.resolve_orchestration_deployment_url()

        self.assertEqual(url, "https://new-deployment")

    def test_list_available_models(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        mock_model = SimpleNamespace(
            model="gpt-4",
            provider="openai",
            allowed_scenarios=[{"scenario_id": "orchestration"}],
            versions=[SimpleNamespace(version="1.0", name="gpt-4")]
        )

        with patch(
            "gen_ai_hub.evaluations.client.list_available_llm_models",
            return_value=[mock_model],
        ):
            models = client.list_available_models()

        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["model"], "gpt-4")
        self.assertEqual(models[0]["provider"], "openai")

    def test_get_system_supported_metrics(self):
        with patch("gen_ai_hub.evaluations.client.get_proxy_client"):
            client = EvaluationClient(
                "u",
                resource_group="rg",
                aws_access_key_id="A",
                aws_secret_access_key="B",
                ai_core_client=self.fake_ai_core,
            )

        with patch(
            "gen_ai_hub.evaluations.client.fetch_all_system_predefined_metrics",
            return_value=["metric1", "metric2"],
        ):
            metrics = client.get_system_supported_metrics()

        self.assertEqual(metrics, ["metric1", "metric2"])