# sap-ai-sdk-openai

OpenAI provider for the SAP Cloud SDK for AI (Python). Ships the OpenAI clients
that route through the generative AI Hub proxy of SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.proxy.native.openai`.

## Installation

```bash
# Native OpenAI client only
pip install sap-ai-sdk-openai

# Including the LangChain wrappers (ChatOpenAI, OpenAIEmbeddings, …)
pip install "sap-ai-sdk-openai[langchain]"
```

Installing this package automatically pulls `sap-ai-sdk-proxy` and `openai`. The
`[langchain]` extra additionally pulls `langchain`, `langchain-classic`, and
`langchain-openai`. No other provider's dependencies (boto3, google-genai) are
installed.

## Imports

```python
# Native clients (always available with sap-ai-sdk-openai)
from gen_ai_hub.proxy.native.openai import OpenAI, AsyncOpenAI
from gen_ai_hub.proxy.native.openai.clients import ChatCompletions, Responses

# LangChain wrappers (require the [langchain] extra)
from gen_ai_hub.proxy.native.openai.langchain import ChatOpenAI, OpenAIEmbeddings
# Back-compat shim path (still works with the [langchain] extra installed):
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAIEmbeddings
```

`init_llm("gpt-4o")` / `init_embedding_model(...)` from `sap-ai-sdk-proxy` resolve
to this package's wrappers once `sap-ai-sdk-openai[langchain]` is installed.

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
