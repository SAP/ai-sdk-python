# sap-ai-sdk-google

Google Gemini (google-genai) provider for the SAP Cloud SDK for AI (Python).
Ships the clients that route through the generative AI Hub proxy of SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under
`gen_ai_hub.proxy.native.google_genai`.

## Installation

```bash
# Native google-genai client
pip install sap-ai-sdk-google
```

Installing this package automatically pulls `sap-ai-sdk-proxy` and `google-genai`.
This package ships only the native Google GenAI client. For the LangChain
wrappers (`ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`), install
`pip install "sap-ai-sdk-langchain[google]"` (see ../langchain/README.md).

## Imports

```python
# Native client (always available with sap-ai-sdk-google)
from gen_ai_hub.proxy.native.google_genai import Client

# LangChain wrappers are importable from gen_ai_hub.proxy.langchain.google_genai
# once sap-ai-sdk-langchain[google] is installed.
```

`init_llm("gemini-2.5-flash-lite")` from `sap-ai-sdk-proxy` resolves to the
LangChain wrappers once `sap-ai-sdk-langchain[google]` is installed.

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
