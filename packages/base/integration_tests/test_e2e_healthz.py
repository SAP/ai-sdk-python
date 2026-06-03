from ai_api_client_sdk.models.healthz_status import HealthStatus
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EHealthz(AIAPIV2ClientE2ETestBase):
    def test_healthz(self):
        healthz_status = self.ai_api_v2_client.healthz.get()
        self.assertEqual(HealthStatus.READY, healthz_status.status)
        self.assertIsNotNone(healthz_status.message)
