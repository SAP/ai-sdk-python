"""Backwards-compatible shim for ``gen_ai_hub.proxy.langchain.openai``.

The OpenAI LangChain wrappers moved to :mod:`gen_ai_hub.proxy.native.openai.langchain`
(shipped by ``sap-ai-sdk-openai[langchain]``). This module re-exports them lazily so the
historical import path keeps working when that distribution is installed.
"""
from typing import Any

_TARGET = 'gen_ai_hub.proxy.native.openai.langchain'
_DISTRIBUTION = 'sap-ai-sdk-openai[langchain]'

__all__ = [
    'ChatOpenAI', 'OpenAI', 'OpenAIEmbeddings', 'ProxyOpenAI',
    'init_chat_model', 'init_embedding_model', 'get_client_params',
]


def __getattr__(name: str) -> Any:
    import importlib
    try:
        module = importlib.import_module(_TARGET)
    except ImportError as exc:
        raise ImportError(
            f"'gen_ai_hub.proxy.langchain.openai' requires the '{_DISTRIBUTION}' package. "
            f"Install it with `pip install '{_DISTRIBUTION}'`."
        ) from exc
    return getattr(module, name)
