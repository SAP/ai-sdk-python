import copy
from unittest.mock import MagicMock

from ai_api_client_sdk.models.ai_api_meta import AIAPIMeta
from ai_api_client_sdk.models.capabilities import Capabilities
from ai_api_client_sdk.models.extensions import Extensions
from ai_api_client_sdk.models.version_list import VersionList
from ai_api_client_sdk.resource_clients.meta_client import MetaClient
from .resource_client_test_base import ResourceClientTestBase


class TestMetaClient(ResourceClientTestBase):
    @staticmethod
    def create_capabilities_dict():
        return {
            "runtime_identifier": "aicore",
            "runtime_api_version": "1.2.3",
            "description": "test_description",
            "ai_api": {
                "version": "1.2.3",
                "capabilities": {
                    "multitenant": True,
                    "shareable": True,
                    "static_deployments": True,
                    "user_deployments": True,
                    "user_executions": True,
                    "time_to_live_deployments": True,
                    "bulk_updates": {
                        "deployments": True,
                        "executions": True
                    },
                    "execution_schedules": True,
                    "logs": {
                        "executions": True,
                        "deployments": True
                    }
                },
                "limits": {
                    "executions": {
                        "max_running_count": -1
                    },
                    "deployments": {
                        "max_running_count": -1
                    }
                }
            },
            "extensions": {
                "analytics": {
                    "version": "1.2.3"
                },
                "resource_groups": {
                    "version": "1.2.3"
                },
                "dataset": {
                    "version": "1.2.3",
                    "capabilities": {
                        "upload": True,
                        "download": True,
                        "delete": True
                    },
                    "limits": {
                        "max_upload_file_size": 104857600,
                        "max_files_per_dataset": -1
                    }
                }
            }
        }

    @staticmethod
    def create_versions_dict():
        return {
            "versions": [
                {
                    "version_id": "test_v1",
                    "url": "https://api.test.com/v1",
                    "description": "Test API 1"
                },
                {
                    "version_id": "test_v2",
                    "url": "https://api.test.com/v2",
                    "description": "Test API 2"
                }
            ]
        }

    def assert_capabilities(self, c_dict: dict, c: Capabilities):
        c_dict['ai_api'] = AIAPIMeta.from_dict(c_dict['ai_api'])
        if 'extensions' in c_dict:
            c_dict['extensions'] = Extensions.from_dict(c_dict['extensions'])
        self.assert_object(c_dict, c)

    def assert_version_list(self, vl_dict: dict, vl: VersionList):
        if 'versions' in vl_dict:
            self.assert_object_lists(vl_dict['versions'], vl.versions, sort_key='version_id')
            del vl_dict['versions']
        self.assert_object(vl_dict, vl)

    def test_get_capabilities(self):
        c_dict = self.create_capabilities_dict()
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = copy.deepcopy(c_dict)
        mc = MetaClient(rest_client_mock)
        c = mc.get()
        rest_client_mock.get.assert_called_with(path='/meta')
        self.assert_capabilities(c_dict, c)

    def test_get_capabilities_bare_minimum(self):
        c_dict = {'ai_api': {'version': '1.2.3'}}
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = copy.deepcopy(c_dict)
        mc = MetaClient(rest_client_mock)
        c = mc.get()
        rest_client_mock.get.assert_called_with(path='/meta')
        self.assert_capabilities(c_dict, c)

    def test_get_versions(self):
        vl_dict = self.create_versions_dict()
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = copy.deepcopy(vl_dict)
        mc = MetaClient(rest_client_mock)
        vl = mc.get_versions()
        rest_client_mock.get.assert_called_with(path='/meta/versions')
        self.assert_version_list(vl_dict, vl)
