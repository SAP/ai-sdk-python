from typing import List, Optional
from pydantic import model_validator

from gen_ai_hub.orchestration_v2.models.base import ABCBaseModel as BaseModel
from gen_ai_hub.orchestration_v2.models.config import (OrchestrationConfig, OrchestrationConfigReference,
                                                       PartialOrchestrationConfig)
from gen_ai_hub.orchestration_v2.models.message import ChatMessage

class CompletionPostRequest(BaseModel):
    """
    Represents a request for the orchestration process, including configuration,
    template values, and message history.

    When ``config_ref`` is used, ``config`` may carry a ``PartialOrchestrationConfig``
    that overrides parts of the referenced configuration.
    """
    config: Optional[OrchestrationConfig | PartialOrchestrationConfig] = None
    config_ref: Optional[OrchestrationConfigReference] = None
    placeholder_values: Optional[dict[str, str]] = None
    messages_history: Optional[List[ChatMessage]] = None

    @model_validator(mode="after")
    def validate_config_or_ref(self):
        """Validates the config / config_ref combination.

        Mirrors the three request shapes defined by the spec:
          - inline: a full ``OrchestrationConfig`` in ``config`` and no ``config_ref``;
          - by reference: a ``config_ref`` optionally accompanied by a
            ``PartialOrchestrationConfig`` in ``config`` that overrides the referenced config.

        :raises ValueError: If neither is provided, if an inline ``config`` is not a full
            ``OrchestrationConfig``, or if a ``config`` override alongside ``config_ref`` is
            not a ``PartialOrchestrationConfig``.
        :return: The validated CompletionPostRequest instance.
        :rtype: CompletionPostRequest
        """
        if self.config is None and self.config_ref is None:
            raise ValueError(
                "At least one of 'config' or 'config_ref' must be provided."
            )
        if self.config_ref is None:
            if not isinstance(self.config, OrchestrationConfig):
                raise ValueError(
                    "Inline usage requires a full 'config' (OrchestrationConfig). "
                    "A PartialOrchestrationConfig is only valid as an override alongside 'config_ref'."
                )
        elif self.config is not None and not isinstance(self.config, PartialOrchestrationConfig):
            raise ValueError(
                "When 'config_ref' is provided, 'config' must be a PartialOrchestrationConfig override."
            )
        return self

__all__ = ["CompletionPostRequest"]
