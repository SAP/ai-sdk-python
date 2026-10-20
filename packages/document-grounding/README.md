# sap-ai-sdk-document-grounding

Document Grounding client for the SAP Cloud SDK for AI (Python). Ships the API
clients for document vectorization pipelines, vector collections, and retrieval
over data repositories in SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.document_grounding`.

## Installation

```bash
pip install sap-ai-sdk-document-grounding
```

Installing this package automatically pulls `sap-ai-sdk-proxy`, `pydantic`, and
`pyhumps`. It installs no model-provider SDK and no LangChain.

## Imports

```python
from gen_ai_hub.document_grounding import (
    PipelineAPIClient, VectorAPIClient, RetrievalAPIClient,
)

# or from the real modules:
from gen_ai_hub.document_grounding.clients.pipeline_api_client import PipelineAPIClient
from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient
from gen_ai_hub.document_grounding.clients.retrieval_api_client import RetrievalAPIClient
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
