import unittest
from typing import cast

from ai_api_client_sdk.exception import AIAPIServerException

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.prompt_registry.client import PromptTemplateClient, OrchestrationConfigClient
from gen_ai_hub.prompt_registry.models.prompt_template import (PromptTemplate,
                                                               PromptTemplateSpec,
                                                               PromptTemplateListResponse,
                                                               PromptTemplatePostResponse,
                                                               PromptTemplateGetResponse,
                                                               PromptTemplateDeleteResponse,
                                                               PromptTemplateSubstitutionResponse)
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

from gen_ai_hub.proxy import get_proxy_client
from tests.mock import TEMPLATE_YAML, ORCHESTRATION_CONFIG_YAML
from integration_tests.test_helpers import retry_on_429_or_503


class TestPromptTemplate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scenario = "integration_test_scenario"
        cls.template_name = "test_prompt_template"
        cls.version = "0.1.0"
        cls.spec = PromptTemplateSpec(template=[PromptTemplate(role="system", content="You are a system under test.")])
        proxy_client = cast(GenAIHubProxyClient, get_proxy_client())
        cls.client = PromptTemplateClient(proxy_client=proxy_client)

    @classmethod
    def tearDownClass(cls):
        prompt_templates = cls.client.get_prompt_templates(scenario=cls.scenario, name=cls.template_name,
                                                           version=cls.version)
        for template in prompt_templates.resources:
            cls.client.delete_prompt_template_by_id(template.id)

    def setUp(self):
        response = self.client.get_prompt_templates(scenario=self.scenario, name=self.template_name,
                                                    version=self.version)
        if response.count > 0:
            self.template_id = response.resources[0].id
        else:
            self.template_id = self.create_prompt_template(self.template_name)

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def create_prompt_template(self, template_name: str) -> str:
        spec = PromptTemplateSpec(template=[PromptTemplate(role="user", content="{{ ?user_input }}")])
        template_id = self.client.create_prompt_template(scenario=self.scenario, name=template_name,
                                                         version=self.version, prompt_template_spec=spec).id
        return template_id

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_create_prompt_template(self):
        response = self.client.create_prompt_template(scenario=self.scenario, name=self.template_name,
                                                      version=self.version, prompt_template_spec=self.spec)
        self.assertIsInstance(response, PromptTemplatePostResponse)

    def test_get_prompt_templates(self):
        response = self.client.get_prompt_templates(scenario=self.scenario, name=self.template_name,
                                                    version=self.version)
        self.assertIsInstance(response, PromptTemplateListResponse)
        self.assertGreater(response.count, 0, "No prompt templates found")

    def test_get_prompt_template_by_id(self):
        response = self.client.get_prompt_template_by_id(self.template_id)
        self.assertIsInstance(response, PromptTemplateGetResponse)
        self.assertEqual(response.id, self.template_id)

    def test_get_prompt_template_by_id_not_found(self):
        with self.assertRaises(AIAPIServerException):
            self.client.get_prompt_template_by_id("non_existent_id")

    def test_get_prompt_template_history(self):
        response = self.client.get_prompt_template_history(scenario=self.scenario, name=self.template_name,
                                                           version=self.version)
        self.assertIsInstance(response, PromptTemplateListResponse)

    def test_delete_prompt_template_by_id(self):
        template_id = self.client.create_prompt_template(scenario=self.scenario, name=self.template_name + '_delete',
                                                         version=self.version, prompt_template_spec=self.spec).id
        response = self.client.delete_prompt_template_by_id(template_id)
        self.assertIsInstance(response, PromptTemplateDeleteResponse)

    def test_import_prompt_template(self):
        response = self.client.import_prompt_template(TEMPLATE_YAML.encode('utf-8'))
        self.assertIsInstance(response, PromptTemplatePostResponse)

        # cleanup
        response = self.client.delete_prompt_template_by_id(response.id)
        self.assertIn("deleted successfully", response.message, "Template was not deleted")

    def test_export_prompt_template(self):
        response = self.client.export_prompt_template(self.template_id)
        self.assertEqual(type(response), bytes, "Exported template is not a byte stream")

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_fill_prompt_template_by_id(self):
        template_id = self.create_prompt_template(template_name='test_substitute')
        response = self.client.fill_prompt_template_by_id(template_id=template_id, input_params={"user_input": "Howdy"})
        self.assertIsInstance(response, PromptTemplateSubstitutionResponse)

        # cleanup
        response = self.client.delete_prompt_template_by_id(template_id)
        self.assertIn("deleted successfully", response.message, "Template was not deleted")

    def test_fill_prompt_template(self):
        template_id = self.create_prompt_template(template_name='test_substitute')
        response = self.client.fill_prompt_template(scenario=self.scenario, name='test_substitute',
                                                    version=self.version, metadata=True,
                                                    input_params={"user_input": "Howdy"},)
        self.assertIsInstance(response, PromptTemplateSubstitutionResponse)
        self.assertTrue(response.resource)

        # cleanup
        response = self.client.delete_prompt_template_by_id(template_id)
        self.assertIn("deleted successfully", response.message, "Template was not deleted")

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_create_prompt_template_with_response_format(self):
        spec_with_response_format = PromptTemplateSpec(template=[
            PromptTemplate(role="user", content="Who is thw first man on the moon? Answer in json format.")
        ],
        response_format=ResponseFormatJsonObject())
        response = self.client.create_prompt_template(scenario=self.scenario, name=self.template_name,
                                                      version=self.version,
                                                      prompt_template_spec=spec_with_response_format)
        self.assertIsInstance(response, PromptTemplatePostResponse)

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_create_prompt_template_with_tools(self):
        def modify_string(a: str) -> str:
            """Modify a string by adding 'Hello' to the beginning."""
            return f'Hello {a}'

        tool = FunctionTool.from_function(modify_string)
        spec_with_tools = PromptTemplateSpec(template=[
            PromptTemplate(role="user", content="Modify string using the function in tools. String: {{ ?string }} ")
        ],
        tools=[tool])
        response = self.client.create_prompt_template(scenario=self.scenario, name=self.template_name,
                                                      version=self.version,
                                                      prompt_template_spec=spec_with_tools)
        self.assertIsInstance(response, PromptTemplatePostResponse)

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_create_prompt_template_with_image_input(self):
        data_url = (
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAE0lEQVR4nGP8z4APMOGVZRip0gBBLAETee26JgAAAABJRU5ErkJggg=='
        )
        spec = PromptTemplateSpec(
            template=[
                PromptTemplate(role="user", content=['What color is this image?', ImageItem(url=data_url)])
            ]
        )

        response = self.client.create_prompt_template(scenario=self.scenario, name=self.template_name,
                                                      version=self.version,
                                                      prompt_template_spec=spec)
        self.assertIsInstance(response, PromptTemplatePostResponse)


class TestOrchestrationConfigClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scenario = "integration_test_scenario"
        cls.config_name = "test_config"
        cls.version = "0.1.0"
        cls.config_spec = OrchestrationConfig(
            modules=ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(
                    prompt=Template(template=[UserMessage(content="Hello, World!")]),
                    model=LLMModelDetails(name="gpt-4o-mini")
                )
            )
        )
        proxy_client = cast(GenAIHubProxyClient, get_proxy_client())
        cls.client = OrchestrationConfigClient(proxy_client=proxy_client)

    @classmethod
    def tearDownClass(cls):
        configs = cls.client.get_orchestration_configs(scenario=cls.scenario, name=cls.config_name,
                                                       version=cls.version)
        for config in configs.resources:
            cls.client.delete_orchestration_config_by_id(config.id)

    def setUp(self):
        response = self.client.get_orchestration_configs(scenario=self.scenario, name=self.config_name,
                                                         version=self.version)
        if response.count > 0:
            self.config = response.resources[0]
        else:
            self.config = self.create_orchestration_config(self.config_name)

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def create_orchestration_config(self, template_name: str) -> OrchestrationConfigPostResponse:
        config = self.client.create_orchestration_config(scenario=self.scenario,
                                                         name=template_name,
                                                         version=self.version,
                                                         spec=self.config_spec)
        return config

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_create_orchestration_config(self):
        response = self.client.create_orchestration_config(scenario=self.scenario, name=self.config_name,
                                                           version=self.version, spec=self.config_spec)
        self.assertIsInstance(response, OrchestrationConfigPostResponse)

    def test_get_orchestration_configs_without_spec(self):
        response = self.client.get_orchestration_configs(scenario=self.scenario, name=self.config_name,
                                                         version=self.version)
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertGreater(response.count, 0)
        self.assertIsNone(response.resources[0].spec)

    def test_get_orchestration_configs_with_spec(self):
        response = self.client.get_orchestration_configs(scenario=self.scenario, name=self.config_name,
                                                         version=self.version, include_spec=True)
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertGreater(response.count, 0)
        self.assertIsNotNone(response.resources[0].spec)

    def test_get_orchestration_config_by_id(self):
        response = self.client.get_orchestration_config_by_id(self.config.id)
        self.assertIsInstance(response, OrchestrationConfigGetResponse)
        self.assertEqual(response.id, self.config.id)
        self.assertIsNotNone(response.spec)
        self.assertEqual(response.spec.modules.prompt_templating.model.name, "gpt-4o-mini")

    def test_get_orchestration_config_by_id_not_found(self):
        with self.assertRaises(AIAPIServerException):
            self.client.get_orchestration_config_by_id("non_existent_id")

    def test_get_orchestration_config_history(self):
        response = self.client.get_orchestration_config_history(scenario=self.scenario, name=self.config_name,
                                                                version=self.version)
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertIsNone(response.resources[0].spec)

    def test_get_orchestration_config_history_with_spec(self):
        response = self.client.get_orchestration_config_history(scenario=self.scenario, name=self.config_name,
                                                                version=self.version, include_spec=True, )
        self.assertIsInstance(response, OrchestrationConfigListResponse)
        self.assertIsNotNone(response.resources[0].spec)

    def test_delete_orchestration_config_by_id(self):
        config_id = self.client.create_orchestration_config(scenario=self.scenario,
                                                            name=self.config_name + '_delete',
                                                            version=self.version,
                                                            spec=self.config_spec).id
        response = self.client.delete_orchestration_config_by_id(config_id)
        self.assertIsInstance(response, OrchestrationConfigDeleteResponse)
        self.assertIn("deleted successfully", response.message, "Config was not deleted")

    def test_import_orchestration_config(self):
        response = self.client.import_orchestration_config(ORCHESTRATION_CONFIG_YAML.encode('utf-8'))
        self.assertIsInstance(response, OrchestrationConfigPostResponse)

        # cleanup
        response = self.client.delete_orchestration_config_by_id(response.id)
        self.assertIn("deleted successfully", response.message, "Config was not deleted")

    def test_export_orchestration_config(self):
        response = self.client.export_orchestration_config(self.config.id)
        self.assertEqual(type(response), bytes, "Exported config is not a byte stream")
