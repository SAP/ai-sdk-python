import uuid
from copy import deepcopy

from ai_api_client_sdk.helpers.datetime_parser import parse_datetime
from ai_api_client_sdk.models.artifact import Artifact
from ai_api_client_sdk.models.label import Label
from ai_api_client_sdk.models.scenario import Scenario
from ai_api_client_sdk.resource_clients.artifact_client import ArtifactClient
from .resource_client_test_base import ResourceClientTestBase


class TestArtifactClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ArtifactClient(self.rest_client_mock)

    @staticmethod
    def create_artifact_dict(labels=None):
        if labels is None:
            labels = [
                {'key': 'ext.ai.sap.com/s4hana-version', 'value': 'string'}]
        return {
            "labels": labels,
            "name": "string",
            "kind": "model",
            "url": "https://example.com/some_path",
            "description": "string",
            "id": str(uuid.uuid4()),
            "scenario_id": str(uuid.uuid4()),
            "execution_id": str(uuid.uuid4()),
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z"
        }

    @staticmethod
    def create_artifact_with_expand_scenario_dict(labels=None):
        if labels is None:
            labels = [
                {'key': 'ext.ai.sap.com/s4hana-version', 'value': 'string'}]
        return {
            "labels": labels,
            "name": "string",
            "kind": "model",
            "url": "https://example.com/some_path",
            "description": "string",
            "id": str(uuid.uuid4()),
            "scenario_id": str(uuid.uuid4()),
            "execution_id": str(uuid.uuid4()),
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z",
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

    def assert_artifact(self, artifact_dict: dict, artifact: Artifact):
        artifact_dict['created_at'] = parse_datetime(artifact_dict['created_at'])
        artifact_dict['modified_at'] = parse_datetime(artifact_dict['modified_at'])
        artifact_dict['kind'] = Artifact.Kind(artifact_dict['kind'])
        artifact_dict['labels'] = [Label.from_dict(l) for l in artifact_dict['labels']]
        if artifact_dict.get('scenario'):
            artifact_dict['scenario'] = Scenario.from_dict(artifact_dict['scenario'])
        self.assert_object(artifact_dict, artifact)

    def test_get_artifact(self):
        artifact_dict = self.create_artifact_dict()
        self.rest_client_mock.get.return_value = artifact_dict.copy()
        a = self.client.get(artifact_id=artifact_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/artifacts/{artifact_dict["id"]}', params=None,
                                                     resource_group=self.resource_group)
        self.assert_artifact(artifact_dict, a)
        self.assertIn("Artifact id: ", a.__str__())
        self.assertIn(artifact_dict['id'], a.__str__())
        self.assertIn("Label key: ", artifact_dict['labels'][0].__str__())
        self.assertIn(artifact_dict['labels'][0].key, artifact_dict['labels'][0].__str__())
        self.assertIn("Label value: ", artifact_dict['labels'][0].__str__())
        self.assertIn(artifact_dict['labels'][0].value, artifact_dict['labels'][0].__str__())

    def test_get_artifact_with_expand_scenario(self):
        artifact_with_expanded_scenario_dict = self.create_artifact_with_expand_scenario_dict()
        self.rest_client_mock.get.return_value = deepcopy(artifact_with_expanded_scenario_dict)
        response = self.client.get(artifact_id=artifact_with_expanded_scenario_dict['id'], expand='scenario',
                                   resource_group=self.resource_group)
        params = {'$expand': 'scenario'}
        self.rest_client_mock.get.assert_called_with(path=f'/artifacts/{artifact_with_expanded_scenario_dict["id"]}',
                                                     params=params,
                                                     resource_group=self.resource_group)
        self.assert_artifact(artifact_with_expanded_scenario_dict, response)

    def test_query_artifacts(self):
        n = 3
        artifacts = [self.create_artifact_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [a.copy() for a in artifacts], 'count': n}
        aqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=None, resource_group=None)
        self.assert_object_lists(artifacts, aqr.resources, self.assert_artifact)
        self.assertIn("Resources: ", aqr.__str__())
        for artifact in artifacts:
            self.assertIn(artifact['id'], aqr.__str__())
        self.assertIn("Count: " + str(len(artifacts)), aqr.__str__())

        params = {'scenario_id': 'test_scenario_id', 'execution_id': 'test_execution_id', 'name': 'test_name',
                  'kind': Artifact.Kind.MODEL, 'top': 5, 'skip': 1, 'search': 'test_search'}  # type:dict
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['kind'] = params['kind'].value
        params['$search'] = params['search']
        del params['search']
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=params,
                                                     resource_group=self.resource_group)

    def test_query_artifacts_search_case_insensitive(self):
        params = {'scenario_id': 'test_scenario_id', 'execution_id': 'test_execution_id', 'name': 'test_name',
                  'kind': Artifact.Kind.MODEL, 'top': 5, 'skip': 1, 'search': 'test_search',
                  'search_case_insensitive': True}  # type:dict
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['kind'] = params['kind'].value
        params['$search'] = params['search']
        del params['search']
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=params,
                                                     resource_group=self.resource_group)

    def test_query_artifacts_with_expand_scenario(self):
        n = 3
        artifacts = [self.create_artifact_with_expand_scenario_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [deepcopy(a) for a in artifacts], 'count': n}
        aqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=None, resource_group=None)
        self.assert_object_lists(artifacts, aqr.resources, self.assert_artifact)

        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        params = {'scenario_id': 'test_scenario_id', 'execution_id': 'test_execution_id', 'name': 'test_name',
                  'kind': Artifact.Kind.MODEL, 'top': 5, 'skip': 1, 'search': 'test_search',
                  'expand': 'scenario'}  # type:dict
        self.client.query(resource_group=self.resource_group, **params)
        params['kind'] = params['kind'].value
        params['$search'] = params['search']
        del params['search']
        params['$expand'] = params['expand']
        del params['expand']
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=params,
                                                     resource_group=self.resource_group)

    def test_filter_artifacts_by_labels(self):
        labels = []
        artifacts = []
        labels.append({'key': 'ext.ai.sap.com/s4hana-version', 'value': 'test'})
        artifacts.append(self.create_artifact_dict(labels=[labels[0]]))
        labels.append({'key': 'ext.ai.sap.com/s4hana-version', 'value': 'test2'})
        artifacts.append(self.create_artifact_dict(labels=[labels[1]]))
        artifacts.append(self.create_artifact_dict(labels=labels))
        self.rest_client_mock.get.return_value = {'resources': [a.copy() for a in artifacts], 'count': 3}
        ac = ArtifactClient(self.rest_client_mock)

        params = {'artifact_label_selector': 'ext.ai.sap.com/s4hana-version!=test'}
        self.rest_client_mock.get.return_value = {'resources': [artifacts[0]], 'count': 1}
        ac.query(resource_group=self.resource_group, **params)
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=params,
                                                     resource_group=self.resource_group)

        params = {'artifact_label_selector': 'ext.ai.sap.com/s4hana-version=test, ext.ai.sap.com/dummy=dummy'}
        self.rest_client_mock.get.return_value = {'resources': [artifacts[2]], 'count': 1}
        ac.query(resource_group=self.resource_group, **params)
        self.rest_client_mock.get.assert_called_with(path='/artifacts', params=params,
                                                     resource_group=self.resource_group)

    def test_create_artifact(self):
        artifact_dict = self.create_artifact_dict()
        response_message = 'Artifact created'
        self.rest_client_mock.post.return_value = {'id': artifact_dict['id'], 'message': response_message,
                                                   'url': artifact_dict['url']}
        acr = self.client.create(name=artifact_dict['name'], kind=Artifact.Kind(artifact_dict['kind']),
                                 url=artifact_dict['url'],
                                 scenario_id=artifact_dict['scenario_id'],
                                 description=artifact_dict['description'],
                                 labels=[Label.from_dict(l) for l in artifact_dict['labels']],
                                 resource_group=self.resource_group)
        body = artifact_dict.copy()
        del body['id']
        del body['execution_id']
        del body['created_at']
        del body['modified_at']
        self.rest_client_mock.post.assert_called_with(path='/artifacts', body=body, resource_group=self.resource_group)
        self.assertEqual(artifact_dict['id'], acr.id)
        self.assertEqual(response_message, acr.message)
        self.assertEqual(artifact_dict['url'], acr.url)

    def test_artifact_kind_other(self):
        # Make sure artifact of type `other` can be created
        artifact_dict = self.create_artifact_dict()
        artifact_dict['kind'] = 'other'
        self.rest_client_mock.post.return_value = {'id': artifact_dict['id'],
                                                   'message': 'Artifact of type `other` created',
                                                   'url': artifact_dict['url']}
        acr = self.client.create(name=artifact_dict['name'], kind=Artifact.Kind(artifact_dict['kind']),
                                 url=artifact_dict['url'],
                                 scenario_id=artifact_dict['scenario_id'],
                                 description=artifact_dict['description'],
                                 labels=[Label.from_dict(l) for l in artifact_dict['labels']],
                                 resource_group=self.resource_group)

        self.rest_client_mock.get.return_value = artifact_dict.copy()
        response = self.client.get(acr.id, resource_group=self.resource_group)
        self.assertEqual(response.kind, Artifact.Kind.OTHER)

    def test_count_artifacts(self):
        self.assert_count('/artifacts/$count', 12)
        self.assert_count('/artifacts/$count', 10, {'scenario_id': 'test_scenario_id'})
        self.assert_count('/artifacts/$count', 9, {'execution_id': 'test_execution_id'})
        self.assert_count('/artifacts/$count', 1, {'name': 'test_name'})
        self.assert_count('/artifacts/$count', 9, {'kind': Artifact.Kind.MODEL})
        self.assert_count('/artifacts/$count', 9, {'artifact_label_selector': 'ext.ai.sap.com/dummy!=dummy'})
        self.assert_count('/artifacts/$count', 1,
                          {'scenario_id': 'test_scenario_id', 'execution_id': 'test_execution_id', 'name': 'test_name',
                           'kind': Artifact.Kind.MODEL, 'artifact_label_selector': 'ext.ai.sap.com/dummy!=dummy'})
