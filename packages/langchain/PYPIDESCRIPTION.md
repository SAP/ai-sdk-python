# SAP Cloud SDK for AI (Python) - langchain integration

This package provides the [langchain](https://python.langchain.com) integration
for the SAP generative AI SDK: `init_llm` / `init_embedding_model`, and the
OpenAI langchain chat/embedding model wrappers that route through the generative
AI Hub proxy of SAP AI Core.

Provider-specific langchain adapters (Amazon Bedrock, Google) ship with their
respective provider packages (`sap-ai-sdk-amazon[langchain]`,
`sap-ai-sdk-google[langchain]`). `init_llm` / `init_embedding_model` import the
needed provider adapter lazily and raise an actionable error if it is missing.

## Installation

    pip install sap-ai-sdk-langchain

## Usage

```python
from sap_ai_sdk_langchain import init_llm

llm = init_llm("gpt-4o-mini")
```
