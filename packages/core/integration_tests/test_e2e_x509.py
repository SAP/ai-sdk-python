import json
import os
import tempfile
from typing import List
from unittest.mock import patch

from . import (BASE_URL, CLIENT_ID, RESOURCE_GROUP_ID, X509_CERT_URL, X509_CERT_FILE_PATH, X509_KEY_FILE_PATH,
               X509_CERT_STR, X509_KEY_STR)
from . import write_x509_credentials_into_files, remove_x509_credentials
from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.helpers.constants import (AI_CORE_PREFIX, HOME_PATH_ENV_VAR, VCAP_AICORE_SERVICE_NAME,
                                           VCAP_SERVICES_ENV_VAR)
from ai_core_sdk.models import Scenario


VCAP_SERVICE_X509_DICT = {
    VCAP_AICORE_SERVICE_NAME: [{
        'label': VCAP_AICORE_SERVICE_NAME,
        'name': f'{VCAP_AICORE_SERVICE_NAME}-instance',
        'instance_guid': '53ad5b47-a49a-4fec-9f0b-cd921c00b828',
        'credentials': {
            'serviceurls': {
                'AI_API_URL': BASE_URL[:-3]
            },
            'certurl': X509_CERT_URL,
            'clientid': CLIENT_ID,
            'key': X509_KEY_STR.replace('\n', '\\n'),
            'certificate': X509_CERT_STR.replace('\n', '\\n')
        }
    }]
}
VCAP_SERVICE_X509_ENV_VALUE = json.dumps(VCAP_SERVICE_X509_DICT, indent=4)


class TestE2EX509(AICoreV2ClientE2ETestBase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE
        # write_x509_credentials_into_files()
        cls.valid_x509_config = {
            f'{AI_CORE_PREFIX}_CLIENT_ID': CLIENT_ID,
            f'{AI_CORE_PREFIX}_CERT_URL': X509_CERT_URL,
            f'{AI_CORE_PREFIX}_CERT_FILE_PATH': X509_CERT_FILE_PATH,
            f'{AI_CORE_PREFIX}_KEY_FILE_PATH': X509_KEY_FILE_PATH,
            f'{AI_CORE_PREFIX}_RESOURCE_GROUP': RESOURCE_GROUP_ID,
            f'{AI_CORE_PREFIX}_BASE_URL': BASE_URL
        }

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

    def _query_and_assert_scenarios(self, client: AICoreV2Client):
        response = client.scenario.query()
        scenarios = response.resources
        self.assertEqual(response.count, len(scenarios))
        queried_scenario = self._get_scenario_from_scenarios(scenarios, self.test_scenario_id)
        scenario = client.scenario.get(scenario_id=self.test_scenario_id)
        self.assertEqual(queried_scenario, scenario)
        self.assertIsNotNone(scenario.id)
        self.assertIsNotNone(scenario.name)

    @patch.dict(os.environ, {VCAP_SERVICES_ENV_VAR: VCAP_SERVICE_X509_ENV_VALUE, 'AICORE_RESOURCE_GROUP': RESOURCE_GROUP_ID})
    def test_x509_from_vcap(self):
        client = AICoreV2Client.from_env()
        self._query_and_assert_scenarios(client)

    def test_x509_from_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile = 'test'
            default_config_path = os.path.join(temp_dir, 'config.json')
            profile_config_path = os.path.join(temp_dir, f'config_{profile}.json')
            with open(default_config_path, 'w') as f:
                json.dump({}, f)
            with open(profile_config_path, 'w') as f:
                json.dump(self.valid_x509_config, f)
            with patch.dict(os.environ, {HOME_PATH_ENV_VAR: str(temp_dir)}):
                client = AICoreV2Client.from_env(profile_name=profile)
                self._query_and_assert_scenarios(client)


    def test_x509_file_path(self):
        client = AICoreV2Client(base_url=BASE_URL, auth_url=X509_CERT_URL, client_id=CLIENT_ID,
                                             cert_file_path=X509_CERT_FILE_PATH, key_file_path=X509_KEY_FILE_PATH,
                                             resource_group=RESOURCE_GROUP_ID)
        self._query_and_assert_scenarios(client)

    def test_x509_str(self):
        client = AICoreV2Client(base_url=BASE_URL, auth_url=X509_CERT_URL, client_id=CLIENT_ID, cert_str=X509_CERT_STR,
                               key_str=X509_KEY_STR, resource_group=RESOURCE_GROUP_ID)
        self._query_and_assert_scenarios(client)