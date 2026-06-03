from typing import List

from . import get_random_string
from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.models.secret import Secret


class TestE2ESecrets(AICoreV2ClientE2ETestBase):

    @staticmethod
    def _get_secret_data():
        return {
            'name': f'test-{get_random_string()}',
            'data': {
                "prop1": get_random_string(),
                "prop2": get_random_string()
            }
        }

    @staticmethod
    def _is_name_in_secrets(name: str, secrets: List[Secret]):
        for secret in secrets:
            if name == secret.name:
                return True
        return False

    def test_secrets(self):
        secret_dict = self._get_secret_data()
        response = self.ai_core_v2_client.secrets.create(name=secret_dict['name'],
                                                         data=secret_dict['data'],
                                                         ai_tenant_scope=False)
        self.assertIsNotNone(response.message)

        secrets = self.ai_core_v2_client.secrets.query(ai_tenant_scope=False)
        self.assertIsNotNone(secrets.resources)
        self.assertTrue(secrets.count >= 1)
        self.assertTrue(self._is_name_in_secrets(secret_dict['name'], secrets.resources))
        n = secrets.count

        secrets_top = self.ai_core_v2_client.secrets.query(top=2, ai_tenant_scope=False)
        self.assertTrue(1 <= len(secrets_top.resources) <= 2)

        secrets_skip = self.ai_core_v2_client.secrets.query(skip=1, ai_tenant_scope=False)
        self.assertEqual(n-1, len(secrets_skip.resources))

        patch_data = {"prop1": get_random_string(), "prop2": get_random_string()}
        response = self.ai_core_v2_client.secrets.modify(name=secret_dict['name'],
                                                         data=patch_data,
                                                         ai_tenant_scope=False)

        self.assertEqual("The secret has been modified", response.message)

        response = self.ai_core_v2_client.secrets.delete(name=secret_dict['name'],
                                                         ai_tenant_scope=False)
        self.assertEqual("Secret has been deleted", response.message)

        secrets = self.ai_core_v2_client.secrets.query(ai_tenant_scope=False)
        deleted_secret = [secret for secret in secrets.resources if secret.name == secret_dict['name']]
        self.assertEqual(len(deleted_secret), 0)
