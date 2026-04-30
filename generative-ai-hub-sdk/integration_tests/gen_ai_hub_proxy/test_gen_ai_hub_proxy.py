from __future__ import annotations

import importlib
import os
import unittest
from unittest.mock import patch

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context
from gen_ai_hub.proxy.gen_ai_hub_proxy.client import GenAIHubProxyClient, Deployment
from integration_tests.constants import OPENAI_GPT_4O_MINI_TEST_MODEL
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin


class TestProxyClient(TestCaseAICoreSetupMixin, unittest.TestCase):

    @staticmethod
    def _are_deployments_same(d1: Deployment, d2: Deployment):
        return (d1.url == d2.url and d1.deployment_id == d2.deployment_id and d1.model_name == d2.model_name
                and d1.config_id == d2.config_id)

    def test_deployment_discovery(self):
        proxy_client = self.proxy_client
        self.assertGreaterEqual(len(proxy_client.deployments), len(self.aicore_deployments))
        self.assertIsInstance(proxy_client, GenAIHubProxyClient)
        for kwarg in ('deployment_id', 'config_name', 'config_id', 'model_name', 'not_existing'):
            kwargs = {kwarg: 'NOT_EXISTING'}
            with self.assertRaises(ValueError):
                proxy_client.select_deployment(**kwargs)

        aicore_test_deployment = self.aicore_deployments[OPENAI_GPT_4O_MINI_TEST_MODEL]
        test_deployment = [dep for dep in proxy_client.deployments if dep.model_name == OPENAI_GPT_4O_MINI_TEST_MODEL][
            0]
        self.assertEqual(test_deployment.deployment_id, aicore_test_deployment.id)

        deployment = proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL)
        self.assertTrue(self._are_deployments_same(deployment, test_deployment))
        deployment = proxy_client.select_deployment(model_name=OPENAI_GPT_4O_MINI_TEST_MODEL, model_version='latest')
        self.assertTrue(self._are_deployments_same(deployment, test_deployment))
        for kwarg in ('deployment_id', 'config_id', 'model_name'):
            value = getattr(test_deployment, kwarg)
            deployment_other = proxy_client.select_deployment(**{kwarg: value})
            self.assertTrue(self._are_deployments_same(test_deployment, deployment_other))
            deployment_other = proxy_client.select_deployment(**{kwarg: value, 'executable_id': 'azure-openai'})
            self.assertTrue(self._are_deployments_same(test_deployment, deployment_other))
        with self.assertRaises(ValueError):
            proxy_client.select_deployment(**{'executable_id': 'INVALID_EXECUTABLE_ID'})


class TestCustomHeaders(unittest.TestCase):
    """
    Test that custom AI_CLIENT_TYPE from environment variable is correctly applied
    - i.e. propagated from ai-api-client and ai-core-sdk
    """

    def test_custom_ai_client_type_from_env(self):
        test_client_type = 'Custom Integration Test Client'
        original_value = os.environ.get('AI_CLIENT_TYPE')

        try:
            os.environ['AI_CLIENT_TYPE'] = test_client_type

            # Setup: Reload the client module to pick up the new environment variable
            from gen_ai_hub.proxy.gen_ai_hub_proxy import client
            importlib.reload(client)
            client.GenAIHubProxyClient.clear_cache()

            with proxy_version_context('gen-ai-hub'):
                proxy_client = get_proxy_client()
            headers = proxy_client.request_header

            self.assertIn('AI-Client-Type', headers)
            self.assertEqual(test_client_type, headers['AI-Client-Type'])

        # Cleanup
        finally:
            if original_value is not None:
                os.environ['AI_CLIENT_TYPE'] = original_value
            else:
                os.environ.pop('AI_CLIENT_TYPE', None)

            from gen_ai_hub.proxy.gen_ai_hub_proxy import client
            importlib.reload(client)
            client.GenAIHubProxyClient.clear_cache()

    def test_default_ai_client_type(self):
        original_value = os.environ.get('AI_CLIENT_TYPE')

        try:
            # Setup: Remove the environment variable if it exists
            os.environ.pop('AI_CLIENT_TYPE', None)
            from gen_ai_hub.proxy.gen_ai_hub_proxy import client
            importlib.reload(client)
            client.GenAIHubProxyClient.clear_cache()

            with proxy_version_context('gen-ai-hub'):
                proxy_client = get_proxy_client()

            headers = proxy_client.request_header

            self.assertIn('AI-Client-Type', headers)
            self.assertEqual('GenAI Hub SDK (Python)', headers['AI-Client-Type'])

        # Cleanup
        finally:
            if original_value is not None:
                os.environ['AI_CLIENT_TYPE'] = original_value
            else:
                os.environ.pop('AI_CLIENT_TYPE', None)

            from gen_ai_hub.proxy.gen_ai_hub_proxy import client
            importlib.reload(client)
            client.GenAIHubProxyClient.clear_cache()
