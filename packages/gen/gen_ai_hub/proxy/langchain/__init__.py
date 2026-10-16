"""Shim for ``gen_ai_hub.proxy.langchain`` (OpenAI subset only).

Requires the ``[langchain]`` extra (``pip install "sap-ai-sdk-gen[langchain]"``).

TODO(compat): the pre-split ``gen_ai_hub.proxy.langchain`` root re-exported OpenAI +
Bedrock + Google symbols from one namespace. Bedrock/Google now live in
``sap_ai_sdk_amazon.langchain`` / ``sap_ai_sdk_google.langchain``. Re-aggregating them
here would make ``sap-ai-sdk-gen`` depend on amazon+google (pulling boto3/google-genai
back into the base install), so it is intentionally omitted for now. To restore full
fidelity later, extend this module with::

    from sap_ai_sdk_amazon.langchain import (
        ChatBedrock, ChatBedrockConverse, BedrockEmbeddings, AICoreBedrockBaseModel,
    )
    from sap_ai_sdk_google.langchain import (
        ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings,
    )

and add langchain+amazon+google to the package dependencies (or gate behind an extra).
Until then, import those adapters from their new provider packages directly.
"""

from sap_ai_sdk_langchain import (
    AsyncOpenAIClient,
    ChatOpenAI,
    OpenAI,
    OpenAIClient,
    OpenAIEmbeddings,
    init_embedding_model,
    init_llm,
)

__all__ = [
    'init_llm',
    'init_embedding_model',
    'OpenAIClient',
    'OpenAIEmbeddings',
    'AsyncOpenAIClient',
    'ChatOpenAI',
    'OpenAI',
]
