import os
from unittest import TestCase
from typing import Any, Dict

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.credentials import CORE_CREDENTIAL_VALUES
from ai_core_sdk.helpers.constants import AI_CORE_PREFIX
from ai_core_sdk.tracking import Tracking
from . import AUTH_URL, BASE_URL, CLIENT_ID, CLIENT_SECRET, RESOURCE_GROUP_ID, get_random_string


class AICoreV2ClientE2ETestBase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Uncomment the following line and the one in tearDownClass to run integration_tests via IDE
        # provision_resource_group()
        cls.remove_existing_aicore_env_vars()
        cls.ai_core_v2_client = AICoreV2Client(base_url=BASE_URL, auth_url=AUTH_URL, client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET, resource_group=RESOURCE_GROUP_ID)
        cls.tracking_client = Tracking(base_url=BASE_URL, auth_url=AUTH_URL, client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET, resource_group=RESOURCE_GROUP_ID)
        cls.test_scenario_id = '88888888-4444-4444-4444-cccccccccccc'

    @classmethod
    def tearDownClass(cls) -> None:
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE
        # deprovision_resource_group()
        super().tearDownClass()

    @staticmethod
    def remove_existing_aicore_env_vars():
        for cred_value in CORE_CREDENTIAL_VALUES:
            config_name = f'{AI_CORE_PREFIX}_{cred_value.name.upper()}'
            if config_name in os.environ.keys():
                del os.environ[config_name]

    def assert_object(self, d: Dict[str, Any], o: object):
        for k in d.keys():
            self.assertEqual(d[k], getattr(o, k))

    @staticmethod
    def _get_repo_dict():
        return {
            "name": f"test-repo-{get_random_string()}",
            "url": f"https://non.existent/bla/bla/{get_random_string()}",
            "username": "test_username",
            "password": "test_password"
        }
