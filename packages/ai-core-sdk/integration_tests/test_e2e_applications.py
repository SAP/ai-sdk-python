import copy
from typing import List

from . import get_random_string
from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase
from ai_core_sdk.models.application import Application
from ai_core_sdk.models.application_status import ApplicationStatus


class TestE2EApplications(AICoreV2ClientE2ETestBase):

    @classmethod
    def _create_repo(cls):
        cls.repo_dict = cls._get_repo_dict()
        cls.ai_core_v2_client.rest_client.post(path='/admin/repositories', body=cls.repo_dict)

    @classmethod
    def _delete_repo(cls):
        cls.ai_core_v2_client.rest_client.delete(path=f'/admin/repositories/{cls.repo_dict["name"]}')

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._create_repo()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._delete_repo()
        super().tearDownClass()

    @classmethod
    def _get_application_dict(cls):
        return {
            "repository_url": cls.repo_dict['url'],
            "revision": "test_revision",
            "path": "test_path",
            "application_name": f"test-application-name-{get_random_string()}"
        }

    def assert_app_dict_in_app_objects(self, app_dict: dict, apps: List[Application]):
        for app in apps:
            if app.application_name == app_dict['application_name']:
                self.assert_object(app_dict, app)
                return

    def assert_app_status(self, app_status: ApplicationStatus):
        self.assertTrue(app_status.health_status)
        self.assertTrue(app_status.sync_status)
        self.assertTrue(app_status.message)
        self.assertTrue(app_status.sync_finished_at)
        self.assertTrue(app_status.sync_started_at)
        self.assertTrue(app_status.reconciled_at)

        self.assertIsNotNone(app_status.source)
        self.assertTrue(app_status.source.path)
        self.assertTrue(app_status.source.revision)
        self.assertTrue(app_status.source.repourl)

        self.assertIsNotNone(app_status.sync_ressources_status)
        for resource_sync_status in app_status.sync_ressources_status:
            self.assertTrue(resource_sync_status.name)
            self.assertTrue(resource_sync_status.kind)
            self.assertTrue(resource_sync_status.status)
            self.assertTrue(resource_sync_status.message)

    def assert_application(self, app_dict: dict, app: Application):
        app_dict_c = copy.deepcopy(app_dict)
        self.assertTrue(app_dict_c['application_name'] in app.application_name)
        del app_dict_c['application_name']
        self.assert_object(app_dict_c, app)

    def test_applications(self):
        # create with repo url
        app_dict = self._get_application_dict()
        response = self.ai_core_v2_client.applications.create(**app_dict)
        self.assertTrue(app_dict['application_name'] in response.id)
        self.assertIsNotNone(response.message)

        # get
        app = self.ai_core_v2_client.applications.get(application_name=app_dict['application_name'])
        self.assert_application(app_dict, app)

        # get_status
        app_status = self.ai_core_v2_client.applications.get_status(application_name=app_dict['application_name'])
        self.assert_app_status(app_status)

        # force sync git repo
        response = self.ai_core_v2_client.applications.refresh(application_name=app_dict['application_name'])
        self.assertTrue(app_dict['application_name'] in response.id)
        print(response.message)
        for t in ['refresh', 'scheduled']:
            self.assertIn(t, response.message)

        # create with repo name
        app_dict_2 = self._get_application_dict()
        app_dict_2['repository_name'] = self.repo_dict['name']
        del app_dict_2['repository_url']
        response = self.ai_core_v2_client.applications.create(**app_dict_2)
        self.assertTrue(app_dict_2['application_name'] in response.id)
        self.assertIsNotNone(response.message)

        # get
        app_2 = self.ai_core_v2_client.applications.get(application_name=app_dict_2['application_name'])
        app_dict_2_url = app_dict_2.copy()
        app_dict_2_url['repository_url'] = self.repo_dict['url']
        del app_dict_2_url['repository_name']
        self.assert_application(app_dict_2_url, app_2)

        # query
        apps_qr = self.ai_core_v2_client.applications.query()
        self.assertTrue(apps_qr.count >= 2)
        self.assert_app_dict_in_app_objects(app_dict, apps_qr.resources)
        self.assert_app_dict_in_app_objects(app_dict_2_url, apps_qr.resources)

        # modify
        app_patch_dict = self._get_application_dict()
        app_patch_dict['application_name'] = app_dict_2['application_name']
        app_patch_dict['revision'] = 'test-patch-revision'
        app_patch_dict['path'] = 'test-patch-path'
        response = self.ai_core_v2_client.applications.modify(**app_patch_dict)
        self.assertTrue(app_patch_dict['application_name'] in response.id)
        self.assertIsNotNone(response.message)

        # get modified app
        app_patched = self.ai_core_v2_client.applications.get(app_dict_2['application_name'])
        self.assert_application(app_patch_dict, app_patched)

        # delete
        response = self.ai_core_v2_client.applications.delete(application_name=app_dict['application_name'])
        self.assertTrue(app_dict['application_name'] in response.id)
        self.assertIsNotNone(response.message)
        self.ai_core_v2_client.applications.delete(application_name=app_dict_2['application_name'])
