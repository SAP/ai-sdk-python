import uuid
from copy import deepcopy

from ai_api_client_sdk.helpers.datetime_parser import parse_datetime
from ai_api_client_sdk.models.configuration import Configuration
from ai_api_client_sdk.models.input_artifact_binding import InputArtifactBinding
from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_api_client_sdk.models.scenario import Scenario
from ai_api_client_sdk.resource_clients.configuration_client import ConfigurationClient
from .resource_client_test_base import ResourceClientTestBase


class TestConfigurationClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ConfigurationClient(self.rest_client_mock)

    @staticmethod
    def create_configuration_dict():
        return {
            "id": str(uuid.uuid4()),
            "name": "configuration_name",
            "executable_id": str(uuid.uuid4()),
            "scenario_id": str(uuid.uuid4()),
            "parameter_bindings": [
                {
                    "key": "param_key",
                    "value": "param_value"
                }
            ],
            "input_artifact_bindings": [
                {
                    "key": "input_artifact",
                    "artifact_id": str(uuid.uuid4())
                }
            ],
            "created_at": "2021-03-29T12:58:05Z"
        }

    @staticmethod
    def create_configuration_dict_with_expand_scenario_dict():
        return {
            "id": str(uuid.uuid4()),
            "name": "configuration_name",
            "executable_id": str(uuid.uuid4()),
            "scenario_id": str(uuid.uuid4()),
            "parameter_bindings": [
                {
                    "key": "param_key",
                    "value": "param_value"
                }
            ],
            "input_artifact_bindings": [
                {
                    "key": "input_artifact",
                    "artifact_id": str(uuid.uuid4())
                }
            ],
            "created_at": "2021-03-29T12:58:05Z",
            "scenario": {
                "created_at": "2021-03-29T12:57:05Z",
                "description": "ML API Facade Test Scenario description",
                "id": "88888888-4444-4444-4444-cccccccccccc",
                "labels": [
                    {
                        "key": "ext.ai.sap.com/xyz",
                        "value": "string"
                    }
                ],
                "modified_at": "2021-03-29T12:57:05Z",
                "name": "ML-API-Facade-Test-Scenario"
            }
        }

    def assert_configuration(self, conf_dict: dict, conf: Configuration):
        conf_dict['parameter_bindings'] = [ParameterBinding.from_dict(pb) for pb in conf_dict['parameter_bindings']]
        conf_dict['input_artifact_bindings'] = [InputArtifactBinding.from_dict(iab)
                                                for iab in conf_dict['input_artifact_bindings']]
        conf_dict['created_at'] = parse_datetime(conf_dict['created_at'])
        if conf_dict.get('scenario'):
            conf_dict['scenario'] = Scenario.from_dict(conf_dict['scenario'])
        self.assert_object(conf_dict, conf)

    def test_get_configuration(self):
        conf_dict = self.create_configuration_dict()
        self.rest_client_mock.get.return_value = conf_dict.copy()
        conf = self.client.get(configuration_id=conf_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/configurations/{conf_dict["id"]}', params=None,
                                                     resource_group=self.resource_group)
        self.assert_configuration(conf_dict, conf)
        self.assertIn("Configuration id: ", conf.__str__())
        self.assertIn(conf_dict['id'], conf.__str__())

    def test_get_configuration_with_expand_scenario(self):
        conf_with_expanded_scenario_dict = self.create_configuration_dict_with_expand_scenario_dict()
        self.rest_client_mock.get.return_value = deepcopy(conf_with_expanded_scenario_dict)
        response = self.client.get(configuration_id=conf_with_expanded_scenario_dict['id'], expand='scenario',
                                   resource_group=self.resource_group)
        params = {'$expand': 'scenario'}
        self.rest_client_mock.get.assert_called_with(path=f'/configurations/{conf_with_expanded_scenario_dict["id"]}',
                                                     params=params,
                                                     resource_group=self.resource_group)
        self.assert_configuration(conf_with_expanded_scenario_dict, response)

    def test_query_configurations(self):
        n = 3
        conf_dicts = [self.create_configuration_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [cd.copy() for cd in conf_dicts], 'count': n}
        cqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/configurations', params=None, resource_group=None)
        self.assert_object_lists(conf_dicts, cqr.resources, self.assert_configuration)

        params = {'scenario_id': 'test_scenario_id', 'executable_ids': ['test_executable_id'], 'top': 5, 'skip': 1,
                  'search': 'test_search'}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['executable_ids'] = ','.join(params['executable_ids'])
        params['$search'] = params['search']
        del params['search']
        self.rest_client_mock.get.assert_called_with(path='/configurations', params=params,
                                                     resource_group=self.resource_group)

    def test_query_configurations_search_case_insensitive(self):
        params = {'scenario_id': 'test_scenario_id', 'executable_ids': ['test_executable_id'], 'top': 5, 'skip': 1,
                  'search': 'test_search', 'search_case_insensitive': True}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['executable_ids'] = ','.join(params['executable_ids'])
        params['$search'] = params['search']
        del params['search']
        self.rest_client_mock.get.assert_called_with(path='/configurations', params=params,
                                                     resource_group=self.resource_group)

    def test_query_configurations_with_expand_scenario(self):
        n = 3
        conf_dicts = [self.create_configuration_dict_with_expand_scenario_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [deepcopy(cd) for cd in conf_dicts], 'count': n}
        cqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/configurations', params=None, resource_group=None)
        self.assert_object_lists(conf_dicts, cqr.resources, self.assert_configuration)

        params = {'scenario_id': 'test_scenario_id', 'executable_ids': ['test_executable_id'], 'top': 5, 'skip': 1,
                  'search': 'test_search', 'expand': 'scenario'}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['executable_ids'] = ','.join(params['executable_ids'])
        params['$search'] = params['search']
        del params['search']
        params['$expand'] = params['expand']
        del params['expand']
        self.rest_client_mock.get.assert_called_with(path='/configurations', params=params,
                                                     resource_group=self.resource_group)

    def test_create_configuration(self):
        conf_dict = self.create_configuration_dict()
        response_message = 'Configuration created'
        self.rest_client_mock.post.return_value = {'id': conf_dict['id'], 'message': response_message}
        parameter_bindings = [ParameterBinding.from_dict(pb) for pb in conf_dict['parameter_bindings']]
        ccr = self.client.create(name=conf_dict['name'], scenario_id=conf_dict['scenario_id'],
                                 executable_id=conf_dict['executable_id'],
                                 parameter_bindings=parameter_bindings,
                                 input_artifact_bindings=[InputArtifactBinding.from_dict(iab) for
                                                          iab in conf_dict['input_artifact_bindings']],
                                 resource_group=self.resource_group)
        body = conf_dict.copy()
        del body['id']
        del body['created_at']
        self.rest_client_mock.post.assert_called_with(path='/configurations', body=body,
                                                      resource_group=self.resource_group)
        self.assertEqual(conf_dict['id'], ccr.id)
        self.assertEqual(response_message, ccr.message)
        self.assertIn("Parameter binding key: ", parameter_bindings[0].__str__())
        self.assertIn(parameter_bindings[0].key, parameter_bindings[0].__str__())
        self.assertIn("Parameter binding value: ", parameter_bindings[0].__str__())
        self.assertIn(parameter_bindings[0].value, parameter_bindings[0].__str__())

    def test_count_configurations(self):
        self.assert_count('/configurations/$count', 3)
        self.assert_count('/configurations/$count', 0, {'scenario_id': 'test_scenario_id'})
        self.assert_count('/configurations/$count', 1, {'executable_ids': ['test_executable_id']})
        self.assert_count('/configurations/$count', 1,
                          {'scenario_id': 'test_scenario_id', 'executable_ids': ['test_executable_id']})
        self.assert_count('/configurations/$count', 2,
                          {'scenario_id': 'test_scenario_id', 'search': 'test_search'})
