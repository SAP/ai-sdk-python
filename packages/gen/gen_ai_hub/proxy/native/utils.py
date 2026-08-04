"""Shared utilities for spec-generated native proxy clients."""
from typing import Any, Optional, Union

import httpx

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy import get_proxy_client


def get_proxy_client_instance(proxy_client: Optional[GenAIHubProxyClient] = None) -> GenAIHubProxyClient:
    """Return the provided proxy client, or the process-default one."""
    return proxy_client or get_proxy_client(proxy_version="gen-ai-hub")


def resolve_deployment_url(
    proxy_client: GenAIHubProxyClient,
    model_name: str,
    model_version: Optional[str] = None,
) -> str:
    """Resolve a deployment base URL from model identity via the proxy client."""
    filters = {"model_name": model_name}
    if model_version:
        filters["model_version"] = model_version
    try:
        return proxy_client.select_deployment(**filters).url
    except ValueError:
        raise ValueError(f"No deployment found for the given parameters: {filters}.")


def _make_auth_hook(proxy_client: GenAIHubProxyClient):
    async def inject_auth(request: httpx.Request) -> None:
        for key, value in proxy_client.request_header.items():
            request.headers[key] = value
    return inject_auth


def build_sap_async_httpx_client(
    proxy_client: GenAIHubProxyClient,
    timeout: Union[int, float, "httpx.Timeout", None] = None,
) -> "httpx.AsyncClient":
    """httpx.AsyncClient with SAP auth injected via event hook."""
    kwargs: dict[str, Any] = {"event_hooks": {"request": [_make_auth_hook(proxy_client)]}}
    if timeout is not None:
        kwargs["timeout"] = timeout
    return httpx.AsyncClient(**kwargs)


def build_sap_api_client(
    base_url: str,
    proxy_client: GenAIHubProxyClient,
    api_client_class: Any,
    configuration_class: Any,
    rest_client_class: Any,
    timeout: Union[int, float, None] = None,
) -> Any:
    """Build a generated ApiClient subclassed with SAP auth and deployment URL.

    Each generated package has its own ApiClient, Configuration, and RESTClientObject.
    Pass those classes here so the SAP auth wiring can be applied generically.

    :param base_url: Deployment URL resolved from the proxy client.
    :param proxy_client: Authenticated SAP proxy client.
    :param api_client_class: The generated ApiClient class for this package.
    :param configuration_class: The generated Configuration class for this package.
    :param rest_client_class: The generated RESTClientObject class for this package.
    :param timeout: Optional request timeout.
    :return: Configured ApiClient instance with SAP auth.
    """
    _build_sap_async_httpx_client = build_sap_async_httpx_client  # capture for closure

    class _SapRESTClientObject(rest_client_class):
        def __init__(self, configuration: Any) -> None:
            super().__init__(configuration)
            self._sap_proxy = proxy_client
            self._sap_timeout = timeout

        def _create_pool_manager(self) -> Any:
            return _build_sap_async_httpx_client(self._sap_proxy, self._sap_timeout)

    class _SapApiClient(api_client_class):
        def __init__(self) -> None:
            config = configuration_class(host=base_url)
            super().__init__(configuration=config)
            self.rest_client = _SapRESTClientObject(config)

    return _SapApiClient()
