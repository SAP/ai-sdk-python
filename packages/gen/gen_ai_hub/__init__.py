"""Compatibility shim for the ``gen_ai_hub`` package root.

Kept as a regular package (not an ``alias()`` forwarder) so the real child shim
packages contributed across distributions — ``proxy``, ``prompt_registry``,
``orchestration_v2``, ``document_grounding``, ``batch_service``, ``evaluations`` —
keep resolving. Re-exports the single pre-split root-level symbol so that
``from gen_ai_hub import GenAIHubProxyClient`` keeps working.
"""

from sap_ai_sdk_proxy import GenAIHubProxyClient

__all__ = ('GenAIHubProxyClient',)
