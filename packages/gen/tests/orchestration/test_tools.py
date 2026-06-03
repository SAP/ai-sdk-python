import asyncio
import unittest
from typing import Optional

from gen_ai_hub.orchestration.models.tools import FunctionTool, function_tool


class TestFunctionTool(unittest.TestCase):
    def test_from_function_basic(self):
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        tool = FunctionTool.from_function(add)
        self.assertEqual(tool.name, "add")
        self.assertEqual(tool.description, "Add two numbers.")
        self.assertIn("a", tool.parameters["properties"])
        self.assertIn("b", tool.parameters["properties"])
        self.assertIn("a", tool.parameters["required"])
        self.assertIn("b", tool.parameters["required"])
        self.assertEqual(tool.parameters["properties"]["a"]["type"], "number")
        self.assertEqual(tool.parameters["properties"]["b"]["type"], "number")
        self.assertEqual(tool.execute(a=2, b=3), 5)

    def test_from_function_optional(self):
        def greet(name: str, title: Optional[str] = None) -> str:
            """Greet a person."""
            return f"Hello, {title + ' ' if title else ''}{name}"

        tool = FunctionTool.from_function(greet)
        self.assertEqual(tool.name, "greet")
        self.assertIn("title", tool.parameters["properties"])
        self.assertNotIn("title", tool.parameters["required"])
        self.assertTrue(tool.parameters["properties"]["title"]["nullable"])
        self.assertEqual(tool.execute(name="Alice"), "Hello, Alice")
        self.assertEqual(tool.execute(name="Alice", title="Dr."), "Hello, Dr. Alice")

    def test_decorator(self):
        @function_tool()
        def echo(msg: str) -> str:
            """Echo a message."""
            return msg

        self.assertIsInstance(echo, FunctionTool)
        self.assertEqual(echo.name, "echo")
        self.assertEqual(echo.execute(msg="hi"), "hi")

    def test_strict_mode(self):
        def foo(x: int) -> int:
            """Foo."""
            return x

        tool = FunctionTool.from_function(foo, strict=True)
        with self.assertRaises(ValueError):
            tool.execute(x=1, y=2)  # y is not a valid parameter

    def test_missing_type_hint(self):
        def no_type(a, b: int) -> int:
            """No type for a."""
            return b

        with self.assertRaises(TypeError):
            FunctionTool.from_function(no_type)

    def test_description_precedence(self):
        # Case 1: No description provided, should use docstring
        def sample(a: int) -> int:
            """This is the docstring."""
            return a

        tool1 = FunctionTool.from_function(sample)
        self.assertEqual(tool1.description, "This is the docstring.")
        self.assertIn("description", tool1.to_dict()["function"])

        # Case 2: Description provided, should take precedence over docstring
        tool2 = FunctionTool.from_function(sample, description="Explicit description.")
        self.assertEqual(tool2.description, "Explicit description.")
        self.assertIn("description", tool2.to_dict()["function"])
        self.assertEqual(tool2.to_dict()["function"]["description"], "Explicit description.")

        # Case 3: No docstring and no description, description should not be in dict
        @function_tool
        def no_desc(a: int) -> int:
            return a

        tool3 = no_desc
        self.assertIsNone(tool3.description)
        self.assertNotIn("description", tool3.to_dict()["function"])


class TestFunctionToolAsync(unittest.IsolatedAsyncioTestCase):
    async def test_async_function_tool(self):
        async def async_add(a: int, b: int) -> int:
            """Add two numbers asynchronously."""
            await asyncio.sleep(0.01)
            return a + b

        tool = FunctionTool.from_function(async_add)
        result = await tool.aexecute(a=2, b=3)
        self.assertEqual(result, 5)

    async def test_async_decorator(self):
        @function_tool()
        async def async_echo(msg: str) -> str:
            """Echo a message asynchronously."""
            await asyncio.sleep(0.01)
            return msg

        self.assertIsInstance(async_echo, FunctionTool)
        result = await async_echo.aexecute(msg="hi")
        self.assertEqual(result, "hi")

    async def test_strict_mode_async(self):
        async def foo(x: int) -> int:
            """Async foo."""
            return x

        tool = FunctionTool.from_function(foo, strict=True)
        result = await tool.aexecute(x=42)
        self.assertEqual(result, 42)

        # This should raise ValueError because 'y' is not a valid parameter
        with self.assertRaises(ValueError):
            await tool.aexecute(x=1, y=2)
