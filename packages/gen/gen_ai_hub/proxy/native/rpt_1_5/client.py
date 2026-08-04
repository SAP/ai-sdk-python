"""RPT 1.5 typed client with SAP proxy authentication."""
from __future__ import annotations

from typing import Self

from generated.api.default_api import DefaultApi
from generated.api_client import ApiClient
from generated.configuration import Configuration
from generated.models.predict_request_payload import PredictRequestPayload
from generated.models.predict_request_payload_one_of import (
    PredictRequestPayloadOneOf as RowsRequest,
)
from generated.models.predict_request_payload_one_of1 import (
    PredictRequestPayloadOneOf1 as ColumnsRequest,
)
from generated.rest import RESTClientObject

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy.native.utils import (
    build_sap_api_client,
    get_proxy_client_instance,
    resolve_deployment_url,
)


class RPT15Client:
    """Async client for the RPT 1.5 prediction service.

    Resolves the deployment URL from the proxy client credentials using
    model_name and optional model_version. All requests are authenticated
    automatically via the SAP proxy client.

    Usage::

        async with RPT15Client(model_name="sap-rpt-1.5") as client:
            response = await client.predict(request)

        # or without context manager
        client = RPT15Client(model_name="sap-rpt-1.5")
        response = await client.predict(request)
        await client.close()
    """

    def __init__(
        self,
        model_name: str,
        model_version: str | None = None,
        proxy_client: GenAIHubProxyClient | None = None,
        timeout: float | None = None,
    ) -> None:
        self._proxy = get_proxy_client_instance(proxy_client)
        base_url = resolve_deployment_url(self._proxy, model_name, model_version)
        self._api_client = build_sap_api_client(
            base_url=base_url,
            proxy_client=self._proxy,
            api_client_class=ApiClient,
            configuration_class=Configuration,
            rest_client_class=RESTClientObject,
            timeout=timeout,
        )
        self._api = DefaultApi(self._api_client)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._api_client.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def predict(self, request: RowsRequest | ColumnsRequest) -> object:
        """Make predictions from JSON data.

        Returns the raw response dict. The generated PredictResponsePayload
        deserializer cannot handle the spec's nested anyOf response structure,
        so response_types_map is set to "object" to bypass it.
        """
        payload = PredictRequestPayload(request)
        _param = self._api._predict_serialize(  # type: ignore[attr-defined]  # pylint: disable=protected-access
            predict_request_payload=payload,
            content_encoding=None,
            _request_auth=None,
            _content_type=None,
            _headers=None,
            _host_index=0,
        )
        response_data = await self._api_client.call_api(*_param)  # type: ignore[arg-type]
        await response_data.read()  # type: ignore[misc]
        return self._api_client.response_deserialize(  # type: ignore[no-any-return]
            response_data=response_data,
            response_types_map={"200": "object"},
        ).data

    async def health(self) -> object:
        """Check the health of the RPT deployment."""
        return await self._api.health()  # type: ignore[no-any-return]
