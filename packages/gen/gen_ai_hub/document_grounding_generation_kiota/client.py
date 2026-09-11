"""SAP wrapper client for the Document Grounding service using Kiota-generated code.

The generated code under `generated/` is produced by running:

    cd packages/gen && make generate-kiota

This requires `kiota` on PATH (install via `brew install kiota` or
`dotnet tool install --global Microsoft.OpenApi.Kiota`).

Usage::

    from gen_ai_hub.document_grounding_generation_kiota import KiotaGroundingApiClient

    client = KiotaGroundingApiClient()
    result = await client.retrieval.search.post(body)
"""

from __future__ import annotations

from typing import Optional

from kiota_abstractions.authentication.authentication_provider import AuthenticationProvider
from kiota_abstractions.request_information import RequestInformation
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from gen_ai_hub.proxy.core.base import BaseProxyClient
from gen_ai_hub.proxy import get_proxy_client

from gen_ai_hub.document_grounding_generation_kiota.generated.document_grounding_client import (
    DocumentGroundingClient,
)


class _SapAuthProvider(AuthenticationProvider):
    """Injects SAP AI Core auth headers into every Kiota request."""

    def __init__(self, proxy_client: BaseProxyClient) -> None:
        self._client = proxy_client

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: Optional[dict] = None,
    ) -> None:
        for key, value in self._client.request_header.items():
            request.headers.try_add(key, value)


def _get_base_url(client: BaseProxyClient) -> str:
    ai_core = getattr(client, "ai_core_client", None)
    if ai_core is None:
        raise ValueError("proxy client has no ai_core_client configured")
    return ai_core.base_url.rstrip("/") + "/lm/document-grounding"


class KiotaGroundingApiClient:
    """Kiota-based async client for the Document Grounding service.

    Resolves auth and base URL from the proxy client automatically.
    If no proxy client is provided, one is created via get_proxy_client().

    Usage::

        client = KiotaGroundingApiClient()
        # access request builders directly on the generated root client
        result = await client.generated.retrieval.search.post(body)
    """

    def __init__(
        self,
        proxy_client: Optional[BaseProxyClient] = None,
        base_url: Optional[str] = None,
    ) -> None:
        client = proxy_client or get_proxy_client()
        url = base_url or _get_base_url(client)
        auth = _SapAuthProvider(client)
        adapter = HttpxRequestAdapter(auth, base_url=url)
        self.generated = DocumentGroundingClient(adapter)
