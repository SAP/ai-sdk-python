from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.models.secret import Secret
from ai_core_sdk.resource_clients.secrets_client import SecretsClient


class TestSecretsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = SecretsClient(self.rest_client_mock)
        self.url_prefix = "/admin/secrets"

    def assert_secret(self, secret_dict: dict, response_secret: Secret):
        self.assertEqual(secret_dict['name'], response_secret.name)
        self.assertEqual(secret_dict['data'], response_secret.data)

    @staticmethod
    def create_secret_dict():
        return {
            'name': 'test_secret_name',
            'data': {
                "AWS_ACCESS_KEY_ID": "test",
                "AWS_SECRET_ACCESS_KEY": "test"
            }
        }

    @staticmethod
    def get_secret_response():
        return {
            'name': 'test_secret_name',
            'data': {
                "AWS_ACCESS_KEY_ID": "test",
                "AWS_SECRET_ACCESS_KEY": "test"
            },
        }

    def test_query_secrets(self):
        n = 3
        secret_dicts = [self.create_secret_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [self.get_secret_response() for secret in secret_dicts],
                                                  'count': n}
        secret_gr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=self.url_prefix, params=None,
                                                     headers={'AI-Tenant-Scope': 'true'}, resource_group=None)
        self.assert_object_lists(secret_dicts, secret_gr.resources, sort_key='name',
                                 assert_object_function=self.assert_secret)

        params = {'top': 5, 'skip': 1}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(**params, resource_group=self.resource_group)
        params['$top'] = params['top']
        del params['top']
        params['$skip'] = params['skip']
        del params['skip']
        self.rest_client_mock.get.assert_called_with(path=self.url_prefix, params=params,
                                                     resource_group=self.resource_group,
                                                     headers={'AI-Tenant-Scope': 'true'})

    def test_create_secret(self):
        secret_dict = self.create_secret_dict()
        response_message = 'secret has been been created'
        self.rest_client_mock.post.return_value = {'name': secret_dict['name'], 'message': response_message}
        secrets = self.client.create(name=secret_dict['name'], data=secret_dict['data'],
                                     resource_group=self.resource_group)
        body = {'name': secret_dict['name'], 'data': secret_dict['data']}
        self.rest_client_mock.post.assert_called_with(path=self.url_prefix, body=body,
                                                      resource_group=self.resource_group,
                                                      headers={'AI-Tenant-Scope': 'true'})
        self.assertEqual(response_message, secrets.message)

    def test_modify_secret(self):
        secret_dict = self.create_secret_dict()
        response_dict = {'message': 'Secret has been modified'}
        body = {'data': secret_dict['data']}
        self.rest_client_mock.patch.return_value = response_dict
        br = self.client.modify(name=secret_dict['name'], **body, resource_group=self.resource_group)
        self.rest_client_mock.patch.assert_called_with(path=f'{self.url_prefix}/{secret_dict["name"]}', body=body,
                                                       resource_group=self.resource_group,
                                                       headers={'AI-Tenant-Scope': 'true'})
        self.assertEqual(response_dict['message'], br.message)

    def test_delete_secret(self):
        test_secret_name = 'test_secret_name'
        response_dict = {'id': test_secret_name, 'message': 'The secret has been removed'}
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(name=test_secret_name, resource_group=self.resource_group)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.url_prefix}/{test_secret_name}',
                                                        resource_group=self.resource_group,
                                                        headers={'AI-Tenant-Scope': 'true'})
        self.assertEqual(response_dict['message'], br.message)
