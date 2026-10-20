# sap-ai-sdk-rpt

SAP Relational Prediction Transformer (RPT) provider for the SAP Cloud SDK for AI
(Python). Ships the RPT client that routes through the generative AI Hub proxy of
SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.proxy.native.sap`.

## Installation

```bash
pip install sap-ai-sdk-rpt
```

Installing this package automatically pulls `sap-ai-sdk-proxy`, `httpx`, and
`pydantic`. It has no optional extras and no heavy model-provider dependencies.

## Imports

```python
from gen_ai_hub.proxy.native.sap import (
    RPTClient, RPTRequest, RPTResponse, PredictionConfig, TargetColumn,
)
```

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
