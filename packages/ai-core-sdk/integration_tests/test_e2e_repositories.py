from typing import List

from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.models.repository import Repository


class TestE2ERepositories(AICoreV2ClientE2ETestBase):

    def assert_repo(self, repo_dict: dict, repo: Repository):
        self.assertEqual(repo_dict['name'], repo.name)
        self.assertEqual(repo_dict['url'], repo.url)
        self.assertIsNotNone(repo.status)

    def assert_repo_dict_in_repo_objects(self, repo_dict: dict, repos: List[Repository]):
        for repo in repos:
            if repo.name == repo_dict['name']:
                self.assert_repo(repo_dict, repo)
                return

    def test_repositories(self):
        # create
        repo_dict = self._get_repo_dict()
        response = self.ai_core_v2_client.repositories.create(**repo_dict)
        self.assertIsNotNone(response.message)

        # get
        repo = self.ai_core_v2_client.repositories.get(name=repo_dict['name'])
        self.assert_repo(repo_dict, repo)

        # query
        repo_qr = self.ai_core_v2_client.repositories.query()
        self.assertTrue(repo_qr.count >= 1)
        self.assert_repo_dict_in_repo_objects(repo_dict, repo_qr.resources)

        # modify
        repo_patch_dict = {
            'name': repo_dict['name'],
            'username': 'test-patch-username',
            'password': 'test-patch-password'
        }
        response = self.ai_core_v2_client.repositories.modify(**repo_patch_dict)
        self.assertEqual(repo_dict['name'], response.id)
        self.assertIsNotNone(response.message)

        # delete
        response = self.ai_core_v2_client.repositories.delete(name=repo_dict['name'])
        self.assertEqual(repo_dict['name'], response.id)
        self.assertIsNotNone(response.message)
