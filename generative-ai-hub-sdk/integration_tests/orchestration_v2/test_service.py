import requests
import time
from httpx import TimeoutException
from gen_ai_hub.orchestration_v2.models.config import (OrchestrationConfig, ModuleConfig,
CompletionRequestConfigurationReferenceByIdConfigRef,
CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.response import CompletionPostResponse
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase


class TestService(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(self.api_url)
        self.template = Template(
            template=[
                SystemMessage(content="This is a system message."),
                UserMessage(content="Hello, {{?name}}!"),
            ],
            defaults={"name": "Integration Test"}
        )
        self.llm = LLMModelDetails(
            name="gemini-2.5-flash",
            params={
                'temperature': 0.0,
            }
        )
        self.prompt_template = PromptTemplatingModuleConfig(prompt=self.template, model=self.llm)
        self.module_config = ModuleConfig(prompt_templating=self.prompt_template)
        self.config_ref: dict = None
        self.config_ref = self.create_config_ref()
        self.config_ref_id = CompletionRequestConfigurationReferenceByIdConfigRef(id=self.config_ref["id"])
        self.config_ref_name = CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef(
            name=self.config_ref["name"],
            version=self.config_ref["version"],
            scenario=self.config_ref["scenario"]
        )

    def tearDown(self):
        headers = self.service.proxy_client.request_header
        url = self.service.api_url.split("/inference")[0]
        endpoint = f"{url}/registry/v2/orchestrationConfigs/{self.config_ref['id']}"
        requests.delete(endpoint, headers=headers)

    def create_config_ref(self) -> dict:
        if self.config_ref is not None:
            return self.config_ref
        headers = self.service.proxy_client.request_header
        url = self.service.api_url.split("/inference")[0]
        endpoint = f"{url}/registry/v2/orchestrationConfigs"
        body = {
            "scenario": "gen-ai-hub-sdk-config-ref-test-scenario",
            "name": "gen-ai-hub-sdk-config-ref-test",
            "version": "0.1.0",
            "model_name": "gpt-4o",
            "spec": {
                "modules": {
                    "prompt_templating": {
                        "prompt": {
                            "template": [
                                {"role": "user", "content": "Hello World"},
                            ]
                        },
                        "model": {
                            "name": "gpt-4o",
                            "version": "latest"
                        }
                    },
                },
            }
        }

        # Retry logic to handle potential rate limiting or transient issues when creating config reference
        max_retries = 3
        delay = 2.0
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(endpoint, json=body, headers=headers)
                response_json = response.json()

                # Check if response has required 'id' field
                if 'id' not in response_json:
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= 2
                        continue
                    else:
                        raise KeyError(f"Response missing 'id' field: {response_json}")

                return response_json
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise

        raise RuntimeError("Failed to create config reference after multiple attempts "
                           "due to rate limiting or missing 'id' in response.")

    def test_service_request_with_default_config(self):
        service = OrchestrationService(api_url=self.api_url, config=OrchestrationConfig(modules=self.module_config))
        response = service.run()

        self.assertEqual(
            response.intermediate_results.templating[1].content, "Hello, Integration Test!"
        )

    def test_service_request_with_list_of_config(self):
        service = OrchestrationService(api_url=self.api_url,
                                       config=OrchestrationConfig(modules=[self.module_config]))
        response = service.run()

        self.assertEqual(response.intermediate_results.templating[1].content, "Hello, Integration Test!")

    def test_service_with_inference_config(self):
        service = OrchestrationService(api_url=self.api_url)
        config = OrchestrationConfig(modules=self.module_config)

        config.modules.prompt_templating.model.name = "gemini-2.0-flash"

        response = service.run(
            config=config, placeholder_values={"name": "World"}
        )

        self.assertTrue(
            response.final_result.model.startswith("gemini-2.0-flash")
        )
        self.assertEqual(response.intermediate_results.templating[1].content, "Hello, World!")

    def test_service_with_history(self):
        template = Template(
            template=[
                SystemMessage(content="This is a system message.")
            ]
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template, model=self.llm)
        module_config = ModuleConfig(prompt_templating=prompt_template)
        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(
            config=config,
            history=[
                UserMessage(content="Hello, World!"),
                UserMessage(content="How are you?"),
                UserMessage(content="What is your name?"),
            ]
        )

        self.assertEqual(len(response.intermediate_results.templating), 4)
        self.assertEqual(response.intermediate_results.templating[0].content, "Hello, World!")
        self.assertEqual(response.intermediate_results.templating[1].content, "How are you?")
        self.assertEqual(
            response.intermediate_results.templating[2].content, "What is your name?"
        )
        self.assertEqual(
            response.intermediate_results.templating[3].content, "This is a system message."
        )
        self.assertTrue(response.final_result.model.startswith("gemini-2")
        )

    def test_reuse_client(self):
        """
        ensures the client is reused and not closed when making multiple requests
        """
        reusable_client = self.service.client

        #First request
        config = OrchestrationConfig(modules=self.module_config)
        self.service.run(config=config, placeholder_values={"name": "World"})
        self.assertFalse(reusable_client.is_closed)

        # Second request
        self.service.run(config=config, placeholder_values={"name": "Sun"})

        # ensure httpx client is reused
        self.assertEqual(reusable_client, self.service.client)

        self.service.close_http_connection()
        self.assertTrue(reusable_client.is_closed)

    def test_timeout_per_request(self):
        """
        set low default timeout for reusable client, which leads to a timeout.
        overwrite timeout with higher value via request and show that response is returned.
        """
        template = Template(
            template=[
                SystemMessage(content="You are a famous professor for theoretical physics."),
                UserMessage(content="Elaborate on the relativity theory."),
            ]
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template, model=self.llm)
        config = OrchestrationConfig(modules=ModuleConfig(prompt_templating=prompt_template))

        # First request - should time out
        with self.assertRaises(TimeoutException):
            self.service.run(config=config, timeout=1)

        # Second request - should succeed due to overwrite in request with higher timeout
        result = self.service.run(config=config, timeout=300)
        self.assertIsInstance(result, CompletionPostResponse)

    def test_config_ref_by_id(self):
        service = OrchestrationService(api_url=self.api_url, config_ref=self.config_ref_id)
        response = service.run()
        self.assertIsInstance(response, CompletionPostResponse)
        self.assertEqual(response.intermediate_results.templating[0].content, "Hello World")

    def test_config_ref_by_snv(self):
        service = OrchestrationService(api_url=self.api_url, config_ref=self.config_ref_name)
        response = service.run()
        self.assertIsInstance(response, CompletionPostResponse)
        self.assertEqual(response.intermediate_results.templating[0].content, "Hello World")

    def test_config_and_config_ref_provided_error_class(self):
        with self.assertRaises(ValueError):
            OrchestrationService(api_url=self.api_url,
                                 config=OrchestrationConfig(modules=self.module_config),
                                 config_ref=self.config_ref_id)

    def test_config_and_config_ref_provided_error_class_and_methode(self):
        service = OrchestrationService(api_url=self.api_url, config=OrchestrationConfig(modules=self.module_config))
        with self.assertRaises(ValueError):
            service.run(config_ref=self.config_ref_name)

    def test_config_and_config_ref_provided_error_methode(self):
        service = OrchestrationService(api_url=self.api_url)
        with self.assertRaises(ValueError):
            service.run(config=OrchestrationConfig(modules=self.module_config), config_ref=self.config_ref_id)

