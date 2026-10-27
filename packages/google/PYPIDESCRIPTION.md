# SAP Cloud SDK for AI (Python) - Google GenAI

Google GenAI integration for the SAP generative AI SDK. Provides the native
`google-genai` client (`Client`) wired to route calls through the generative AI
Hub of SAP AI Core.

Looking for the langchain adapters (`ChatGoogleGenerativeAI`,
`GoogleGenerativeAIEmbeddings`)? They now ship with the langchain package —
install `sap-ai-sdk-langchain[google]`.

## Installation

    pip install sap-ai-sdk-google

## Usage

```python
from sap_ai_sdk_google import Client

client = Client(model="gemini-2.5-flash-lite")
```

## Documentation

See the project documentation for full usage details.
