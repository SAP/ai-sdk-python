from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.models.kpi import Kpi


class TestE2EKpis(AICoreV2ClientE2ETestBase):

    def _validate_data(self, kpis_data: dict):
        self.assertIsInstance(kpis_data, Kpi)
        for row in kpis_data.rows:
            self.assertEqual(len(kpis_data.header), len(row))
    def test_kpis(self):
        kpis_data = self.ai_core_v2_client.kpis.query()
        #validating created data
        self._validate_data(kpis_data)
