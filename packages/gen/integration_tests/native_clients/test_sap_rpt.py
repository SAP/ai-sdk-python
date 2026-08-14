import unittest

from integration_tests.constants import SAP_RPT_1_SMALL_TEST_MODEL
from integration_tests.setup_aicore import TestCaseStandardSetupMixin
from gen_ai_hub.proxy.native.sap.client import RPTClient
from gen_ai_hub.proxy.native.sap.models import RPTRequest, RPTResponse, PredictionConfig, TargetColumn

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

rows_regression = [
    {
        "PRODUCT": "Couch",
        "PRICE": 999.99,
        "ORDERDATE": "28-11-2025",
        "ID": "35",
        "DISCOUNT_RATE": "[PREDICT]",
    },
    {
        "PRODUCT": "Office Chair",
        "PRICE": 150.80,
        "ORDERDATE": "02-11-2025",
        "ID": "44",
        "DISCOUNT_RATE": 0.12,
    },
    {
        "PRODUCT": "Server Rack",
        "PRICE": 2200.00,
        "ORDERDATE": "01-11-2025",
        "ID": "104",
        "DISCOUNT_RATE": 0.05,
    },
    {
        "PRODUCT": "Standing Desk",
        "PRICE": 640.00,
        "ORDERDATE": "05-11-2025",
        "ID": "205",
        "DISCOUNT_RATE": 0.10,
    },
    {
        "PRODUCT": "Monitor 27 inch",
        "PRICE": 289.99,
        "ORDERDATE": "08-11-2025",
        "ID": "306",
        "DISCOUNT_RATE": "[PREDICT]",
    },
]

class RPTClientTests(TestCaseStandardSetupMixin, unittest.TestCase):

    def setUp(self) -> None:
        self.client = RPTClient(proxy_client=self.proxy_client)

    def test_client_find_url_by_model_name(self):
        url = self.client._get_url(model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        self.assertIsNotNone(url)

    def test_client_find_url_by_model_name_and_version(self):
        url = self.client._get_url(model_name=SAP_RPT_1_SMALL_TEST_MODEL, model_version="latest")
        self.assertIsNotNone(url)

    def test_client_find_url_by_config_name(self):
        url = self.client._get_url(config_name="sap-rpt-1-small-latest")
        self.assertIsNotNone(url)

    def test_client_find_url_with_invalid_model_name(self):
        with self.assertRaises(ValueError):
            self.client._get_url(model_name="invalid-model-name")

    def test_predict_by_row(self):
        body = RPTRequest(**request_by_row_dict)
        response = self.client.predict(body=body, model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        self.assertIsInstance(response, RPTResponse)
        self.assertEqual(response.status.code, 0)
        self.assertEqual(response.predictions[0]["ID"], "35")
        self.assertEqual(response.metadata.num_columns, 5)
        self.assertEqual(response.metadata.num_predictions, 1)
        self.assertIn("COSTCENTER", response.predictions[0].model_dump())

    def test_predict_by_columns(self):
        body = RPTRequest(**request_by_columns_dict)
        response = self.client.predict(body=body, model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        self.assertIsInstance(response, RPTResponse)
        self.assertEqual(response.status.code, 0)
        self.assertEqual(response.metadata.num_columns, 5)
        self.assertEqual(response.metadata.num_predictions, 1)
        self.assertIn("COSTCENTER", response.predictions[0].model_dump())
        self.assertNotIn("ID", response.predictions[0].model_dump())

    def test_predict_with_api_url(self):
        body = RPTRequest(**request_by_columns_dict)
        deployment_url = self.client._get_url(model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        response = self.client.predict(body=body, deployment_url=deployment_url)
        self.assertIsInstance(response, RPTResponse)
        self.assertEqual(response.status.code, 0)
        self.assertEqual(response.metadata.num_columns, 5)
        self.assertEqual(response.metadata.num_predictions, 1)
        self.assertIn("COSTCENTER", response.predictions[0].model_dump())

    def test_regression_prediction(self):
        body = RPTRequest(
            prediction_config=PredictionConfig(
                target_columns=[
                    TargetColumn(name="DISCOUNT_RATE", task_type="regression")
                ]),
            rows=rows_regression
        )
        response = self.client.predict(body=body, model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        self.assertIsInstance(response, RPTResponse)
        self.assertEqual(response.status.code, 0)
        self.assertEqual(response.metadata.num_predictions, 2)
        self.assertIn("DISCOUNT_RATE", response.predictions[0].model_dump())

    def test_timeout_error(self):
        body = RPTRequest(
            prediction_config=PredictionConfig(
                target_columns=[
                    TargetColumn(name="DISCOUNT_RATE", task_type="regression")
                ]),
            rows=rows_regression
        )

        with self.assertRaises(Exception):
            self.client.predict(body=body, model_name=SAP_RPT_1_SMALL_TEST_MODEL, timeout=0.001)


class AsyncRPTClientTests(TestCaseStandardSetupMixin, unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.client = RPTClient(proxy_client=self.proxy_client)

    async def test_apredict_by_row(self):
        body = RPTRequest(**request_by_row_dict)
        response = await self.client.apredict(body=body, model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        self.assertIsInstance(response, RPTResponse)
        self.assertEqual(response.status.code, 0)
        self.assertEqual(response.predictions[0]["ID"], "35")
        self.assertEqual(response.metadata.num_columns, 5)
        self.assertEqual(response.metadata.num_predictions, 1)
        self.assertIn("COSTCENTER", response.predictions[0].model_dump())

    async def test_apredict_by_columns(self):
        body = RPTRequest(**request_by_columns_dict)
        response = await self.client.apredict(body=body, model_name=SAP_RPT_1_SMALL_TEST_MODEL)
        self.assertIsInstance(response, RPTResponse)
        self.assertEqual(response.status.code, 0)
        self.assertEqual(response.metadata.num_columns, 5)
        self.assertEqual(response.metadata.num_predictions, 1)
        self.assertIn("COSTCENTER", response.predictions[0].model_dump())
        self.assertNotIn("ID", response.predictions[0].model_dump())
