"""
Service-specific request headers for the Orchestration Service.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrchestrationRequestHeaders(BaseModel):
    """Service-specific headers for orchestration requests.

    - ``AI-Object-Store-Secret-Name`` is documented explicitly; it is used by the
      feedback service to persist an inference.
    - Arbitrary additional headers are allowed (``extra="allow"``), mirroring the
      JS index signature ``[key: string]: any``.
    - ``AI-Resource-Group`` must not be set here; it is managed by the proxy client
      / deployment configuration.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    ai_object_store_secret_name: Optional[str] = Field(
        default=None,
        alias="AI-Object-Store-Secret-Name",
        description="Name of the object store secret used by the feedback service.",
    )

    @model_validator(mode="before")
    @classmethod
    def _reject_ai_resource_group(cls, data):
        if isinstance(data, dict):
            for key in data:
                if isinstance(key, str) and key.lower() == "ai-resource-group":
                    raise ValueError(
                        "AI-Resource-Group must not be set here; "
                        "it is managed by the proxy client / deployment configuration."
                    )
        return data

    def to_headers(self) -> dict:
        """Serialize to a plain header dict using alias names, dropping unset values."""
        return self.model_dump(by_alias=True, exclude_none=True)
