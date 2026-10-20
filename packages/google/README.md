# sap-ai-sdk-google

Google Gemini (google-genai) provider for the SAP Cloud SDK for AI (Python).
Ships the clients that route through the generative AI Hub proxy of SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under
`gen_ai_hub.proxy.native.google_genai`.

## Installation

```bash
# Native google-genai client only
pip install sap-ai-sdk-google

# Including the LangChain wrappers (ChatGoogleGenerativeAI, …)
pip install "sap-ai-sdk-google[langchain]"
```

Installing this package automatically pulls `sap-ai-sdk-proxy` and `google-genai`.
The `[langchain]` extra additionally pulls `langchain`, `langchain-classic`, and
`langchain-google-genai`.

## Imports

```python
# Native client (always available with sap-ai-sdk-google)
from gen_ai_hub.proxy.native.google_genai import Client

# LangChain wrappers (require the [langchain] extra)
from gen_ai_hub.proxy.native.google_genai.langchain import (
    ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings,
)
# Back-compat shim path (still works with the [langchain] extra installed):
from gen_ai_hub.proxy.langchain.google_genai import ChatGoogleGenerativeAI
```

`init_llm("gemini-2.5-flash-lite")` from `sap-ai-sdk-proxy` resolves to this
package's wrappers once `sap-ai-sdk-google[langchain]` is installed.

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
