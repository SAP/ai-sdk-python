# SAP Cloud SDK for AI (Python) - langchain integration

This package is the single [langchain](https://python.langchain.com) integration
for the SAP generative AI SDK. It provides `init_llm` / `init_embedding_model`
and owns all provider langchain adapters — OpenAI, Amazon Bedrock, and Google —
that route through the generative AI Hub proxy of SAP AI Core.

The base install carries only the provider-agnostic core. Each provider adapter
ships behind an optional extra that pulls in the matching native SDK:

| Extra | Adapters | Install |
| --- | --- | --- |
| `openai` | OpenAI chat / embeddings | `pip install "sap-ai-sdk-langchain[openai]"` |
| `amazon` | `ChatBedrock`, `ChatBedrockConverse`, `BedrockEmbeddings` | `pip install "sap-ai-sdk-langchain[amazon]"` |
| `google` | `ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings` | `pip install "sap-ai-sdk-langchain[google]"` |
| `all` | every provider above | `pip install "sap-ai-sdk-langchain[all]"` |

`init_llm` / `init_embedding_model` import the needed provider adapter lazily and
raise an actionable error naming the required extra if it is missing.

## Installation

    pip install "sap-ai-sdk-langchain[openai]"   # or [amazon], [google], [all]

## Usage

```python
from sap_ai_sdk_langchain import init_llm

llm = init_llm("gpt-4o-mini")
```
