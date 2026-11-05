"""Compatibility shim for the ``gen_ai_hub.proxy`` package root.

Unlike the leaf forwarders in this tree, this module must NOT swap itself out of
``sys.modules`` via ``alias()``: ``gen_ai_hub.proxy`` owns real child shim packages
(``gen_ai_hub_proxy``, ``core``, ``native``, ``langchain``) that are contributed by
several distributions. Replacing this module object with ``sap_ai_sdk_proxy`` would
drop those children. Instead we keep this as a regular package and re-export the
pre-split top-level symbols, matching the old ``gen_ai_hub.proxy`` surface.
"""

from sap_ai_sdk_proxy import (
    GenAIHubProxyClient,
    get_proxy_client,
    get_proxy_version,
    set_proxy_version,
)

__all__ = (
    'GenAIHubProxyClient',
    'set_proxy_version',
    'get_proxy_version',
    'get_proxy_client',
)
