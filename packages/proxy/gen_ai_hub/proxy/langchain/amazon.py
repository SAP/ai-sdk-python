"""Backwards-compatible shim for ``gen_ai_hub.proxy.langchain.amazon``.

The Amazon Bedrock LangChain wrappers moved to
:mod:`gen_ai_hub.proxy.native.amazon.langchain` (shipped by
``sap-ai-sdk-amazon[langchain]``). This module re-exports them lazily so the historical
import path keeps working when that distribution is installed.
"""
from typing import Any

_TARGET = 'gen_ai_hub.proxy.native.amazon.langchain'
_DISTRIBUTION = 'sap-ai-sdk-amazon[langchain]'

__all__ = [
    'AICoreBedrockBaseModel', 'ChatBedrock', 'ChatBedrockConverse', 'BedrockEmbeddings',
    'init_chat_model', 'init_chat_converse_model', 'init_embedding_model',
]


def __getattr__(name: str) -> Any:
    import importlib
    try:
        module = importlib.import_module(_TARGET)
    except ImportError as exc:
        raise ImportError(
            f"'gen_ai_hub.proxy.langchain.amazon' requires the '{_DISTRIBUTION}' package. "
            f"Install it with `pip install '{_DISTRIBUTION}'`."
        ) from exc
    return getattr(module, name)
