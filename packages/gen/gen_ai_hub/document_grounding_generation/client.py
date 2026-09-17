from __future__ import annotations

from typing import Optional

import httpx
from gen_ai_hub.proxy.core.base import BaseProxyClient
from gen_ai_hub.proxy import get_proxy_client

from gen_ai_hub.document_grounding_generation.generated.api_client import ApiClient
from gen_ai_hub.document_grounding_generation.generated.configuration import (
    Configuration,
)
from gen_ai_hub.document_grounding_generation.generated.rest import RESTClientObject


def _get_base_url(client: BaseProxyClient) -> str:
    ai_core = getattr(client, "ai_core_client", None)
    if ai_core is None:
        raise ValueError("proxy client has no ai_core_client configured")
    return ai_core.base_url.rstrip("/") + "/lm/document-grounding"


class _SapRESTClientObject(RESTClientObject):
    def __init__(self, configuration: Configuration, client: BaseProxyClient) -> None:
        super().__init__(configuration)
        self._client = client

    def _create_pool_manager(self) -> httpx.AsyncClient:
        pool = super()._create_pool_manager()
        hooks = dict(pool.event_hooks)
        hooks["request"] = list(hooks.get("request", [])) + [self._inject_auth]
        pool.event_hooks = hooks
        return pool

    async def _inject_auth(self, request: httpx.Request) -> None:
        for key, value in self._client.request_header.items():
            request.headers[key] = value


class GroundingApiClient(ApiClient):
    """ApiClient for the Document Grounding service.

    Resolves auth and base URL from the proxy client automatically.
    If no proxy client is provided, one is created via get_proxy_client().
    """

    def __init__(
        self,
        proxy_client: Optional[BaseProxyClient] = None,
        base_url: Optional[str] = None,
    ) -> None:
        client = proxy_client or get_proxy_client()
        config = Configuration(host=base_url or _get_base_url(client))
        super().__init__(configuration=config)
        self.rest_client = _SapRESTClientObject(config, client)
