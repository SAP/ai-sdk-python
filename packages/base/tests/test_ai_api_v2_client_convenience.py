import os
import unittest
from unittest.mock import MagicMock, patch

from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client
from ai_api_client_sdk.helpers.constants import SKIP_AUTH_ENV_VAR
from ai_api_client_sdk.models.model import Model
from ai_api_client_sdk.models.model_version import ModelVersion


def _make_client():
    """Create an AIAPIV2Client with auth skipped."""
    os.environ[SKIP_AUTH_ENV_VAR] = 'true'
    try:
        return AIAPIV2Client(base_url='https://test.example.com/v2/lm')
    finally:
        del os.environ[SKIP_AUTH_ENV_VAR]


class TestAIAPIV2ClientGetModels(unittest.TestCase):
    def test_get_models_delegates_to_model_query(self):
        client = _make_client()
        sentinel = [MagicMock(spec=Model)]
        mock_response = MagicMock()
        mock_response.resources = sentinel
        client.model = MagicMock()
        client.model.query.return_value = mock_response

        result = client.get_models()
        client.model.query.assert_called_once_with(resource_group=None)
        self.assertIs(result, sentinel)

    def test_get_models_passes_resource_group(self):
        client = _make_client()
        sentinel = [MagicMock(spec=Model)]
        mock_response = MagicMock()
        mock_response.resources = sentinel
        client.model = MagicMock()
        client.model.query.return_value = mock_response

        result = client.get_models(resource_group='my-group')
        client.model.query.assert_called_once_with(resource_group='my-group')


class TestAIAPIV2ClientGetFoundationModelDeploymentId(unittest.TestCase):
    def test_resolves_deployment_id(self):
        client = _make_client()
        mock_deployment = MagicMock()
        mock_deployment.id = 'dep-123'
        mock_deployment.details = {
            'resources': {
                'backend_details': {
                    'model': {'name': 'gpt-4o', 'version': 'latest'}
                }
            }
        }
        mock_response = MagicMock()
        mock_response.resources = [mock_deployment]
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        result = client.get_foundation_model_deployment_id('gpt-4o', 'azure-openai')
        self.assertEqual(result, 'dep-123')

    def test_raises_when_no_match(self):
        client = _make_client()
        mock_deployment = MagicMock()
        mock_deployment.id = 'dep-123'
        mock_deployment.details = {
            'resources': {
                'backend_details': {
                    'model': {'name': 'other-model', 'version': 'latest'}
                }
            }
        }
        mock_response = MagicMock()
        mock_response.resources = [mock_deployment]
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        with self.assertRaises(ValueError) as ctx:
            client.get_foundation_model_deployment_id('gpt-4o', 'azure-openai')
        self.assertIn('gpt-4o', str(ctx.exception))


class TestAIAPIV2ClientGetOrchestrationDeploymentId(unittest.TestCase):
    def test_resolves_orchestration_deployment_id(self):
        client = _make_client()
        mock_deployment = MagicMock()
        mock_deployment.id = 'orch-dep-1'
        mock_response = MagicMock()
        mock_response.resources = [mock_deployment]
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        result = client.get_orchestration_deployment_id()
        self.assertEqual(result, 'orch-dep-1')

    def test_raises_when_no_deployment(self):
        client = _make_client()
        mock_response = MagicMock()
        mock_response.resources = []
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        with self.assertRaises(ValueError):
            client.get_orchestration_deployment_id()


class TestAIAPIV2ClientGetOrchestrationDeploymentUrl(unittest.TestCase):
    def test_resolves_orchestration_deployment_url(self):
        client = _make_client()
        mock_deployment = MagicMock()
        mock_deployment.deployment_url = 'https://api.example.com/v2/inference/deployments/orch-1'
        mock_response = MagicMock()
        mock_response.resources = [mock_deployment]
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        result = client.get_orchestration_deployment_url()
        self.assertIn('orch-1', result)

    def test_raises_when_no_deployment(self):
        client = _make_client()
        mock_response = MagicMock()
        mock_response.resources = []
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        with self.assertRaises(ValueError):
            client.get_orchestration_deployment_url()

    def test_raises_when_no_url(self):
        client = _make_client()
        mock_deployment = MagicMock()
        mock_deployment.deployment_url = None
        mock_response = MagicMock()
        mock_response.resources = [mock_deployment]
        client.deployment = MagicMock()
        client.deployment.query.return_value = mock_response

        with self.assertRaises(ValueError) as ctx:
            client.get_orchestration_deployment_url()
        self.assertIn('no deployment URL', str(ctx.exception))
