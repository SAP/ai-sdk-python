import uuid
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from ai_api_client_sdk.models.status import Status

from gen_ai_hub.evaluations.models.evaluation_run import (
    EvaluationRun,
    Results,
    ExecutionStatusDetails,
    _RunContext,
    configure_pandas_display,
)
from gen_ai_hub.evaluations._internal._models import _AWSObjectStoreData
from gen_ai_hub.evaluations.constants import (
    DEFAULT_KEY,
    AWS_OSS_PATH_PREFIX_URL_KEY,
    RESULTS_FILE_KEY,
    AWS_OSS_BUCKET_URL_KEY,
    AWS_OSS_REGION_URL_KEY,
    COMPLETIONS_TABLE_KEY,
    METRICS_TABLE_KEY,
)


class TestRunContext(unittest.TestCase):

    def test_run_context_init(self):
        mock_client = MagicMock()
        mock_credentials = MagicMock()

        context = _RunContext(
            execution_id="exec-123",
            configuration_id="config-456",
            artifact_id="artifact-789",
            ai_core_client=mock_client,
            resource_group="rg-test",
            object_store_credentials=mock_credentials,
            metrics_list=["metric1", "metric2"],
            cached_results_data={"data": "test"},
        )

        self.assertEqual(context.execution_id, "exec-123")
        self.assertEqual(context.configuration_id, "config-456")
        self.assertEqual(context.artifact_id, "artifact-789")
        self.assertIs(context.ai_core_client, mock_client)
        self.assertEqual(context.resource_group, "rg-test")
        self.assertIs(context.object_store_credentials, mock_credentials)
        self.assertEqual(context.metrics_list, ["metric1", "metric2"])
        self.assertEqual(context.cached_results_data, {"data": "test"})


class TestEvaluationRun(unittest.TestCase):

    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.execution = MagicMock()
        self.mock_ai_core_client.object_store_secrets = MagicMock()
        self.mock_ai_core_client.base_url = "https://api.example.com"
        self.mock_ai_core_client.rest_client = MagicMock()

        self.mock_object_store_credentials = _AWSObjectStoreData(
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
        )

        self.evaluation_run = EvaluationRun(
            run_id="run-123",
            execution_id="exec-456",
            ai_core_client=self.mock_ai_core_client,
            configuration_id="config-789",
            artifact_id="artifact-abc",
            resource_group="rg-test",
            object_store_credentials=self.mock_object_store_credentials,
            metrics_list=["metric1", "metric2"],
        )

    def test_evaluation_run_init(self):
        run = self.evaluation_run

        self.assertEqual(run.id, "run-123")
        self.assertEqual(run.status, Status.UNKNOWN)
        self.assertEqual(run._run_context.execution_id, "exec-456")
        self.assertEqual(run._run_context.configuration_id, "config-789")
        self.assertEqual(run._run_context.artifact_id, "artifact-abc")
        self.assertEqual(run._run_context.resource_group, "rg-test")
        self.assertEqual(run._run_context.metrics_list, ["metric1", "metric2"])

    def test_set_cached_results_data(self):
        test_data = {"completions": [], "metrics": []}
        self.evaluation_run.set_cached_results_data(test_data)
        self.assertEqual(self.evaluation_run._cached_results_data, test_data)

    def test_execution_status_fetcher(self):
        mock_response = MagicMock()
        self.mock_ai_core_client.execution.get.return_value = mock_response

        result = self.evaluation_run._execution_status_fetcher()

        self.mock_ai_core_client.execution.get.assert_called_once_with(
            execution_id="exec-456",
            resource_group="rg-test",
            select="status",
        )
        self.assertIs(result, mock_response)

    @patch("gen_ai_hub.evaluations.models.evaluation_run.wait_for_target_status")
    def test_wait_for_completion(self, mock_wait):
        mock_wait.return_value = None
        self.evaluation_run.wait_for_completion(timeout=100)

        mock_wait.assert_called_once()
        self.assertEqual(mock_wait.call_args[1]["target_status"], Status.COMPLETED)
        self.assertEqual(mock_wait.call_args[1]["timeout"], 100)

    @patch("gen_ai_hub.evaluations.models.evaluation_run.wait_for_target_status")
    def test_wait_for_completion_default_timeout(self, mock_wait):
        mock_wait.return_value = None
        self.evaluation_run.wait_for_completion()

        self.assertEqual(mock_wait.call_args[1]["timeout"], 3600)

    def test_get_current_status_success(self):
        mock_response = MagicMock()
        mock_response.status = Status.RUNNING
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        status = self.evaluation_run.get_current_status()
        self.assertEqual(status, Status.RUNNING)

    def test_get_current_status_exception(self):
        self.evaluation_run._execution_status_fetcher = MagicMock(side_effect=Exception("API Error"))

        with self.assertRaises(ValueError):
            self.evaluation_run.get_current_status()

    def test_get_debug_info_without_status_details(self):
        mock_response = MagicMock()
        mock_response.status = Status.DEAD
        mock_response.status_details = None
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        result = self.evaluation_run.get_debug_info()

        self.assertIsInstance(result, ExecutionStatusDetails)
        self.assertEqual(result.status, Status.DEAD)
        self.assertIn("No specific details found", result.details)

    def test_get_debug_logs(self):
        mock_log_item1 = MagicMock()
        mock_log_item1.__dict__ = {"message": "log1", "level": "INFO"}
        mock_log_item2 = MagicMock()
        mock_log_item2.__dict__ = {"message": "log2", "level": "ERROR"}

        mock_logs = MagicMock()
        mock_logs.data.result = [mock_log_item1, mock_log_item2]
        self.mock_ai_core_client.execution.query_logs.return_value = mock_logs

        result = self.evaluation_run.get_debug_logs()

        self.mock_ai_core_client.execution.query_logs.assert_called_once_with(
            execution_id="exec-456"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["message"], "log1")
        self.assertEqual(result[1]["message"], "log2")

    def test_results_with_completed_status(self):
        mock_response = MagicMock()
        mock_response.status = Status.COMPLETED
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        result = self.evaluation_run.results()

        self.assertIsInstance(result, Results)
        self.assertIs(result.run, self.evaluation_run)

    def test_results_with_running_status(self):
        mock_response = MagicMock()
        mock_response.status = Status.RUNNING
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        with self.assertRaises(ValueError):
            self.evaluation_run.results()

    def test_results_with_other_status(self):
        mock_response = MagicMock()
        mock_response.status = Status.DEAD
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        with self.assertRaises(ValueError):
            self.evaluation_run.results()

    def test_load_results_tables_with_cached_data(self):
        cached_data = {"completions": [], "metrics": []}
        self.evaluation_run._run_context.cached_results_data = cached_data

        result = self.evaluation_run.load_results_tables()

        self.assertEqual(result, cached_data)
        self.mock_ai_core_client.object_store_secrets.get.assert_not_called()

    @patch("gen_ai_hub.evaluations.models.evaluation_run.S3FileClient")
    def test_load_results_tables_from_s3(self, mock_s3_client_class):
        self.evaluation_run._run_context.cached_results_data = None

        mock_secret_response = MagicMock()
        mock_secret_response.metadata = {
            AWS_OSS_PATH_PREFIX_URL_KEY: "prefix/path",
            AWS_OSS_BUCKET_URL_KEY: "bucket-name",
            AWS_OSS_REGION_URL_KEY: "us-east-1",
        }

        self.mock_ai_core_client.object_store_secrets.get.return_value = mock_secret_response

        mock_s3_client = MagicMock()
        mock_s3_client.get_sqlitedb_tables_data_from_s3.return_value = {
            COMPLETIONS_TABLE_KEY: [{"id": 1}],
            METRICS_TABLE_KEY: [{"id": 2}],
        }
        mock_s3_client_class.return_value = mock_s3_client

        result = self.evaluation_run.load_results_tables()

        self.mock_ai_core_client.object_store_secrets.get.assert_called_once_with(
            name=DEFAULT_KEY,
            resource_group="rg-test",
        )

        expected_key = f"prefix/path/exec-456/tmp/{RESULTS_FILE_KEY}"

        mock_s3_client.get_sqlitedb_tables_data_from_s3.assert_called_once_with(
            expected_key,
            [COMPLETIONS_TABLE_KEY, METRICS_TABLE_KEY],
        )

        self.assertIn(COMPLETIONS_TABLE_KEY, result)
        self.assertIn(METRICS_TABLE_KEY, result)

    def test_load_results_tables_exception(self):
        self.evaluation_run._run_context.cached_results_data = None
        self.mock_ai_core_client.object_store_secrets.get.side_effect = Exception("S3 Error")

        with self.assertRaises(RuntimeError):
            self.evaluation_run.load_results_tables()

    def test_results_with_completed_status(self):
        mock_response = MagicMock()
        mock_response.status = Status.COMPLETED
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        result = self.evaluation_run.results()

        self.assertIsInstance(result, Results)
        self.assertIs(result.run, self.evaluation_run)

    def test_results_with_running_status(self):
        mock_response = MagicMock()
        mock_response.status = Status.RUNNING
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        with self.assertRaises(ValueError):
            self.evaluation_run.results()

    def test_results_with_other_status(self):
        mock_response = MagicMock()
        mock_response.status = Status.DEAD
        self.evaluation_run._execution_status_fetcher = MagicMock(return_value=mock_response)

        with self.assertRaises(ValueError):
            self.evaluation_run.results()



class TestConfigurePandasDisplay(unittest.TestCase):

    @patch("pandas.set_option")
    def test_configure_pandas_display(self, mock_set_option):
        configure_pandas_display()

        self.assertEqual(mock_set_option.call_count, 4)

        calls = [call.args for call in mock_set_option.call_args_list]

        self.assertIn(("display.max_columns", None), calls)
        self.assertIn(("display.max_rows", None), calls)
        self.assertIn(("display.max_colwidth", None), calls)
        self.assertIn(("display.expand_frame_repr", False), calls)


class TestResults(unittest.TestCase):

    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.execution = MagicMock()
        self.mock_ai_core_client.object_store_secrets = MagicMock()
        self.mock_ai_core_client.base_url = "https://api.example.com"
        self.mock_ai_core_client.rest_client = MagicMock()
        self.mock_ai_core_client.rest_client.get_token = MagicMock(return_value="mock-token")

        self.mock_object_store_credentials = _AWSObjectStoreData(
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
        )

        self.evaluation_run = EvaluationRun(
            run_id="run-123",
            execution_id="exec-456",
            ai_core_client=self.mock_ai_core_client,
            resource_group="rg-test",
            object_store_credentials=self.mock_object_store_credentials,
        )

        mock_response = MagicMock()
        mock_response.status = Status.COMPLETED
        self.evaluation_run._execution_status_fetcher = MagicMock(
            return_value=mock_response
        )

        # Patch Tracking before creating Results
        self.tracking_patcher = patch("gen_ai_hub.evaluations.models.evaluation_run.Tracking")
        self.mock_tracking_class = self.tracking_patcher.start()
        self.mock_tracking_instance = MagicMock()
        self.mock_tracking_class.return_value = self.mock_tracking_instance

        self.results = Results(self.evaluation_run)

    def tearDown(self):
        self.tracking_patcher.stop()

    @patch("gen_ai_hub.evaluations.models.evaluation_run.configure_pandas_display")
    def test_results_init(self, mock_configure):
        # Reset the mock to count calls from this test
        self.mock_tracking_class.reset_mock()

        result = Results(self.evaluation_run)

        self.assertIs(result.run, self.evaluation_run)
        self.assertIsNone(result._data_store)
        self.assertIs(result._run_context, self.evaluation_run._run_context)
        mock_configure.assert_called_once()

        # Verify Tracking client was created
        self.mock_tracking_class.assert_called_once_with(
            base_url=self.mock_ai_core_client.base_url,
            token_creator=self.mock_ai_core_client.rest_client.get_token,
            resource_group="rg-test",
        )

    def test_ensure_loaded(self):
        test_data = {
            COMPLETIONS_TABLE_KEY: [{"id": 1}],
            METRICS_TABLE_KEY: [{"id": 2}],
        }

        self.evaluation_run.load_results_tables = MagicMock(return_value=test_data)
        self.evaluation_run.set_cached_results_data = MagicMock()

        self.results._ensure_loaded()

        self.assertEqual(self.results._data_store, test_data)
        self.evaluation_run.set_cached_results_data.assert_called_once_with(test_data)

    def test_ensure_loaded_already_loaded(self):
        existing_data = {"data": "exists"}
        self.results._data_store = existing_data

        self.results._ensure_loaded()

        self.assertEqual(self.results._data_store, existing_data)

    def test_filter_by_run_id(self):
        run_id_uuid = uuid.uuid4()
        run_id_hex = run_id_uuid.hex

        data = [
            {"run_id": run_id_hex, "value": 1},
            {"run_id": run_id_hex, "value": 2},
            {"run_id": "other-run-id", "value": 3},
        ]

        filtered = self.results._filter_by_run_id(data, str(run_id_uuid))

        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(row["run_id"] == run_id_hex for row in filtered))

    def test_completions(self):
        run_id_uuid = uuid.uuid4()
        run_id_hex = run_id_uuid.hex
        self.evaluation_run.id = str(run_id_uuid)

        test_data = {
            COMPLETIONS_TABLE_KEY: [
                {"run_id": run_id_hex, "completion": "test1"},
                {"run_id": run_id_hex, "completion": "test2"},
                {"run_id": "other-id", "completion": "test3"},
            ],
            METRICS_TABLE_KEY: [],
        }

        self.evaluation_run.load_results_tables = MagicMock(return_value=test_data)

        df = self.results.completions()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertTrue(all(row["run_id"] == run_id_hex for row in df.to_dict("records")))

    def test_completions_exception(self):
        self.evaluation_run.load_results_tables = MagicMock(
            side_effect=Exception("Load error")
        )

        with self.assertRaises(ValueError):
            self.results.completions()

    def test_metrics(self):
        run_id_uuid = uuid.uuid4()
        run_id_hex = run_id_uuid.hex
        self.evaluation_run.id = str(run_id_uuid)

        test_data = {
            COMPLETIONS_TABLE_KEY: [],
            METRICS_TABLE_KEY: [
                {"run_id": run_id_hex, "metric": "metric1", "value": 0.9},
                {"run_id": run_id_hex, "metric": "metric2", "value": 0.8},
                {"run_id": "other-id", "metric": "metric3", "value": 0.7},
            ],
        }

        self.evaluation_run.load_results_tables = MagicMock(return_value=test_data)

        df = self.results.metrics()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertTrue(all(row["run_id"] == run_id_hex for row in df.to_dict("records")))

    def test_metrics_exception(self):
        self.evaluation_run.load_results_tables = MagicMock(
            side_effect=Exception("Load error")
        )

        with self.assertRaises(ValueError):
            self.results.metrics()

    def test_aggregations(self):
        run_id_uuid = uuid.uuid4()
        run_id_hex = run_id_uuid.hex
        self.evaluation_run.id = str(run_id_uuid)

        self.mock_tracking_instance.query.return_value = {"aggregations": {"metric1": 0.9}}

        result = self.results.aggregations()

        self.mock_tracking_instance.query.assert_called_once_with(
            execution_ids=[run_id_hex]
        )

        self.assertEqual(result, {"aggregations": {"metric1": 0.9}})

    def test_aggregations_exception(self):
        run_id_uuid = uuid.uuid4()
        self.evaluation_run.id = str(run_id_uuid)

        self.mock_tracking_instance.query.side_effect = Exception("Network error")

        with self.assertRaises(ValueError):
            self.results.aggregations()
