"""Backwards-compatible shim for ``gen_ai_hub.proxy.langchain.google_genai``.

The Google GenAI LangChain wrappers moved to
:mod:`gen_ai_hub.proxy.native.google_genai.langchain` (shipped by
``sap-ai-sdk-google[langchain]``). This module re-exports them lazily so the historical
import path keeps working when that distribution is installed.
"""
from typing import Any

_TARGET = 'gen_ai_hub.proxy.native.google_genai.langchain'
_DISTRIBUTION = 'sap-ai-sdk-google[langchain]'

__all__ = [
    'ChatGoogleGenerativeAI', 'GoogleGenerativeAIEmbeddings',
    'init_chat_model', 'init_embedding_model',
]


def __getattr__(name: str) -> Any:
    import importlib
    try:
        module = importlib.import_module(_TARGET)
    except ImportError as exc:
        raise ImportError(
            f"'gen_ai_hub.proxy.langchain.google_genai' requires the '{_DISTRIBUTION}' package. "
            f"Install it with `pip install '{_DISTRIBUTION}'`."
        ) from exc
    return getattr(module, name)
