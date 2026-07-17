from typing import List

from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client
from ai_api_client_sdk.models.scenario import Scenario
from . import (BASE_URL, CLIENT_ID, RESOURCE_GROUP_ID, X509_CERT_URL, X509_CERT_FILE_PATH, X509_KEY_FILE_PATH,
               X509_CERT_STR, X509_KEY_STR)
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EX509Credentials(AIAPIV2ClientE2ETestBase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE
        # write_x509_credentials_into_files()
        cls.ai_api_v2_client = AIAPIV2Client(base_url=BASE_URL, auth_url=X509_CERT_URL, client_id=CLIENT_ID,
                                             cert_file_path=X509_CERT_FILE_PATH, key_file_path=X509_KEY_FILE_PATH,
                                             resource_group=RESOURCE_GROUP_ID)

    @classmethod
    def tearDownClass(cls) -> None:
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE
        # remove_x509_credentials()
        super().tearDownClass()

    @staticmethod
    def _get_scenario_from_scenarios(scenarios: List[Scenario], scenario_id: str):
        for s in scenarios:
            if s.id == scenario_id:
                return s
        return None

    def _query_and_assert_scenarios(self, client: AIAPIV2Client):
        response = client.scenario.query()
        scenarios = response.resources
        self.assertEqual(response.count, len(scenarios))
        queried_scenario = self._get_scenario_from_scenarios(scenarios, self.test_scenario_id)
        scenario = client.scenario.get(scenario_id=self.test_scenario_id)
        self.assertEqual(queried_scenario, scenario)
        self.assertIsNotNone(scenario.id)
        self.assertIsNotNone(scenario.name)
        self.assert_datetime(scenario.created_at)
        self.assert_datetime(scenario.modified_at)

    def test_query_and_get_scenarios(self):
        self._query_and_assert_scenarios(self.ai_api_v2_client)

    def test_with_x509_str(self):
        client = AIAPIV2Client(base_url=BASE_URL, auth_url=X509_CERT_URL, client_id=CLIENT_ID, cert_str=X509_CERT_STR,
                               key_str=X509_KEY_STR, resource_group=RESOURCE_GROUP_ID)
        self._query_and_assert_scenarios(client)
