# `gen_ai_hub.proxy` is a namespace shared across several distributions
# (proxy, amazon, google, openai, rpt, langchain). The proxy distribution owns
# this __init__ and uses pkgutil.extend_path so the sibling distributions'
# subpackages (gen_ai_hub.proxy.native.*, gen_ai_hub.proxy.langchain, ...) are
# still discovered on sys.path, while we re-export the core proxy API to keep
# the historic `from gen_ai_hub.proxy import GenAIHubProxyClient` import alive.
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from .core.proxy_clients import get_proxy_client, get_proxy_version, set_proxy_version
from .gen_ai_hub_proxy import GenAIHubProxyClient

__all__ = ('GenAIHubProxyClient', 'set_proxy_version', 'get_proxy_version', 'get_proxy_client')
