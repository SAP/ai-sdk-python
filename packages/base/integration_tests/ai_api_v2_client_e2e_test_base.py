from datetime import timezone
from time import sleep
from typing import Any, Dict, List
from unittest import TestCase

from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client
from ai_api_client_sdk.models.artifact import Artifact
from ai_api_client_sdk.models.executable import Executable
from ai_api_client_sdk.models.input_artifact import InputArtifact
from ai_api_client_sdk.models.input_artifact_binding import InputArtifactBinding
from ai_api_client_sdk.models.label import Label
from ai_api_client_sdk.models.parameter import Parameter
from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.resource_clients.base_client import BaseClient
from . import AUTH_URL, BASE_URL, CLIENT_ID, CLIENT_SECRET, RESOURCE_GROUP_ID


class AIAPIV2ClientE2ETestBase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE
        # provision_resource_group()
        cls.ai_api_v2_client = AIAPIV2Client(base_url=BASE_URL, auth_url=AUTH_URL, client_id=CLIENT_ID,
                                             client_secret=CLIENT_SECRET, resource_group=RESOURCE_GROUP_ID)
        cls.test_scenario_id = '88888888-4444-4444-4444-cccccccccccc'

    @classmethod
    def tearDownClass(cls) -> None:
        # Uncomment the following line and the one in setUpClass to run integration_tests via IDE
        # deprovision_resource_group()
        super().tearDownClass()

    def assert_object(self, d: Dict[str, Any], o: object):
        for k in d.keys():
            self.assertEqual(d[k], getattr(o, k))

    def assert_dicts_in_objects(self, dict_list: List[Dict[str, Any]], object_list: list,
                                key: str = 'id'):
        dict_keys = [d[key] for d in dict_list]
        object_list = list(filter(lambda o: getattr(o, key) in dict_keys, object_list))
        self.assertEqual(len(dict_list), len(object_list))
        dict_list = sorted(dict_list, key=lambda d: d[key])
        object_list = sorted(object_list, key=lambda o: getattr(o, key))
        for i in range(len(object_list)):
            self.assert_object(dict_list[i], object_list[i])

    def assert_datetime(self, response_obj_dt_field):
        self.assertIsNotNone(response_obj_dt_field)
        self.assertEqual(response_obj_dt_field.tzinfo, timezone.utc)

    def wait_until_enactment_has_status(self, resource_client: BaseClient, params: Dict[str, str], status: Status):
        for _ in range(400):
            enactment = resource_client.get(**params)
            if enactment.status in [status, Status.DEAD]:
                break
            sleep(3)
        print(enactment.status_details)
        self.assertEqual(status, enactment.status)
        return enactment

    def get_an_executable(self, deployable: bool = False, scenario_id: str = None) -> Executable:
        if not scenario_id:
            scenario_id = self.test_scenario_id
        res = self.ai_api_v2_client.executable.query(scenario_id=scenario_id)
        for e in res.resources:
            if e.deployable == deployable:
                return e
        return None

    def create_artifact_dicts(self, n):
        artifact_dicts = []
        for i in range(n):
            artifact = self.create_artifact_dict(i)
            artifact_dicts.append(artifact)
        return artifact_dicts

    def create_artifact_dict(self, i=1, labels=None, kind: Artifact.Kind = Artifact.Kind.MODEL):
        if not labels:
            labels = [
                Label(**{
                    "key": "ext.ai.sap.com/s4hana-version",
                    "value": "string"
                })
            ]
        return {
            'name': f'Test Artifact {i}',
            'kind': kind,
            'labels': labels,
            'url': 'gs://kfserving-examples/models/tensorflow/flowers',
            'scenario_id': self.test_scenario_id,
            'description': f'Test Artifact {i} description'
        }

    def get_an_artifact(self) -> Artifact:
        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id)
        if res.count > 0:
            return res.resources[0]
        artifact_dict = self.create_artifact_dicts(1)[0]
        res = self.ai_api_v2_client.artifact.create(**artifact_dict)
        return self.ai_api_v2_client.artifact.get(artifact_id=res.id)

    def create_configuration_dicts(self, n: int, executable_id: str, parameters: List[Parameter] = None,
                                   input_artifacts: List[InputArtifact] = None, scenario_id: str = None):
        if scenario_id:
            test_scenario_id = scenario_id
        else:
            test_scenario_id = self.test_scenario_id

        configuration_dicts = []
        for i in range(n):
            configuration_dict = {
                'name': f'Test Configuration {i}',
                'scenario_id': test_scenario_id,
                'executable_id': executable_id
            }
            if parameters:
                configuration_dict['parameter_bindings'] = [
                    ParameterBinding(key=p.name, value=f'Test {p.name} value {i}') for p in parameters
                ]
            if input_artifacts:
                artifact = self.get_an_artifact()
                configuration_dict['input_artifact_bindings'] = [
                    InputArtifactBinding(key=ia.name, artifact_id=artifact.id) for ia in input_artifacts
                ]
            configuration_dicts.append(configuration_dict)
        return configuration_dicts

    def get_a_configuration(self, deployable: bool = False, scenario_id: str = None):
        executable = self.get_an_executable(deployable=deployable, scenario_id=scenario_id)
        cfg_dict = self.create_configuration_dicts(n=1, executable_id=executable.id, parameters=executable.parameters,
                                                   input_artifacts=executable.input_artifacts, scenario_id=scenario_id)[
            0]
        res = self.ai_api_v2_client.configuration.create(**cfg_dict)
        return self.ai_api_v2_client.configuration.get(configuration_id=res.id)
