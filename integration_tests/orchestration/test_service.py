from httpx import TimeoutException
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.response import OrchestrationResponse
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503


class TestService(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(self.api_url)

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_service_request_with_default_config(self):
        config = OrchestrationConfig(
            template=Template(
                messages=[
                    SystemMessage("This is a system message."),
                    UserMessage("Hello, {{?name}}!"),
                ],
                defaults=[TemplateValue(name="name", value="Integration Test")],
            ),
            llm=LLM(
                name="gemini-2.5-flash",
                parameters={
                    'temperature': 0.0,
                }
            ),
        )

        service = OrchestrationService(api_url=self.api_url, config=config)

        response = service.run()

        self.assertEqual(
            response.module_results.templating[1].content, "Hello, Integration Test!"
        )

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_service_with_inference_config(self):
        config = OrchestrationConfig(
            template=Template(
                messages=[
                    SystemMessage("This is a system message."),
                    UserMessage("Hello, {{?name}}!"),
                ],
            ),
            llm=LLM(
                name="gemini-2.5-flash",
                parameters={
                    'temperature': 0.0,
                }
            ),
        )

        service = OrchestrationService(api_url=self.api_url, config=config)

        config.llm.name = "gemini-2.0-flash"

        response = service.run(
            config=config, template_values=[TemplateValue("name", "World")]
        )

        self.assertTrue(
            response.orchestration_result.model.startswith("gemini-2.0-flash")
        )
        self.assertEqual(response.module_results.templating[1].content, "Hello, World!")

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_service_with_history(self):
        response = self.service.run(
            config=OrchestrationConfig(
                template=Template(
                    messages=[
                        SystemMessage("This is a system message."),
                    ],
                ),
                llm=LLM(
                    name="gemini-2.5-flash",
                    parameters={
                        'temperature': 0.0,
                    }
                ),
            ),
            history=[
                UserMessage("Hello, World!"),
                UserMessage("How are you?"),
                UserMessage("What is your name?"),
            ],
        )

        self.assertEqual(len(response.module_results.templating), 4)
        self.assertEqual(response.module_results.templating[0].content, "Hello, World!")
        self.assertEqual(response.module_results.templating[1].content, "How are you?")
        self.assertEqual(
            response.module_results.templating[2].content, "What is your name?"
        )
        self.assertEqual(
            response.module_results.templating[3].content, "This is a system message."
        )
        self.assertEqual(
            response.orchestration_result.model.startswith("gemini-2"), True
        )

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_reuse_client(self):
        """
        ensures the client is reused and not closed when making multiple requests
        """
        reusable_client = self.service.client

        #First request
        config = OrchestrationConfig(
            template=Template(
                messages=[
                    SystemMessage("This is a system message."),
                    UserMessage("Hello, {{?name}}!"),
                ],
            ),
            llm=LLM(
                name="gemini-2.5-flash",
                parameters={
                    'temperature': 0.0,
                }
            ),
        )
        self.service.run(config=config, template_values=[TemplateValue("name", "World")])
        self.assertFalse(reusable_client.is_closed)

        # Second request
        self.service.run(config=config, template_values=[TemplateValue("name", "Earth")])

        # ensure httpx client is reused
        self.assertEqual(reusable_client, self.service.client)

        self.service.close_http_connection()
        self.assertTrue(reusable_client.is_closed)

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_timeout_per_request(self):
        """
        set low default timeout for reusable client, which leads to a timeout.
        overwrite timeout with higher value via request and show that response is returned.
        """
        self.service = OrchestrationService(self.api_url, timeout=0.1)
        config = OrchestrationConfig(
            template=Template(
                messages=[
                    SystemMessage("You are a famous professor for theoretical physics."),
                    UserMessage("Elaborate on the relativity theory."),
                ],
            ),
            llm=LLM(name="gpt-5-nano")
        )

        # First request - should time out
        with self.assertRaises(TimeoutException):
            self.service.run(config=config)

        # Second request - should succeed due to overwrite in request with higher timeout
        result = self.service.run(config=config, timeout=300)
        self.assertIsInstance(result, OrchestrationResponse)

