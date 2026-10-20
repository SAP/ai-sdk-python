import unittest
from unittest.mock import patch

from gen_ai_hub.proxy.native.sap.models import (
    RPTRequest, PredictionConfig, TargetColumn, RPTResponse, RPTException,
    PredictionItem, ExplanationConfig, ExplanationResult
)
from gen_ai_hub.proxy.native.sap.client import RPTClient
from tests.mock import (
    get_mocked_ai_core_client,
    sap_rpt_mock_response_code_0,
    sap_rpt_mock_response_code_2,
    RPT_RESPONSE_CODE_0,
    RPT_RESPONSE_CODE_0_WITH_EXPLANATIONS,
)

mock_url = "https://mock-rpt-deployment"

request_by_row_dict = {
            "prediction_config": {
                "target_columns": [
                    {
                        "name": "COSTCENTER",
                        "prediction_placeholder": "[PREDICT]",
                        "task_type": "classification"
                    }
                ]
            },
            "index_column": "ID",
            "rows": [
                {
                    "PRODUCT": "Couch",
                    "PRICE": 999.99,
                    "ORDERDATE": "28-11-2025",
                    "ID": "35",
                    "COSTCENTER": "[PREDICT]"
                },
                {
                    "PRODUCT": "Office Chair",
                    "PRICE": 150.8,
                    "ORDERDATE": "02-11-2025",
                    "ID": "44",
                    "COSTCENTER": "Office Furniture"
                },
                {
                    "PRODUCT": "Server Rack",
                    "PRICE": 2200.00,
                    "ORDERDATE": "01-11-2025",
                    "ID": "104",
                    "COSTCENTER": "Data Infrastructure"
                }
            ],
            "data_schema": {
                "PRODUCT": {
                    "dtype": "string"
                },
                "PRICE": {
                    "dtype": "numeric"
                },
                "ORDERDATE": {
                    "dtype": "date"
                },
                "ID": {
                    "dtype": "string"
                },
                "COSTCENTER": {
                    "dtype": "string"
                }
            }
        }

request_by_columns_dict = {
  "prediction_config": {
    "target_columns": [
      {
        "name": "COSTCENTER",
        "prediction_placeholder": "[PREDICT]",
        "task_type": "classification"
      }
    ]
  },
  "index_column": "ID",
  "columns": {
      "PRODUCT": ["Couch", "Office Chair", "Server Rack"],
      "PRICE": [999.99, 150.8, 2200.00],
      "ORDERDATE": ["28-11-2025", "02-11-2025", "01-11-2025"],
      "ID": ["35", "44", "104"],
      "COSTCENTER": ["[PREDICT]", "Office Furniture", "Data Infrastructure"]
  },
  "data_schema": {
      "PRODUCT": {
          "dtype": "string"
      },
      "PRICE": {
          "dtype": "numeric"
      },
      "ORDERDATE": {
          "dtype": "date"
      },
      "ID": {
          "dtype": "string"
      },
      "COSTCENTER": {
          "dtype": "string"
      }
  }
}

class RPTRequestModels(unittest.TestCase):

    def test_prediction_config(self):
        expected_dict = {
            "target_columns": [
                {
                    "name": "COSTCENTER",
                    "prediction_placeholder": "[PREDICT]",
                    "task_type": "classification",
                    "top_k": None
                }
            ],
            "explanations": None,
            "context_mode": None
        }
        prediction_config = PredictionConfig(target_columns=[
            TargetColumn(name="COSTCENTER", prediction_placeholder="[PREDICT]", task_type="classification")
        ])

        assert prediction_config.model_dump() == expected_dict

    def test_rpt_request_by_rows_from_dict(self):

        request = RPTRequest.model_validate(request_by_row_dict)
        assert request.prediction_config.target_columns[0].name == "COSTCENTER"
        assert request.rows[0]["COSTCENTER"] == "[PREDICT]"
        assert "columns" not in request.model_dump()

    def test_rpt_request_by_columns_from_dict(self):
        request = RPTRequest.model_validate(request_by_columns_dict)
        assert request.prediction_config.target_columns[0].name == "COSTCENTER"
        assert request.columns["COSTCENTER"][0] == "[PREDICT]"
        assert "rows" not in request.model_dump()

    def test_prediction_item_confidence_valid_boundaries(self):
        item_low = PredictionItem(prediction="cat", confidence=0.0)
        item_high = PredictionItem(prediction="cat", confidence=1.0)
        self.assertEqual(item_low.confidence, 0.0)
        self.assertEqual(item_high.confidence, 1.0)

    def test_prediction_item_confidence_valid_midrange(self):
        item = PredictionItem(prediction="cat", confidence=0.85)
        self.assertEqual(item.confidence, 0.85)

    def test_prediction_item_confidence_none(self):
        item = PredictionItem(prediction=3.14)
        self.assertIsNone(item.confidence)

    def test_prediction_item_confidence_above_max(self):
        with self.assertRaises(ValueError):
            PredictionItem(prediction="cat", confidence=1.1)

    def test_prediction_item_confidence_below_min(self):
        with self.assertRaises(ValueError):
            PredictionItem(prediction="cat", confidence=-0.1)


    def test_target_column_top_k(self):
        tc = TargetColumn(name="CATEGORY", prediction_placeholder="[PREDICT]", task_type="classification", top_k=3)
        self.assertEqual(tc.top_k, 3)
        self.assertEqual(tc.model_dump()["top_k"], 3)

    def test_target_column_top_k_default_none(self):
        tc = TargetColumn(name="CATEGORY", prediction_placeholder="[PREDICT]", task_type="classification")
        self.assertIsNone(tc.top_k)

    def test_prediction_item_confidence_interval_regression(self):
        item = PredictionItem(prediction=195.09, confidence_interval=[191.42, 198.76])
        self.assertEqual(item.confidence_interval, [191.42, 198.76])
        self.assertIsNone(item.confidence)

    def test_prediction_item_confidence_interval_none_for_classification(self):
        item = PredictionItem(prediction="Office Furniture", confidence=0.96, confidence_interval=None)
        self.assertIsNone(item.confidence_interval)
        self.assertEqual(item.confidence, 0.96)

    def test_explanation_config_defaults(self):
        config = ExplanationConfig()
        self.assertEqual(config.top_column_scores, 0)
        self.assertEqual(config.top_relevant_context_rows, 0)

    def test_explanation_config_custom_values(self):
        config = ExplanationConfig(top_column_scores=5, top_relevant_context_rows=3)
        self.assertEqual(config.top_column_scores, 5)
        self.assertEqual(config.top_relevant_context_rows, 3)

    def test_explanation_result_deserialization(self):
        data = {
            "top_column_scores": [{"PRODUCT": 0.523, "PRICE": 0.234, "ORDERDATE": 0.121}],
            "top_relevant_context_rows": [[1, 2]]
        }
        result = ExplanationResult(**data)
        self.assertEqual(result.top_column_scores[0]["PRODUCT"], 0.523)
        self.assertEqual(result.top_relevant_context_rows[0], [1, 2])

    def test_explanation_result_nullable_fields(self):
        result = ExplanationResult(top_column_scores=None, top_relevant_context_rows=None)
        self.assertIsNone(result.top_column_scores)
        self.assertIsNone(result.top_relevant_context_rows)

    def test_response_without_explanations(self):
        response = RPTResponse(**RPT_RESPONSE_CODE_0)
        self.assertIsNone(response.explanations)
        self.assertEqual(response.predictions[0]["COSTCENTER"][0].prediction, "Office Furniture")
        self.assertEqual(response.predictions[0]["COSTCENTER"][0].confidence, 0.96)
        self.assertIsNone(response.predictions[0]["COSTCENTER"][0].confidence_interval)

    def test_response_with_explanations(self):
        response = RPTResponse(**RPT_RESPONSE_CODE_0_WITH_EXPLANATIONS)
        self.assertIsNotNone(response.explanations)
        self.assertEqual(response.explanations.top_column_scores[0]["PRODUCT"], 0.523)
        self.assertEqual(response.explanations.top_relevant_context_rows[0], [1, 2])

    def test_response_classification_prediction(self):
        response = RPTResponse(**RPT_RESPONSE_CODE_0)
        costcenter_predictions = response.predictions[0]["COSTCENTER"]
        self.assertEqual(costcenter_predictions[0].prediction, "Office Furniture")
        self.assertEqual(costcenter_predictions[0].confidence, 0.96)
        self.assertIsNone(costcenter_predictions[0].confidence_interval)

    def test_rpt_request_omits_context_mode_when_not_set(self):
        request = RPTRequest.model_validate(request_by_row_dict)
        self.assertNotIn("context_mode", request.model_dump()["prediction_config"])

    def test_rpt_request_includes_context_mode_when_set(self):
        request = RPTRequest(
            prediction_config=PredictionConfig(
                target_columns=[TargetColumn(name="COSTCENTER", prediction_placeholder="[PREDICT]", task_type="classification")],
                context_mode="deep"
            ),
            rows=request_by_row_dict["rows"]
        )
        self.assertEqual(request.model_dump()["prediction_config"]["context_mode"], "deep")

    def test_rpt_request_columns_and_rows_provided(self):
        with self.assertRaises(ValueError) as err:
            RPTRequest(
                prediction_config=request_by_row_dict["prediction_config"],
                columns=request_by_columns_dict["columns"],
                rows=request_by_row_dict["rows"]
            )
            assert "Exactly one of 'rows' or 'columns' must be provided." in str(err.exception)

class RPTClientTests(unittest.TestCase):

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='testopenaiclient')
        self.client = RPTClient(proxy_client=self.proxy_client)

    def test_request_with_response_code_0(self):
        with patch.object(RPTClient, "_get_url", return_value=mock_url) as url_mock:
            with sap_rpt_mock_response_code_0(url_mock.return_value):
                response = self.client.predict(body=request_by_row_dict, model_name="sap-rpt-1.6")
                self.assertIsInstance(response, RPTResponse)
                self.assertEqual(response.status.code, 0)
                self.assertEqual(response.predictions[0]["COSTCENTER"][0].prediction, "Office Furniture")
                self.assertIsNotNone(response.explanations)
                self.assertEqual(response.metadata.num_columns, 5)
                self.assertEqual(response.metadata.num_predictions, 1)

    def test_request_with_response_code_0_request_by_api_url(self):
        with sap_rpt_mock_response_code_0(mock_url):
            response = self.client.predict(body=request_by_row_dict, deployment_url=mock_url)
            self.assertIsInstance(response, RPTResponse)
            self.assertEqual(response.status.code, 0)
            self.assertEqual(response.id, "c334f854-0d70-4c79-bd73-9ac581fd8cda")


    def test_request_with_response_code_2(self):
        with patch.object(RPTClient, "_get_url", return_value=mock_url) as url_mock:
            with sap_rpt_mock_response_code_2(url_mock.return_value):
                with self.assertRaises(RPTException) as err:
                    self.client.predict(body=request_by_row_dict, model_name="sap-rpt-1.6")
                    self.assertEqual(err.exception.status.code, 2)
                    self.assertIsNotNone(err.exception.detail)

    def test_request_with_invalid_body(self):
        with self.assertRaises(ValueError):
            self.client.predict(body={}, model_name="sap-rpt-1.6")

    def test_request_without_model_name_api_url_and_kwargs(self):
        with self.assertRaises(ValueError):
            self.client.predict(body=request_by_row_dict)

    def test_timeout_determination(self):
        self.assertEqual(self.client._determine_timeout(10), 10)

class RPTClientAsyncTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='testopenaiclient')
        self.client = RPTClient(proxy_client=self.proxy_client)

    async def test_async_request_with_response_code_0(self):
        with patch.object(RPTClient, "_get_url", return_value=mock_url) as url_mock:
            with sap_rpt_mock_response_code_0(url_mock.return_value):
                response = await self.client.apredict(body=request_by_row_dict, model_name="sap-rpt-1.6")
                self.assertIsInstance(response, RPTResponse)
                self.assertEqual(response.status.code, 0)
                self.assertEqual(response.predictions[0]["COSTCENTER"][0].prediction, "Office Furniture")
                self.assertIsNotNone(response.explanations)
                self.assertEqual(response.metadata.num_columns, 5)
                self.assertEqual(response.metadata.num_predictions, 1)

    async def test_async_request_with_response_code_2(self):
        with patch.object(RPTClient, "_get_url", return_value=mock_url) as url_mock:
            with sap_rpt_mock_response_code_2(url_mock.return_value):
                with self.assertRaises(RPTException) as err:
                    await self.client.apredict(body=request_by_row_dict, model_name="sap-rpt-1.6")
                    self.assertEqual(err.exception.status.code, 2)
                    self.assertIsNotNone(err.exception.detail)

def test_flat_import_sap_rpt_client():
    # here inline import is OK
    from gen_ai_hub.proxy.native.sap.client import RPTClient as client
    from gen_ai_hub.proxy.native.sap import RPTClient as client_flat
    assert client == client_flat
