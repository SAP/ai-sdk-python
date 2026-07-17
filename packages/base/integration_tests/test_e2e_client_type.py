import os
from unittest.mock import patch

from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client
from integration_tests.ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EClientType(AIAPIV2ClientE2ETestBase):

    auth_url = os.getenv('XSUAA_AUTH_URL')
    client_id = os.getenv('XSUAA_CLIENT_ID')
    client_secret = os.getenv('XSUAA_CLIENT_SECRET')
    cluster_base_url = os.getenv('CLUSTER_BASE_URL')
    base_url = f"{cluster_base_url}/v2/lm"
    resource_group = "resource_group_for_client_type_test"

    def test_client_type_from_parameter(self):
        client_type = 'test_client_type'
        ai_api_v2_client = AIAPIV2Client(
            base_url=self.base_url,
            auth_url=self.auth_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            resource_group=self.resource_group,
            client_type=client_type
        )
        rest_client = ai_api_v2_client.rest_client
        headers = rest_client.headers
        self.assertEqual(client_type, headers['AI-Client-Type'])

    def test_client_type_from_env_var(self):
        backup = os.environ.get('AI_CLIENT_TYPE', None)
        try:
            env_client_type = 'env_client_type'
            os.environ['AI_CLIENT_TYPE'] = env_client_type
            ai_api_v2_client = AIAPIV2Client(
                base_url=self.base_url,
                auth_url=self.auth_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                resource_group=self.resource_group
            )
            rest_client = ai_api_v2_client.rest_client
            headers = rest_client.headers
            self.assertEqual(env_client_type, headers['AI-Client-Type'])
        finally:
            if backup is not None:
                os.environ['AI_CLIENT_TYPE'] = backup
            else:
                del os.environ['AI_CLIENT_TYPE']
