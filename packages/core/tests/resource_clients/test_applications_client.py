import copy

from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.exception import AICoreInvalidInputException
from ai_core_sdk.models.application import Application
from ai_core_sdk.models.application_source import ApplicationSource
from ai_core_sdk.models.application_status import ApplicationStatus
from ai_core_sdk.resource_clients.applications_client import ApplicationsClient


class TestApplicationsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ApplicationsClient(self.rest_client_mock)
        self.app_path = '/admin/applications'

    @staticmethod
    def create_application_dict():
        return {
            'revision': 'test_revision',
            'path': 'test_path',
            'application_name': 'test_app_name',
            'repository_url': 'test_repo_url'
        }

    @staticmethod
    def get_application_status_dict():
        return {
            "health_status": "test_health_status",
            "sync_status": "test_sync_status",
            "message": "test_status_message",
            "source": {
                "repo_url": "test_source_repo_url",
                "path": "test_source_path",
                "revision": "test_source_revision"
            },
            "sync_finished_at": "test_sync_finished_at",
            "sync_started_at": "test_sync_started_at",
            "reconciled_at": "test_reconciled_at",
            "sync_resources_status": [
                {
                  "name": "test_resource_name",
                  "kind": "test_resource_kind",
                  "status": "test_resource_sync_status",
                  "message": "test_resource_sync_message"
                }
            ]
        }

    def assert_application(self, app_dict: dict, app: Application):
        app_dict_c = copy.deepcopy(app_dict)
        self.assertTrue(app_dict_c['application_name'] in app.application_name)
        del app_dict_c['application_name']
        self.assert_object(app_dict_c, app)

    @staticmethod
    def prepend_tenant_hash(s: str):
        return f'tenant_hash-{s}'

    def assert_application_source(self, source_dict: dict, source: ApplicationSource):
        self.assertEqual(source_dict['repo_url'], source.repourl)
        del source_dict['repo_url']
        self.assert_object(source_dict, source)
        self.assertIn("ApplicationSource repourl: ", source.__str__())
        self.assertIn(source.repourl, source.__str__())
        self.assertIn("ApplicationSource revision: ", source.__str__())
        self.assertIn(source.revision, source.__str__())

    def assert_application_status(self, status_dict: dict, status: ApplicationStatus):
        sd = copy.deepcopy(status_dict)
        self.assert_application_source(sd['source'], status.source)
        del sd['source']
        self.assert_object_lists(sd['sync_resources_status'], status.sync_resources_status, sort_key='name')
        self.assert_object_lists(sd['sync_resources_status'], status.sync_ressources_status, sort_key='name')
        del sd['sync_resources_status']
        self.assert_object(sd, status)
        self.assertIn("ApplicationStatus health status: ", status.__str__())
        self.assertIn(sd['health_status'], status.__str__())
        self.assertIn("ApplicationStatus sync status: ", status.__str__())
        self.assertIn(sd['sync_status'], status.__str__())
        self.assertIn("ApplicationStatus message:", status.__str__())
        self.assertIn(sd['message'], status.__str__())
        self.assertIn("ApplicationSource repourl: ", status.source.__str__())
        self.assertIn(status.source.repourl, status.source.__str__())
        self.assertIn("ApplicationSource revision: ", status.source.__str__())
        self.assertIn(status.source.revision, status.source.__str__())

    def _test_create_application(self, app_dict: dict):
        response_message = 'application has been been created'
        self.rest_client_mock.post.return_value = {'id': self.prepend_tenant_hash(app_dict['application_name']),
                                                   'message': response_message}
        response = self.client.create(**app_dict)
        self.rest_client_mock.post.assert_called_with(path=self.app_path, body=app_dict)
        self.assertEqual(response_message, response.message)

    def test_create_application_with_repository_url(self):
        app_dict = self.create_application_dict()
        self._test_create_application(app_dict)

    def test_create_application_with_repository_name(self):
        app_dict = self.create_application_dict()
        del app_dict['repository_url']
        app_dict['repository_name'] = 'test_repository_name'
        self._test_create_application(app_dict)

    def test_create_application_fails_with_both_name_and_url(self):
        app_dict = self.create_application_dict()
        app_dict['repository_name'] = 'test_repository_name'
        with self.assertRaises(AICoreInvalidInputException):
            self.client.create(**app_dict)
        self.rest_client_mock.get.assert_not_called()

    def test_create_application_fails_with_no_name_no_url(self):
        app_dict = self.create_application_dict()
        del app_dict['repository_url']
        with self.assertRaises(AICoreInvalidInputException):
            self.client.create(**app_dict)
        self.rest_client_mock.assert_not_called()

    def test_get_application(self):
        app_dict = self.create_application_dict()
        self.rest_client_mock.get.return_value = app_dict.copy()
        app = self.client.get(application_name=app_dict['application_name'])
        self.rest_client_mock.get.assert_called_with(path=f'{self.app_path}/{app_dict["application_name"]}')
        self.assert_object(app_dict, app)
        self.assertIn("Application name: ", app.__str__())
        self.assertIn(app_dict['application_name'], app.__str__())

    def test_get_application_status(self):
        app_name = 'test_app_name'
        status_dict = self.get_application_status_dict()
        self.rest_client_mock.get.return_value = status_dict.copy()
        app_status = self.client.get_status(application_name=app_name)
        self.rest_client_mock.get.assert_called_with(path=f'{self.app_path}/{app_name}/status')
        self.assert_application_status(status_dict, app_status)

    def test_get_application_status_bare_minimum(self):
        app_name = 'test_app_bare_minimum'
        self.rest_client_mock.get.return_value = {}
        app_status = self.client.get_status(application_name=app_name)
        self.rest_client_mock.get.assert_called_with(path=f'{self.app_path}/{app_name}/status')
        self.assert_all_attributes_none(app_status)

    def test_query_applications(self):
        n = 3
        app_dicts = [self.create_application_dict() for _ in range(n)]
        response_ads = []
        for ad in app_dicts:
            adc = ad.copy()
            adc['application_name'] = self.prepend_tenant_hash(ad["application_name"])
            response_ads.append(adc)
        self.rest_client_mock.get.return_value = {'resources': response_ads, 'count': n}
        app_qr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=self.app_path)
        self.assert_object_lists(app_dicts, app_qr.resources, sort_key='application_name',
                                 assert_object_function=self.assert_application)

    def test_modify_application(self):
        app_dict = self.create_application_dict()
        response_dict = {'id': self.prepend_tenant_hash(app_dict['application_name']),
                         'message': 'application has been updated'}
        self.rest_client_mock.patch.return_value = response_dict
        response = self.client.modify(**app_dict)
        body = app_dict.copy()
        del body['application_name']
        self.rest_client_mock.patch.assert_called_with(path=f'{self.app_path}/{app_dict["application_name"]}',
                                                       body=body)
        self.assert_object(response_dict, response)

    def test_delete_application(self):
        app_name = 'test_app_name'
        response_dict = {'id': self.prepend_tenant_hash(app_name), 'message': 'application deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        response = self.client.delete(application_name=app_name)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.app_path}/{app_name}')
        self.assert_object(response_dict, response)

    def test_refresh_application(self):
        app_name = 'test_app_name'
        response_dict = {'id': self.prepend_tenant_hash(app_name),
                         'message': 'A refresh of the application has been scheduled.'}
        self.rest_client_mock.post.return_value = response_dict
        response = self.client.refresh(application_name=app_name)
        self.rest_client_mock.post.assert_called_with(path=f'{self.app_path}/{app_name}/refresh')
        self.assert_object(response_dict, response)
