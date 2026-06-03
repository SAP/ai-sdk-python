from unittest.mock import MagicMock

from ai_api_client_sdk.models.healthz_status import HealthStatus
from ai_api_client_sdk.resource_clients.healthz_client import HealthzClient
from .resource_client_test_base import ResourceClientTestBase


class TestHealthzClient(ResourceClientTestBase):
    @staticmethod
    def create_healthz_status_dict():
        return {
            "status": "READY",
            "message": "test_message"
        }

    def test_test(self):
        hs_dict = self.create_healthz_status_dict()
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = hs_dict.copy()
        hc = HealthzClient(rest_client_mock)
        hs = hc.get()
        rest_client_mock.get.assert_called_with(path='/healthz')
        self.assertEqual(hs_dict['message'], hs.message)
        self.assertEqual(HealthStatus(hs_dict['status']), hs.status)
        self.assertIn("Healthz status message: ", hs.__str__())
        self.assertIn(hs_dict['message'], hs.__str__())
