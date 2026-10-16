import unittest
from unittest.mock import patch

from sap_ai_sdk_proxy.gen_ai_hub_proxy.client import temporary_headers_addition
from sap_ai_sdk_prompt_registry.client import PromptTemplateClient

from tests.mock import get_mocked_ai_core_client


class TestClientHeaderInjection(unittest.TestCase):
    """Test that PromptTemplateClient properly uses GenAIHubRestClient for header injection."""

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='test')

    def tearDown(self):
        # get_mocked_ai_core_client returns a cached per-version singleton, so
        # instance-level header additions must be reset to avoid leaking into
        # sibling tests that assert on exact request kwargs.
        self.proxy_client.set_headers_addition({})

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_prompt_template_client_injects_headers(self, mock_get):
        """Test PromptTemplateClient passes headers via GenAIHubRestClient."""
        mock_get.return_value = {'count': 0, 'resources': []}
        client = PromptTemplateClient(proxy_client=self.proxy_client)

        self.proxy_client.set_headers_addition({'X-Instance': 'value1'})
        with temporary_headers_addition({'X-Temp': 'value2'}):
            client.get_prompt_templates(scenario='s', name='n', version='v')

        call_kwargs = mock_get.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertEqual(call_kwargs['headers']['X-Instance'], 'value1')
        self.assertEqual(call_kwargs['headers']['X-Temp'], 'value2')


if __name__ == '__main__':
    unittest.main()
