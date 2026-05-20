from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.models.docker_registry_secret import DockerRegistrySecret
from ai_core_sdk.resource_clients.docker_registry_secrets_client import DockerRegistrySecretsClient


class TestDockerRegistrySecretsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = DockerRegistrySecretsClient(self.rest_client_mock)
        self.drs_path = '/admin/dockerRegistrySecrets'

    def assert_docker_registry_secret(self, drs_dict: dict, drs: DockerRegistrySecret):
        self.assertEqual(drs_dict['name'], drs.name)
        self.assertIn("DockerRegistrySecret name: ", drs.__str__())
        self.assertIn(drs_dict['name'], drs.__str__())

    @staticmethod
    def create_docker_registry_secret_dict():
        return {
            'name': 'test_docker_registry_secret_name',
            'data': {
                ".dockerconfigjson": "{\"auths\": {\"test_docker_registry_url\": {\"username\": \"test_docker_username\", \"password\": \"test_docker_password\"}}}"
            }
        }

    def test_get_docker_registry_secret(self):
        drs_dict = self.create_docker_registry_secret_dict()
        self.rest_client_mock.get.return_value = drs_dict.copy()
        drs = self.client.get(name=drs_dict['name'])
        self.rest_client_mock.get.assert_called_with(path=f'{self.drs_path}/{drs_dict["name"]}')
        self.assertEqual(drs_dict['name'], drs.name)

    def test_query_docker_registry_secrets(self):
        n = 3
        drs_dicts = [self.create_docker_registry_secret_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [dd.copy() for dd in drs_dicts], 'count': n}
        drs_qr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=self.drs_path, params=None)
        self.assert_object_lists(drs_dicts, drs_qr.resources, sort_key='name',
                                 assert_object_function=self.assert_docker_registry_secret)

        params = {'top': 5, 'skip': 1}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(**params)
        params['$top'] = params['top']
        del params['top']
        params['$skip'] = params['skip']
        del params['skip']
        self.rest_client_mock.get.assert_called_with(path=self.drs_path, params=params)

    def test_create_docker_registry_secret(self):
        drs_dict = self.create_docker_registry_secret_dict()
        response_message = 'secret has been been created'
        self.rest_client_mock.post.return_value = {'message': response_message}
        response = self.client.create(name=drs_dict['name'], data=drs_dict['data'])
        body = {'name': drs_dict['name'], 'data': drs_dict['data']}
        self.rest_client_mock.post.assert_called_with(path=self.drs_path, body=body)
        self.assertEqual(response_message, response.message)

    def test_modify_deployment(self):
        drs_dict = self.create_docker_registry_secret_dict()
        response_dict = {'id': drs_dict['name'], 'message': 'Secret has been modified'}
        body = {'data': drs_dict['data']}
        self.rest_client_mock.patch.return_value = response_dict
        br = self.client.modify(name=drs_dict['name'], **body)
        self.rest_client_mock.patch.assert_called_with(path=f'{self.drs_path}/{drs_dict["name"]}', body=body)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_delete_deployment(self):
        test_drs_name = 'test_docker_registry_secret_name'
        response_dict = {'id': test_drs_name, 'message': 'Deployment deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(name=test_drs_name)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.drs_path}/{test_drs_name}')
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)
