#!/usr/bin/env bash
# Regenerates rpt_1_5/generated/ from the vendored OpenAPI spec.
# Run from packages/gen/ directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(dirname "$SCRIPT_DIR")"

docker run --rm \
  -v "${PKG_DIR}:/local" \
  openapitools/openapi-generator-cli generate \
    -i /local/openapi_specs/sap-rpt-1.5_openapi.json \
    -g python \
    --additional-properties=library=httpx,packageName=rpt_1_5_generated \
    -o /local/gen_ai_hub/proxy/native/rpt_1_5/generated
