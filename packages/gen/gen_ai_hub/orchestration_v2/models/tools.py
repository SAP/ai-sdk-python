# pylint: disable=duplicate-code
"""
Models for tools used in chat completions with function calling.
"""

import inspect
import typing
from typing import Any, Callable
from typing import Literal, Optional

from pydantic import Field

from gen_ai_hub.orchestration_v2.models.base import ABCBaseModel as BaseModel
from gen_ai_hub.orchestration_v2.models.cache_control import CacheControl


def python_type_to_json_type(py_type):
    """Convert a Python type to a JSON Schema type.

    :param py_type: the Python type to convert
    :type py_type: any
    :return: A dictionary representing the JSON Schema type.
    :rtype: dict
    """
    origin = typing.get_origin(py_type)
    args = typing.get_args(py_type)

    # Simple types
    if py_type is str:
        return {"type": "string"}
    if py_type in (int, float):
        return {"type": "number"}
    if py_type is bool:
        return {"type": "boolean"}
    if py_type is type(None):
        return {"type": "null"}

    # List/array
    if origin in (list, typing.List):
        item_type = args[0] if args else str
        return {
            "type": "array",
            "items": python_type_to_json_type(item_type)
        }

    # Dict/object
    if origin in (dict, typing.Dict):
        value_type = args[1] if len(args) > 1 else str
        return {
            "type": "object",
            "additionalProperties": python_type_to_json_type(value_type)
        }

    # Union/Optional
    if origin is typing.Union:
        json_types = [python_type_to_json_type(a) for a in args]
        # Handle Optional[X] (Union[X, NoneType])
        non_null_types = [t for t in json_types if t.get("type") != "null"]
        if len(json_types) == 2 and len(non_null_types) == 1:
            result = non_null_types[0].copy()
            result["nullable"] = True
            return result
        return {"anyOf": json_types}

    # Fallback
    return {"type": "string"}


class ChatCompletionTool(BaseModel):
    """A tool the model may call, identified by type ``"function"``.

    Args:
        cache_control: Prompt-caching directive. Supported on Anthropic Claude only;
            not supported on Amazon Nova.
    """
    type_: Literal["function"] = Field(default="function", alias="type")
    cache_control: Optional[CacheControl] = None


class FunctionObject(BaseModel):
    """A function definition used inside a ``FunctionTool``.

    Args:
        name: Function name. Must match ``^[a-zA-Z0-9_-]+$``, max 64 chars.
        description: What the function does; used by the model to decide when to call it.
        parameters: JSON Schema object describing accepted parameters.
        strict: When ``True``, the model follows the schema exactly. Defaults to ``False``.
    """
    description: Optional[str] = None
    name: str
    parameters: Optional[dict]
    strict: bool = False
    function: Optional[Callable] = Field(default=None, exclude=True)


class FunctionTool(ChatCompletionTool):
    """A callable function tool for OpenAI-style function calling.

    Inherits all fields from :class:`ChatCompletionTool`:

    Args:
        type: Always ``"function"``. Serialized via the ``type`` alias.
        cache_control: Prompt-caching directive. Supported on Anthropic Claude only;
            not supported on Amazon Nova.

    Additional args:

        function: The function definition — name, description, parameters schema,
            and optional strict flag. See :class:`FunctionObject`.
    """
    function: FunctionObject

    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the function with the provided arguments.
        """
        if self.function.function is None:
            raise ValueError("Function is not set.")

        if self.function.strict:
            for key in kwargs.keys():
                if key not in self.function.parameters["properties"]:
                    raise ValueError(f"Unexpected argument '{key}' for function '{self.function.name}'")

        return self.function.function(**kwargs)

    async def aexecute(self, **kwargs: Any) -> Any:
        """
        Asynchronously execute the function with the provided arguments.
        """
        if self.function.function is None:
            raise ValueError("Function is not set.")

        if self.function.strict:
            for key in kwargs.keys():
                if key not in self.function.parameters["properties"]:
                    raise ValueError(f"Unexpected argument '{key}' for function '{self.function.name}'")

        return await self.function.function(**kwargs)

    @staticmethod
    def from_function(
            func: Callable,
            *,
            description: Optional[str] = None,
            strict: bool = False
    ) -> "FunctionTool":
        """
        Create a FunctionTool from a Python function.

        Args:
                func (Callable): The function to be converted to a FunctionTool.

                description (Optional[str]): A description of the function. Defaults to the docstring of the function.

                strict (bool): Whether to enable strict schema adherence when generating the function call.
        """
        tool_description = description or inspect.getdoc(func)
        sig = inspect.signature(func)
        type_hints = typing.get_type_hints(func)
        param_schema = {}

        for name, param in sig.parameters.items():
            if name not in type_hints:
                raise TypeError(
                    f"Parameter '{name}' in '{func.__name__}' is missing a type hint."
                )
            param_type = type_hints.get(name, str)
            param_schema[name] = python_type_to_json_type(param_type)

        parameters = {
            "type": "object",
            "properties": param_schema,
            "required": [
                name for name, param in sig.parameters.items()
                if param.default is inspect.Parameter.empty
            ],
            "additionalProperties": False
        }

        return FunctionTool(
            function=FunctionObject(
                name=func.__name__,
                description=tool_description,
                parameters=parameters,
                strict=strict,
                function=func)
        )


def function_tool(
        func: Optional[Callable] = None, *, description: Optional[str] = None, strict: bool = False
) -> Callable[[Callable], FunctionTool] | FunctionTool:
    """
    Decorator that converts a function into a FunctionTool.

    Usage:
        @function_tool
        def my_func(...): ...

        @function_tool()
        def my_func(...): ...
    """

    def decorator(func_: Callable) -> FunctionTool:
        return FunctionTool.from_function(func=func_, description=description, strict=strict)

    if func is not None and callable(func):
        # Used as @function_tool
        return decorator(func)

    # Used as @function_tool()
    return decorator

__all__ = [
    "python_type_to_json_type",
    "ChatCompletionTool",
    "FunctionObject",
    "FunctionTool",
    "function_tool"
]
