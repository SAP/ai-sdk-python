import json
import os
import tempfile

from PIL import Image
from typing import Dict, Any, List

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.orchestration.exceptions import OrchestrationError
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.multimodal_items import ImageItem
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage, Message, ToolMessage, AssistantMessage
from gen_ai_hub.orchestration.models.response_format import ResponseFormatJsonSchema
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.template_ref import TemplateRef
from gen_ai_hub.orchestration.models.tools import function_tool
from gen_ai_hub.orchestration.service import OrchestrationService
from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplateSpec, PromptTemplate
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503


def check_response_from_referenced_template(response, content: str):
    assert response.module_results.templating[0].content == content
    assert len(response.orchestration_result.choices) > 0


class TestTemplating(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLM(
            name="gpt-4o-mini",
            version="latest",
            parameters={
                "max_tokens": 50,
                "temperature": 0.0,
            },
        )

    def test_templating_with_default(self):
        default = TemplateValue(name="user_query", value="Why is the sky blue?")

        template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ],
            defaults=[default],
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        response = self.service.run(config=config)

        self.assertEqual(response.module_results.templating[1].content, default.value)
        self.assertIsNone(response.module_results.input_filtering)
        self.assertIsNone(response.module_results.output_filtering)
        self.assertTrue(response.orchestration_result.model.startswith(self.llm.name))

    def test_templating_with_user_input(self):
        template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ],
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        user_input = TemplateValue(name="user_query", value="Why is the sky blue?")

        response = self.service.run(
            config=config,
            template_values=[user_input],
        )

        self.assertEqual(
            response.module_results.templating[1].content, user_input.value
        )
        self.assertIsNone(response.module_results.input_filtering)
        self.assertIsNone(response.module_results.output_filtering)
        self.assertTrue(response.orchestration_result.model.startswith(self.llm.name))

    def test_templating_with_no_messages(self):
        template = Template(
            messages=[],
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_templating_with_invalid_message(self):
        template = Template(
            messages=[Message(role="unknown-role", content="Hello, world!")],
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        with self.assertRaises(OrchestrationError):
            self.service.run(config=config)

    def test_templating_by_reference(self):
        # create prompt template
        prompt_template_scenario = "scenario_template_by_reference"
        prompt_template_name = "prompt_template_by_reference"
        prompt_template_version = "1.0.0"
        user_content = "You are a system under test."
        tenant_scoped_prompt_client = GenAIHubProxyClient(resource_group="")
        prompt_template_client = PromptTemplateClient(tenant_scoped_prompt_client)        
        spec = PromptTemplateSpec(template=[PromptTemplate(role="user", content=user_content)])
        # reference prompt template
        prompt_template_id = prompt_template_client.create_prompt_template(scenario=prompt_template_scenario,
                                                                           name=prompt_template_name,
                                                                           version=prompt_template_version,
                                                                           prompt_template_spec=spec).id
        config = OrchestrationConfig(
            template=TemplateRef.from_id(prompt_template_id=prompt_template_id),
            llm=self.llm,
        )

        response = self.service.run(config=config)

        check_response_from_referenced_template(response, user_content)

        config = OrchestrationConfig(
            template=TemplateRef.from_tuple(scenario=prompt_template_scenario, name=prompt_template_name,
                                            version=prompt_template_version),
            llm=self.llm
        )

        response = self.service.run(config=config)

        check_response_from_referenced_template(response, user_content)

        # clean up
        prompt_template_client.delete_prompt_template_by_id(prompt_template_id)

    def test_templating_with_response_format_text(self):
        template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ],
            response_format="text"
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        user_input = TemplateValue(name="user_query", value="Who was the first person on the moon?")

        response = self.service.run(
            config=config,
            template_values=[user_input],
        )

        result = response.orchestration_result.choices[0].message.content
        self.assertIsInstance(result, str)
        try:
            json.loads(result)
            self.fail(msg="Response should be a text.")
        except json.JSONDecodeError:
            # The error means result is not a JSON object, so the test passes in this block
            pass

    def test_templating_with_response_format_json_object(self):       
        template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ],
            response_format="json_object"
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        user_input = TemplateValue(name="user_query", value="Who was the first person on the moon? in json")

        response = self.service.run(
            config=config,
            template_values=[user_input],
        )

        try:
            parsed_result = json.loads(response.orchestration_result.choices[0].message.content)
        except json.JSONDecodeError:
            self.fail("Result of LLM is not a valid JSON object")

        self.assertIsInstance(parsed_result, dict)

    def test_templating_with_response_format_json_schema(self): 
        json_schema = {
            "title": "Person",
            "type": "object",
            "properties": {
                    "firstName": {
                    "type": "string",
                    "description": "The person's first name."
                },
                    "lastName": {
                    "type": "string",
                    "description": "The person's last name."
                }
            }
        }

        exp_result = {
            "firstName": "Neil",
            "lastName": "Armstrong"
        }

        template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ],
            response_format=ResponseFormatJsonSchema(name="person", description="person mapping", schema=json_schema)
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        user_input = TemplateValue(name="user_query", value="Who was the first person on the moon? in json")

        response = self.service.run(
            config=config,
            template_values=[user_input],
        )

        try:
            parsed_result = json.loads(response.orchestration_result.choices[0].message.content)
        except json.JSONDecodeError:
            self.fail("Result of LLM is not a valid JSON object")

        self.assertIsInstance(parsed_result, dict)
        self.assertEqual(parsed_result, exp_result)

    def test_templating_with_response_format_json_schema_strict(self): 
        json_schema = {
            "type": "object",
            "properties": {
                    "firstName": {
                    "type": "string",
                    "description": "The person's first name."
                },
                    "lastName": {
                    "type": "string",
                    "description": "The person's last name."
                }
            },
            "additionalProperties": False,
            "required" :["firstName", "lastName"]
        }

        exp_result = {
            "firstName": "Neil",
            "lastName": "Armstrong"
        }

        template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("{{?user_query}}"),
            ],
            response_format=ResponseFormatJsonSchema(name="person", description="person mapping", schema=json_schema, strict=True)
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        user_input = TemplateValue(name="user_query", value="Who was the first person on the moon?")

        response = self.service.run(
            config=config,
            template_values=[user_input],
        )

        try:
            parsed_result = json.loads(response.orchestration_result.choices[0].message.content)
        except json.JSONDecodeError:
            self.fail("Result of LLM is not a valid JSON object")

        self.assertIsInstance(parsed_result, dict)
        self.assertEqual(parsed_result, exp_result)

class TestTemplateWithTools(OrchestrationServiceTestBase):
    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLM(
            name="gpt-4o-mini",
            version="latest",
            parameters={
                "max_tokens": 200,
                "temperature": 0.0,
            },
        )

    def test_sync_tool_call_loop(self):
        @function_tool()
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        tool_map: Dict[str, Any] = {
            "multiply": multiply,
        }

        template = Template(
            messages=[
                SystemMessage("You are a math assistant."),
                UserMessage("What is {{?a}} times {{?b}}?"),
            ],
            tools=[multiply],
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        template_values = [
            TemplateValue(name="a", value=3),
            TemplateValue(name="b", value=7),
        ]

        # First run: should trigger a tool call
        response = self.service.run(
            config=config,
            template_values=template_values,
        )

        # Check tool_calls in the response
        tool_calls = response.orchestration_result.choices[0].message.tool_calls
        self.assertIsNotNone(tool_calls)
        self.assertGreaterEqual(len(tool_calls), 1)
        tool_call = tool_calls[0]
        self.assertEqual(tool_call.function.name, "multiply")
        self.assertEqual(json.loads(tool_call.function.arguments), {"a": 3, "b": 7})
        self.assertIsNotNone(tool_call.id)

        # Check new fields if present
        self.assertTrue(hasattr(tool_call, "id"))
        self.assertTrue(hasattr(tool_call.function, "arguments"))
        self.assertTrue(hasattr(tool_call.function, "name"))

        # Simulate tool execution and build new history
        history: List[Message] = []
        history.extend(response.module_results.templating)

        assistant_message = AssistantMessage(
            content=response.orchestration_result.choices[0].message.content,
            refusal=response.orchestration_result.choices[0].message.refusal,
            tool_calls=response.orchestration_result.choices[0].message.tool_calls)

        self.assertIsNone(assistant_message.refusal)
        self.assertTrue(assistant_message.tool_calls)  # assert some tool calls are present

        history.append(assistant_message)

        for tool_call in tool_calls:
            tool = tool_map[tool_call.function.name]
            result = tool.execute(**tool_call.function.parse_arguments())
            self.assertEqual(result, 21)
            tool_message = ToolMessage(
                content=f"{result}",
                tool_call_id=tool_call.id,
            )
            self.assertEqual(tool_message.tool_call_id, tool_call.id)
            self.assertEqual(tool_message.content, str(result))
            self.assertEqual(tool_message.role, "tool")
            history.append(tool_message)

        # Second run: should return the final answer
        response2 = self.service.run(
            config=config,
            template_values=template_values,
            history=history,
        )

        final_content = response2.orchestration_result.choices[0].message.content
        self.assertIn("21", str(final_content))

        tool_calls2 = response2.orchestration_result.choices[0].message.tool_calls
        self.assertFalse(tool_calls2)

    def test_streaming_two_tool_call_buffering(self):
        @function_tool()
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        @function_tool()
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        template = Template(
            messages=[
                SystemMessage("You are a math assistant."),
                UserMessage("What is 3 * 12? Also, what is 11 + 49?"),
            ],
            tools=[multiply, add],
        )

        config = OrchestrationConfig(
            template=template,
            llm=self.llm,
        )

        # Start streaming
        stream = self.service.stream(config=config)

        final_tool_calls = {}

        for chunk in stream:
            for tool_call in chunk.orchestration_result.choices[0].delta.tool_calls or []:
                index = tool_call.index

                if index not in final_tool_calls:
                    final_tool_calls[index] = tool_call
                else:
                    # Concatenate arguments if split across chunks
                    final_tool_calls[index].function.arguments += tool_call.function.arguments

        self.assertEqual(len(final_tool_calls), 2)

        multiply_call = next(
            call for call in final_tool_calls.values()
            if call.function.name == "multiply"
        )
        self.assertIsNotNone(multiply_call.id)

        add_call = next(
            call for call in final_tool_calls.values()
            if call.function.name == "add"
        )
        self.assertIsNotNone(add_call.id)

        self.assertEqual(
            json.loads(multiply_call.function.arguments), {"a": 3, "b": 12}
        )

        self.assertEqual(
            json.loads(add_call.function.arguments), {"a": 11, "b": 49}
        )

class TestMultimodalTemplating(OrchestrationServiceTestBase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.image_path = os.path.join(cls.temp_dir.name, "test_image.png")
        img = Image.new("RGB", (10, 10), color="red")
        img.save(cls.image_path)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLM(
            name="gpt-4o",
            version="latest",
            parameters={
                "max_tokens": 50,
                "temperature": 0.0,
            },
        )

    def test_image_from_url(self):
        data_url = (
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAE0lEQVR4nGP8z4APMOGVZRip0gBBLAETee26JgAAAABJRU5ErkJggg=='
        )
        image_item = ImageItem(url=data_url)
        multimodal_content = [image_item, "What color is this image?"]

        template = Template(messages=[UserMessage(multimodal_content)])
        config = OrchestrationConfig(template=template, llm=self.llm)
        response = self.service.run(config=config)

        self.assertIn("red", response.content.lower())

    def test_image_from_file(self):
        image_item = ImageItem.from_file(self.image_path)
        multimodal_content = [image_item, "What color is this image?"]

        template = Template(messages=[UserMessage(multimodal_content)])
        config = OrchestrationConfig(template=template, llm=self.llm)
        response = self.service.run(config=config)

        self.assertIn("red", response.content.lower())

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_only_image(self):
        image_item = ImageItem.from_file(self.image_path)
        multimodal_content = [image_item]

        template = Template(messages=[UserMessage(multimodal_content)])
        config = OrchestrationConfig(template=template, llm=self.llm)
        response = self.service.run(config=config)

        self.assertTrue(response.content)

    def test_multi_text_parts_are_handled(self):
        multimodal_content = [
            "This is a text message.",
            "This is another text message.",
        ]
        template = Template(messages=[UserMessage(multimodal_content)])
        config = OrchestrationConfig(template=template, llm=self.llm)
        response = self.service.run(config=config)

        self.assertEqual(
            len(response.module_results.templating[0].content), 2
        )
        self.assertTrue(response.content)

    def test_multimodal_input_streaming(self):
        image_item = ImageItem.from_file(self.image_path)
        multimodal_content = [image_item, "What color is this image?"]

        template = Template(messages=[UserMessage(multimodal_content)])
        config = OrchestrationConfig(template=template, llm=self.llm)
        response = self.service.stream(config=config)

        message = ''

        for chunk in response:
            if chunk.orchestration_result.choices:
                message += chunk.orchestration_result.choices[0].delta.content

        self.assertIn("red", message.lower())
