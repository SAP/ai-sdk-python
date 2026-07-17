import unittest
from unittest.mock import MagicMock, patch

from gen_ai_hub.proxy.gen_ai_hub_proxy.client import GenAIHubRestClient, temporary_headers_addition
from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.document_grounding.clients.pipeline_api_client import PipelineAPIClient
from gen_ai_hub.document_grounding.clients.retrieval_api_client import RetrievalAPIClient
from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient
from gen_ai_hub.orchestration.service import OrchestrationService
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.template import Template
from gen_ai_hub.orchestration.models.message import Message
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService as OrchestrationServiceV2
from gen_ai_hub.orchestration_v2.models.template import Template as TemplateV2, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig as OrchestrationConfigV2, ModuleConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import UserMessage
from tests.mock import get_mocked_ai_core_client


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


class TestClientHeaderInjection(unittest.TestCase):
    """Test that each client properly uses GenAIHubRestClient for header injection."""

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='test')

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

    @patch('httpx.Client.post')
    def test_orchestration_service_injects_headers(self, mock_post):
        """Test OrchestrationService passes headers via request_header."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'request_id': 'test-id',
            'module_results': {},
            'orchestration_result': {
                'id': 'test',
                'object': 'chat.completion',
                'created': 1234567890,
                'model': 'gpt-4',
                'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Hello'}, 'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        config = OrchestrationConfig(
            llm=LLM(name='gpt-4'),
            template=Template(messages=[Message(role='user', content='Hello')])
        )
        service = OrchestrationService(
            api_url='https://test.example.com',
            proxy_client=self.proxy_client,
            config=config
        )

        self.proxy_client.set_headers_addition({'X-Instance': 'value1'})
        with temporary_headers_addition({'X-Temp': 'value2'}):
            service.run()

        call_kwargs = mock_post.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertEqual(call_kwargs['headers']['X-Instance'], 'value1')
        self.assertEqual(call_kwargs['headers']['X-Temp'], 'value2')

    @patch('httpx.Client.post')
    def test_orchestration_service_v2_injects_headers(self, mock_post):
        """Test OrchestrationService V2 passes headers via request_header."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'request_id': 'test-id',
            'intermediate_results': {},
            'final_result': {
                'id': 'test',
                'object': 'chat.completion',
                'created': 1234567890,
                'model': 'gpt-4',
                'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Hello'}, 'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        config = OrchestrationConfigV2(
            modules=ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=TemplateV2(template=[UserMessage(content='Hello')]),
                    model=LLMModelDetails(name='gpt-4')
                )
            )
        )
        service = OrchestrationServiceV2(
            api_url='https://test.example.com',
            proxy_client=self.proxy_client,
            config=config
        )

        self.proxy_client.set_headers_addition({'X-Instance': 'value1'})
        with temporary_headers_addition({'X-Temp': 'value2'}):
            service.run()

        call_kwargs = mock_post.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertEqual(call_kwargs['headers']['X-Instance'], 'value1')
        self.assertEqual(call_kwargs['headers']['X-Temp'], 'value2')


if __name__ == '__main__':
    unittest.main()
