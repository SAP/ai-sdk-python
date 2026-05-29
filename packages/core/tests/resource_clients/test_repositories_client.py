from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.models.repository import Repository
from ai_core_sdk.models.repository_status import RepositoryStatus
from ai_core_sdk.resource_clients.repositories_client import RepositoriesClient


class TestRepositoriesClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = RepositoriesClient(self.rest_client_mock)
        self.repo_path = '/admin/repositories'

    def assert_repository(self, repo_dict: dict, repo: Repository):
        self.assertEqual(repo_dict['name'], repo.name)
        self.assertEqual(repo_dict['url'], repo.url)
        if 'status' in repo_dict:
            self.assertEqual(repo_dict['status'], repo.status.value)

    @staticmethod
    def create_repository_dict():
        return {
            'name': 'test_repo_name',
            'url': 'test_repo_url',
            'username': 'test_username',
            'password': 'test_password'
        }

    @staticmethod
    def create_repo_status_dict():
        return {
            'name': 'test_repo_name',
            'url': 'test_repo_url',
            'status': RepositoryStatus.IN_PROGRESS.value
        }

    def test_create_repository(self):
        repo_dict = self.create_repository_dict()
        response_message = 'Repository has been on-boarded'
        self.rest_client_mock.post.return_value = {'message': response_message}
        response = self.client.create(name=repo_dict['name'], url=repo_dict['url'],  username=repo_dict['username'],
                                      password=repo_dict['password'])
        self.rest_client_mock.post.assert_called_with(path=self.repo_path, body=repo_dict)
        self.assertEqual(response_message, response.message)

    def test_delete_repository(self):
        test_repo_name = 'test_repo_name'
        response_dict = {'id': test_repo_name, 'message': 'Repo deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        response = self.client.delete(name=test_repo_name)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.repo_path}/{test_repo_name}')
        self.assertEqual(test_repo_name, response.id)
        self.assertEqual(response_dict['message'], response.message)
        
    def test_get_repository(self):
        repo_dict = self.create_repo_status_dict()
        self.rest_client_mock.get.return_value = repo_dict.copy()
        repo = self.client.get(name=repo_dict['name'])
        self.rest_client_mock.get.assert_called_with(path=f'{self.repo_path}/{repo_dict["name"]}')
        self.assert_repository(repo_dict, repo)
        self.assertIn("Repository name: ", repo.__str__())
        self.assertIn(repo_dict['name'], repo.__str__())
        self.assertIn("Repository url: ", repo.__str__())
        self.assertIn(repo_dict['url'], repo.__str__())

    def test_get_repository_bare_minimum(self):
        repo_dict = self.create_repo_status_dict()
        del repo_dict['status']
        self.rest_client_mock.get.return_value = repo_dict.copy()
        repo = self.client.get(name=repo_dict['name'])
        self.rest_client_mock.get.assert_called_with(path=f'{self.repo_path}/{repo_dict["name"]}')
        self.assert_repository(repo_dict, repo)

    def test_modify_repository(self):
        repo_dict = self.create_repository_dict()
        response_dict = {'id': repo_dict['name'], 'message': 'Repo has been modified'}
        body = {'username': repo_dict['username'], 'password': repo_dict['password']}
        self.rest_client_mock.patch.return_value = response_dict
        response = self.client.modify(name=repo_dict['name'], **body)
        self.rest_client_mock.patch.assert_called_with(path=f'{self.repo_path}/{repo_dict["name"]}', body=body)
        self.assertEqual(repo_dict['name'], response.id)
        self.assertEqual(response_dict['message'], response.message)
        
    def test_query_repository(self):
        n = 3
        repo_dicts = [self.create_repo_status_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [rd.copy() for rd in repo_dicts], 'count': n}
        repo_qr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=self.repo_path)
        self.assert_object_lists(repo_dicts, repo_qr.resources, sort_key='name',
                                 assert_object_function=self.assert_repository)


