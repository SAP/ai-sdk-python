import unittest
from unittest.mock import MagicMock

from sap_ai_sdk_proxy.gen_ai_hub_proxy.client import GenAIHubRestClient


class TestGenAIHubRestClient(unittest.TestCase):
    """Unit tests for GenAIHubRestClient header injection logic."""

    def setUp(self):
        self.mock_rest_client = MagicMock()
        self.mock_proxy_client = MagicMock()
        self.mock_proxy_client.ai_core_client.rest_client = self.mock_rest_client
        self.mock_proxy_client.get_additional_headers.return_value = {'X-Custom': 'custom-value', 'X-Another': 'another-value'}
        self.rest_client = GenAIHubRestClient(self.mock_proxy_client)

    def test_get_injects_headers(self):
        """Test GET requests include additional headers."""
        self.rest_client.get('/test-path', params={'key': 'value'})

        self.mock_rest_client.get.assert_called_once_with(
            path='/test-path',
            params={'key': 'value'},
            headers={'X-Custom': 'custom-value', 'X-Another': 'another-value'}
        )

    def test_post_injects_headers(self):
        """Test POST requests include additional headers."""
        self.rest_client.post('/test-path', body={'data': 'test'})

        self.mock_rest_client.post.assert_called_once_with(
            path='/test-path',
            body={'data': 'test'},
            headers={'X-Custom': 'custom-value', 'X-Another': 'another-value'}
        )

    def test_delete_injects_headers(self):
        """Test DELETE requests include additional headers."""
        self.rest_client.delete('/test-path')

        self.mock_rest_client.delete.assert_called_once_with(
            path='/test-path',
            headers={'X-Custom': 'custom-value', 'X-Another': 'another-value'}
        )

    def test_patch_injects_headers(self):
        """Test PATCH requests include additional headers."""
        self.rest_client.patch('/test-path', body={'update': 'data'})

        self.mock_rest_client.patch.assert_called_once_with(
            path='/test-path',
            body={'update': 'data'},
            headers={'X-Custom': 'custom-value', 'X-Another': 'another-value'}
        )

    def test_explicit_headers_merged(self):
        """Test that explicit headers are merged with additional headers."""
        self.rest_client.get('/test-path', headers={'X-Explicit': 'explicit-value'})

        self.mock_rest_client.get.assert_called_once()
        call_kwargs = self.mock_rest_client.get.call_args[1]
        self.assertEqual(call_kwargs['headers']['X-Custom'], 'custom-value')
        self.assertEqual(call_kwargs['headers']['X-Another'], 'another-value')
        self.assertEqual(call_kwargs['headers']['X-Explicit'], 'explicit-value')

    def test_explicit_headers_override_additional_headers(self):
        """Test that explicit headers override additional headers."""
        self.rest_client.get('/test-path', headers={'X-Custom': 'overridden'})

        call_kwargs = self.mock_rest_client.get.call_args[1]
        self.assertEqual(call_kwargs['headers']['X-Custom'], 'overridden')

    def test_kwargs_propagated(self):
        """Test that all kwargs are propagated to underlying rest_client."""
        self.rest_client.get('/test-path', params={'p': 1}, return_bytes_content=True)

        call_kwargs = self.mock_rest_client.get.call_args[1]
        self.assertEqual(call_kwargs['params'], {'p': 1})
        self.assertTrue(call_kwargs['return_bytes_content'])

    def test_no_headers_when_no_additional_headers(self):
        """Test that no headers kwarg is added when there are no additional headers."""
        self.mock_proxy_client.get_additional_headers.return_value = {}
        self.rest_client.get('/test-path', params={'key': 'value'})

        self.mock_rest_client.get.assert_called_once_with(
            path='/test-path',
            params={'key': 'value'}
        )


if __name__ == '__main__':
    unittest.main()
