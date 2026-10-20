"""LangChain integration for the Generative AI Hub.

The provider-agnostic model factories (:func:`init_llm`, :func:`init_embedding_model`)
live here and ship with ``sap-ai-sdk-proxy``. The provider-specific wrapper classes
(``ChatOpenAI``, ``ChatBedrock``, ``ChatGoogleGenerativeAI``, ...) are shipped by the
provider distributions (``sap-ai-sdk-openai``/``-amazon``/``-google``) and are imported
lazily on first access, so importing this package never pulls in an uninstalled
provider's dependencies.
"""
from typing import Any

from .init_models import init_embedding_model, init_llm

# Make sure the user has a recent version of langchain installed - but only if it is
# installed at all. The base proxy distribution does not depend on langchain.
try:
    import langchain
except ImportError:
    pass
else:
    from packaging import version
    if version.parse(langchain.__version__) < version.parse('0.1.0'):
        raise ImportError('langchain<0.1.0 is no longer supported. Please upgrade to version 0.1.0 or higher.')


__all__ = [
    'init_llm',
    'init_embedding_model',
    # Provider wrappers, resolved lazily via __getattr__ (see _LAZY_EXPORTS):
    'OpenAI',
    'OpenAIClient',
    'OpenAIEmbeddings',
    'AsyncOpenAIClient',
    'ChatOpenAI',
    'BedrockEmbeddings',
    'AICoreBedrockBaseModel',
    'ChatBedrock',
    'ChatBedrockConverse',
    'ChatGoogleGenerativeAI',
    'GoogleGenerativeAIEmbeddings',
]

# Back-compat: map names that previously lived in this package to their new
# provider-local module and the distribution (with extra) that supplies them.
_OPENAI_LC = ('gen_ai_hub.proxy.native.openai.langchain', 'sap-ai-sdk-openai[langchain]')
_AMAZON_LC = ('gen_ai_hub.proxy.native.amazon.langchain', 'sap-ai-sdk-amazon[langchain]')
_GOOGLE_LC = ('gen_ai_hub.proxy.native.google_genai.langchain', 'sap-ai-sdk-google[langchain]')

_LAZY_EXPORTS = {
    'OpenAI': _OPENAI_LC,
    'OpenAIEmbeddings': _OPENAI_LC,
    'ChatOpenAI': _OPENAI_LC,
    'BedrockEmbeddings': _AMAZON_LC,
    'AICoreBedrockBaseModel': _AMAZON_LC,
    'ChatBedrock': _AMAZON_LC,
    'ChatBedrockConverse': _AMAZON_LC,
    'ChatGoogleGenerativeAI': _GOOGLE_LC,
    'GoogleGenerativeAIEmbeddings': _GOOGLE_LC,
    # The native OpenAI clients were historically re-exported here under these aliases.
    'OpenAIClient': ('gen_ai_hub.proxy.native.openai', 'sap-ai-sdk-openai'),
    'AsyncOpenAIClient': ('gen_ai_hub.proxy.native.openai', 'sap-ai-sdk-openai'),
}

# Names that resolve to a differently-named attribute in the target module.
_LAZY_ATTR = {
    'OpenAIClient': 'OpenAI',
    'AsyncOpenAIClient': 'AsyncOpenAI',
}


def __getattr__(name: str) -> Any:
    """Lazily resolve provider wrapper classes from their provider distribution."""
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    import importlib
    module_path, distribution = _LAZY_EXPORTS[name]
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ImportError(
            f"'{name}' requires the '{distribution}' package. "
            f"Install it with `pip install '{distribution}'`."
        ) from exc
    return getattr(module, _LAZY_ATTR.get(name, name))
