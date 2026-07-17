from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.resource_clients.kpi_client import KpiClient


class TestKpiClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = KpiClient(self.rest_client_mock)
        self.url_prefix = "/analytics/kpis"

    @staticmethod
    def get_kpi_response():
        return {
            "header": [
                "ResourceGroup",
                "Executions",
                "Artifacts",
                "Deployments"
            ],
            "rows": [
                [
                    "00112233-4455-6677-8899-aabbccddeeff",
                    30,
                    30,
                    3
                ]
            ]
        }

    def test_get_kpi(self):
        kpi_data = self.get_kpi_response()
        self.rest_client_mock.get.return_value = kpi_data
        kpi_response = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=f'{self.url_prefix}')
        self.assert_object(kpi_data, kpi_response)
        self.assertIn("KPIs header(s): ", kpi_response.__str__())
        self.assertIn(", ".join(kpi_data['header']), kpi_response.__str__())
