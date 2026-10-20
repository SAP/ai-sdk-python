# sap-ai-sdk-prompt-registry

Prompt Registry client for the SAP Cloud SDK for AI (Python). Ships the clients
for managing prompt templates and orchestration configurations in SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.prompt_registry`.

## Installation

```bash
pip install sap-ai-sdk-prompt-registry
```

Installing this package automatically pulls `sap-ai-sdk-proxy`,
`sap-ai-sdk-orchestration`, and `pydantic`. It installs no model-provider SDK and
no LangChain.

## Imports

```python
from gen_ai_hub.prompt_registry import PromptTemplateClient, OrchestrationConfigClient
from gen_ai_hub.prompt_registry import PromptTemplate, PromptTemplateSpec

# or from the real modules:
from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplate
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
