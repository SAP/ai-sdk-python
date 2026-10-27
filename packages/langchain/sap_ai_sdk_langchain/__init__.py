from .init_models import init_embedding_model, init_llm

# Make sure that the user has a recent version of langchain installed
_langchain_is_below_0_1_0 = None
try:
    import langchain
except ImportError:
    pass
else:
    from packaging import version
    _langchain_is_below_0_1_0 = version.parse(langchain.__version__) < version.parse('0.1.0')
    if _langchain_is_below_0_1_0:
        raise ImportError('langchain<0.1.0 is no longer supported. Please upgrade to version 0.1.0 or higher.')


__all__ = [
    'init_llm',
    'init_embedding_model',
]

# The OpenAI langchain wrappers require the ``[openai]`` extra (langchain-openai +
# sap-ai-sdk-openai). Re-export them when present so a base install still works.
try:
    from .openai import OpenAI, OpenAIEmbeddings, OpenAIClient, AsyncOpenAIClient, ChatOpenAI
except ImportError:
    pass
else:
    __all__ += [
        'OpenAIClient',
        'OpenAIEmbeddings',
        'AsyncOpenAIClient',
        'ChatOpenAI',
        'OpenAI',
    ]
