# `gen_ai_hub` is the root namespace shared by every SAP AI SDK distribution.
# All individual distributions (proxy, amazon, google, ...) ship it as a plain
# PEP 420 namespace package with NO __init__.py. The `sap-ai-sdk-gen`
# meta-package is the sole exception: it owns this __init__ purely to keep the
# historic top-level `from gen_ai_hub import GenAIHubProxyClient` import alive
# for users of the legacy all-in-one distribution. pkgutil.extend_path keeps the
# sibling distributions' subpackages (gen_ai_hub.evaluations, gen_ai_hub.proxy,
# gen_ai_hub.orchestration_v2, ...) discoverable on sys.path. When `gen` is
# eventually retired, this backwards-compat shim is dropped with it and the
# remaining distributions stay clean PEP 420 namespaces.
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient

__all__ = ['GenAIHubProxyClient']
