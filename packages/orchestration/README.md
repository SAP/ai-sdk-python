# sap-ai-sdk-orchestration

Orchestration service client for the SAP Cloud SDK for AI (Python). Ships the
orchestration v2 API: templating, model configuration, content filtering, data
masking, and document grounding modules.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.orchestration_v2`.

> Orchestration **v1** (`gen_ai_hub.orchestration`) has been removed. Use
> `gen_ai_hub.orchestration_v2`.

## Installation

```bash
pip install sap-ai-sdk-orchestration
```

Installing this package automatically pulls `sap-ai-sdk-proxy`, `pydantic`, and
`httpx`. It installs no model-provider SDK and no LangChain.

## Imports

```python
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.template import Template
from gen_ai_hub.orchestration_v2.models.message import UserMessage
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails

# The public models are also re-exported at the subsystem root:
from gen_ai_hub.orchestration_v2 import OrchestrationService, OrchestrationConfig
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
