import os
import pathlib
import unittest
from unittest import TestCase
from unittest.mock import patch

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context
from tests.mock import MockDeployment, MockProxyClient


class TestBaseClasses(TestCase):

    def test_instance_cache(self):
        with proxy_version_context('mock'):
            client_a = get_proxy_client()
            self.assertIsInstance(client_a, MockProxyClient)
            client_b = get_proxy_client()
            self.assertIs(client_a, client_b)
            MockProxyClient.refresh_instance_cache()
            client_c = get_proxy_client()
            self.assertIsNot(client_a, client_c)

    def test_base_class_functions(self):
        proxy_client = MockProxyClient()
        self.assertEqual(proxy_client.deployment_class, MockDeployment)
        self.assertDictEqual(proxy_client.request_header, {'token': 'mock_token'})
        self.assertEqual(len(proxy_client.deployments), 1)
        self.assertTrue(all([isinstance(deployment, MockDeployment) for deployment in proxy_client.deployments]))
        deployment = proxy_client.select_deployment()
        self.assertIsInstance(deployment, MockDeployment)
        self.assertEqual(deployment.url, 'mock_url')
        self.assertEqual(deployment.prediction_url, 'mock_url/predict')
        self.assertEqual(deployment.get_main_model_identification_kwargs(), 'a')
        self.assertEqual(deployment.get_model_identification_kwargs(), ('a', 'b', 'c'))


class TestBaseClasses(TestCase):

    def test_instance_cache(self):
        with proxy_version_context('mock'):
            client_a = get_proxy_client()
            self.assertIsInstance(client_a, MockProxyClient)
            client_b = get_proxy_client()
            self.assertIs(client_a, client_b)
            MockProxyClient.refresh_instance_cache()
            client_c = get_proxy_client()
            self.assertIsNot(client_a, client_c)

    def test_base_class_functions(self):
        proxy_client = MockProxyClient()
        self.assertEqual(proxy_client.deployment_class, MockDeployment)
        self.assertDictEqual(proxy_client.request_header, {'token': 'mock_token'})
        self.assertEqual(len(proxy_client.deployments), 1)
        self.assertTrue(all([isinstance(deployment, MockDeployment) for deployment in proxy_client.deployments]))
        deployment = proxy_client.select_deployment()
        self.assertIsInstance(deployment, MockDeployment)
        self.assertEqual(deployment.url, 'mock_url')
        self.assertEqual(deployment.prediction_url, 'mock_url/predict')
        self.assertEqual(deployment.get_main_model_identification_kwargs(), 'a')
        self.assertEqual(deployment.get_model_identification_kwargs(), ('a', 'b', 'c'))

        self.assertEqual(proxy_client.get_home(), pathlib.Path('~/.mock_llm').expanduser())
        with patch.dict(os.environ, {'MOCK_LLM_HOME': '~/mock_home'}):
            self.assertEqual(proxy_client.get_home(), pathlib.Path('~/mock_home').expanduser())


if __name__ == '__main__':
    unittest.main()
