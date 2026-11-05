# sap-ai-sdk-langchain

LangChain integration for the SAP Cloud SDK for AI (Python). Ships the LangChain
wrapper classes and the provider-agnostic model factories that route through the
generative AI Hub proxy of SAP AI Core.

This package owns the entire **`gen_ai_hub.proxy.langchain`** subtree and contributes
to the **`gen_ai_hub` namespace** (PEP 420). It ships no `gen_ai_hub/__init__.py` or
`gen_ai_hub/proxy/__init__.py`.

## Installation

The provider-specific LangChain libraries are **optional extras**. Install only the
providers you need:

```bash
# Provider-agnostic factories only (init_llm / init_embedding_model)
pip install sap-ai-sdk-langchain

# OpenAI wrappers (ChatOpenAI, OpenAI, OpenAIEmbeddings)
pip install "sap-ai-sdk-langchain[openai]"

# Amazon Bedrock wrappers (ChatBedrock, ChatBedrockConverse, BedrockEmbeddings)
pip install "sap-ai-sdk-langchain[amazon]"

# Google GenAI wrappers (ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings)
pip install "sap-ai-sdk-langchain[google]"

# Everything
pip install "sap-ai-sdk-langchain[all]"
```

Each extra pulls the matching provider package (`sap-ai-sdk-openai`/`-amazon`/`-google`)
and its LangChain integration (`langchain-openai`/`langchain-aws`/`langchain-google-genai`).
No other provider's dependencies are installed.

## Imports

```python
# Provider-agnostic factories (always available)
from gen_ai_hub.proxy.langchain import init_llm, init_embedding_model

# Provider wrappers (require the matching extra)
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock, ChatBedrockConverse, BedrockEmbeddings
from gen_ai_hub.proxy.langchain.google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
```

`init_llm` / `init_embedding_model` dispatch to the right provider by model name and
import the wrapper lazily, raising an actionable `ImportError` naming the extra to
install if the provider is missing.

## Configuration, Usage

Please refer to the official documentation hosted on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html)
for details on how to configure and use the SAP Cloud SDK for AI (Python).
