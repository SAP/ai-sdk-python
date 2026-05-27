import copy
import uuid
from unittest.mock import MagicMock

from ai_api_client_sdk.helpers.datetime_parser import parse_datetime
from ai_api_client_sdk.models.executable import Executable
from ai_api_client_sdk.models.input_artifact import InputArtifact
from ai_api_client_sdk.models.label import Label
from ai_api_client_sdk.models.output_artifact import OutputArtifact
from ai_api_client_sdk.models.parameter import Parameter
from ai_api_client_sdk.resource_clients.executable_client import ExecutableClient
from .resource_client_test_base import ResourceClientTestBase


class TestExecutableClient(ResourceClientTestBase):
    @staticmethod
    def create_executable_dict():
        return {
            "labels": [
                {
                    "key": "ext.ai.sap.com/s4hana-version",
                    "value": "label_value"
                }
            ],
            "name": "test_name",
            "description": "test_description",
            "id": str(uuid.uuid4()),
            "scenario_id": str(uuid.uuid4()),
            "version_id": "test_version_id",
            "parameters": [
                {
                    "name": "test_param_name",
                    "type": "string",
                    "default": "test",
                    "description": "test description"

                }
            ],
            "input_artifacts": [
                {
                    "name": "test_input_artifact_name",
                    "kind": "dataset",
                    "description": "artifact description",
                    "labels": [{'key': 'ext.ai.sap.com/customkey1', 'value': 'customvalue1'},
                               {'key': 'ext.ai.sap.com/customkey2', 'value': 'customvalue2'}]
                }
            ],
            "output_artifacts": [
                {
                    "name": "test_output_artifact_name",
                    "kind": "model",
                    "description": "artifact description",
                    "labels": [{'key': 'ext.ai.sap.com/customkey1', 'value': 'customvalue1'},
                               {'key': 'ext.ai.sap.com/customkey2', 'value': 'customvalue2'}]
                }
            ],
            "deployable": False,
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z"
        }

    def assert_executable(self, e_dict: dict, e: Executable):
        e_dict['labels'] = [Label.from_dict(ld) for ld in e_dict['labels']]
        e_dict['parameters'] = [Parameter.from_dict(pd) for pd in e_dict['parameters']]
        e_dict['input_artifacts'] = [InputArtifact.from_dict(iad) for iad in e_dict['input_artifacts']]
        e_dict['output_artifacts'] = [OutputArtifact.from_dict(oad) for oad in e_dict['output_artifacts']]
        e_dict['created_at'] = parse_datetime(e_dict['created_at'])
        e_dict['modified_at'] = parse_datetime(e_dict['modified_at'])
        self.assert_object(e_dict, e)

    def test_get_executable(self):
        exc_dict = self.create_executable_dict()
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = copy.deepcopy(exc_dict)
        ec = ExecutableClient(rest_client_mock)
        exc = ec.get(scenario_id=exc_dict['scenario_id'], executable_id=exc_dict['id'],
                     resource_group=self.resource_group)
        rest_client_mock.get.assert_called_with(
            path=f'/scenarios/{exc_dict["scenario_id"]}/executables/{exc_dict["id"]}',
            resource_group=self.resource_group)
        self.assert_executable(exc_dict, exc)
        self.assertIn("Executable id: ", exc.__str__())
        self.assertIn(exc_dict['id'], exc.__str__())
        self.assertIn("Input artifact name: ", exc_dict['input_artifacts'][0].__str__())
        self.assertIn(exc.input_artifacts[0].name, exc_dict['input_artifacts'][0].__str__())
        self.assertIn("Output artifact name: ", exc_dict['output_artifacts'][0].__str__())
        self.assertIn(exc.output_artifacts[0].name, exc_dict['output_artifacts'][0].__str__())
        self.assertIn("Parameter name: ", exc_dict['parameters'][0].__str__())
        self.assertIn(exc.parameters[0].name, exc_dict['parameters'][0].__str__())
        self.assertIn("Parameter type: ", exc_dict['parameters'][0].__str__())
        self.assertIn(exc.parameters[0].type.value, exc_dict['parameters'][0].__str__())

    def test_query_executables(self):
        n = 3
        exc_dicts = [self.create_executable_dict() for _ in range(n)]
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = {'resources': copy.deepcopy(exc_dicts), 'count': n}
        ec = ExecutableClient(rest_client_mock)
        eqr = ec.query(scenario_id=exc_dicts[0]['scenario_id'])
        rest_client_mock.get.assert_called_with(path=f'/scenarios/{exc_dicts[0]["scenario_id"]}/executables',
                                                params=None, resource_group=None)
        self.assert_object_lists(exc_dicts, eqr.resources, self.assert_executable)

        params = {'version_id': 'test_version_id'}
        sid = 'test_scenario_id'
        rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        ec.query(scenario_id=sid, resource_group=self.resource_group, **params)
        rest_client_mock.get.assert_called_with(path=f'/scenarios/{sid}/executables', params=params,
                                                resource_group=self.resource_group)
