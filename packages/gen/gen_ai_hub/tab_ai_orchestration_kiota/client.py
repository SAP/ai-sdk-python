"""SAP wrapper client for the Tabular AI Orchestration service using Kiota-generated code.

The generated code under `generated/` is produced by running:

    cd packages/gen && make generate-kiota

This requires `kiota` on PATH (install via `brew install kiota` or
`dotnet tool install --global Microsoft.OpenApi.Kiota`).

Usage::

    from gen_ai_hub.tab_ai_orchestration_kiota import KiotaTabAiOrchestrationClient
    from gen_ai_hub.tab_ai_orchestration_kiota.generated.models.predict_request import PredictRequest

    async with KiotaTabAiOrchestrationClient(model_name="sap-rpt-1.5") as client:
        response = await client.predict.post(PredictRequest(...))
"""

from __future__ import annotations

from typing import Any, Optional, Self, Union

from kiota_abstractions.authentication.authentication_provider import AuthenticationProvider
from kiota_abstractions.request_information import RequestInformation
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy import get_proxy_client

from gen_ai_hub.tab_ai_orchestration_kiota.generated.tab_ai_orchestration_client import (
    TabAiOrchestrationClient as _GeneratedClient,
)


class _SapAuthProvider(AuthenticationProvider):
    """Injects SAP AI Core auth headers into every Kiota request."""

    def __init__(self, proxy: GenAIHubProxyClient) -> None:
        self._proxy = proxy

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: Optional[dict] = None,
    ) -> None:
        for key, value in self._proxy.request_header.items():
            request.headers.try_add(key, value)


def _get_proxy(proxy_client: Optional[GenAIHubProxyClient]) -> GenAIHubProxyClient:
    return proxy_client or get_proxy_client()


def _resolve_deployment_url(
    proxy: GenAIHubProxyClient, model_name: str, model_version: Optional[str]
) -> str:
    from ai_core_sdk.models import Status

    query = proxy.ai_core_client.deployment.query(
        status=Status.RUNNING,
        scenario_id="tabular-orchestration",
        resource_group=proxy.resource_group or "default",
    )
    if not query.resources:
        raise ValueError("No running tabular-orchestration deployment found.")
    return query.resources[0].deployment_url


class KiotaTabAiOrchestrationClient:
    """Kiota-based async client for the Tabular AI Orchestration service.

    Resolves the deployment URL from the proxy client credentials using
    ``model_name`` and optional ``model_version``. Auth headers are injected
    automatically via the SAP proxy client.

    The underlying Kiota-generated client is exposed as ``.generated`` for
    direct access to all request builders.

    Usage::

        async with KiotaTabAiOrchestrationClient(model_name="sap-rpt-1.5") as client:
            response = await client.generated.predict.post(PredictRequest(...))
    """

    def __init__(
        self,
        model_name: str,
        model_version: Optional[str] = None,
        proxy_client: Optional[GenAIHubProxyClient] = None,
        timeout: Union[float, None] = None,
    ) -> None:
        import httpx

        proxy = _get_proxy(proxy_client)
        self._resource_group = proxy.resource_group or "default"
        base_url = _resolve_deployment_url(proxy, model_name, model_version)
        auth = _SapAuthProvider(proxy)

        http_client: Any = None
        if timeout is not None:
            http_client = httpx.AsyncClient(timeout=timeout)

        adapter = HttpxRequestAdapter(
            auth,
            http_client=http_client,
            base_url=base_url,
        )
        self.generated = _GeneratedClient(adapter)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.generated.request_adapter.get_http_client().aclose()  # type: ignore[union-attr]

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
