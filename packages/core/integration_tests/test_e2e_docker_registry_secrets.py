from typing import List

from . import get_random_string
from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.models.docker_registry_secret import DockerRegistrySecret


class TestE2EDockerRegistrySecrets(AICoreV2ClientE2ETestBase):

    @staticmethod
    def _get_docker_registry_secret_data():
        return {
            'name': f'test-docker-registry-secret-{get_random_string()}',
            'data': {
                ".dockerconfigjson": "{\"auths\": {\"test_docker_registry_url\": {\"username\": \"test_docker_username\", \"password\": \"test_docker_password\"}}}"
            }
        }

    @staticmethod
    def _is_name_in_secrets(name: str, secrets: List[DockerRegistrySecret]):
        for drs in secrets:
            if name == drs.name:
                return True
        return False

    def test_docker_registry_secrets(self):
        drs_dict = self._get_docker_registry_secret_data()
        response = self.ai_core_v2_client.docker_registry_secrets.create(name=drs_dict['name'], data=drs_dict['data'])
        self.assertIsNotNone(response.message)

        drs = self.ai_core_v2_client.docker_registry_secrets.get(name=drs_dict['name'])
        self.assertEqual(drs_dict['name'], drs.name)

        dr_secrets = self.ai_core_v2_client.docker_registry_secrets.query()
        self.assertIsNotNone(dr_secrets.resources)
        self.assertTrue(dr_secrets.count >= 1)
        self.assertTrue(self._is_name_in_secrets(drs_dict['name'], dr_secrets.resources))
        n = dr_secrets.count

        dr_secrets_top = self.ai_core_v2_client.docker_registry_secrets.query(top=2)
        self.assertTrue(1 <= len(dr_secrets_top.resources) <= 2)

        dr_secrets_skip = self.ai_core_v2_client.docker_registry_secrets.query(skip=1)
        self.assertEqual(n-1, len(dr_secrets_skip.resources))

        patch_data = {".dockerconfigjson": "{\"auths\": {\"test_docker_registry_url\": {\"username\": \"test_docker_username2\", \"password\": \"test_docker_password\"}}}"}
        response = self.ai_core_v2_client.docker_registry_secrets.modify(name=drs_dict['name'], data=patch_data)
        self.assertEqual(drs_dict['name'], response.id)
        self.assertIsNotNone(response.message)

        response = self.ai_core_v2_client.docker_registry_secrets.delete(name=drs_dict['name'])
        self.assertEqual(drs_dict['name'], response.id)
        self.assertIsNotNone(response.message)
