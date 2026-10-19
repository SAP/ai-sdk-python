"""
Module defining the LLM (Large Language Model) configuration model.
"""

from typing import Optional, Dict

from pydantic import Field, StrictBool

from gen_ai_hub.orchestration_v2.models.base import ABCBaseModel as BaseModel


class LLMModelDetails(BaseModel):
    """
    The model and parameters to be used for the prompt templating.
    This is the model that will be used to generate the response.

    Args:
        name: Name of the model as in LLM Access configuration.

        version: Version of the model to be used. Defaults to "latest".

        params: Additional parameters for the model. Default values are used for mandatory parameters.

        timeout: Timeout for the LLM request in seconds. This parameter is currently ignored for Vertex AI models.

        max_retries: Maximum number of retries for the LLM request. This parameter is currently ignored for Vertex AI models.

        drop_unsupported_params: Controls behaviour when Chat Completions parameters not supported by the
            Responses API are present in the request. Only applies to models that use the Responses API.
            When True: unsupported params are silently dropped and reported in the
            X-Orchestration-Dropped-Model-Params response header. When False: any unsupported parameter
            causes a 400 error with an actionable message. Defaults to True on the server when omitted.
    """
    name: str
    version: Optional[str] = "latest"
    params: Optional[Dict] = None
    timeout: Optional[int] = Field(default=600, ge=1, le=1200)
    max_retries: Optional[int] = Field(default=2, ge=0, le=5)
    # Server defaults this to True when omitted.
    drop_unsupported_params: Optional[StrictBool] = None

__all__ = ["LLMModelDetails"]
