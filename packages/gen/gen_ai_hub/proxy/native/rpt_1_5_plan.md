# RPT 1.5 Native Client — Implementation Plan

## Overview

Add a new `rpt_1_5` package under `gen_ai_hub/proxy/native/` that introduces spec-driven
development for the first time in this SDK. Models **and** the API client class are
auto-generated from the RPT 1.5 OpenAPI spec via `openapi-generator`. A thin hand-written
wrapper wires SAP proxy authentication and deployment URL resolution on top.

---

## What Changed in RPT 1.5 vs 1.0

| Area | RPT 1.0 | RPT 1.5 |
|---|---|---|
| `TargetColumn` | `prediction_placeholder: str = "[PREDICT]"`, no `top_k` | `prediction_placeholder: str\|number\|null` (required), adds `top_k: int\|null` |
| `PredictionConfig` | `list[TargetColumn]` (RootModel) | Object with `target_columns` + optional `explanations` |
| `DataType.dtype` | `"string"\|"numeric"\|"date"` only | Full `ColumnType` enum (17 values: `integer`, `timestamp`, `boolean`, …) |
| `PredictionItem` | `prediction`, `confidence` | Adds `confidence_interval: [float, float]\|null` |
| Response | No explanations | Adds `explanations: ExplanationResult\|null` |
| Endpoints | `/predict` only | `/predict`, `/predict_parquet` (multipart), `/health` |

---

## Generator: `openapi-generator` (`python` + `library=httpx`)

`openapi-generator` generates both **models and a full typed API class** (`DefaultApi`) with
one method per endpoint — `predict()`, `predict_parquet()`, `health()`. This sets the
reusable pattern for future services.

The generated `ApiClient` accepts a custom `httpx.Client` / `httpx.AsyncClient`, which is
the clean intercept point for injecting SAP auth headers without touching generated code.

**Regeneration command** (via Docker, no local Java needed):

```bash
docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
  -i /local/openapi_specs/sap-rpt-1.5_openapi.json \
  -g python \
  --additional-properties=library=httpx,packageName=rpt_1_5_generated \
  -o /local/gen_ai_hub/proxy/native/rpt_1_5/generated
```

The command is checked in at `codegen/rpt_1_5_generate.sh` for reproducibility.

---

## Target File Structure

```
packages/gen/
├── openapi_specs/
│   └── sap-rpt-1.5_openapi.json               # vendored spec snapshot
├── codegen/
│   └── rpt_1_5_generate.sh                    # Docker regeneration command
└── gen_ai_hub/proxy/native/
    ├── utils.py                                # NEW: shared proxy/auth utilities
    ├── sap/                                    # unchanged
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    └── rpt_1_5/                                # NEW
        ├── __init__.py                         # re-exports public surface
        ├── client.py                           # factory functions wrapping DefaultApi
        └── generated/                          # openapi-generator output — DO NOT EDIT
            ├── __init__.py
            ├── api/
            │   └── default_api.py             # DefaultApi: predict(), predict_parquet(), health()
            ├── models/
            │   ├── predict_request_payload.py
            │   ├── predict_response_payload.py
            │   ├── prediction_config.py
            │   ├── target_column_config.py
            │   ├── explanation_config.py
            │   ├── explanation_result.py
            │   ├── prediction_result.py
            │   ├── predict_response_status.py
            │   ├── predict_response_metadata.py
            │   ├── schema_field_config.py
            │   ├── column_type.py
            │   └── body_predict_parquet.py
            ├── api_client.py
            ├── configuration.py
            └── rest.py
```

---

## Shared Utilities (`native/utils.py`)

Extracts the deployment-resolution and auth-injection logic that is currently duplicated
in every hand-written client. Becomes the canonical place for all future generated clients.

```python
# gen_ai_hub/proxy/native/utils.py

def get_proxy_client_instance(proxy_client=None) -> GenAIHubProxyClient:
    """Returns provided proxy client or the default one."""

def resolve_deployment_url(
    proxy_client: GenAIHubProxyClient,
    model_name: str,
    model_version: Optional[str] = None,
) -> str:
    """Resolves deployment base URL via proxy_client.select_deployment()."""

def build_sap_httpx_client(
    proxy_client: GenAIHubProxyClient,
    timeout=None,
) -> httpx.Client:
    """httpx.Client with SAP auth injected via event hook."""

def build_sap_async_httpx_client(
    proxy_client: GenAIHubProxyClient,
    timeout=None,
) -> httpx.AsyncClient:
    """httpx.AsyncClient with SAP auth injected via event hook."""
```

Auth injection uses httpx event hooks — clean, non-invasive, no subclassing:

```python
def _make_auth_hook(proxy_client):
    def inject_auth(request: httpx.Request) -> None:
        for key, value in proxy_client.request_header.items():
            request.headers[key] = value
    return inject_auth
```

`resolve_deployment_url` mirrors `_get_url()` from `sap/client.py`:

```python
def resolve_deployment_url(proxy_client, model_name, model_version=None):
    filters = {"model_name": model_name}
    if model_version:
        filters["model_version"] = model_version
    try:
        return proxy_client.select_deployment(**filters).url
    except ValueError:
        raise ValueError(f"No deployment found for the given parameters: {filters}.")
```

---

## Client Factory (`rpt_1_5/client.py`)

```python
def create_rpt15_client(
    model_name: str,
    model_version: Optional[str] = None,   # None — server defaults to latest
    proxy_client=None,
    timeout=None,
) -> DefaultApi:
    """
    Returns a sync DefaultApi client wired with SAP proxy authentication.

    The deployment URL is resolved automatically from the proxy client credentials
    using model_name and optional model_version.
    model_version=None means the server will use its default (latest).
    """
    proxy = get_proxy_client_instance(proxy_client)
    base_url = resolve_deployment_url(proxy, model_name, model_version)
    configuration = Configuration(host=base_url)
    http_client = build_sap_httpx_client(proxy, timeout)
    return DefaultApi(ApiClient(configuration=configuration, http_client=http_client))


async def create_async_rpt15_client(
    model_name: str,
    model_version: Optional[str] = None,
    proxy_client=None,
    timeout=None,
) -> DefaultApi:
    """Async variant — same signature, uses httpx.AsyncClient."""
    proxy = get_proxy_client_instance(proxy_client)
    base_url = resolve_deployment_url(proxy, model_name, model_version)
    configuration = Configuration(host=base_url)
    http_client = build_sap_async_httpx_client(proxy, timeout)
    return DefaultApi(ApiClient(configuration=configuration, http_client=http_client))
```

`base_url` is resolved from `proxy_client.select_deployment(model_name=..., model_version=...).url`.
The proxy client derives this URL from the credentials it was configured with (AI Core API URL +
deployment ID). The generated `DefaultApi` appends `/predict`, `/predict_parquet`, `/health` to it.

---

## Public API (`rpt_1_5/__init__.py`)

```python
from .client import create_rpt15_client, create_async_rpt15_client
from .generated.models import (
    PredictRequestPayload,
    PredictResponsePayload,
    PredictionConfig,
    TargetColumnConfig,
    ExplanationConfig,
    ExplanationResult,
    PredictionResult,
    PredictResponseStatus,
    PredictResponseMetadata,
    ColumnType,
    SchemaFieldConfig,
)
```

---

## Usage Example

```python
from gen_ai_hub.proxy.native.rpt_1_5 import create_rpt15_client

# model_version=None → server picks latest
client = create_rpt15_client(model_name="sap-rpt")

# or pin a specific version
client = create_rpt15_client(model_name="sap-rpt", model_version="1.5.0")

# call generated method directly — fully typed
response = client.predict(body={
    "prediction_config": {"target_columns": [{"name": "PRICE", "prediction_placeholder": None}]},
    "rows": [{"PRODUCT": "Laptop", "PRICE": None}],
})
```

---

## Execution Steps

| # | Step | Output |
|---|---|---|
| 1 | Vendor spec | `openapi_specs/sap-rpt-1.5_openapi.json` |
| 2 | Write regeneration script | `codegen/rpt_1_5_generate.sh` |
| 3 | Run openapi-generator (Docker) | `rpt_1_5/generated/` — models + DefaultApi + ApiClient |
| 4 | Write `native/utils.py` | `get_proxy_client_instance`, `resolve_deployment_url`, `build_sap_httpx_client`, `build_sap_async_httpx_client` |
| 5 | Write `rpt_1_5/client.py` | `create_rpt15_client` / `create_async_rpt15_client` |
| 6 | Write `rpt_1_5/__init__.py` | Public re-exports |
| 7 | No new pip runtime dependency | `openapi-generator` runs via Docker at codegen time only |

---

## Out of Scope (Follow-up)

- Refactoring `sap/client.py` to use `native/utils.py` (no behaviour change, safe to do later)
- Adding `datamodel-code-generator` as an alternative model-only generator option
- Unit and integration tests for `RPT15Client`
