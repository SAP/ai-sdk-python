import unittest
from unittest.mock import MagicMock, patch

from ai_api_client_sdk.models.status import Status
from gen_ai_hub.evaluations.constants import (
    AWS_OSS_BUCKET_URL_KEY,
    AWS_OSS_REGION_URL_KEY,
    AWS_OSS_PATH_PREFIX_URL_KEY as AWS_PATH_KEY,
    CSV_FILE_TYPE as CSV,
    AI_PROTOCOL_PREFIX as AI_PREFIX,
    DATASET_FOLDER_KEY,
    SYSTEM_DEFINED_METRIC_MAPPING,
)
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector
from gen_ai_hub.evaluations.models.artifact_source import ArtifactSource
from gen_ai_hub.evaluations.models.metric_config import MetricConfig, MetricRef
from gen_ai_hub.evaluations._internal._models import (
    _AWSObjectStoreData,
    _EvaluationConfigData,
)
from gen_ai_hub.evaluations.utils.aicore_utils import (
    generate_random_id,
    find_configuration_id_by_name,
    get_all_configurations,
    get_running_deployments_by_configuration_id,
    create_deployment_by_configuration_id,
    create_llm_orchestration_deployment_url,
    wait_for_target_status,
    read_data_from_artifact,
    build_s3_file_key,
    resolve_artifact_path,
    fetch_deployment_config,
    fetch_configuration_by_id,
    call_orchestration_service_with_v2_config,
    upload_file_to_aws_s3,
    upload_evaluation_dataset_data,
    register_aicore_artifact,
    register_aicore_configuration,
    register_aicore_execution,
    list_available_llm_models,
    fetch_orchestration_config_from_registry,
    resolve_metric_identifiers,
    resolve_metric_names,
)

MODULE_PATH = "gen_ai_hub.evaluations.utils.aicore_utils"

DUMMY_ORCH_CONFIG = {
    "modules": {
        "prompt_templating": {
            "prompt": {
                "template": [{"content": "Hello {{?name}}", "role": "user"}],
                "defaults": {"name": ""}
            },
            "model": {
                "name": "gpt-4o",
                "version": "latest",
                "params": {},
                "timeout": 100,
                "max_retries": 1
            }
        }
    }
}

DUMMY_METRIC_TEMPLATES = [
    {
        "id": "metric-1",
        "name": "test_metric",
        "version": "1.0.0",
        "spec": {"outputType": "numerical"}
    }
]


class TestGenerateRandomId(unittest.TestCase):
    def test_generate_random_id_format(self):
        rid = generate_random_id()
        self.assertIsInstance(rid, str)
        self.assertEqual(len(rid), 32)  # hex of uuid4


class TestFindConfigurationIdByName(unittest.TestCase):
    def test_find_configuration_id_by_name_found_and_not_found(self):
        a = MagicMock()
        a.id = "id-a"
        a.name = "one"

        b = MagicMock()
        b.id = "id-b"
        b.name = "two"
        self.assertEqual(find_configuration_id_by_name([a, b], "two"), "id-b")
        self.assertIsNone(find_configuration_id_by_name([a, b], "missing"))


class TestGetAllConfigurations(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.configuration = MagicMock()
        self.mock_ai_core_client.deployment = MagicMock()
        self.mock_ai_core_client.artifact = MagicMock()
        self.mock_ai_core_client.execution = MagicMock()
        self.mock_ai_core_client.model = MagicMock()
        self.mock_ai_core_client.rest_client = MagicMock()
        self.mock_ai_core_client.artifact.get = MagicMock()
        self.mock_ai_core_client.artifact.create = MagicMock()
        self.mock_ai_core_client.configuration.create = MagicMock()
        self.mock_ai_core_client.execution.create = MagicMock()
        self.mock_ai_core_client.deployment.get = MagicMock()

    def test_get_all_configurations_success(self):
        self.mock_ai_core_client.configuration.query.return_value.resources = ["cfg1", "cfg2"]
        out = get_all_configurations(self.mock_ai_core_client, resource_group="rg", scenario_id="s")
        self.assertEqual(out, ["cfg1", "cfg2"])

    def test_get_all_configurations_raises_value_error(self):
        self.mock_ai_core_client.configuration.query.side_effect = Exception("boom")
        with self.assertRaises(ValueError):
            get_all_configurations(self.mock_ai_core_client, "rg", "s")


class TestGetRunningDeploymentsByConfigurationId(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.deployment = MagicMock()

    def test_get_running_deployments_by_configuration_id_success(self):
        self.mock_ai_core_client.deployment.query.return_value.resources = ["d1"]
        out = get_running_deployments_by_configuration_id(self.mock_ai_core_client, "cfg", "rg")
        self.assertEqual(out, ["d1"])

    def test_get_running_deployments_by_configuration_id_raises(self):
        self.mock_ai_core_client.deployment.query.side_effect = Exception("err")
        with self.assertRaises(ValueError):
            get_running_deployments_by_configuration_id(self.mock_ai_core_client, "cfg", "rg")


class TestWaitForTargetStatus(unittest.TestCase):
    def test_wait_for_target_status_success_and_extract_url(self):
        step1 = MagicMock(status=Status.PENDING)
        step2 = MagicMock(status=Status.RUNNING, deployment_url="http://ok")
        fetcher = MagicMock(side_effect=[step1, step2])

        url = wait_for_target_status(
            status_fetcher=fetcher,
            target_status=Status.RUNNING,
            extract_url=lambda r: r.deployment_url,
            timeout=5,
            initial_interval=0,
            pending_interval=0,
        )
        self.assertEqual(url, "http://ok")

    def test_wait_for_target_status_timeout_and_dead(self):
        dead = MagicMock(status=Status.DEAD)
        fetcher = MagicMock(return_value=dead)
        result = wait_for_target_status(
            status_fetcher=fetcher,
            target_status=Status.RUNNING,
            extract_url=None,
            timeout=1,
            initial_interval=0,
        )
        self.assertIsNone(result)


class TestCreateDeploymentByConfigurationId(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.deployment = MagicMock()
        self.mock_ai_core_client.configuration = MagicMock()

    @patch(f"{MODULE_PATH}.wait_for_target_status")
    def test_create_deployment_by_configuration_id_happy_path(self, mock_wait):
        deployment_response = MagicMock()
        deployment_response.id = "dep-1"
        self.mock_ai_core_client.deployment.create.return_value = deployment_response

        running_resp = MagicMock(status=getattr(Status, "RUNNING", "RUNNING"), deployment_url="http://dep")
        self.mock_ai_core_client.deployment.get.return_value = running_resp

        mock_wait.return_value = "http://dep"

        url = create_deployment_by_configuration_id(self.mock_ai_core_client, "cfg", "rg")
        self.assertEqual(url, "http://dep")
        self.mock_ai_core_client.deployment.create.assert_called_once()

    def test_create_deployment_by_configuration_id_raises_on_failure(self):
        self.mock_ai_core_client.deployment.create.side_effect = Exception("nope")
        with self.assertRaises(RuntimeError):
            create_deployment_by_configuration_id(self.mock_ai_core_client, "cfg", "rg")


class TestCreateLlmOrchestrationDeploymentUrl(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.configuration = MagicMock()

    @patch(f"{MODULE_PATH}.create_deployment_by_configuration_id")
    def test_create_llm_orchestration_deployment_url_happy(self, mock_create_deployment):
        self.mock_ai_core_client.configuration.create.return_value.id = "cfg-1"
        mock_create_deployment.return_value = "http://deployed"

        url = create_llm_orchestration_deployment_url(self.mock_ai_core_client, resource_group="rg")
        self.assertEqual(url, "http://deployed")

    def test_create_llm_orchestration_deployment_url_raises(self):
        self.mock_ai_core_client.configuration.create.side_effect = Exception("fail")
        with self.assertRaises(RuntimeError):
            create_llm_orchestration_deployment_url(self.mock_ai_core_client, resource_group="rg")


class TestReadDataFromArtifact(unittest.TestCase):
    def setUp(self):
        self.collector = ValidationCollector()

    @patch(f"{MODULE_PATH}.S3FileClient")
    def test_read_data_from_artifact_csv(self, mock_s3_client):
        mock_boto = MagicMock()
        mock_boto.read_csv.return_value = [["a", "b"]]
        mock_s3_client.return_value = mock_boto

        aws_creds = _AWSObjectStoreData(aws_access_key_id="k", aws_secret_access_key="s")
        meta = {AWS_OSS_BUCKET_URL_KEY: "bucket", AWS_OSS_REGION_URL_KEY: "r"}
        out = read_data_from_artifact(aws_creds, meta, "key", CSV, self.collector)
        self.assertEqual(out, [["a", "b"]])
        mock_boto.read_csv.assert_called_once_with("key")

    @patch(f"{MODULE_PATH}.S3FileClient")
    def test_read_data_from_artifact_jsonl(self, mock_s3_client):
        mock_boto = MagicMock()
        mock_boto.read_jsonl.return_value = [{"x": 1}]
        mock_s3_client.return_value = mock_boto

        aws_creds = _AWSObjectStoreData(aws_access_key_id="k", aws_secret_access_key="s")
        meta = {AWS_OSS_BUCKET_URL_KEY: "bucket", AWS_OSS_REGION_URL_KEY: "r"}
        out = read_data_from_artifact(aws_creds, meta, "key", "jsonl", self.collector)
        self.assertEqual(out, [{"x": 1}])
        mock_boto.read_jsonl.assert_called_once_with("key")


class TestBuildS3FileKey(unittest.TestCase):
    def test_build_s3_file_key_all_parts(self):
        meta = {AWS_PATH_KEY: "prefix"}
        rel = "artifact/path"
        src = MagicMock(path="inner/file.csv")
        self.assertEqual(build_s3_file_key(meta, rel, src), "prefix/artifact/path/inner/file.csv")

    def test_build_s3_file_key_minimal(self):
        meta = {}
        rel = "only/path"
        src = MagicMock(path=None)
        self.assertEqual(build_s3_file_key(meta, rel, src), "only/path")


class TestResolveArtifactPath(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.artifact = MagicMock()
        self.collector = ValidationCollector()

    @patch(f"{MODULE_PATH}.read_data_from_artifact")
    @patch(f"{MODULE_PATH}.fetch_object_store_secret_by_name")
    def test_resolve_artifact_path_success(self, mock_fetch_secret, mock_read_data):
        artifact = MagicMock()
        artifact.url = AI_PREFIX + "secretName/folder/file.csv"
        self.mock_ai_core_client.artifact.get.return_value = artifact

        mock_secret = MagicMock()
        mock_secret.metadata = {AWS_PATH_KEY: "pref"}
        mock_fetch_secret.return_value = mock_secret
        mock_read_data.return_value = [{"ok": 1}]

        aws_creds = _AWSObjectStoreData(aws_access_key_id="a", aws_secret_access_key="b")
        src = ArtifactSource(artifact="artifact-id", path="inner/file.csv", file_type="csv")
        result = resolve_artifact_path(src, self.mock_ai_core_client, aws_creds, "rg", self.collector)
        self.assertEqual(result, [{"ok": 1}])

    @patch(f"{MODULE_PATH}.fetch_object_store_secret_by_name")
    def test_resolve_artifact_path_bad_url(self, mock_fetch_secret):
        artifact = MagicMock()
        artifact.url = AI_PREFIX + "onlysecret"  # no slash
        self.mock_ai_core_client.artifact.get.return_value = artifact
        mock_fetch_secret.return_value = None

        aws_creds = _AWSObjectStoreData(aws_access_key_id="a", aws_secret_access_key="b")
        src = ArtifactSource(artifact="id", path=None, file_type="csv")
        out = resolve_artifact_path(src, self.mock_ai_core_client, aws_creds, "rg", self.collector)
        self.assertEqual(out, [])


class TestFetchDeploymentConfig(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.deployment = MagicMock()

    def test_fetch_deployment_config_success(self):
        self.mock_ai_core_client.deployment.get.return_value = "depconfig"
        c = ValidationCollector()
        out = fetch_deployment_config("did", self.mock_ai_core_client, "rg", c)
        self.assertEqual(out, "depconfig")

    def test_fetch_deployment_config_failure(self):
        self.mock_ai_core_client.deployment.get.side_effect = Exception("no")
        c = ValidationCollector()
        out = fetch_deployment_config("did", self.mock_ai_core_client, "rg", c)
        self.assertEqual(out, [])


class TestFetchConfigurationById(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.configuration = MagicMock()

    def test_fetch_configuration_by_id_success(self):
        self.mock_ai_core_client.configuration.get.return_value = "cfg"
        c = ValidationCollector()
        out = fetch_configuration_by_id("cfgid", self.mock_ai_core_client, "rg", c)
        self.assertEqual(out, "cfg")

    def test_fetch_configuration_by_id_failure(self):
        self.mock_ai_core_client.configuration.get.side_effect = Exception("fail")
        c = ValidationCollector()
        out = fetch_configuration_by_id("cfgid", self.mock_ai_core_client, "rg", c)
        self.assertEqual(out, [])


class TestCallOrchestrationServiceWithV2Config(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.rest_client = MagicMock()
        self.collector = ValidationCollector()

    def test_call_orchestration_service_with_v2_config_success(self):
        # Test that no errors are added when the call succeeds
        # We use a real simple test dict that should pass validation
        test_config = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "1.0", "params": {}},
                    "prompt": {"template": [{"role": "user", "content": "test"}]}
                }
            }
        }

        # Mock the OrchestrationService where it's used (in aicore_utils)
        with patch(f"{MODULE_PATH}.OrchestrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.run.return_value = {"ok": True}
            mock_service_class.return_value = mock_service

            call_orchestration_service_with_v2_config(
                test_config, self.mock_ai_core_client, "http://or", "rg", self.collector
            )

            self.assertFalse(self.collector.errors)

    def test_call_orchestration_service_with_v2_config_failure(self):
        # Test that errors are collected when the call fails
        test_config = {"test": "config"}

        # Mock the OrchestrationService where it's used (in aicore_utils)
        with patch(f"{MODULE_PATH}.OrchestrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.run.side_effect = Exception("Service error")
            mock_service_class.return_value = mock_service

            call_orchestration_service_with_v2_config(
                test_config, self.mock_ai_core_client, "http://or", "rg", self.collector
            )

            self.assertTrue(self.collector.errors)

    def test_call_orchestration_service_with_proxy_client_provided(self):
        # Test that when proxy_client is provided, it's passed to OrchestrationService
        test_config = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "1.0", "params": {}},
                    "prompt": {"template": [{"role": "user", "content": "test"}]}
                }
            }
        }

        mock_proxy_client = MagicMock()

        with patch(f"{MODULE_PATH}.OrchestrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.run.return_value = {"ok": True}
            mock_service_class.return_value = mock_service

            call_orchestration_service_with_v2_config(
                test_config,
                self.mock_ai_core_client,
                "http://or",
                "rg",
                self.collector,
                proxy_client=mock_proxy_client
            )

            # Verify OrchestrationService was called with the proxy_client
            mock_service_class.assert_called_once_with(
                api_url="http://or",
                proxy_client=mock_proxy_client
            )
            self.assertFalse(self.collector.errors)

    def test_call_orchestration_service_with_proxy_client_none(self):
        # Test that when proxy_client is None, it's still passed to OrchestrationService
        # OrchestrationService will handle None by creating its own proxy client
        test_config = {
            "modules": {
                "prompt_templating": {
                    "model": {"name": "gpt-4", "version": "1.0", "params": {}},
                    "prompt": {"template": [{"role": "user", "content": "test"}]}
                }
            }
        }

        with patch(f"{MODULE_PATH}.OrchestrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.run.return_value = {"ok": True}
            mock_service_class.return_value = mock_service

            call_orchestration_service_with_v2_config(
                test_config,
                self.mock_ai_core_client,
                "http://or",
                "rg",
                self.collector,
                proxy_client=None
            )

            # Verify OrchestrationService was called with proxy_client=None
            mock_service_class.assert_called_once_with(
                api_url="http://or",
                proxy_client=None
            )
            self.assertFalse(self.collector.errors)


class TestUploadFileToAwsS3(unittest.TestCase):
    def setUp(self):
        self.collector = ValidationCollector()

    @patch(f"{MODULE_PATH}.S3FileClient")
    def test_upload_file_to_aws_s3_csv(self, mock_s3_client):
        mock_boto = MagicMock()
        mock_boto.upload_csv.return_value = "ok"
        mock_s3_client.return_value = mock_boto

        aws_creds = _AWSObjectStoreData(aws_access_key_id="a", aws_secret_access_key="b")
        meta = {AWS_OSS_BUCKET_URL_KEY: "b"}
        out = upload_file_to_aws_s3(aws_creds, meta, [["r"]], "k", CSV, self.collector)
        self.assertEqual(out, "ok")

    @patch(f"{MODULE_PATH}.S3FileClient")
    def test_upload_file_to_aws_s3_jsonl(self, mock_s3_client):
        mock_boto = MagicMock()
        mock_boto.upload_jsonl.return_value = "ok"
        mock_s3_client.return_value = mock_boto
        aws_creds = _AWSObjectStoreData(aws_access_key_id="a", aws_secret_access_key="b")
        out = upload_file_to_aws_s3(aws_creds, {}, {"k": "v"}, "k", "jsonl", self.collector)
        self.assertEqual(out, "ok")


class TestUploadEvaluationDatasetData(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.collector = ValidationCollector()

    @patch(f"{MODULE_PATH}.upload_file_to_aws_s3")
    @patch(f"{MODULE_PATH}.fetch_object_store_secret_by_name")
    def test_upload_evaluation_dataset_data_success(self, mock_fetch_secret, mock_upload):
        mock_secret = MagicMock()
        mock_secret.metadata = {AWS_PATH_KEY: "prefix"}
        mock_fetch_secret.return_value = mock_secret
        mock_upload.return_value = True

        eval_data = _EvaluationConfigData(
            dataset_data=[{"x": 1}],
            dataset_type="csv",
            metrics_list=["m"],
            variable_mapping={},
            tags={},
            test_row_count=10,
            repetitions=1,
            debug_mode=True,
            orch_config_data={},
            metric_templates=[],
        )

        aws_creds = _AWSObjectStoreData(
            aws_access_key_id="a",
            aws_secret_access_key="b",
        )

        folder, path = upload_evaluation_dataset_data(
            eval_data,
            aws_creds,
            "secret-name",
            self.mock_ai_core_client,
            "rg",
            self.collector,
        )

        self.assertIsInstance(folder, str)
        self.assertIsInstance(path, str)
        self.assertTrue(path.startswith(DATASET_FOLDER_KEY) or path == "")

    @patch(f"{MODULE_PATH}.upload_file_to_aws_s3")
    @patch(f"{MODULE_PATH}.fetch_object_store_secret_by_name")
    def test_upload_evaluation_dataset_data_upload_failure(self, mock_fetch_secret, mock_upload):
        mock_secret = MagicMock()
        mock_secret.metadata = {}
        mock_fetch_secret.return_value = mock_secret
        mock_upload.return_value = False

        eval_data = _EvaluationConfigData(
            dataset_data=[{"x": 1}],
            dataset_type="csv",
            metrics_list=[],
            variable_mapping={},
            tags={},
            test_row_count=10,
            repetitions=1,
            debug_mode=True,
            orch_config_data=DUMMY_ORCH_CONFIG,
            metric_templates=DUMMY_METRIC_TEMPLATES
        )

        aws_creds = _AWSObjectStoreData(aws_access_key_id="a", aws_secret_access_key="b")
        folder, path = upload_evaluation_dataset_data(
            eval_data, aws_creds, "secret-name", self.mock_ai_core_client, "rg", self.collector
        )

        self.assertEqual(path, "")


class TestRegisterAicoreArtifact(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.artifact = MagicMock()
        self.collector = ValidationCollector()

    def test_register_aicore_artifact_success(self):
        self.mock_ai_core_client.artifact.create.return_value.id = "art-1"
        res = register_aicore_artifact("folder", self.mock_ai_core_client, "rg", "secret", self.collector)
        self.assertEqual(res, "art-1")

    def test_register_aicore_artifact_failure(self):
        self.mock_ai_core_client.artifact.create.side_effect = Exception("no")
        res = register_aicore_artifact("folder", self.mock_ai_core_client, "rg", "secret", self.collector)
        self.assertEqual(res, "")


class TestRegisterAicoreConfiguration(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.configuration = MagicMock()
        self.collector = ValidationCollector()

    def test_register_aicore_configuration_with_llm_and_template(self):
        acc = _EvaluationConfigData(
            dataset_data=None,
            dataset_type="csv",
            metrics_list=["m"],
            variable_mapping={},
            tags={},
            test_row_count=1,
            repetitions=1,
            debug_mode=True,
            orch_config_data=DUMMY_ORCH_CONFIG,
            metric_templates=DUMMY_METRIC_TEMPLATES
        )

        self.mock_ai_core_client.configuration.create.return_value.id = "cfg-1"

        config_id = register_aicore_configuration(
            aicore_artifact_id="aid",
            ai_core_client=self.mock_ai_core_client,
            resource_group="rg",
            accumulated_config_data=acc,
            orchestration_url="http://orch",
            dataset_file_key="x.csv",
            run_ids_list=["r1", "r2"],
            llm_model_config="modelcfg",
            template_config=["tpl"],
            orchestration_registry_config=None,
            error_collector=self.collector,
        )

        self.assertEqual(config_id, "cfg-1")

    def test_register_aicore_configuration_with_orch_registry(self):
        acc = _EvaluationConfigData(
            dataset_data=None,
            dataset_type="csv",
            metrics_list=["m"],
            variable_mapping={},
            tags={},
            test_row_count=1,
            repetitions=1,
            debug_mode=False,
            orch_config_data=DUMMY_ORCH_CONFIG,
            metric_templates=DUMMY_METRIC_TEMPLATES
        )

        self.mock_ai_core_client.configuration.create.return_value.id = "cfg-2"

        config_id = register_aicore_configuration(
            aicore_artifact_id="aid",
            ai_core_client=self.mock_ai_core_client,
            resource_group="rg",
            accumulated_config_data=acc,
            orchestration_url="http://orch",
            dataset_file_key="x.csv",
            run_ids_list=["r1"],
            llm_model_config=None,
            template_config=None,
            orchestration_registry_config="orch-ids",
            error_collector=self.collector,
        )

        self.assertEqual(config_id, "cfg-2")

    def test_register_aicore_configuration_failure(self):
        self.mock_ai_core_client.configuration.create.side_effect = Exception("bad")

        acc = _EvaluationConfigData(
            dataset_data=None,
            dataset_type="csv",
            metrics_list=["m"],
            variable_mapping={},
            tags={},
            test_row_count=1,
            repetitions=1,
            debug_mode=True,
            orch_config_data=DUMMY_ORCH_CONFIG,
            metric_templates=DUMMY_METRIC_TEMPLATES
        )

        res = register_aicore_configuration(
            aicore_artifact_id="aid",
            ai_core_client=self.mock_ai_core_client,
            resource_group="rg",
            accumulated_config_data=acc,
            orchestration_url="http://orch",
            dataset_file_key="x.csv",
            run_ids_list=["r1"],
            llm_model_config="modelcfg",
            template_config=["tpl"],
            orchestration_registry_config=None,
            error_collector=self.collector,
        )

        self.assertIsNone(res)


class TestRegisterAicoreExecution(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.execution = MagicMock()
        self.collector = ValidationCollector()

    def test_register_aicore_execution_success(self):
        self.mock_ai_core_client.execution.create.return_value.id = "exec-1"
        exec_id = register_aicore_execution(self.mock_ai_core_client, "cfg", "rg", self.collector)
        self.assertEqual(exec_id, "exec-1")

    def test_register_aicore_execution_failure(self):
        self.mock_ai_core_client.execution.create.side_effect = Exception("err")
        res = register_aicore_execution(self.mock_ai_core_client, "cfg", "rg", self.collector)
        self.assertIsNone(res)


class TestListAvailableLlmModels(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.model = MagicMock()

    def test_list_available_llm_models_success(self):
        self.mock_ai_core_client.model.query.return_value.resources = ["m1"]
        out = list_available_llm_models(self.mock_ai_core_client, "rg")
        self.assertEqual(out, ["m1"])

    def test_list_available_llm_models_failure(self):
        self.mock_ai_core_client.model.query.side_effect = Exception("err")
        with self.assertRaises(RuntimeError):
            list_available_llm_models(self.mock_ai_core_client, "rg")


class TestFetchOrchestrationConfigFromRegistry(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.rest_client = MagicMock()
        self.collector = ValidationCollector()

    def test_fetch_orchestration_config_from_registry_ok(self):
        self.mock_ai_core_client.rest_client.get.return_value = {"spec": {"one": 1}}
        out = fetch_orchestration_config_from_registry("ref-1", self.mock_ai_core_client, self.collector)
        self.assertEqual(out, {"one": 1})

    def test_fetch_orchestration_config_from_registry_error(self):
        self.mock_ai_core_client.rest_client.get.side_effect = Exception("bad")
        out = fetch_orchestration_config_from_registry("ref-1", self.mock_ai_core_client, self.collector)
        self.assertIsNone(out)


class TestResolveMetricIdentifiers(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.collector = ValidationCollector()

    @patch(f"{MODULE_PATH}.get_custom_metric_by_id")
    @patch(f"{MODULE_PATH}.get_metric_version_history")
    @patch(f"{MODULE_PATH}.get_metric_template_info_from_server")
    def test_resolve_metric_identifiers_all_paths(self, mock_sys, mock_hist, mock_by_id):
        mc_id = MetricConfig(reference=MetricRef(id="id-1"))
        mc_hist = MetricConfig(reference=MetricRef(scenario="s", name="n", version="v"))
        mc_sys = MetricConfig(reference=MetricRef(name=list(SYSTEM_DEFINED_METRIC_MAPPING.values())[0]))

        mock_by_id.return_value = {"id": "id-1"}
        mock_hist.return_value = {"id": "hist-1"}
        mock_sys.return_value = {"id": "sys-1"}

        out = resolve_metric_identifiers([mc_id, mc_hist, mc_sys], self.mock_ai_core_client, "rg", self.collector)
        self.assertIsInstance(out, list)
        self.assertEqual({o["id"] for o in out}, {"id-1", "hist-1", "sys-1"})


class TestResolveMetricNames(unittest.TestCase):
    def setUp(self):
        self.collector = ValidationCollector()

    def test_resolve_metric_names_valid_and_invalid(self):
        m1 = MetricConfig(reference=MetricRef(id="uuid-1"))
        m2 = MetricConfig(reference=MetricRef(scenario="sc", name="n", version="1"))
        m3 = MetricConfig(reference=MetricRef(name="metric-name"))
        m4 = MetricConfig(reference=MetricRef())

        res = resolve_metric_names([m1, m2, m3], self.collector)
        self.assertEqual(res, ["uuid-1", "sc/n/1", "metric-name"])

        c = ValidationCollector()
        resolve_metric_names([m4], c)
        self.assertTrue(c.errors)


if __name__ == "__main__":
    unittest.main()
