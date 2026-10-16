# SAP Cloud SDK for AI (Python) - Google GenAI

Google GenAI integration for the SAP generative AI SDK. Provides the native
`google-genai` client (`Client`) wired to route calls through the generative AI
Hub of SAP AI Core.

The optional `[langchain]` extra adds the langchain adapters
(`ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`) built on
`langchain-google-genai`.

## Installation

    pip install sap-ai-sdk-google            # native google-genai client only
    pip install "sap-ai-sdk-google[langchain]"  # + langchain adapters

## Usage

```python
from sap_ai_sdk_google import Client

client = Client(model="gemini-2.5-flash-lite")
```

## Documentation

See the project documentation for full usage details.
