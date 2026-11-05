# `gen_ai_hub` is the root namespace shared by every SAP AI SDK distribution.
# The proxy distribution owns this __init__ and uses pkgutil.extend_path so all
# sibling distributions' subpackages (gen_ai_hub.evaluations, gen_ai_hub.proxy,
# gen_ai_hub.orchestration_v2, ...) are still discovered on sys.path, while we
# re-export GenAIHubProxyClient to keep the historic top-level
# `from gen_ai_hub import GenAIHubProxyClient` import alive.
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from .proxy.gen_ai_hub_proxy import GenAIHubProxyClient

__all__ = ['GenAIHubProxyClient']
