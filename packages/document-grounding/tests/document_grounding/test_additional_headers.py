import unittest
from unittest.mock import patch

from sap_ai_sdk_proxy.gen_ai_hub_proxy.client import temporary_headers_addition
from sap_ai_sdk_document_grounding.clients.pipeline_api_client import PipelineAPIClient
from sap_ai_sdk_document_grounding.clients.retrieval_api_client import RetrievalAPIClient
from sap_ai_sdk_document_grounding.clients.vector_api_client import VectorAPIClient

from tests.mock import get_mocked_ai_core_client


class TestClientHeaderInjection(unittest.TestCase):
    """Test that document-grounding clients properly use GenAIHubRestClient for header injection."""

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='test')

    def tearDown(self):
        # get_mocked_ai_core_client returns a cached per-version singleton, so
        # instance-level header additions must be reset to avoid leaking into
        # sibling tests that assert on exact request kwargs.
        self.proxy_client.set_headers_addition({})

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_pipeline_api_client_injects_headers(self, mock_get):
        """Test PipelineAPIClient passes headers via GenAIHubRestClient."""
        mock_get.return_value = {'count': 0, 'resources': []}
        client = PipelineAPIClient(proxy_client=self.proxy_client)

        self.proxy_client.set_headers_addition({'X-Instance': 'value1'})
        with temporary_headers_addition({'X-Temp': 'value2'}):
            client.get_pipelines()

        call_kwargs = mock_get.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertEqual(call_kwargs['headers']['X-Instance'], 'value1')
        self.assertEqual(call_kwargs['headers']['X-Temp'], 'value2')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_retrieval_api_client_injects_headers(self, mock_get):
        """Test RetrievalAPIClient passes headers via GenAIHubRestClient."""
        mock_get.return_value = {'count': 0, 'resources': []}
        client = RetrievalAPIClient(proxy_client=self.proxy_client)

        self.proxy_client.set_headers_addition({'X-Instance': 'value1'})
        with temporary_headers_addition({'X-Temp': 'value2'}):
            client.get_data_repositories()

        call_kwargs = mock_get.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertEqual(call_kwargs['headers']['X-Instance'], 'value1')
        self.assertEqual(call_kwargs['headers']['X-Temp'], 'value2')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_vector_api_client_injects_headers(self, mock_get):
        """Test VectorAPIClient passes headers via GenAIHubRestClient."""
        mock_get.return_value = {'count': 0, 'resources': []}
        client = VectorAPIClient(proxy_client=self.proxy_client)

        self.proxy_client.set_headers_addition({'X-Instance': 'value1'})
        with temporary_headers_addition({'X-Temp': 'value2'}):
            client.get_collections()

        call_kwargs = mock_get.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertEqual(call_kwargs['headers']['X-Instance'], 'value1')
        self.assertEqual(call_kwargs['headers']['X-Temp'], 'value2')


if __name__ == '__main__':
    unittest.main()
