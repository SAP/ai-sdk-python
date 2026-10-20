# sap-ai-sdk-batch

Batch service client for the SAP Cloud SDK for AI (Python). Ships the client for
creating, monitoring, and managing batch inference jobs in SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.batch_service`.

## Installation

```bash
pip install sap-ai-sdk-batch
```

Installing this package automatically pulls `sap-ai-sdk-proxy`, `pydantic`, and
`httpx`. It installs no model-provider SDK and no LangChain.

## Imports

```python
from gen_ai_hub.batch_service import BatchService, BatchCreateRequest, BatchStatus

# or from the real modules:
from gen_ai_hub.batch_service.service import BatchService
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
