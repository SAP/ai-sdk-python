"""Cache control for prompt caching on supported Anthropic and Amazon Nova models."""
from typing import Any, Dict, Literal, Optional

from pydantic import model_serializer

from gen_ai_hub.orchestration_v2.models.base import ABCBaseModel as BaseModel


class CacheControl(BaseModel):
    """Marks a message content block or tool definition for prompt caching.

    When attached to a content block, the model stores intermediate computation
    results for that content and reuses them on subsequent requests within the
    TTL window, reducing both latency and token costs.

    Supported models:
        - Anthropic Claude: system and user content blocks; tools.
        - Amazon Nova: system and user content blocks only (no tools, no TTL).

    Attach ``CacheControl`` directly to a content block (``TextPart``, ``ImagePart``) or
    to a ``ChatCompletionTool``.
    
    Args:
        type: ``"ephemeral"``
        ttl: Cache duration. ``"5m"`` (default) or ``"1h"`` (select Anthropic
             models only). Omit for Amazon Nova or when the default is sufficient.
    """

    type: Literal["ephemeral"]
    ttl: Optional[Literal["5m", "1h"]] = None

    @model_serializer(mode="wrap")
    def serialize_wire_format(self, handler: Any) -> Dict[str, Any]:
        """Serialize to the wire format, omitting ``ttl`` when not set.

        :return: ``{"type": "ephemeral"}`` or ``{"type": "ephemeral", "ttl": "<value>"}``
        :rtype: dict
        """
        data: Dict[str, Any] = handler(self)
        if data.get("ttl") is None:
            data.pop("ttl", None)
        return data
