# RPT 1.5 Native Client

Async Python client for the SAP RPT 1.5 prediction service. Models are auto-generated from
the OpenAPI spec; a thin hand-written wrapper wires SAP proxy authentication and deployment
URL resolution on top.

## File Structure

```
packages/gen/
├── openapi_specs/
│   └── sap-rpt-1.5_openapi.json               # vendored spec snapshot
├── codegen/
│   ├── rpt_1_5_generate.sh                    # Docker regeneration command
│   └── .openapi-generator-ignore              # excludes docs/tests from generator output
└── gen_ai_hub/proxy/native/
    ├── utils.py                                # shared proxy/auth utilities
    └── rpt_1_5/
        ├── __init__.py                         # public surface re-exports
        ├── client.py                           # RPT15Client
        ├── models.py                           # readable aliases + factory functions
        └── generated/                          # openapi-generator output — DO NOT EDIT
            ├── api/
            │   └── default_api.py
            ├── models/
            ├── api_client.py
            ├── configuration.py
            └── rest.py
```

## Usage

```python
from gen_ai_hub.proxy.native.rpt_1_5 import (
    RPT15Client,
    PredictionConfig,
    PredictionPlaceholder,
    TargetColumnConfig,
    rows_request,
    columns_request,
)

# Build a row-oriented request
request = rows_request(
    prediction_config=PredictionConfig(
        target_columns=[
            TargetColumnConfig(
                name="SALESGROUP",
                prediction_placeholder=PredictionPlaceholder("[PREDICT]"),
            )
        ]
    ),
    index_column="__row_idx__",
    rows=[
        {
            "PRODUCT": "Laptop",
            "PRICE": 999.99,
            "SALESGROUP": "[PREDICT]",
            "__row_idx__": "1",
        },
    ],
)

# Predict — deployment URL and auth are resolved automatically
async with RPT15Client(model_name="sap-rpt-1.5") as client:
    response = await client.predict(request)
    predictions = response["predictions"]
```

## Request formats

### Row-oriented (`rows_request`)

Each row is a plain `dict`. Columns with `"[PREDICT]"` as the value are prediction targets.

```python
rows_request(
    prediction_config=PredictionConfig(...),
    rows=[{"COL_A": "value", "COL_B": 1.0}],
    index_column="__row_idx__",     # optional
    parse_data_types=True,           # optional, default True
)
```

### Column-oriented (`columns_request`)

Each column is a list of values, one per row.

```python
columns_request(
    prediction_config=PredictionConfig(...),
    columns={
        "PRODUCT": ["Laptop", "Chair"],
        "PRICE":   [999.99, 142.99],
    },
)
```

## Client

```python
RPT15Client(
    model_name: str,
    model_version: str | None = None,   # None → server default (latest)
    proxy_client: GenAIHubProxyClient | None = None,   # None → process default
    timeout: float | None = None,
)
```

Methods:

| Method | Description |
|---|---|
| `await client.predict(request)` | Run predictions; returns raw response dict |
| `await client.health()` | Check deployment health |
| `await client.close()` | Release the underlying HTTP connection pool |

Supports use as an async context manager (`async with`).

## Regenerating the generated code

```bash
cd packages/gen
bash codegen/rpt_1_5_generate.sh
```

The script runs `openapi-generator` via Docker — no local Java installation required.
The source spec is at `openapi_specs/sap-rpt-1.5_openapi.json`.

> **Do not edit files under `generated/` by hand.** Run the generator and commit the result.
