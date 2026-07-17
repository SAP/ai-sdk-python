from typing import List

from . import get_random_string
from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.models.object_store_secret import ObjectStoreSecret


class TestE2EObjectStoreSecrets(AICoreV2ClientE2ETestBase):

    @staticmethod
    def _get_object_store_secret_data():
        return {
            'name': f'test-{get_random_string()}',
            'type': 'S3',
            'bucket': f'{get_random_string()}-bucket',
            'endpoint': f's3-{get_random_string()}.com',
            'pathPrefix': get_random_string(),
            'verifyssl': '0',
            'usehttps': '1',
            'region': 'eu-central-1',
            'data': {
                "AWS_ACCESS_KEY_ID": get_random_string(),
                "AWS_SECRET_ACCESS_KEY": get_random_string()
            }
        }

    @staticmethod
    def _is_name_in_secrets(name: str, secrets: List[ObjectStoreSecret]):
        for oss in secrets:
            if name == oss.name:
                return True
        return False

    def _validate_data(self, oss_dict: dict, response_oss: ObjectStoreSecret):
        STORAGE_PREFIX = 'storage.ai.sap.com/'
        SERVING_KUBEFLOW_PREFIX = 'serving.kubeflow.org/'
        self.assertEqual(oss_dict['name'], response_oss.name)
        self.assertEqual(oss_dict['type'], response_oss.metadata[f'{STORAGE_PREFIX}type'])
        self.assertEqual(oss_dict['bucket'], response_oss.metadata[f'{STORAGE_PREFIX}bucket'])
        self.assertEqual(oss_dict['endpoint'], response_oss.metadata[f'{STORAGE_PREFIX}endpoint'])
        self.assertEqual(oss_dict['region'], response_oss.metadata[f'{STORAGE_PREFIX}region'])
        self.assertEqual(oss_dict['pathPrefix'], response_oss.metadata[f'{STORAGE_PREFIX}pathPrefix'])
        self.assertEqual(oss_dict['endpoint'], response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-endpoint'])
        self.assertEqual(oss_dict['region'], response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-region'])
        self.assertEqual(oss_dict['usehttps'], response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-usehttps'])
        self.assertEqual(oss_dict['verifyssl'], response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-verifyssl'])

    def test_object_store_secrets(self):
        STORAGE_PREFIX = 'storage.ai.sap.com/'
        SERVING_KUBEFLOW_PREFIX = 'serving.kubeflow.org/'
        oss_dict = self._get_object_store_secret_data()
        response = self.ai_core_v2_client.object_store_secrets.create(name=oss_dict['name'],
                                                                      type=oss_dict['type'],
                                                                      bucket=oss_dict['bucket'],
                                                                      endpoint=oss_dict['endpoint'],
                                                                      path_prefix=oss_dict['pathPrefix'],
                                                                      verifyssl=oss_dict['verifyssl'],
                                                                      usehttps=oss_dict['usehttps'],
                                                                      region=oss_dict['region'],
                                                                      data=oss_dict['data'])
        self.assertIsNotNone(response.message)

        oss = self.ai_core_v2_client.object_store_secrets.get(name=oss_dict['name'])
        #validating created data
        self._validate_data(oss_dict, oss)

        os_secrets = self.ai_core_v2_client.object_store_secrets.query()
        self.assertIsNotNone(os_secrets.resources)
        self.assertTrue(os_secrets.count >= 1)
        self.assertTrue(self._is_name_in_secrets(oss_dict['name'], os_secrets.resources))
        n = os_secrets.count

        os_secrets_top = self.ai_core_v2_client.object_store_secrets.query(top=2)
        self.assertTrue(1 <= len(os_secrets_top.resources) <= 2)

        os_secrets_skip = self.ai_core_v2_client.object_store_secrets.query(skip=1)
        self.assertEqual(n-1, len(os_secrets_skip.resources))

        patch_data = {"AWS_ACCESS_KEY_ID": get_random_string(), "AWS_SECRET_ACCESS_KEY": get_random_string()}
        response = self.ai_core_v2_client.object_store_secrets.modify(name=oss_dict['name'], 
                                                                      type=oss_dict['type'], 
                                                                      bucket=oss_dict['bucket'],
                                                                      endpoint=oss_dict['endpoint'],
                                                                      path_prefix=oss_dict['pathPrefix'],
                                                                      region=oss_dict['region'],
                                                                      data=patch_data)

        self.assertEqual(oss_dict['name'], response.id)
        self.assertIsNotNone(response.message)

        oss = self.ai_core_v2_client.object_store_secrets.get(name=oss_dict['name'])
        
        # validating modified data
        self._validate_data(oss_dict, oss)

        response = self.ai_core_v2_client.object_store_secrets.delete(name=oss_dict['name'])
        self.assertEqual(oss_dict['name'], response.id)
        self.assertIsNotNone(response.message)
