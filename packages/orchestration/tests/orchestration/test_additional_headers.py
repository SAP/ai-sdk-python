import unittest
from unittest.mock import patch, MagicMock

from sap_ai_sdk_proxy.gen_ai_hub_proxy.client import temporary_headers_addition
from sap_ai_sdk_orchestration.service import OrchestrationService as OrchestrationServiceV2
from sap_ai_sdk_orchestration.models.template import Template as TemplateV2, PromptTemplatingModuleConfig
from sap_ai_sdk_orchestration.models.config import OrchestrationConfig as OrchestrationConfigV2, ModuleConfig
from sap_ai_sdk_orchestration.models.llm_model_details import LLMModelDetails
from sap_ai_sdk_orchestration.models.message import UserMessage

from tests.mock import get_mocked_ai_core_client


class TestClientHeaderInjection(unittest.TestCase):
    """Test that OrchestrationService V2 properly injects headers."""

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='test')

    def tearDown(self):
        # get_mocked_ai_core_client returns a cached per-version singleton, so
        # instance-level header additions must be reset to avoid leaking into
        # sibling tests that assert on exact request kwargs.
        self.proxy_client.set_headers_addition({})

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
