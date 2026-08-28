"""SAP AI Core authentication wiring for the generated document grounding client.

Subclasses the generated RESTClientObject and ApiClient to inject auth headers
from an AiCoreV2Client or GenAIHubProxyClient via httpx event hooks — the same
pattern used in packages/gen (PR #44 utils.py).

Usage:
    from ai_core_sdk.ai_core_v2_client import AICoreV2Client
    from gen_ai_hub.document_grounding_generation import GroundingApiClient, VectorApi

    client = GroundingApiClient(AICoreV2Client.from_env())
    collections = await VectorApi(client).get_all_collections(
        header_parameters={"AI-Resource-Group": "default"}
    )
"""

from __future__ import annotations

from typing import Any

import httpx

from gen_ai_hub.document_grounding_generation.generated.api_client import ApiClient
from gen_ai_hub.document_grounding_generation.generated.configuration import Configuration
from gen_ai_hub.document_grounding_generation.generated.rest import RESTClientObject


def _make_auth_hook(proxy_client: Any):
    """Return an httpx request event hook that injects SAP AI Core auth headers."""

    async def inject_auth(request: httpx.Request) -> None:
        for key, value in proxy_client.request_header.items():
            request.headers[key] = value

    return inject_auth


class _SapRESTClientObject(RESTClientObject):
    def __init__(self, configuration: Configuration, proxy_client: Any) -> None:
        super().__init__(configuration)
        self._proxy_client = proxy_client

    def _create_pool_manager(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            event_hooks={"request": [_make_auth_hook(self._proxy_client)]}
        )


class GroundingApiClient(ApiClient):
    """ApiClient pre-wired with SAP AI Core authentication.

    Args:
        proxy_client: An AICoreV2Client or GenAIHubProxyClient instance.
            Its request_header property is called per-request to inject
            Authorization and AI-* headers.
        base_url: Optional override for the service base URL. Defaults to the
            basePath baked into Configuration (/lm/document-grounding).
    """

    def __init__(self, proxy_client: Any, base_url: str | None = None) -> None:
        config = Configuration(host=base_url) if base_url else Configuration()
        super().__init__(configuration=config)
        self.rest_client = _SapRESTClientObject(config, proxy_client)
