from __future__ import annotations

import os
import threading
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context
from gen_ai_hub.proxy.gen_ai_hub_proxy.client import (GenAIHubProxyClient, Deployment, temporary_headers_addition)
from tests.mock import get_mocked_ai_core_client, ai_core_ai_api_mocker


class TestProxyClient(unittest.TestCase):
    proxy_kwargs = dict(
        client_id='XXXX',
        client_secret='YYYY',
        auth_url='https://auth_url/oauth/token',
        base_url='https://base_url/v2',
    )

    def create_deployment(self):
        return Deployment(
            url='url',
            deployment_id='deployment_id',
            config_name='config_name',
            config_id='config_id',
            model_name='gpt-4o-mini',
            model_version='1337',
            additonal_parameters={},
            created_at=datetime.now(),
        )

    def test_get_proxy_client(self):
        with proxy_version_context('gen-ai-hub'):
            client_a = get_proxy_client(**self.proxy_kwargs)
            self.assertIsInstance(client_a, GenAIHubProxyClient)
            client_b = get_proxy_client(**self.proxy_kwargs)
            self.assertIsInstance(client_b, GenAIHubProxyClient)
            self.assertEqual(client_b, client_a)

    def test_deployment(self):
        deployment = self.create_deployment()
        self.assertEqual(deployment.model_version, '1337')
        self.assertEqual(deployment.model_name, 'gpt-4o-mini')
        self.assertTupleEqual(deployment.get_model_identification_kwargs(),
                              ('model_name', 'model_version', 'config_id', 'config_name', 'deployment_id'))
        self.assertEqual(deployment.prediction_url, None)
        with self.assertRaises(AttributeError):
            deployment.not_existing
        self.assertEqual(deployment.model_version, '1337')

    def test_deployment_discovery(self):
        with (proxy_version_context('gen-ai-hub')):
            proxy_client = get_proxy_client(**self.proxy_kwargs)
            deployment = self.create_deployment()
            proxy_client._deployments = [deployment]
            deployments_dict = {deployment.deployment_id: deployment}
            proxy_client._get_scenario_deployments = MagicMock()
            proxy_client._get_scenario_deployments.return_value = deployments_dict
            self.assertIsInstance(proxy_client, GenAIHubProxyClient)
            for kwarg in ('deployment_id', 'config_name', 'config_id', 'model_name', 'not_existing'):
                kwargs = {kwarg: 'NOT_EXISTING'}
                with self.assertRaises(ValueError):
                    proxy_client.select_deployment(**kwargs)
                proxy_client._get_scenario_deployments.assert_called_once_with(
                    proxy_client.foundational_model_scenarios[0])
                proxy_client._get_scenario_deployments.reset_mock()
            deployment = proxy_client.select_deployment(model_name='gpt-4o-mini')
            self.assertIs(deployment, proxy_client.deployments[0])
            for kwarg in ('deployment_id', 'config_name', 'config_id', 'model_name'):
                value = getattr(deployment, kwarg)
                deployment_other = proxy_client.select_deployment(**{kwarg: value})
                self.assertIs(deployment, deployment_other)
                search_kwargs = {kwarg: value, 'model_version': '1337'}
                if kwarg != "model_name":
                    search_kwargs['model_name'] = getattr(deployment, 'model_name')
                deployment_other = proxy_client.select_deployment(**search_kwargs)
                self.assertIs(deployment, deployment_other)
                with self.assertRaises(ValueError):
                    proxy_client.select_deployment(**{kwarg: value, 'model_version': '1340'})

    def test_deployment_discovery_error_model_version_without_model_name(self):
        with (proxy_version_context('gen-ai-hub')):
            proxy_client = get_proxy_client(**self.proxy_kwargs)
            deployment = self.create_deployment()
            proxy_client._deployments = [deployment]
            deployments_dict = {deployment.deployment_id: deployment}
            proxy_client._get_scenario_deployments = MagicMock()
            proxy_client._get_scenario_deployments.return_value = deployments_dict
            self.assertIsInstance(proxy_client, GenAIHubProxyClient)
            with self.assertRaises(ValueError):
                proxy_client.select_deployment(model_version = '1337')

    def test_client_mock_discovery(self):
        proxy_client = get_mocked_ai_core_client()
        self.assertEqual(len(proxy_client.get_deployments()), 8)
        self.assertIsInstance(proxy_client.request_header, dict)

    def test_client_mock_discovery_with_additional_fm_scenario(self):
        from gen_ai_hub.proxy.gen_ai_hub_proxy.client import GenAIHubProxyClient
        from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context

        with proxy_version_context('gen-ai-hub'):
            kwargs = dict(
                client_id='XXXX',
                client_secret='YYYY',
                auth_url='https://auth_url/oauth/token',
                base_url='https://base_url/v2',
            )
            with unittest.mock.patch.object(GenAIHubProxyClient, 'foundational_model_scenarios', []):
                proxy_client: GenAIHubProxyClient = get_proxy_client(**kwargs)
                with ai_core_ai_api_mocker(auth_url=kwargs['auth_url'], base_url=kwargs['base_url']):
                    proxy_client.get_request_header()
                    self.assertEqual(len(proxy_client.get_deployments()), 0)
                    proxy_client.add_foundation_model_scenario(
                        scenario_id='foundation-models',
                        config_names='not-existing-config-1',
                    )
                    self.assertEqual(len(proxy_client.get_deployments()), 0)
                    proxy_client.add_foundation_model_scenario(
                        scenario_id='foundation-models',
                        config_names=['not-existing-config-2', 'not-existing-config-3'],
                    )
                    self.assertEqual(len(proxy_client.get_deployments()), 0)
                    proxy_client.add_foundation_model_scenario(
                        scenario_id='foundation-models',
                        config_names='*',
                    )
                    self.assertEqual(len(proxy_client.get_deployments()), 8)
                    proxy_client.add_foundation_model_scenario(
                        scenario_id='dox-llm',
                        config_names='dox-llm-cinder?lla*',
                    )
                    self.assertEqual(len(proxy_client.get_deployments()), 9)

    def test_ai_client_type_headers(self):
        test_client = 'Custom Test Client'

        with unittest.mock.patch.object(GenAIHubProxyClient, 'AI_CLIENT_TYPE_VAL', test_client):
            GenAIHubProxyClient.clear_cache()
            proxy_client = get_mocked_ai_core_client()
            headers = proxy_client.request_header
            self.assertIn('AI-Client-Type', headers)
            self.assertEqual(test_client, headers['AI-Client-Type'])
        GenAIHubProxyClient.clear_cache()

    def test_setting_headers_addition(self):
        proxy_client = get_mocked_ai_core_client()
        default_headers = proxy_client.request_header

        proxy_client.set_headers_addition({'X-Test-Header': 'default'})

        self.assertEqual(proxy_client.request_header, {
            **default_headers,
            'X-Test-Header': 'default'
        })

    def test_updating_headers_addition(self):
        proxy_client = get_mocked_ai_core_client()
        headers = proxy_client.request_header

        self.assertIn('AI-Client-Type', headers, )
        self.assertEqual('GenAI Hub SDK (Python)', headers['AI-Client-Type'])

    def test_when_token_generation_is_skipped(self):
        os.environ['SKIP_AUTHORIZATION'] = 'true'
        mock_client = MagicMock()
        mock_client.ai_core_client.rest_client.headers = {"Existing": "Header"}
        mock_client.get_ai_core_token.return_value = "token123"
        result = GenAIHubProxyClient.get_request_header(mock_client)
        self.assertNotIn("Authorization", result)
        del os.environ['SKIP_AUTHORIZATION']

    def test_when_token_is_generated(self):
        mock_client = MagicMock()
        mock_client.ai_core_client.rest_client.headers = {"Existing": "Header"}
        mock_client.get_ai_core_token.return_value = "token123"
        result = GenAIHubProxyClient.get_request_header(mock_client)
        self.assertIn("Authorization", result)
        self.assertEqual(result["Authorization"], "token123")

    def test_setting_temporary_headers(self):
        proxy_client = get_mocked_ai_core_client()
        default_headers = proxy_client.request_header

        proxy_client.set_headers_addition({
            'X-Test-Header': 'default'
        })

        with temporary_headers_addition({
            'X-Test-Header': 'override', 'X-New-Header': 'new'
        }):
            self.assertEqual(proxy_client.request_header, {
                **default_headers,
                'X-Test-Header': 'override',
                'X-New-Header': 'new'
            })

        self.assertEqual(proxy_client.request_header, {
            **default_headers,
            'X-Test-Header': 'default'
        })

    def test_nesting_temporary_headers(self):
        proxy_client = get_mocked_ai_core_client()
        default_headers = proxy_client.request_header

        proxy_client.set_headers_addition({
            'X-Test-Header': 'default'
        })

        with temporary_headers_addition({
            'X-Test-Header': 'override', 'X-New-Header': 'new'
        }):
            with temporary_headers_addition({
                'X-Test-Header': 'override-2', 'X-Another-Header': 'another'
            }):
                self.assertEqual(proxy_client.request_header, {
                    **default_headers,
                    'X-Test-Header': 'override-2',
                    'X-Another-Header': 'another'
                })

            self.assertEqual(proxy_client.request_header, {
                **default_headers,
                'X-Test-Header': 'override',
                'X-New-Header': 'new'
            })

        self.assertEqual(proxy_client.request_header, {
            **default_headers,
            'X-Test-Header': 'default'
        })

    def test_setting_temporary_headers_multi_threaded(self):
        proxy_client = get_mocked_ai_core_client()
        default_headers = proxy_client.request_header

        proxy_client.set_headers_addition({
            'X-Test-Header': 'default'
        })

        def task1():
            with temporary_headers_addition({
                'X-Test-Header': 'override_thread1',
                'X-New-Header': 'new_thread1'
            }):
                self.assertEqual(proxy_client.request_header, {
                    **default_headers,
                    'X-Test-Header': 'override_thread1',
                    'X-New-Header': 'new_thread1'
                })

        def task2():
            with temporary_headers_addition({
                'X-Test-Header': 'override_thread2',
                'X-New-Header': 'new_thread2'
            }):
                self.assertEqual(proxy_client.request_header, {
                    **default_headers,
                    'X-Test-Header': 'override_thread2',
                    'X-New-Header': 'new_thread2'
                })

        threads = []

        for _ in range(10):
            threads.append(threading.Thread(target=task1))
            threads.append(threading.Thread(target=task2))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(proxy_client.request_header, {
            **default_headers,
            'X-Test-Header': 'default'
        })
