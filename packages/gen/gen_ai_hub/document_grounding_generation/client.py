"""SAP AI Core authentication wiring for the generated document grounding client.

Subclasses the generated RESTClientObject and ApiClient to inject auth headers
from an AICoreV2Client or GenAIHubProxyClient via httpx event hooks.

Usage:
    from ai_core_sdk.ai_core_v2_client import AICoreV2Client
    from gen_ai_hub.document_grounding_generation import GroundingApiClient, VectorApi

    client = GroundingApiClient(AICoreV2Client.from_env())
    result = await VectorApi(client).get_all_collections(ai_resource_group="default")
"""

from __future__ import annotations

from typing import Any

import httpx

from gen_ai_hub.document_grounding_generation.generated.api_client import ApiClient
from gen_ai_hub.document_grounding_generation.generated.configuration import Configuration
from gen_ai_hub.document_grounding_generation.generated.rest import RESTClientObject


def _get_base_url(proxy_client: Any) -> str:
    """Extract the service base URL from an AICoreV2Client or GenAIHubProxyClient."""
    # GenAIHubProxyClient wraps an AICoreV2Client under .ai_core_client
    ai_core = getattr(proxy_client, "ai_core_client", proxy_client)
    base_url: str = getattr(ai_core, "base_url", "")
    return base_url.rstrip("/") + "/lm/document-grounding"


def _get_headers(proxy_client: Any) -> dict:
    """Get auth headers, supporting both AICoreV2Client and GenAIHubProxyClient."""
    # GenAIHubProxyClient exposes request_header directly
    if hasattr(proxy_client, "request_header"):
        return proxy_client.request_header
    # AICoreV2Client: build headers from the underlying rest_client token
    rest_client = getattr(proxy_client, "rest_client", None)
    if rest_client is not None:
        headers = dict(getattr(rest_client, "headers", {}))
        get_token = getattr(rest_client, "get_token", None)
        if get_token is not None:
            headers["Authorization"] = f"Bearer {get_token()}"
        return headers
    return {}


def _make_auth_hook(proxy_client: Any):
    """Return an httpx request event hook that injects SAP AI Core auth headers."""

    async def inject_auth(request: httpx.Request) -> None:
        for key, value in _get_headers(proxy_client).items():
            request.headers[key] = value

    return inject_auth


class _SapRESTClientObject(RESTClientObject):
    def __init__(self, configuration: Configuration, proxy_client: Any) -> None:
        super().__init__(configuration)
        self._proxy_client = proxy_client

    def _create_pool_manager(self) -> httpx.AsyncClient:
        # Build on top of the parent's pool manager to keep SSL/proxy settings,
        # then add the auth event hook.
        client = super()._create_pool_manager()
        hooks = dict(client.event_hooks)
        hooks["request"] = list(hooks.get("request", [])) + [_make_auth_hook(self._proxy_client)]
        client.event_hooks = hooks
        return client


class GroundingApiClient(ApiClient):
    """ApiClient pre-wired with SAP AI Core authentication.

    Args:
        proxy_client: An AICoreV2Client or GenAIHubProxyClient instance.
        base_url: Optional override for the full service base URL. Defaults to
            <proxy_client.base_url>/lm/document-grounding.
    """

    def __init__(self, proxy_client: Any, base_url: str | None = None) -> None:
        host = base_url or _get_base_url(proxy_client)
        config = Configuration(host=host)
        super().__init__(configuration=config)
        self.rest_client = _SapRESTClientObject(config, proxy_client)
