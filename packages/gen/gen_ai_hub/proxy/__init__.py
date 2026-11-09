# `gen_ai_hub.proxy` is a namespace shared across several distributions
# (proxy, amazon, google, openai, rpt, langchain), each shipping it as a plain
# PEP 420 namespace package with NO __init__.py. The `sap-ai-sdk-gen`
# meta-package is the sole exception: it owns this __init__ purely to keep the
# historic `from gen_ai_hub.proxy import GenAIHubProxyClient` import alive for
# users of the legacy all-in-one distribution. pkgutil.extend_path keeps the
# sibling distributions' subpackages (gen_ai_hub.proxy.native.*,
# gen_ai_hub.proxy.langchain, ...) discoverable on sys.path. When `gen` is
# eventually retired, this backwards-compat shim is dropped with it.
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, get_proxy_version, set_proxy_version
from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient

__all__ = ('GenAIHubProxyClient', 'set_proxy_version', 'get_proxy_version', 'get_proxy_client')
