"""Shim for ``gen_ai_hub.proxy``.

Re-exports the proxy root symbols from ``sap_ai_sdk_proxy``. This stays a real package
(rather than a ``sys.modules`` alias) because its children map to *different* new
packages: ``native.amazon`` -> ``sap_ai_sdk_amazon``, ``native.google_genai`` ->
``sap_ai_sdk_google``, ``langchain`` -> ``sap_ai_sdk_langchain`` (+ providers).
"""

from sap_ai_sdk_proxy import (
    GenAIHubProxyClient,
    get_proxy_client,
    get_proxy_version,
    set_proxy_version,
)

__all__ = ('GenAIHubProxyClient', 'set_proxy_version', 'get_proxy_version', 'get_proxy_client')
