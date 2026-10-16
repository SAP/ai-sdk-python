# SAP Cloud SDK for AI (Python) - proxy client

The lean base of the SAP generative AI SDK. It provides the proxy client
(`get_proxy_client`, `GenAIHubProxyClient`) used to access generative models
deployed in the generative AI Hub of SAP AI Core, the native OpenAI client
wrappers, and the SAP/RPT native client.

Provider SDKs (Amazon, Google), the langchain integration, orchestration,
prompt registry, document grounding, batch, and evaluations each live in their
own `sap-ai-sdk-*` package and depend on this one.

## Installation

    pip install sap-ai-sdk-proxy

## Usage

```python
from sap_ai_sdk_proxy import get_proxy_client

proxy_client = get_proxy_client()
```

## Documentation

See the project documentation for full usage details.
