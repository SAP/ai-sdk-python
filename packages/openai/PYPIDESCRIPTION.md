# SAP Cloud SDK for AI (Python) - native OpenAI client

Native OpenAI client for the SAP generative AI SDK. Provides drop-in `OpenAI` and
`AsyncOpenAI` clients (plus `chat`, `embeddings`, `responses`, `completions`) that route
OpenAI API calls through the generative AI Hub of SAP AI Core — no API key or base URL
required, deployment selection is handled for you.

## Installation

    pip install sap-ai-sdk-openai

## Usage

```python
from sap_ai_sdk_openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model_name="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

The module-level `chat`, `embeddings`, `responses`, and `completions` attributes expose a
lazily-constructed global client for quick one-off calls:

```python
from sap_ai_sdk_openai import chat

chat.completions.create(model_name="gpt-4o-mini", messages=[...])
```

## Documentation

See the project documentation for full usage details.
