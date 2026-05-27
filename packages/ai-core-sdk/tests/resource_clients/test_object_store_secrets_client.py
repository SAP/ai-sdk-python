from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.models.object_store_secret import ObjectStoreSecret
from ai_core_sdk.resource_clients.object_store_secrets_client import ObjectStoreSecretsClient


class TestObjectStoreSecretsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ObjectStoreSecretsClient(self.rest_client_mock)
        self.url_prefix = "/admin/objectStoreSecrets"

    def assert_object_store_secret(self, oss_dict: dict, response_oss: ObjectStoreSecret):
        STORAGE_PREFIX = 'storage.ai.sap.com/'
        SERVING_KUBEFLOW_PREFIX = 'serving.kubeflow.org/'
        self.assertEqual(oss_dict['name'], response_oss.name)
        self.assertEqual(oss_dict['name'], response_oss.name)
        self.assertEqual(oss_dict['type'], response_oss.metadata[f'{STORAGE_PREFIX}type'])
        self.assertEqual(oss_dict['bucket'], response_oss.metadata[f'{STORAGE_PREFIX}bucket'])
        self.assertEqual(oss_dict['endpoint'], response_oss.metadata[f'{STORAGE_PREFIX}endpoint'])
        self.assertEqual(oss_dict['region'], response_oss.metadata[f'{STORAGE_PREFIX}region'])
        self.assertEqual(oss_dict['pathPrefix'], response_oss.metadata[f'{STORAGE_PREFIX}pathPrefix'])
        self.assertEqual(oss_dict['endpoint'], response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-endpoint'])
        self.assertEqual(oss_dict['region'], response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-region'])
        self.assertEqual('1', response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-usehttps'])
        self.assertEqual('0', response_oss.metadata[f'{SERVING_KUBEFLOW_PREFIX}s3-verifyssl'])

    @staticmethod
    def create_object_store_secret_dict():
        return {
            'name': 'test_object_store_secret_name',
            'type': 's3',
            'bucket': 'test_bucket',
            'endpoint': 'www.example.com',
            'region': 'eu',
            'pathPrefix': 'my-api',
            'verifyssl': '0',
            'usehttps': '1',
            'data': {
                "AWS_ACCESS_KEY_ID": "test",
                "AWS_SECRET_ACCESS_KEY": "test"
            }
        }

    @staticmethod
    def get_object_store_secret_response():
        return {
            'name': 'test_object_store_secret_name',
            'metadata': {
                'serving.kubeflow.org/s3-usehttps': '1',
                'serving.kubeflow.org/s3-verifyssl': '0',
                'serving.kubeflow.org/s3-endpoint': 'www.example.com',
                'serving.kubeflow.org/s3-region': 'eu',
                'storage.ai.sap.com/type': 's3',
                'storage.ai.sap.com/bucket': 'test_bucket',
                'storage.ai.sap.com/endpoint': 'www.example.com',
                'storage.ai.sap.com/region': 'eu',
                'storage.ai.sap.com/pathPrefix': 'my-api'
            },
        }

    def test_get_object_store_secret(self):
        oss_dict = self.create_object_store_secret_dict()
        self.rest_client_mock.get.return_value = self.get_object_store_secret_response()
        oss = self.client.get(name=oss_dict['name'], resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'{self.url_prefix}/{oss_dict["name"]}',
                                                     resource_group=self.resource_group)
        self.assert_object_store_secret(oss_dict, oss)
        self.assertIn("Object store secret name: ", oss.__str__())
        self.assertIn(oss_dict['name'], oss.__str__())

    def test_query_object_store_secrets(self):
        n = 3
        oss_dicts = [self.create_object_store_secret_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [self.get_object_store_secret_response() for osd in oss_dicts], 'count': n}
        oss_qr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=self.url_prefix, params=None, resource_group=None)
        self.assert_object_lists(oss_dicts, oss_qr.resources, sort_key='name',
                                 assert_object_function=self.assert_object_store_secret)

        params = {'top': 5, 'skip': 1}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(**params, resource_group=self.resource_group)
        params['$top'] = params['top']
        del params['top']
        params['$skip'] = params['skip']
        del params['skip']
        self.rest_client_mock.get.assert_called_with(path=self.url_prefix, params=params,
                                                     resource_group=self.resource_group)

    def test_create_object_store_secret(self):
        oss_dict = self.create_object_store_secret_dict()
        response_message = 'secret has been been created'
        self.rest_client_mock.post.return_value = {'name': oss_dict['name'], 'message': response_message}
        oss = self.client.create(name=oss_dict['name'], type=oss_dict['type'], bucket=oss_dict['bucket'],
                                 endpoint=oss_dict['endpoint'], region=oss_dict['region'],
                                 path_prefix=oss_dict['pathPrefix'], verifyssl=oss_dict['verifyssl'],
                                 usehttps=oss_dict['usehttps'], data=oss_dict['data'],
                                 resource_group=self.resource_group)
        body = {'name': oss_dict['name'], 'type': oss_dict['type'], 'bucket': oss_dict['bucket'],
                'endpoint': oss_dict['endpoint'], 'region': oss_dict['region'], 'path_prefix': oss_dict['pathPrefix'],
                'verifyssl': oss_dict['verifyssl'], 'usehttps': oss_dict['usehttps'], 'data': oss_dict['data']}
        self.rest_client_mock.post.assert_called_with(path=self.url_prefix, body=body,
                                                      resource_group=self.resource_group)
        self.assertEqual(response_message, oss.message)

    def test_modify_deployment(self):
        oss_dict = self.create_object_store_secret_dict()
        response_dict = {'id': oss_dict['name'], 'message': 'Secret has been modified'}
        body = {'name': oss_dict['name'], 'type': oss_dict['type'], 'data': oss_dict['data']}
        self.rest_client_mock.patch.return_value = response_dict
        br = self.client.modify(**body, resource_group=self.resource_group)
        self.rest_client_mock.patch.assert_called_with(path=f'{self.url_prefix}/{oss_dict["name"]}', body=body,
                                                       resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_delete_deployment(self):
        test_oss_name = 'test_object_store_secret_name'
        response_dict = {'id': test_oss_name, 'message': 'Deployment deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(name=test_oss_name, resource_group=self.resource_group)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.url_prefix}/{test_oss_name}',
                                                        resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)
