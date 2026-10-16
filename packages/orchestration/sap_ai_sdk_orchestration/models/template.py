"""
Defines data models for prompt templating in the orchestration module.
"""

from typing import List, Optional

from sap_ai_sdk_orchestration.models.base import ABCBaseModel as BaseModel
from sap_ai_sdk_orchestration.models.llm_model_details import LLMModelDetails
from sap_ai_sdk_orchestration.models.message import ChatMessage
from sap_ai_sdk_orchestration.models.response_format import (
    ResponseFormatText,
    ResponseFormatJsonObject,
    ResponseFormatJsonSchema
)
from sap_ai_sdk_orchestration.models.template_ref import TemplateRef
from sap_ai_sdk_orchestration.models.tools import FunctionTool


class Template(BaseModel):
    """
    Represents a configurable template for generating prompts or conversations.

    Args:
        template: A list of prompt messages that form the template.

        defaults: A dict of default values for template variables.

        tools: A list of tool definitions.

        response_format: A response format that the model output should adhere to.
    """
    template: List[ChatMessage]
    defaults: Optional[dict] = None
    response_format: Optional[ResponseFormatText | ResponseFormatJsonObject | ResponseFormatJsonSchema] = None
    tools: Optional[List[dict | FunctionTool]] = None


class PromptTemplatingModuleConfig(BaseModel):
    prompt: Template | TemplateRef
    model: LLMModelDetails

__all__ = ["Template", "PromptTemplatingModuleConfig"]
