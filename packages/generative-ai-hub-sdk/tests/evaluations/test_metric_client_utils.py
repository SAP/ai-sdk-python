import unittest
from unittest.mock import MagicMock, patch

from gen_ai_hub.evaluations.utils.metric_client_utils import (
    _get_custom_metric_details,
    get_custom_metric_by_id,
    get_metric_template_info_from_server,
    get_metric_version_history,
    fetch_all_system_predefined_metrics,
)
from gen_ai_hub.evaluations.helpers.collector import ValidationCollector


class TestGetCustomMetricDetails(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.base_url = "https://test.com/v2"
        self.mock_ai_core_client.rest_client.get_token.return_value = "Bearer token123"
        self.resource_group = "test-rg"
        self.error_collector = ValidationCollector()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_custom_metric_details_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"resources": [{"id": "1", "name": "metric1"}]}
        mock_get.return_value = mock_response

        result = _get_custom_metric_details(
            self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertEqual(result, {"resources": [{"id": "1", "name": "metric1"}]})
        mock_get.assert_called_once()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_custom_metric_details_exception(self, mock_get):
        mock_get.side_effect = Exception("Network error")

        result = _get_custom_metric_details(
            self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertIsNone(result)
        self.assertTrue(len(self.error_collector.errors) > 0)
        self.assertIn("GenAI metrics server GET request", self.error_collector.errors[0][1])


class TestGetCustomMetricById(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.base_url = "https://test.com/v2"
        self.mock_ai_core_client.rest_client.get_token.return_value = "Bearer token123"
        self.resource_group = "test-rg"
        self.error_collector = ValidationCollector()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_custom_metric_by_id_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "metric-123",
            "name": "test-metric",
            "description": "Test metric description",
        }
        mock_get.return_value = mock_response

        result = get_custom_metric_by_id(
            "metric-123", self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertEqual(result["id"], "metric-123")
        self.assertEqual(result["name"], "test-metric")
        mock_get.assert_called_once()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_custom_metric_by_id_exception(self, mock_get):
        mock_get.side_effect = Exception("API error")

        result = get_custom_metric_by_id(
            "metric-123", self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertIsNone(result)
        self.assertTrue(len(self.error_collector.errors) > 0)


class TestGetMetricTemplateInfoFromServer(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.base_url = "https://test.com/v2"
        self.mock_ai_core_client.rest_client.get_token.return_value = "Bearer token123"
        self.resource_group = "test-rg"
        self.error_collector = ValidationCollector()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.get_custom_metric_by_id")
    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_get_metric_template_info_found(self, mock_get_details, mock_get_by_id):
        mock_get_details.return_value = {
            "resources": [
                {"id": "metric-1", "name": "test-metric"},
                {"id": "metric-2", "name": "other-metric"},
            ]
        }
        mock_get_by_id.return_value = {
            "id": "metric-1",
            "name": "test-metric",
            "schema": {},
        }

        result = get_metric_template_info_from_server(
            "test-metric", self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "metric-1")
        mock_get_by_id.assert_called_once_with(
            "metric-1", self.mock_ai_core_client, self.resource_group, self.error_collector
        )

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.get_custom_metric_by_id")
    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_get_metric_template_info_not_found(self, mock_get_details, mock_get_by_id):
        mock_get_details.return_value = {
            "resources": [
                {"id": "metric-1", "name": "other-metric"},
            ]
        }

        result = get_metric_template_info_from_server(
            "nonexistent-metric", self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertIsNone(result)
        mock_get_by_id.assert_not_called()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_get_metric_template_info_empty_resources(self, mock_get_details):
        mock_get_details.return_value = {"resources": []}

        result = get_metric_template_info_from_server(
            "test-metric", self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertIsNone(result)


class TestGetMetricVersionHistory(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.base_url = "https://test.com/v2"
        self.mock_ai_core_client.rest_client.get_token.return_value = "Bearer token123"
        self.resource_group = "test-rg"
        self.error_collector = ValidationCollector()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_metric_version_history_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "resources": [
                {"version": "1.0", "metricId": "metric-1"},
                {"version": "1.1", "metricId": "metric-1"},
            ]
        }
        mock_get.return_value = mock_response

        result = get_metric_version_history(
            "scenario1",
            "metric-1",
            "1.0",
            self.mock_ai_core_client,
            self.resource_group,
            self.error_collector,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["version"], "1.0")
        mock_get.assert_called_once()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_metric_version_history_no_resources(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"resources": []}
        mock_get.return_value = mock_response

        result = get_metric_version_history(
            "scenario1",
            "metric-1",
            "1.0",
            self.mock_ai_core_client,
            self.resource_group,
            self.error_collector,
        )

        self.assertIsNone(result)
        self.assertTrue(len(self.error_collector.errors) > 0)
        self.assertIn("No version history resources found", self.error_collector.errors[0][1])

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils.requests.get")
    def test_get_metric_version_history_exception(self, mock_get):
        mock_get.side_effect = Exception("Request failed")

        result = get_metric_version_history(
            "scenario1",
            "metric-1",
            "1.0",
            self.mock_ai_core_client,
            self.resource_group,
            self.error_collector,
        )

        self.assertIsNone(result)
        self.assertTrue(len(self.error_collector.errors) > 0)
        self.assertIn("GenAI metrics server GET request encountered an exception", self.error_collector.errors[0][1])


class TestFetchAllSystemPredefinedMetrics(unittest.TestCase):
    def setUp(self):
        self.mock_ai_core_client = MagicMock()
        self.mock_ai_core_client.base_url = "https://test.com/v2"
        self.mock_ai_core_client.rest_client.get_token.return_value = "Bearer token123"
        self.resource_group = "test-rg"
        self.error_collector = ValidationCollector()

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_fetch_all_system_predefined_metrics_success(self, mock_get_details):
        mock_get_details.return_value = {
            "resources": [
                {"id": "1", "name": "metric1", "systemPredefined": True},
                {"id": "2", "name": "metric2", "systemPredefined": False},
                {"id": "3", "name": "metric3", "systemPredefined": True},
            ]
        }

        result = fetch_all_system_predefined_metrics(
            self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertEqual(len(result), 2)
        self.assertTrue(all(item.get("systemPredefined") for item in result))
        self.assertEqual(result[0]["id"], "1")
        self.assertEqual(result[1]["id"], "3")

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_fetch_all_system_predefined_metrics_empty(self, mock_get_details):
        mock_get_details.return_value = {"resources": []}

        result = fetch_all_system_predefined_metrics(
            self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertEqual(len(result), 0)

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_fetch_all_system_predefined_metrics_no_predefined(self, mock_get_details):
        mock_get_details.return_value = {
            "resources": [
                {"id": "1", "name": "metric1", "systemPredefined": False},
                {"id": "2", "name": "metric2", "systemPredefined": False},
            ]
        }

        result = fetch_all_system_predefined_metrics(
            self.mock_ai_core_client, self.resource_group, self.error_collector
        )

        self.assertEqual(len(result), 0)

    @patch("gen_ai_hub.evaluations.utils.metric_client_utils._get_custom_metric_details")
    def test_fetch_all_system_predefined_metrics_exception(self, mock_get_details):
        mock_get_details.side_effect = Exception("Server error")

        with self.assertRaises(RuntimeError) as context:
            fetch_all_system_predefined_metrics(
                self.mock_ai_core_client, self.resource_group, self.error_collector
            )

        self.assertIn("System Predefined metrics obtained from Metric Management service failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()
