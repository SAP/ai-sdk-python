"""
SAP AI SDK for Python — sample server.

Credentials are read from environment variables (or VCAP_SERVICES on SAP BTP):
  AICORE_BASE_URL       e.g. https://api.ai.prodeu.....
  AICORE_AUTH_URL       e.g. https://<subdomain>.authentication.eu10.hana.ondemand.com
  AICORE_CLIENT_ID
  AICORE_CLIENT_SECRET
  AICORE_RESOURCE_GROUP (optional, defaults to "default")

Alternatively configure ~/.aicore/config.json — all methods are supported by the SDK.

Run:
  pip install fastapi uvicorn
  uvicorn sample_code.server:app --reload
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Make all SDK packages importable when running from the repo root.
_REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
for _pkg in (
    "packages/gen",
    "packages/core",
    "packages/base",
    "packages/gen/gen_ai_hub/proxy/native/rpt_1_5",
):
    _path = os.path.join(_REPO_ROOT, _pkg)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from gen_ai_hub import GenAIHubProxyClient

from sample_code.rpt import predict_sales_group, rpt_health


def _build_proxy_client() -> GenAIHubProxyClient:
    # AICORE_SERVICE_KEY is the raw service key JSON from the SAP BTP service binding.
    # The SDK reads VCAP_SERVICES, so wrap the key in the expected envelope.
    # The entry needs "label": "aicore" so VCAPEnvironment can look it up by name.
    service_key_json = os.environ.get("AICORE_SERVICE_KEY")
    if service_key_json:
        service_key = json.loads(service_key_json)
        os.environ["VCAP_SERVICES"] = json.dumps(
            {"aicore": [{"label": "aicore", "credentials": service_key}]}
        )
    # GenAIHubProxyClient reads VCAP_SERVICES (or individual AICORE_* vars) via from_env().
    return GenAIHubProxyClient()


proxy_client = _build_proxy_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="SAP AI SDK Python Sample", lifespan=lifespan)


@app.get("/health")
async def server_health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# RPT 1.5
# ---------------------------------------------------------------------------

@app.get("/rpt/predict")
async def rpt_predict():
    try:
        predictions = await predict_sales_group(proxy_client)
        return JSONResponse({"predictions": predictions})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/rpt/health")
async def rpt_health_check():
    try:
        result = await rpt_health(proxy_client)
        return JSONResponse({"status": result})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
