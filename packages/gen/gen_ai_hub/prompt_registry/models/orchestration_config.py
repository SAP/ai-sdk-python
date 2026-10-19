from typing import List, Optional
from pydantic import BaseModel, Field


from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig

# Orchestration v2 spec fields that the Prompt Registry config schema does not yet accept.
_PROMPT_REGISTRY_UNSUPPORTED_SPEC_KEYS = ("drop_unsupported_params",)


def _strip_keys(value, keys):
    """Recursively remove ``keys`` from nested dicts/lists."""
    if isinstance(value, dict):
        return {k: _strip_keys(v, keys) for k, v in value.items() if k not in keys}
    if isinstance(value, list):
        return [_strip_keys(item, keys) for item in value]
    return value


class OrchestrationConfigPostRequest(BaseModel):
    """
    Request to create an orchestration config.

    Args:
        name: The name of the orchestration config.
        version: The version of the orchestration config.
        scenario: The scenario of the orchestration config.
        spec: The orchestration config specification.
    """
    name: str = Field(max_length=120)
    version: str = Field(max_length=10)
    scenario: str = Field(max_length=120)
    spec: OrchestrationConfig

    def model_dump(self, **kwargs):
        """Dumps the model, stripping orchestration fields the Prompt Registry rejects."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        data = super().model_dump(**kwargs)
        data["spec"] = _strip_keys(data.get("spec", {}), _PROMPT_REGISTRY_UNSUPPORTED_SPEC_KEYS)
        return data


class OrchestrationConfigPostResponse(BaseModel):
    """
    Response to the orchestration config post request.

    Args:
        message: Response message.
        id: UUID of the created/updated config.
        scenario: The scenario name.
        name: The config name.
        version: The config version.
    """
    message: str
    id: str
    scenario: str
    name: str
    version: str


class OrchestrationConfigGetResponse(BaseModel):
    """
    Response to a get orchestration config request.

    Args:
        id: UUID of the config.
        name: Config name.
        version: Config version.
        scenario: Scenario name.
        creation_timestamp: When the config was created.
        managed_by: Who manages the config.
        is_version_head: Whether this is the head version.
        spec: The orchestration config specification (optional).
    """
    id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    scenario: Optional[str] = None
    creation_timestamp: Optional[str] = None
    managed_by: Optional[str] = None
    is_version_head: Optional[bool] = None
    resource_group_id: Optional[str] = None
    spec: Optional[OrchestrationConfig] = None

    def model_dump(self, **kwargs):
        """Dumps the model to a dictionary with default settings."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        return super().model_dump(**kwargs)



class OrchestrationConfigListResponse(BaseModel):
    """
    Response to list orchestration configs request.

    Args:
        count: Number of configs returned.
        resources: List of OrchestrationConfigGetResponse objects.
    """
    count: int
    resources: List[OrchestrationConfigGetResponse]

    def model_dump(self, **kwargs):
        """Dumps the model to a dictionary with default settings."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        return super().model_dump(**kwargs)


class OrchestrationConfigDeleteResponse(BaseModel):
    """
    Response to a delete orchestration config request.

    Args:
        message: Response message.
    """
    message: str
