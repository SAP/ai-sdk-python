# sap-ai-sdk-openai

OpenAI provider for the SAP Cloud SDK for AI (Python). Ships the OpenAI clients
that route through the generative AI Hub proxy of SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.proxy.native.openai`.

## Installation

```bash
pip install sap-ai-sdk-openai
```

Installing this package automatically pulls `sap-ai-sdk-proxy` and `openai`. No
other provider's dependencies (boto3, google-genai) are installed. This package
ships only the native OpenAI client.

Looking for the LangChain wrappers (`ChatOpenAI`, `OpenAI`, `OpenAIEmbeddings`)?
They now live in the separate `sap-ai-sdk-langchain` package — install them with
`pip install "sap-ai-sdk-langchain[openai]"` (see ../langchain/README.md).

## Imports

```python
# Native clients (always available with sap-ai-sdk-openai)
from gen_ai_hub.proxy.native.openai import OpenAI, AsyncOpenAI
from gen_ai_hub.proxy.native.openai.clients import ChatCompletions, Responses

# LangChain wrappers are importable from gen_ai_hub.proxy.langchain.openai
# once sap-ai-sdk-langchain[openai] is installed.
```

`init_llm("gpt-4o")` / `init_embedding_model(...)` from `sap-ai-sdk-proxy` resolve
to the LangChain wrappers once `sap-ai-sdk-langchain[openai]` is installed.

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
