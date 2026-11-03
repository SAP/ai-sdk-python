import base64
import json
import os
import tempfile

from PIL import Image
from typing import Dict, Any, List

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.multimodal_items import ImageItem, FileItem
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage, AssistantMessage, ToolChatMessage, ChatMessage
from gen_ai_hub.orchestration_v2.models.response_format import ResponseFormatJsonObject, ResponseFormatText, ResponseFormatJsonSchema, JSONResponseSchema
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.models.template_ref import TemplateRef, TemplateRefByID, TemplateRefByScenarioNameVersion
from gen_ai_hub.orchestration_v2.models.tools import function_tool
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplateSpec, PromptTemplate
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


def check_response_from_referenced_template(response, content: str):
    assert response.intermediate_results.templating[0].content == content
    assert len(response.final_result.choices) > 0


@retry_on_429_or_503_class()
class TestTemplating(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o-mini",
            version="latest",
            params={
                "max_tokens": 50,
                "temperature": 0.0,
            },
        )

    def test_templating_with_default(self):
        default = {"user_query": "Why is the sky blue?"}

        template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ],
            defaults=default
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config)

        self.assertEqual(response.intermediate_results.templating[1].content, default["user_query"])
        self.assertIsNone(response.intermediate_results.input_filtering)
        self.assertIsNone(response.intermediate_results.output_filtering)
        self.assertTrue(response.final_result.model.startswith(self.llm.name))

    def test_templating_with_user_input(self):
        user_input = {"user_query": "Why is the sky blue?"}

        template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ]
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config, placeholder_values=user_input)

        self.assertEqual(
            response.intermediate_results.templating[1].content, user_input["user_query"]
        )
        self.assertIsNone(response.intermediate_results.input_filtering)
        self.assertIsNone(response.intermediate_results.output_filtering)
        self.assertTrue(response.final_result.model.startswith(self.llm.name))

    def test_templating_with_no_messages(self):
        template = Template(
            template=[],
        )

        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

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

        prompt_template = PromptTemplatingModuleConfig(
            prompt=TemplateRef(template_ref=TemplateRefByID(id=prompt_template_id)),
            model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config)

        check_response_from_referenced_template(response, user_content)

        prompt_template = PromptTemplatingModuleConfig(
            prompt=TemplateRef(
                template_ref = TemplateRefByScenarioNameVersion(
                    scenario=prompt_template_scenario,
                    name=prompt_template_name,
                    version=prompt_template_version
                )
            ),
            model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config)

        check_response_from_referenced_template(response, user_content)

        # clean up
        prompt_template_client.delete_prompt_template_by_id(prompt_template_id)

    def test_templating_with_response_format_text(self):
        user_input = {"user_query": "Why is the sky blue?"}

        template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ],
            response_format=ResponseFormatText()
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(
            config=config,
            placeholder_values=user_input,
        )

        result = response.final_result.choices[0].message.content
        self.assertIsInstance(result, str)
        try:
            json.loads(result)
            self.fail(msg="Response should be a text.")
        except json.JSONDecodeError:
            # The error means result is not a JSON object, so the test passes in this block
            pass

    def test_templating_with_response_format_json_object(self):
        template = Template(
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ],
            response_format=ResponseFormatJsonObject()
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        user_input = {"user_query":"Who was the first person on the moon? in json"}

        response = self.service.run(
            config=config,
            placeholder_values=user_input,
        )

        try:
            parsed_result = json.loads(response.final_result.choices[0].message.content)
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
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ],
            response_format=ResponseFormatJsonSchema(
                json_schema=JSONResponseSchema(
                    name="person", description="person mapping", schema=json_schema
                ),
            )
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        user_input = {"user_query": "Who was the first person on the moon? in json"}

        response = self.service.run(
            config=config,
            placeholder_values=user_input,
        )

        try:
            parsed_result = json.loads(response.final_result.choices[0].message.content)
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
            template=[
                SystemMessage(content="You are a friendly assistant."),
                UserMessage(content="{{?user_query}}"),
            ],
            response_format=ResponseFormatJsonSchema(
                json_schema=JSONResponseSchema(
                    name="person", description="person mapping", schema=json_schema, strict=True
                ),
            )
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        user_input = {"user_query": "Who was the first person on the moon? in json"}

        response = self.service.run(
            config=config,
            placeholder_values=user_input,
        )

        try:
            parsed_result = json.loads(response.final_result.choices[0].message.content)
        except json.JSONDecodeError:
            self.fail("Result of LLM is not a valid JSON object")

        self.assertIsInstance(parsed_result, dict)
        self.assertEqual(parsed_result, exp_result)

@retry_on_429_or_503_class()
class TestTemplateWithTools(OrchestrationServiceTestBase):
    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o",
            version="latest",
            params={
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
            template=[
                SystemMessage(content="You are a math assistant."),
                UserMessage(content="What is {{?a}} times {{?b}}?"),
            ],
            tools=[multiply],
        )
        prompt_template=PromptTemplatingModuleConfig(prompt=template,
                                                         model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        template_values = {"a": "3", "b": "7"}

        # First run: should trigger a tool call
        response = self.service.run(
            config=config,
            placeholder_values=template_values,
        )

        # Check tool_calls in the response
        tool_calls = response.final_result.choices[0].message.tool_calls
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
        history: List[ChatMessage] = []
        history.extend(response.intermediate_results.templating)

        assistant_message = AssistantMessage(
            content=response.final_result.choices[0].message.content,
            refusal=response.final_result.choices[0].message.refusal,
            tool_calls=response.final_result.choices[0].message.tool_calls)

        self.assertIsNone(assistant_message.refusal)
        self.assertTrue(assistant_message.tool_calls)  # assert some tool calls are present

        history.append(assistant_message)

        for tool_call in tool_calls:
            tool = tool_map[tool_call.function.name]
            result = tool.execute(**tool_call.function.parse_arguments())
            self.assertEqual(result, 21)
            tool_message = ToolChatMessage(
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
            placeholder_values=template_values,
            history=history,
        )

        final_content = response2.final_result.choices[0].message.content
        self.assertIn("21", str(final_content))

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
            template=[
                SystemMessage(content="You are a math assistant."),
                UserMessage(content="What is 3 * 12? Also, what is 11 + 49?"),
            ],
            tools=[multiply, add],
        )
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config, stream={"enabled": True})

        # Start streaming
        stream = self.service.stream(config=config)

        final_tool_calls = {}

        for chunk in stream:
            for tool_call in chunk.final_result.choices[0].delta.tool_calls or []:
                index = tool_call.index

                if index not in final_tool_calls:
                    final_tool_calls[index] = tool_call
                else:
                    # Concatenate arguments if split across chunks
                    final_tool_calls[index].function.arguments += tool_call.function.arguments

        self.assertEqual(len(final_tool_calls), 2)

        for call in final_tool_calls.values():
            if call.function.name == "multiply":
                multiply_call = call
            if call.function.name == "add":
                add_call = call

        self.assertIsNotNone(multiply_call.id)
        self.assertIsNotNone(add_call.id)

        self.assertEqual(
            json.loads(multiply_call.function.arguments), {"a": 3, "b": 12}
        )

        self.assertEqual(
            json.loads(add_call.function.arguments), {"a": 11, "b": 49}
        )

@retry_on_429_or_503_class()
class TestMultimodalTemplating(OrchestrationServiceTestBase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.image_path = os.path.join(cls.temp_dir.name, "test_image.png")
        img = Image.new("RGB", (10, 10), color="red")
        img.save(cls.image_path)

        cls.pdf_path = os.path.join(cls.temp_dir.name, "test_doc.pdf")
        cls.pdf_secret_word = "BANANA"
        cls._write_minimal_pdf(cls.pdf_path, cls.pdf_secret_word)
        with open(cls.pdf_path, "rb") as pdf_file:
            cls.pdf_data_url = "data:application/pdf;base64," + base64.b64encode(pdf_file.read()).decode("utf-8")

    @classmethod
    def _write_minimal_pdf(cls, path: str, text: str) -> None:
        stream_content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        parts = [
            b"%PDF-1.4",
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj",
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj",
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>\nendobj",
            b"4 0 obj<</Length " + str(len(stream_content)).encode() + b">>\nstream\n"
            + stream_content + b"\nendstream\nendobj",
            b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj",
        ]
        buf = b""
        offsets = []
        for part in parts:
            offsets.append(len(buf))
            buf += part + b"\n"
        xref_pos = len(buf)
        buf += b"xref\n0 6\n" + b"0000000000 65535 f \n"
        for off in offsets:
            buf += f"{off:010d} 00000 n \n".encode()
        buf += b"trailer<</Size 6/Root 1 0 R>>\nstartxref\n" + str(xref_pos).encode() + b"\n%%EOF"
        with open(path, "wb") as f:
            f.write(buf)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o",
            version="latest",
            params={
                "max_tokens": 50,
                "temperature": 0.0,
            },
        )
        self.file_llm = LLMModelDetails(
            name="gemini-2.5-flash",
            version="latest",
            params={
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

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIn("red", response.final_result.choices[0].message.content.lower())

    def test_image_from_file(self):
        image_item = ImageItem.from_file(self.image_path)
        multimodal_content = [image_item, "What color is this image?"]

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config)

        self.assertIn("red", response.final_result.choices[0].message.content.lower())

    def test_only_image(self):
        image_item = ImageItem.from_file(self.image_path)
        multimodal_content = [image_item]

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config)

        self.assertIn("red", response.final_result.choices[0].message.content.lower())

    def test_multi_text_parts_are_handled(self):
        multimodal_content = [
            "This is a text message.",
            "This is another text message.",
        ]
        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertEqual(
            len(response.intermediate_results.templating[0].content), 2
        )
        self.assertTrue(response.final_result.choices[0].message.content)

    def test_multimodal_input_streaming(self):
        image_item = ImageItem.from_file(self.image_path)
        multimodal_content = [image_item, "What color is this image?"]

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config, stream={"enabled": True})
        response = self.service.stream(config=config)

        message = ''

        for chunk in response:
            if chunk.final_result.choices:
                message += chunk.final_result.choices[0].delta.content

        self.assertIn("red", message.lower())

    def test_file_from_file_path(self):
        file_item = FileItem.from_file(self.pdf_path, filename="test_doc.pdf")
        multimodal_content = [
            file_item,
            "What word does this PDF contain? Reply with only the word.",
        ]

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.file_llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)

        response = self.service.run(config=config)

        self.assertIn(self.pdf_secret_word,
                      response.final_result.choices[0].message.content.upper())

    def test_file_from_data_url(self):
        file_item = FileItem(file_data=self.pdf_data_url, filename="test_doc.pdf")
        multimodal_content = [
            file_item,
            "What word does this PDF contain? Reply with only the word.",
        ]

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.file_llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config)
        response = self.service.run(config=config)

        self.assertIn(self.pdf_secret_word,
                      response.final_result.choices[0].message.content.upper())

    def test_file_input_streaming(self):
        file_item = FileItem.from_file(self.pdf_path, filename="test_doc.pdf")
        multimodal_content = [
            file_item,
            "What word does this PDF contain? Reply with only the word.",
        ]

        template = Template(template=[UserMessage(content=multimodal_content)])
        prompt_template = PromptTemplatingModuleConfig(prompt=template,
                                                       model=self.file_llm)

        module_config = ModuleConfig(prompt_templating=prompt_template)

        config = OrchestrationConfig(modules=module_config, stream={"enabled": True})
        response = self.service.stream(config=config)

        message = ''

        for chunk in response:
            if chunk.final_result.choices:
                message += chunk.final_result.choices[0].delta.content

        self.assertIn(self.pdf_secret_word, message.upper())
