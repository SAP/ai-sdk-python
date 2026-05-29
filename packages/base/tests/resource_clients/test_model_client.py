import copy
from unittest.mock import MagicMock

import humps

from ai_api_client_sdk.models.model import Model
from ai_api_client_sdk.models.model_version import ModelVersion
from ai_api_client_sdk.resource_clients.model_client import ModelClient
from .resource_client_test_base import ResourceClientTestBase


class TestModelClient(ResourceClientTestBase):
    @staticmethod
    def create_model_dict():
        # humps.decamelize usually called by request method
        return humps.decamelize(
            {
                "description": "Mistral mixtral-8x7b-instruct-v01 model",
                "executableId": "aicore-opensource",
                "model": "mistralai--mixtral-8x7b-instruct-v01",
                "versions": [
                    {
                        "isLatest": True,
                        "name": "1.2",
                        "deprecated": False,
                        "retirementDate": "2025-01-01",
                        "contextLength": 2048,
                        "inputTypes": ["text", "image"],
                        "capabilities": ["classification", "generation"],
                        "metadata": {"key1": "value1"},
                        "cost": {"unit": "USD", "value": "0.01"},
                    },
                    {
                        "isLatest": False,
                        "name": "1.1",
                        "deprecated": True,
                        "retirementDate": "2025-01-01",
                    },
                ],
                "displayName": "Mistral Model",
                "accessType": "public",
                "provider": "MistralAI",
                "allowedScenarios": [
                    {"scenarioId": "scenario1", "executableId": "exec1"},
                ],
            }
        )

    def assert_model_version(self, mv_dict: dict, mv: ModelVersion):
        self.assert_object(mv_dict, mv)

    def assert_model(self, m_dict: dict, m: Model):
        m_dict["versions"] = [ModelVersion.from_dict(mv) for mv in m_dict["versions"]]
        self.assert_object(m_dict, m)

    def test_query_models(self):
        n = 3
        model_dicts = [self.create_model_dict() for _ in range(n)]
        rest_client_mock = MagicMock()
        rest_client_mock.get.return_value = {
            "resources": copy.deepcopy(model_dicts),
            "count": n,
        }
        ec = ModelClient(rest_client_mock)
        eqr = ec.query()
        rest_client_mock.get.assert_called_with(
            path="/scenarios/foundation-models/models",
            resource_group=None,
        )
        self.assert_object_lists(
            copy.deepcopy(model_dicts),
            eqr.resources,
            self.assert_model,
            sort_key="model",
        )
        self.assert_object_lists(
            copy.deepcopy(model_dicts[0]["versions"]),
            eqr.resources[0].versions,
            self.assert_model_version,
            sort_key="name",
        )

        rest_client_mock.get.return_value = {"resources": [], "count": 0}
        ec.query(resource_group=self.resource_group)
        rest_client_mock.get.assert_called_with(
            path="/scenarios/foundation-models/models",
            resource_group=self.resource_group,
        )
