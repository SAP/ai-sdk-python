from __future__ import annotations

import httpx
from gen_ai_hub.proxy.core.base import BaseProxyClient

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
    """ApiClient pre-wired with a BaseProxyClient (e.g. from get_proxy_client())."""

    def __init__(self, client: BaseProxyClient, base_url: str | None = None) -> None:
        config = Configuration(host=base_url or _get_base_url(client))
        super().__init__(configuration=config)
        self.rest_client = _SapRESTClientObject(config, client)
