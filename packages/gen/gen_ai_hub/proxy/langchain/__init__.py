"""Shim for ``gen_ai_hub.proxy.langchain``.

The ``openai`` / ``init_models`` / ``amazon`` / ``google_genai`` submodules of this
package are available as separate forwarders (the latter two require the ``[amazon]`` /
``[google]`` extras). This ``__init__`` re-exports the OpenAI subset of the old merged
namespace; it requires the ``[langchain]`` extra.

TODO(compat): the pre-split ``gen_ai_hub.proxy.langchain`` root *also* re-exported the
Bedrock + Google symbols (``ChatBedrock``, ``ChatGoogleGenerativeAI``, …) at this top
level, so ``from gen_ai_hub.proxy.langchain import ChatBedrock`` used to work. Those
adapters now live in ``sap_ai_sdk_langchain.amazon`` / ``sap_ai_sdk_langchain.google``
and are reachable here only via the submodule paths
(``gen_ai_hub.proxy.langchain.amazon`` / ``.google_genai``). Re-aggregating them at this
top level would make ``sap-ai-sdk-gen`` depend on the ``[amazon]``/``[google]`` extras
(pulling boto3/google-genai into the base install), so it is intentionally omitted for
now. To restore full fidelity later, extend this module with::

    from sap_ai_sdk_langchain.amazon import (
        ChatBedrock, ChatBedrockConverse, BedrockEmbeddings, AICoreBedrockBaseModel,
    )
    from sap_ai_sdk_langchain.google import (
        ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings,
    )

and add the amazon+google extras to the package dependencies (or gate behind an extra).
Until then, import those symbols from the submodules or ``sap_ai_sdk_langchain``
directly.
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
