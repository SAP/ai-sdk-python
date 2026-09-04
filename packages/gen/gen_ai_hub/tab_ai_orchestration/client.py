"""Typed async client for the Tabular AI Orchestration service."""
from __future__ import annotations

from typing import Any, Optional, Self, Union

import httpx

from gen_ai_hub.tab_ai_orchestration.generated.api.predict_api import PredictApi
from gen_ai_hub.tab_ai_orchestration.generated.api_client import ApiClient
from gen_ai_hub.tab_ai_orchestration.generated.configuration import Configuration
from gen_ai_hub.tab_ai_orchestration.generated.models.predict_request import PredictRequest
from gen_ai_hub.tab_ai_orchestration.generated.models.predict_response import PredictResponse
from gen_ai_hub.tab_ai_orchestration.generated.rest import RESTClientObject

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy import get_proxy_client


def _get_proxy(proxy_client: Optional[GenAIHubProxyClient]) -> GenAIHubProxyClient:
    return proxy_client or get_proxy_client(proxy_version="gen-ai-hub")


def _resolve_deployment_url(proxy: GenAIHubProxyClient, model_name: str, model_version: Optional[str]) -> str:
    from ai_core_sdk.models import Status
    query = proxy.ai_core_client.deployment.query(
        status=Status.RUNNING,
        scenario_id="tabular-orchestration",
        resource_group=proxy.resource_group or "default",
    )
    if not query.resources:
        raise ValueError("No running tabular-orchestration deployment found.")
    return query.resources[0].deployment_url


def _make_auth_hook(proxy: GenAIHubProxyClient):
    async def inject_auth(request: httpx.Request) -> None:
        for key, value in proxy.request_header.items():
            request.headers[key] = value
    return inject_auth


class _SapRESTClientObject(RESTClientObject):
    def __init__(self, configuration: Configuration, proxy: GenAIHubProxyClient, timeout: Any) -> None:
        super().__init__(configuration)
        self._proxy = proxy
        self._timeout = timeout

    def _create_pool_manager(self) -> httpx.AsyncClient:
        kwargs: dict[str, Any] = {"event_hooks": {"request": [_make_auth_hook(self._proxy)]}}
        if self._timeout is not None:
            kwargs["timeout"] = self._timeout
        return httpx.AsyncClient(**kwargs)


class _SapApiClient(ApiClient):
    def __init__(self, configuration: Configuration, proxy: GenAIHubProxyClient, timeout: Any) -> None:
        super().__init__(configuration=configuration)
        self.rest_client = _SapRESTClientObject(configuration, proxy, timeout)

    def sanitize_for_serialization(self, obj: Any) -> Any:
        # The base class calls obj.to_dict() which includes additional_properties.
        # Override to strip it at all levels while preserving camelCase aliases.
        from pydantic import BaseModel
        if obj is None:
            return None
        if isinstance(obj, BaseModel):
            d = obj.model_dump(by_alias=True, exclude_none=True, exclude={"additional_properties"})
            return self.sanitize_for_serialization(d)
        if isinstance(obj, dict):
            return {k: self.sanitize_for_serialization(v) for k, v in obj.items() if k != "additional_properties"}
        if isinstance(obj, list):
            return [self.sanitize_for_serialization(i) for i in obj]
        return super().sanitize_for_serialization(obj)


class TabAiOrchestrationClient:
    """Async client for the Tabular AI Orchestration service.

    Resolves the deployment URL from the proxy client credentials using
    ``model_name`` and optional ``model_version``. Auth headers are injected
    automatically via the SAP proxy client.

    Usage::

        async with TabAiOrchestrationClient(model_name="sap-rpt-1.5") as client:
            response = await client.predict(
                ai_resource_group="default",
                predict_request=PredictRequest(...),
            )

        # or without context manager
        client = TabAiOrchestrationClient(model_name="sap-rpt-1.5")
        response = await client.predict(...)
        await client.close()
    """

    def __init__(
        self,
        model_name: str,
        model_version: Optional[str] = None,
        proxy_client: Optional[GenAIHubProxyClient] = None,
        timeout: Union[float, None] = None,
    ) -> None:
        proxy = _get_proxy(proxy_client)
        base_url = _resolve_deployment_url(proxy, model_name, model_version)
        config = Configuration(host=base_url)
        self._api_client = _SapApiClient(config, proxy, timeout)
        self._predict_api = PredictApi(self._api_client)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._api_client.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def predict(
        self,
        predict_request: PredictRequest,
        ai_resource_group: str,
    ) -> PredictResponse:
        """Make predictions using a Tabular Foundation Model.

        :param predict_request: The prediction request payload.
        :param ai_resource_group: AI Core resource group identifier.
        :returns: Prediction response from the model.
        """
        return await self._predict_api.predict(  # type: ignore[no-any-return]
            ai_resource_group=ai_resource_group,
            predict_request=predict_request,
        )
