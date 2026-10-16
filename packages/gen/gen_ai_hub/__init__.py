"""Compatibility shim for the legacy ``gen_ai_hub`` import root.

The former ``sap-ai-sdk-gen`` package was split into independent ``sap-ai-sdk-*``
packages. This shim re-exposes the old ``gen_ai_hub.*`` paths; see the individual
submodules for the forwarding targets. New code should import from the ``sap_ai_sdk_*``
packages directly.
"""

from sap_ai_sdk_proxy import GenAIHubProxyClient

__all__ = ['GenAIHubProxyClient']
