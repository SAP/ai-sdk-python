import unittest
from unittest.mock import patch

from ai_api_client_sdk.exception import AIAPIServerException

from gen_ai_hub.prompt_registry.client import (PromptTemplateClient, OrchestrationConfigClient,
                                               PATH_SCENARIOS, PATH_PROMPT_TEMPLATES, CONTENT_TYPE_JSON_,
                                               PATH_REGISTRY_CONFIG, PATH_REGISTRY_SCENARIOS, )
from gen_ai_hub.prompt_registry.models.prompt_template import (PromptTemplateSpec, PromptTemplate,
                                                               PromptTemplateSubstitutionResponse)
from tests.mock import (TEMPLATE_NAME, TEMPLATE_ID, VERSION, SCENARIO, TEMPLATE_YAML, ORCHESTRATION_CONFIG_NAME,
                        ORCHESTRATION_CONFIG_ID, TEMPLATE_POST_RESPONSE, TEMPLATE_LIST_RESPONSE, TEMPLATE_GET_RESPONSE,
                        TEMPLATE_DELETE_RESPONSE, TEMPLATE_SUBSTITUTION_REQUEST, TEMPLATE_SUBSTITUTION_RESPONSE,
                        ORCHESTRATION_CONFIG_POST_RESPONSE, ORCHESTRATION_CONFIG_LIST_RESPONSE,
                        ORCHESTRATION_CONFIG_GET_RESPONSE, ORCHESTRATION_CONFIG_DELETE_RESPONSE,
                        ORCHESTRATION_CONFIG_YAML, ORCHESTRATION_CONFIG_LIST_RESPONSE_WITH_SPEC,
                        get_mocked_ai_core_client)
from gen_ai_hub.prompt_registry.models.orchestration_config import (OrchestrationConfigDeleteResponse,
                                                                    OrchestrationConfigGetResponse,
                                                                    OrchestrationConfigPostResponse,
                                                                    OrchestrationConfigListResponse)
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.models.response_format import ResponseFormatJsonObject
from gen_ai_hub.orchestration_v2.models.tools import FunctionTool
from gen_ai_hub.orchestration_v2.models.multimodal_items import ImageItem


class TestPromptTemplateClient(unittest.TestCase):

    def setUp(self):
        proxy_client = get_mocked_ai_core_client(client_id='test')
        self.test_client = PromptTemplateClient(proxy_client=proxy_client)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_prompt_template(self, mock_post):
        spec = PromptTemplateSpec(template=[PromptTemplate(role='system', content='Hello, world!')])
        mock_post.return_value = TEMPLATE_POST_RESPONSE.model_dump()

        response = self.test_client.create_prompt_template(scenario=SCENARIO, name=TEMPLATE_NAME, version=VERSION,
                                                           prompt_template_spec=spec)

        self.assertEqual(response, TEMPLATE_POST_RESPONSE)
        mock_post.assert_called_once_with(path=PATH_PROMPT_TEMPLATES,
                                          body={ 'name': TEMPLATE_NAME, 'version': VERSION, 'scenario': SCENARIO,
                                                 'spec': spec.model_dump(by_alias=True, exclude_none=True)},
                                          convert_body_to_camel_case=False
                                          )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_prompt_template_with_response_format(self, mock_post):
        spec = PromptTemplateSpec(template=[PromptTemplate(role='system', content='Hello, world!'),
                                            PromptTemplate(role='user',
                                                           content='What is your name? Answer in JSON format.')],
                                  response_format=ResponseFormatJsonObject())
        mock_post.return_value = TEMPLATE_POST_RESPONSE.model_dump()

        response = self.test_client.create_prompt_template(scenario=SCENARIO, name=TEMPLATE_NAME, version=VERSION,
                                                           prompt_template_spec=spec)

        self.assertEqual(response, TEMPLATE_POST_RESPONSE)
        mock_post.assert_called_once_with(path=PATH_PROMPT_TEMPLATES,
                                          body={'name': TEMPLATE_NAME, 'version': VERSION, 'scenario': SCENARIO,
                                                'spec': spec.model_dump(by_alias=True, exclude_none=True)},
                                          convert_body_to_camel_case=False
                                          )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_prompt_template_with_tool(self, mock_post):
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        tool = FunctionTool.from_function(add)
        spec = PromptTemplateSpec(template=[PromptTemplate(role="user", content='3 + 6')],
                                  tools=[tool])
        mock_post.return_value = TEMPLATE_POST_RESPONSE.model_dump()

        response = self.test_client.create_prompt_template(scenario=SCENARIO, name=TEMPLATE_NAME, version=VERSION,
                                                           prompt_template_spec=spec)

        self.assertEqual(response, TEMPLATE_POST_RESPONSE)
        mock_post.assert_called_once_with(path=PATH_PROMPT_TEMPLATES,
                                          body={'name': TEMPLATE_NAME, 'version': VERSION, 'scenario': SCENARIO,
                                                'spec': spec.model_dump(by_alias=True, exclude_none=True)},
                                          convert_body_to_camel_case=False
                                          )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_prompt_template_with_image_input(self, mock_post):
        spec = PromptTemplateSpec(template=[PromptTemplate(role="user", content='Whai is in the image?'),
                                            PromptTemplate(role="user",
                                                           content=[ImageItem(url="https://example.com/image.png")])])
        mock_post.return_value = TEMPLATE_POST_RESPONSE.model_dump()

        response = self.test_client.create_prompt_template(scenario=SCENARIO, name=TEMPLATE_NAME, version=VERSION,
                                                           prompt_template_spec=spec)

        self.assertEqual(response, TEMPLATE_POST_RESPONSE)
        mock_post.assert_called_once_with(path=PATH_PROMPT_TEMPLATES,
                                          body={'name': TEMPLATE_NAME, 'version': VERSION, 'scenario': SCENARIO,
                                                'spec': spec.model_dump(by_alias=True, exclude_none=True)},
                                          convert_body_to_camel_case=False
                                          )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_prompt_templates(self, mock_get):
        query_params = {'scenario': SCENARIO, 'name': TEMPLATE_ID, 'version': VERSION,
                        'retrieve': None, 'include_spec': None}
        mock_get.return_value = TEMPLATE_LIST_RESPONSE.model_dump()

        response = self.test_client.get_prompt_templates(query_params['scenario'], query_params['name'],
                                                         query_params['version'])
        self.assertEqual(response, TEMPLATE_LIST_RESPONSE)
        mock_get.assert_called_once_with(path=PATH_PROMPT_TEMPLATES, params=query_params)

    @patch('ai_api_client_sdk.helpers.rest_client.requests.Session')
    def test_get_prompt_templates_error(self, mock_handle_request_session):
        mock_handle_request_session.raise_for_status.side_effect = (
            AIAPIServerException(description='Error', error_message='Resource not found', status_code=404))

        with self.assertRaises(AIAPIServerException):
            self.test_client.get_prompt_templates(scenario=SCENARIO, name='XXX', version=VERSION)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_prompt_template_by_id(self, mock_get):
        mock_get.return_value = TEMPLATE_GET_RESPONSE.model_dump()

        response = self.test_client.get_prompt_template_by_id(TEMPLATE_ID)
        self.assertEqual(response, TEMPLATE_GET_RESPONSE)
        mock_get.assert_called_once_with(path=f'{PATH_PROMPT_TEMPLATES}/{TEMPLATE_ID}')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_prompt_template_history(self, mock_get):
        mock_get.return_value = TEMPLATE_LIST_RESPONSE.model_dump()

        response = self.test_client.get_prompt_template_history(SCENARIO, TEMPLATE_NAME, VERSION)
        self.assertEqual(response, TEMPLATE_LIST_RESPONSE)
        mock_get.assert_called_once_with(path=f'{PATH_SCENARIOS}/{SCENARIO}/promptTemplates/{TEMPLATE_NAME}/'
                                              f'versions/{VERSION}/history')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.delete')
    def test_delete_prompt_template_by_id(self, mock_delete):
        mock_delete.return_value = TEMPLATE_DELETE_RESPONSE.model_dump()

        response = self.test_client.delete_prompt_template_by_id(TEMPLATE_ID)
        self.assertEqual(response, TEMPLATE_DELETE_RESPONSE)
        mock_delete.assert_called_once_with(path=f'{PATH_PROMPT_TEMPLATES}/{TEMPLATE_ID}')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_fill_prompt_template_by_id(self, mock_post):
        mock_template = PromptTemplate(role='system', content='Hello, world!')
        mock_response = PromptTemplateSubstitutionResponse(parsed_prompt=[mock_template],
                                                           resource=TEMPLATE_GET_RESPONSE)
        mock_post.return_value = mock_response.model_dump()

        response = self.test_client.fill_prompt_template_by_id(template_id=TEMPLATE_ID,
                                                               input_params=TEMPLATE_SUBSTITUTION_REQUEST.input_params,
                                                               metadata=True)
        self.assertEqual(response, mock_response)
        mock_post.assert_called_once_with(
            path=f'{PATH_PROMPT_TEMPLATES}/{TEMPLATE_ID}/substitution',
            headers={"Content-Type": CONTENT_TYPE_JSON_},
            body=TEMPLATE_SUBSTITUTION_REQUEST.model_dump(by_alias=True),
            params={'metadata': True},
            convert_body_to_camel_case=False
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_fill_prompt_template(self, mock_post):
        mock_post.return_value = TEMPLATE_SUBSTITUTION_RESPONSE.model_dump()

        response = self.test_client.fill_prompt_template(SCENARIO, TEMPLATE_NAME, VERSION,
                                                         TEMPLATE_SUBSTITUTION_REQUEST.input_params)
        self.assertEqual(response, TEMPLATE_SUBSTITUTION_RESPONSE)
        mock_post.assert_called_once_with(
            path= f'{PATH_SCENARIOS}/{SCENARIO}/promptTemplates/{TEMPLATE_NAME}/versions/{VERSION}/substitution',
            headers={"Content-Type": CONTENT_TYPE_JSON_},
            body=TEMPLATE_SUBSTITUTION_REQUEST.model_dump(by_alias=True),
            convert_body_to_camel_case=False
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_import_prompt_template(self, mock_post):
        mock_post.return_value = TEMPLATE_POST_RESPONSE.model_dump()

        binary_file_content = TEMPLATE_YAML.encode('utf-8')
        response = self.test_client.import_prompt_template(binary_file_content)
        self.assertEqual(response, TEMPLATE_POST_RESPONSE)
        mock_post.assert_called_once_with(path=f'{PATH_PROMPT_TEMPLATES}/import', files={'file': binary_file_content})

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_export_prompt_template(self, mock_get):
        mock_get.return_value = TEMPLATE_YAML.encode('utf-8')

        response = self.test_client.export_prompt_template(TEMPLATE_ID)
        self.assertEqual(response, TEMPLATE_YAML.encode('utf-8'))
        mock_get.assert_called_once_with(path=f'{PATH_PROMPT_TEMPLATES}/{TEMPLATE_ID}/export',
                                         return_bytes_content=True)

class TestOrchestrationConfigClient(unittest.TestCase):

    def setUp(self):
        proxy_client = get_mocked_ai_core_client(client_id='test')
        self.test_client = OrchestrationConfigClient(proxy_client=proxy_client)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_orchestration_config(self, mock_post):
        spec = OrchestrationConfig(
            modules=ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content="Hello, World!")]),
                    model=LLMModelDetails(name="gpt-4o-mini")
                )
            )
        )
        mock_post.return_value = ORCHESTRATION_CONFIG_POST_RESPONSE

        response = self.test_client.create_orchestration_config(scenario=SCENARIO, name=ORCHESTRATION_CONFIG_NAME, version=VERSION,
                                                                spec=spec)

        self.assertIsInstance(response, OrchestrationConfigPostResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_POST_RESPONSE)
        mock_post.assert_called_once_with(path=PATH_REGISTRY_CONFIG,
                                          body={ 'name': ORCHESTRATION_CONFIG_NAME, 'version': VERSION, 'scenario': SCENARIO,
                                                 'spec': spec.model_dump()},
                                          convert_body_to_camel_case=False
                                          )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_orchestration_configs(self, mock_get):
        query_params = {'scenario': SCENARIO, 'name': ORCHESTRATION_CONFIG_NAME, 'version': VERSION,
                        'retrieve': None, 'include_spec': None, 'resolve_template_ref': None}
        mock_get.return_value = ORCHESTRATION_CONFIG_LIST_RESPONSE

        response = self.test_client.get_orchestration_configs(**query_params)
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_LIST_RESPONSE)
        mock_get.assert_called_once_with(path=PATH_REGISTRY_CONFIG, params=query_params,
                                         convert_params_to_camel_case=False)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_orchestration_configs_with_spec(self, mock_get):
        query_params = {'scenario': SCENARIO, 'name': ORCHESTRATION_CONFIG_NAME, 'version': VERSION,
                        'retrieve': None, 'include_spec': True, 'resolve_template_ref': None}
        mock_get.return_value = ORCHESTRATION_CONFIG_LIST_RESPONSE_WITH_SPEC

        response = self.test_client.get_orchestration_configs(**query_params)
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_LIST_RESPONSE_WITH_SPEC)
        mock_get.assert_called_once_with(path=PATH_REGISTRY_CONFIG, params=query_params,
                                         convert_params_to_camel_case=False)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_orchestration_config_by_id(self, mock_get):
        mock_get.return_value = ORCHESTRATION_CONFIG_GET_RESPONSE

        response = self.test_client.get_orchestration_config_by_id(ORCHESTRATION_CONFIG_ID, resolve_template_ref=False)
        self.assertIsInstance(response, OrchestrationConfigGetResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_GET_RESPONSE)
        mock_get.assert_called_once_with(path=f'{PATH_REGISTRY_CONFIG}/{ORCHESTRATION_CONFIG_ID}',
                                         params={'resolve_template_ref': False},
                                         convert_params_to_camel_case=False)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_orchestration_config_history(self, mock_get):
        mock_get.return_value = ORCHESTRATION_CONFIG_LIST_RESPONSE

        response = self.test_client.get_orchestration_config_history(scenario=SCENARIO, name=ORCHESTRATION_CONFIG_NAME,
                                                                     version=VERSION, include_spec=None,
                                                                     resolve_template_ref=None,
                                                                     )
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_LIST_RESPONSE)
        mock_get.assert_called_once_with(path=f"{PATH_REGISTRY_SCENARIOS}/{SCENARIO}/orchestrationConfigs/"
                                              f"{ORCHESTRATION_CONFIG_NAME}/versions/{VERSION}/history",
                                         params={'include_spec': None, 'resolve_template_ref': None},
                                         convert_params_to_camel_case=False)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_orchestration_config_history_with_spec(self, mock_get):
        mock_get.return_value = ORCHESTRATION_CONFIG_LIST_RESPONSE_WITH_SPEC

        response = self.test_client.get_orchestration_config_history(scenario=SCENARIO, name=ORCHESTRATION_CONFIG_NAME,
                                                                     version=VERSION, include_spec=True,
                                                                     resolve_template_ref=None,
                                                                     )
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_LIST_RESPONSE_WITH_SPEC)
        mock_get.assert_called_once_with(path=f"{PATH_REGISTRY_SCENARIOS}/{SCENARIO}/orchestrationConfigs/"
                                              f"{ORCHESTRATION_CONFIG_NAME}/versions/{VERSION}/history",
                                         params={'include_spec': True, 'resolve_template_ref': None},
                                         convert_params_to_camel_case=False)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.delete')
    def test_delete_orchestration_config_by_id(self, mock_delete):
        mock_delete.return_value = ORCHESTRATION_CONFIG_DELETE_RESPONSE

        response = self.test_client.delete_orchestration_config_by_id(ORCHESTRATION_CONFIG_ID)
        self.assertIsInstance(response, OrchestrationConfigDeleteResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_DELETE_RESPONSE)
        mock_delete.assert_called_once_with(path=f'{PATH_REGISTRY_CONFIG}/{ORCHESTRATION_CONFIG_ID}')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_import_orchestration_config(self, mock_post):
        mock_post.return_value = ORCHESTRATION_CONFIG_POST_RESPONSE

        binary_file_content = ORCHESTRATION_CONFIG_YAML.encode('utf-8')
        response = self.test_client.import_orchestration_config(binary_file_content)
        self.assertIsInstance(response, OrchestrationConfigPostResponse)
        self.assertEqual(response.model_dump(), ORCHESTRATION_CONFIG_POST_RESPONSE)
        mock_post.assert_called_once_with(path=f'{PATH_REGISTRY_CONFIG}/import', files={'file': binary_file_content})

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_export_orchestration_config(self, mock_get):
        mock_get.return_value = ORCHESTRATION_CONFIG_YAML.encode('utf-8')

        response = self.test_client.export_orchestration_config(ORCHESTRATION_CONFIG_ID)
        self.assertEqual(response, ORCHESTRATION_CONFIG_YAML.encode('utf-8'))
        mock_get.assert_called_once_with(path=f'{PATH_REGISTRY_CONFIG}/{ORCHESTRATION_CONFIG_ID}/export',
                                         return_bytes_content=True)