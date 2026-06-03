import copy
import uuid
from unittest.mock import MagicMock

from ai_api_client_sdk.helpers.datetime_parser import parse_datetime
from ai_api_client_sdk.models.label import Label
from ai_api_client_sdk.models.scenario import Scenario
from ai_api_client_sdk.models.version import Version
from ai_api_client_sdk.resource_clients.scenario_client import ScenarioClient
from .resource_client_test_base import ResourceClientTestBase


class TestScenarioClient(ResourceClientTestBase):
    @staticmethod
    def create_scenario_dict():
        return {
            "labels": [
                {
                    "key": "ext.ai.sap.com/s4hana-version",
                    "value": "test_label_value"
                }
            ],
            "name": "test_scenario_name",
            "description": "test_scenario_description",
            "id": str(uuid.uuid4()),
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z"
        }

    @staticmethod
    def create_llm_scenario_dict():
        return {
            "labels": [
                {
                    "key": "scenarios.ai.sap.com/llm",
                    "value": "true"
                }
            ],
            "name": "test_scenario_name",
            "description": "test_scenario_description",
            "id": str(uuid.uuid4()),
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z"
        }

    @staticmethod
    def create_version_dict():
        return {
            "description": "This is version v1",
            "id": "test_version_id",
            "scenario_id": str(uuid.uuid4()),
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z"
        }

    def assert_scenario(self, s_dict: dict, s: Scenario):
        s_dict['labels'] = [Label.from_dict(ld) for ld in s_dict['labels']]
        s_dict['created_at'] = parse_datetime(s_dict['created_at'])
        s_dict['modified_at'] = parse_datetime(s_dict['modified_at'])
        self.assert_object(s_dict, s)

    def assert_version(self, v_dict: dict, v: Version):
        v_dict['created_at'] = parse_datetime(v_dict['created_at'])
        v_dict['modified_at'] = parse_datetime(v_dict['modified_at'])
        self.assert_object(v_dict, v)

    def test_get_scenario(self):
        s_dict = self.create_scenario_dict()
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = copy.deepcopy(s_dict)
        sc = ScenarioClient(rest_client_mock)
        s = sc.get(scenario_id=s_dict['id'], resource_group=self.resource_group)
        rest_client_mock.get.assert_called_with(path=f'/scenarios/{s_dict["id"]}', resource_group=self.resource_group)
        self.assert_scenario(s_dict, s)
        self.assertIn("Scenario id: ", s.__str__())
        self.assertIn(s_dict['id'], s.__str__())

    def test_query_scenarios(self):
        n = 3
        s_dicts = [self.create_scenario_dict() for _ in range(n)]
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = {'resources': copy.deepcopy(s_dicts), 'count': n}
        sc = ScenarioClient(rest_client_mock)
        sqr = sc.query()
        rest_client_mock.get.assert_called_with(path='/scenarios', resource_group=None)
        self.assert_object_lists(s_dicts, sqr.resources, self.assert_scenario)

    def test_query_scenarios_for_llm(self):
        n = 3
        s_dicts = [self.create_scenario_dict() for _ in range(n)]
        s_llm = self.create_llm_scenario_dict()
        s_dicts.append(s_llm)
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = {'resources': copy.deepcopy(s_dicts), 'count': n+1}
        sc = ScenarioClient(rest_client_mock)
        scenario_llm_query = sc.query(only_llm_scenarios=True)
        rest_client_mock.get.assert_called_with(path='/scenarios', resource_group=None)
        self.assert_object_lists([s_llm], scenario_llm_query.resources, self.assert_scenario)

    def test_query_llm_scenarios(self):
        n = 3
        s_dicts = [self.create_scenario_dict() for _ in range(n)]
        s_llm = self.create_llm_scenario_dict()
        s_dicts.append(s_llm)
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = {'resources': copy.deepcopy(s_dicts), 'count': n + 1}
        sc = ScenarioClient(rest_client_mock)
        scenario_llm_query = sc.query_llm_scenarios()
        rest_client_mock.get.assert_called_with(path='/scenarios', resource_group=None)
        self.assert_object_lists([s_llm], scenario_llm_query.resources, self.assert_scenario)

    def test_query_versions(self):
        n = 3
        ver_dicts = [self.create_version_dict() for _ in range(n)]
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = {'resources': copy.deepcopy(ver_dicts), 'count': n}
        sc = ScenarioClient(rest_client_mock)
        vqr = sc.query_versions(scenario_id=ver_dicts[0]['scenario_id'])
        rest_client_mock.get.assert_called_with(path=f'/scenarios/{ver_dicts[0]["scenario_id"]}/versions',
                                                params=None, resource_group=None)
        self.assert_object_lists(ver_dicts, vqr.resources, self.assert_version)

        params = {'label_selector': ['test_label_selector']}
        sid = 'test_scenario_id'
        rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        sc.query_versions(scenario_id=sid, resource_group=self.resource_group, **params)
        params['label_selector'] = ','.join(params['label_selector'])
        rest_client_mock.get.assert_called_with(path=f'/scenarios/{sid}/versions', params=params,
                                                resource_group=self.resource_group)
        self.assertIn("Version id: ", vqr.resources[0].__str__())
        self.assertIn(ver_dicts[0]['id'], vqr.resources[0].__str__())
