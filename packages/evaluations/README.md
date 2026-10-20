# sap-ai-sdk-evaluations

Evaluations client for the SAP Cloud SDK for AI (Python). Ships the client and
models for configuring and running evaluation jobs in SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.evaluations`.

## Installation

```bash
pip install sap-ai-sdk-evaluations

# With Amazon Bedrock support for evaluations that use Bedrock models
pip install "sap-ai-sdk-evaluations[amazon]"
```

Installing this package automatically pulls `sap-ai-sdk-proxy`,
`sap-ai-sdk-orchestration`, `sap-ai-sdk-prompt-registry`, `pandas`, and
`langcodes`. The `[amazon]` extra additionally pulls `boto3`/`botocore`. Note
that the `[amazon]` extra brings in boto3 only — to also use the Bedrock
LangChain wrappers, install `sap-ai-sdk-amazon[langchain]` alongside it.

## Imports

```python
from gen_ai_hub.evaluations import (
    EvaluationClient, EvaluationConfig, EvaluationRun, Dataset,
    MetricConfig, MetricRef, ArtifactSource, Results,
)

# or from the real modules:
from gen_ai_hub.evaluations.client import EvaluationClient
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
