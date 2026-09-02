import unittest
from unittest.mock import patch

from gen_ai_hub.proxy.native.sap.models import RPTRequest, PredictionConfig, TargetColumn, RPTResponse, RPTException
from gen_ai_hub.proxy.native.sap.client import RPTClient
from tests.mock import get_mocked_ai_core_client, sap_rpt_moke_response_code_0, sap_rpt_moke_response_code_2

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
                "task_type": "classification"
            }]
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
            with sap_rpt_moke_response_code_0(url_mock.return_value):
                response = self.client.predict(body=request_by_row_dict, model_name="sap-rpt-1-small")
                self.assertIsInstance(response, RPTResponse)
                self.assertEqual(response.status.code, 0)
                self.assertEqual(response.predictions[0]["COSTCENTER"][0].prediction, "Office Furniture")
                self.assertEqual(response.metadata.num_columns,5)
                self.assertEqual(response.metadata.num_predictions,1)

    def test_request_with_response_code_0_request_by_api_url(self):
        with sap_rpt_moke_response_code_0(mock_url):
            response = self.client.predict(body=request_by_row_dict, deployment_url=mock_url)
            self.assertIsInstance(response, RPTResponse)
            self.assertEqual(response.status.code, 0)
            self.assertEqual(response.id, "c334f854-0d70-4c79-bd73-9ac581fd8cda")


    def test_request_with_response_code_2(self):
        with patch.object(RPTClient, "_get_url", return_value=mock_url) as url_mock:
            with sap_rpt_moke_response_code_2(url_mock.return_value):
                with self.assertRaises(RPTException) as err:
                    self.client.predict(body=request_by_row_dict, model_name="sap-rpt-1-small")
                    self.assertEqual(err.exception.status.code, 2)
                    self.assertIsNotNone(err.exception.detail)

    def test_request_with_invalid_body(self):
        with self.assertRaises(ValueError):
            self.client.predict(body={}, model_name="sap-rpt-1-small")

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
            with sap_rpt_moke_response_code_0(url_mock.return_value):
                response = await self.client.apredict(body=request_by_row_dict, model_name="sap-rpt-1-small")
                self.assertIsInstance(response, RPTResponse)
                self.assertEqual(response.status.code, 0)
                self.assertEqual(response.predictions[0]["COSTCENTER"][0].prediction, "Office Furniture")
                self.assertEqual(response.metadata.num_columns,5)
                self.assertEqual(response.metadata.num_predictions,1)

    async def test_async_request_with_response_code_2(self):
        with patch.object(RPTClient, "_get_url", return_value=mock_url) as url_mock:
            with sap_rpt_moke_response_code_2(url_mock.return_value):
                with self.assertRaises(RPTException) as err:
                    await self.client.apredict(body=request_by_row_dict, model_name="sap-rpt-1-small")
                    self.assertEqual(err.exception.status.code, 2)
                    self.assertIsNotNone(err.exception.detail)

def test_flat_import_sap_rpt_client():
    from gen_ai_hub.proxy.native.sap.client import RPTClient as client
    from gen_ai_hub.proxy.native.sap import RPTClient as client_flat
    assert client == client_flat
