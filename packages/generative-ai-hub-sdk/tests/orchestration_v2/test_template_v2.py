import base64
import os
import tempfile
import unittest

from pydantic import ValidationError

from gen_ai_hub.orchestration_v2.models.message import (
    Role,
    SystemMessage,
    UserMessage,
    AssistantMessage,
)
from gen_ai_hub.orchestration_v2.models.multimodal_items import ImageItem, ImageDetailLevel
from gen_ai_hub.orchestration_v2.models.response_format import (
    ResponseFormatType,
    ResponseFormatText,
    ResponseFormatJsonObject,
    ResponseFormatJsonSchema,
    JSONResponseSchema
)
from gen_ai_hub.orchestration_v2.models.template import Template


class TestTemplate(unittest.TestCase):
    def test_template_with_defaults(self):
        messages = [
            SystemMessage(content="You are a helpful assistant!"),
            UserMessage(content="Hello, {{?name}}!"),
            AssistantMessage(content="How can I help you today?"),
        ]
        defaults = {"name": "World"}
        template = Template(template=messages, defaults=defaults)

        json_data = template.model_dump()
        self.assertEqual(json_data["defaults"], {"name": "World"})
        self.assertEqual(len(json_data["template"]), len(messages))
        self.assertEqual(json_data["template"][1]["content"], "Hello, {{?name}}!")

    def test_template_without_defaults(self):
        messages = [UserMessage(content="Simple message")]
        template = Template(template=messages)

        json_data = template.model_dump()
        self.assertIsNone(json_data.get("defaults"))
        self.assertEqual(len(json_data["template"]), 1)

    def test_template_without_response_format(self):
        messages = [UserMessage(content="Simple message")]
        template = Template(template=messages)

        json_data = template.model_dump()
        self.assertNotIn("response_format", json_data)

    def test_template_with_response_format_text(self):
        messages = [UserMessage(content="Simple message")]
        template = Template(template=messages, response_format=ResponseFormatText())

        json_data = template.model_dump()
        self.assertEqual(json_data["response_format"]["type"], ResponseFormatType.TEXT)

    def test_template_with_response_format_json_object(self):
        messages = [UserMessage(content="Simple message")]
        template = Template(template=messages, response_format=ResponseFormatJsonObject())

        json_data = template.model_dump()
        self.assertEqual(json_data["response_format"]["type"], ResponseFormatType.JSON_OBJECT)

    def test_template_with_response_format_json_schema(self):
        messages = [UserMessage(content="Simple message")]
        json_schema_example = {
            "$id": "someid",
            "$schema": "someshema",
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

        response_format = ResponseFormatJsonSchema(json_schema=JSONResponseSchema(name="test",
                                                                                  description="desc",
                                                                                  schema=json_schema_example,
                                                                                  strict=True))
        template = Template(template=messages, response_format=response_format)

        json_data = template.model_dump()
        self.assertEqual(json_data["response_format"]["type"], ResponseFormatType.JSON_SCHEMA)
        self.assertEqual(json_data["response_format"]["json_schema"]["name"], "test")
        self.assertTrue(json_data["response_format"]["json_schema"]["strict"])
        self.assertEqual(json_data["response_format"]["json_schema"]["schema"], json_schema_example)

    def test_response_format_name_too_long(self):
        name_too_long = "ThisIsAveryLongNameLongerThenExpectedItShouldBeMaximum64Characters"
        try:
            JSONResponseSchema(name=name_too_long, schema={})
            self.fail("Expected the validation to fail due to length of name")
        except ValidationError:
            pass


class TestTemplateWithTools(unittest.TestCase):
    def test_template_with_tool_dict(self):
        messages = [UserMessage(content="Say hello")]
        tool_dict = {
            "type": "function",
            "function": {
                "name": "hello",
                "description": "Say hello",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                },
                "strict": False
            }
        }
        template = Template(template=messages, tools=[tool_dict])
        json_data = template.model_dump()
        self.assertIn("tools", json_data)
        self.assertEqual(json_data["tools"][0], tool_dict)

    def test_template_with_function_tool(self):
        from gen_ai_hub.orchestration_v2.models.tools import function_tool

        @function_tool()
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        messages = [UserMessage(content="Add two numbers")]
        template = Template(template=messages, tools=[add])
        json_data = template.model_dump()
        self.assertIn("tools", json_data)
        tool = json_data["tools"][0]
        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "add")
        self.assertEqual(tool["function"]["description"], "Add two numbers.")
        self.assertIn("a", tool["function"]["parameters"]["properties"])
        self.assertIn("b", tool["function"]["parameters"]["properties"])

    def test_template_with_multiple_tools(self):
        from gen_ai_hub.orchestration_v2.models.tools import function_tool

        @function_tool()
        def foo(x: int) -> int:
            """Foo."""
            return x

        @function_tool()
        def bar(y: str) -> str:
            """Bar."""
            return y

        messages = [UserMessage(content="Test multiple tools")]
        template = Template(template=messages, tools=[foo, bar])
        json_data = template.model_dump()
        self.assertIn("tools", json_data)
        self.assertEqual(len(json_data["tools"]), 2)
        self.assertEqual(json_data["tools"][0]["function"]["name"], "foo")
        self.assertEqual(json_data["tools"][1]["function"]["name"], "bar")

    def test_template_with_plain_function_raises(self):
        def plain_func(a: int) -> int:
            return a

        messages = [UserMessage(content="Test plain function")]
        with self.assertRaises(ValidationError):
            Template(template=messages, tools=[plain_func])


class TestUserMessageMultimodal(unittest.TestCase):
    def test_user_message_with_single_string(self):
        msg = UserMessage(content="Hello world!")
        expected = {
            "role": Role.USER,
            "content": "Hello world!"
        }
        self.assertEqual(msg.model_dump(), expected)

    def test_user_message_with_list_of_strings(self):
        msg = UserMessage(content=["Hello", "World"])
        expected = {
            "role": Role.USER,
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": "World"}
            ]
        }
        self.assertEqual(msg.model_dump(), expected)

    def test_user_message_with_string_and_image(self):
        img = ImageItem(url="https://example.com/image.png")
        msg = UserMessage(content=["Describe this image:", img])
        expected = {
            "role": Role.USER,
            "content": [
                {"type": "text", "text": "Describe this image:"},
                {"type": "image_url", "image_url": {
                    "url": "https://example.com/image.png"
                }}
            ]
        }
        self.assertEqual(msg.model_dump(), expected)

    def test_user_message_with_multiple_images_and_text(self):
        img1 = ImageItem(url="https://example.com/1.png", detail=ImageDetailLevel.LOW)
        img2 = ImageItem(url="https://example.com/2.png", detail=ImageDetailLevel.HIGH)
        msg = UserMessage(content=["First image:", img1, "Second image:", img2])
        expected = {
            "role": Role.USER,
            "content": [
                {"type": "text", "text": "First image:"},
                {"type": "image_url", "image_url": {
                    "url": "https://example.com/1.png",
                    "detail": ImageDetailLevel.LOW
                }},
                {"type": "text", "text": "Second image:"},
                {"type": "image_url", "image_url": {
                    "url": "https://example.com/2.png",
                    "detail": ImageDetailLevel.HIGH
                }}
            ]
        }
        self.assertEqual(msg.model_dump(), expected)

    def test_image_item_from_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(b"not a real image")
            tmp_path = tmp.name

        try:
            item = ImageItem.from_file(tmp_path)
            self.assertTrue(item.url.startswith("data:image/png;base64,"))
            # Check that the base64 part decodes to the original file content
            encoded = item.url.split(",", 1)[1]
            with open(tmp_path, "rb") as f:
                original = f.read()
            decoded = base64.b64decode(encoded)

            self.assertEqual(decoded, original)
        finally:
            os.unlink(tmp_path)
