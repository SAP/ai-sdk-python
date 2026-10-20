# sap-ai-sdk-proxy

Foundation distribution of the SAP Cloud SDK for AI (Python). It provides the
generative AI Hub proxy client, the proxy-client registry, and the
provider-agnostic LangChain model factories. Every other `sap-ai-sdk-*`
distribution depends on this one.

This package contributes to the **`gen_ai_hub` namespace** (a
[PEP 420](https://peps.python.org/pep-0420/) implicit namespace package). It ships
no `gen_ai_hub/__init__.py` — the `gen_ai_hub.*` import tree is assembled from all
installed `sap-ai-sdk-*` distributions.

## Installation

```bash
pip install sap-ai-sdk-proxy
```

This pulls only lightweight dependencies (`httpx`, `pydantic`, `sap-ai-sdk-core`,
…). It does **not** install any model-provider SDK (no `openai`, `boto3`,
`google-genai`) or LangChain. Install the provider distributions you need
alongside it (see `sap-ai-sdk-openai`, `-amazon`, `-google`, `-rpt`).

## Imports

```python
# Proxy client + registry helpers
from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, set_proxy_version
from gen_ai_hub.proxy.core import get_proxy_version

# Provider-agnostic LangChain factories
from gen_ai_hub.proxy.langchain import init_llm, init_embedding_model
```

> **Note on `GenAIHubProxyClient`.** Because `gen_ai_hub.proxy` is a namespace
> package it cannot expose top-level re-exports. Import the client from its real
> module: `from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient`
> (the old `from gen_ai_hub import GenAIHubProxyClient` no longer exists).

### LangChain factories and lazy provider dispatch

`init_llm` / `init_embedding_model` live here and work with whatever provider
distributions are installed. The provider wrapper classes themselves ship with
their provider distribution and are imported **lazily** — requesting a model whose
provider is not installed raises an actionable error:

```python
from gen_ai_hub.proxy.langchain import init_llm

init_llm("gpt-4o")              # works if sap-ai-sdk-openai[langchain] is installed
init_llm("amazon--nova-micro")  # raises ImportError: install 'sap-ai-sdk-amazon[langchain]'
```

The historical per-provider shim paths still resolve when the provider
distribution is installed:

```python
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI          # sap-ai-sdk-openai[langchain]
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock         # sap-ai-sdk-amazon[langchain]
from gen_ai_hub.proxy.langchain.google_genai import ChatGoogleGenerativeAI  # sap-ai-sdk-google[langchain]
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
