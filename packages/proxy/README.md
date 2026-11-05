# sap-ai-sdk-proxy

Foundation distribution of the SAP Cloud SDK for AI (Python). It provides the
generative AI Hub proxy client and the proxy-client registry. Every other
`sap-ai-sdk-*` distribution depends on this one.

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
alongside it (see `sap-ai-sdk-openai`, `-amazon`, `-google`, `-rpt`). For the
LangChain integration, install `sap-ai-sdk-langchain` (see
[packages/langchain](../langchain/README.md)).

## Imports

```python
# Proxy client + registry helpers
from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, set_proxy_version
from gen_ai_hub.proxy.core import get_proxy_version
```

> **Note on `GenAIHubProxyClient`.** Because `gen_ai_hub.proxy` is a namespace
> package it cannot expose top-level re-exports. Import the client from its real
> module: `from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient`
> (the old `from gen_ai_hub import GenAIHubProxyClient` no longer exists).

> **LangChain support moved.** The provider-agnostic factories
> (`init_llm` / `init_embedding_model`) and the provider wrapper classes now live
> in the separate `sap-ai-sdk-langchain` distribution, which owns the whole
> `gen_ai_hub.proxy.langchain` subtree. See
> [packages/langchain](../langchain/README.md).

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
