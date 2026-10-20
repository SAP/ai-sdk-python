# SAP Cloud SDK for AI (Python) - native SAP RPT client

Native client for SAP's Relational Pretrained Transformer (RPT) tabular prediction models
deployed via the generative AI Hub of SAP AI Core. Provides `RPTClient` (sync `predict` /
async `apredict`) and the pydantic request/response models.

## Installation

    pip install sap-ai-sdk-rpt

## Usage

```python
from sap_ai_sdk_rpt import RPTClient, RPTRequest, PredictionConfig, TargetColumn

client = RPTClient()
response = client.predict(
    body=RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[TargetColumn(name="label", prediction_placeholder=None)],
        ),
        rows=[...],
    ),
    model_name="sap-rpt-1.6",
)
```

## Documentation

See the project documentation for full usage details.
