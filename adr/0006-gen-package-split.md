# Gen package split

## Status

proposed

## Context

The `sap-ai-sdk-gen` package (import root `gen_ai_hub`) bundles the entire generative-AI
surface of the SDK into a single distribution. A single `pip install sap-ai-sdk-gen`
pulls a large dependency footprint — `pandas`, the full `langchain` stack
(`langchain`, `langchain-classic`, `langchain-openai`), `openai`, and, via extras,
`boto3`/`aiobotocore` and `google-genai` — even though most users consume only a
slice of the functionality (e.g. the proxy client, or orchestration, but not
evaluations or every model provider).

The package already decomposes cleanly into independent modules — `proxy`,
`orchestration_v2`, `prompt_registry`, `document_grounding`, `batch_service`,
`evaluations`, and provider adapters — with an acyclic internal dependency graph
rooted at `proxy` (every module imports `get_proxy_client` from it). The heavy,
optional-feeling dependencies are isolated to specific modules: `pandas`/`langcodes`
to `evaluations`, the langchain stack to `proxy/langchain`, and the provider SDKs to
`proxy/native/{amazon,google_genai}`.

This makes the single-distribution packaging the main driver of the oversized
footprint rather than any genuine coupling.

## Decision

Split `sap-ai-sdk-gen` into multiple independently published packages, each mapping
to a module boundary and each exposing its own flat top-level import root under the
`sap_ai_sdk_*` prefix (mirroring the `sap-ai-sdk-*` distribution names). The shared
`gen_ai_hub` import namespace is **not** preserved — this is an intentional breaking
change, documented via a migration guide rather than a compatibility shim.

Packages (with the module each contains):

| Distribution | Import root | Module(s) |
|---|---|---|
| `sap-ai-sdk-proxy` | `sap_ai_sdk_proxy` | `proxy.core`, `proxy.gen_ai_hub_proxy`, native `openai` + `sap` |
| `sap-ai-sdk-langchain` | `sap_ai_sdk_langchain` | langchain base + `init_models` + openai adapter |
| `sap-ai-sdk-amazon` | `sap_ai_sdk_amazon` | native amazon wrapper (+ langchain-aws adapter, `[langchain]` extra) |
| `sap-ai-sdk-google` | `sap_ai_sdk_google` | native google wrapper (+ langchain-google-genai adapter, `[langchain]` extra) |
| `sap-ai-sdk-orchestration` | `sap_ai_sdk_orchestration` | `orchestration_v2` only |
| `sap-ai-sdk-prompt-registry` | `sap_ai_sdk_prompt_registry` | `prompt_registry` |
| `sap-ai-sdk-document-grounding` | `sap_ai_sdk_document_grounding` | `document_grounding` |
| `sap-ai-sdk-batch` | `sap_ai_sdk_batch` | `batch_service` |
| `sap-ai-sdk-evaluations` | `sap_ai_sdk_evaluations` | `evaluations` |

Supporting decisions:

- **`proxy` is the mandatory lean base.** It keeps only `openai` and the httpx-only
  SAP/RPT native client — no langchain, no pandas, no provider SDKs.
- **Each heavy provider is its own package.** The langchain adapter for a provider
  lives in that provider's package and is gated behind a `[langchain]` extra, because
  the adapter imports the native wrapper anyway. The provider-agnostic
  `init_llm`/`init_embedding_model` dispatcher imports provider adapters lazily and
  raises an actionable error when the needed provider package is not installed.
- **Orchestration v1 is dropped.** The legacy `orchestration` module
  (dataclasses/dacite) is removed entirely; nothing in the source depends on it, and
  v2 has full parallel test coverage. Only `orchestration_v2` is carried forward,
  under the `sap_ai_sdk_orchestration` root.
- **Cross-package dependencies follow ADR-0002**: declared as normal runtime
  dependencies plus a `[tool.uv.sources] = { workspace = true }` entry — never
  vendored — preserving object identity for `isinstance`/pydantic model reuse (e.g.
  `prompt_registry` reusing `orchestration` models).
- Empty generated-code scaffolding directories (`context_registry`,
  `document_grounding_generation(_kiota)`, `tab_ai_orchestration(_kiota)`) are not
  carried into any package.

## Consequences

- Users install only what they need: `pip install sap-ai-sdk-proxy` no longer pulls
  `pandas`, `langchain`, `boto3`, or `google-genai`.
- Each service area is versioned, released, and owned independently, following the
  existing per-package commitizen `tag_format`/`bump_pattern` conventions.
- **Breaking change for all consumers:** every `gen_ai_hub.*` import must be rewritten
  to the new roots. There is no compatibility shim; a migration guide is provided.
- More distributions to publish and keep version-aligned, and more CI matrix entries,
  integration-test jobs, bump choices, and PyPI projects to maintain.
- Two latent bugs are fixed as part of the split: the undeclared `pyhumps` dependency
  used by `document_grounding`, and the unconditional `boto3`/`botocore` import in
  `evaluations/helpers/s3_file_client.py` (now lazy, behind the `[amazon]` extra).

# Appendix

## Option A — Split into distinct packages with new import roots (chosen)

Physically separate packages, each a distinct top-level import root; no shared
namespace. Breaking, but delivers genuine footprint reduction and independent
release/ownership.

**Pros:** real dependency isolation; independent release cadence; simplest mental
model (one responsibility → one package); no namespace-package machinery.

**Cons:** breaks all existing imports; large mechanical rewrite; more
packaging/CI/PyPI overhead.

## Option B — PEP 420 namespace packages under `gen_ai_hub`

Keep the `gen_ai_hub.*` import paths, shipping each new distribution as an implicit
namespace package contribution.

**Pros:** zero breakage for existing users.

**Cons:** namespace-package subtleties (editable installs, `__init__` boundaries); the
existing `gen_ai_hub/__init__.py` re-export complicates a clean namespace boundary;
rejected by the team in favour of exploring true separation.

## Option C — Keep one distribution, move heavy deps to extras

Keep `sap-ai-sdk-gen` whole and gate `pandas`/`langchain`/providers behind extras.

**Pros:** no import breakage; smaller change.

**Cons:** does not deliver independent release/ownership; the base install still
carries the non-extra heavy deps (e.g. langchain-openai); does not match the goal of
exploring package separation.

## Addendum — opt-in `sap-ai-sdk-gen` compatibility package

The no-shim decision above was **partially reversed** by re-introducing
`sap-ai-sdk-gen` as a thin *compatibility meta package* (`packages/gen`). It ships no
logic: it depends on the new `sap-ai-sdk-*` distributions and re-exposes the legacy
`gen_ai_hub.*` import paths as forwarders (PEP 562 / `sys.modules` aliasing in
`gen_ai_hub/_alias.py`), preserving object identity so cross-package `isinstance`/
pydantic reuse keeps working. This is a migration aid, not a return to the single-
distribution model: the split packages remain the canonical, independently released
units, and new code should import the `sap_ai_sdk_*` roots directly.

The footprint win is largely preserved — the base `sap-ai-sdk-gen` install forwards
proxy/orchestration/prompt-registry/document-grounding/batch/evaluations, while the
heavy providers and langchain stay behind extras: `[amazon]`, `[google]`,
`[langchain]`, and `[all]`.

**Known fidelity gap (intentional, deferred):** the pre-split
`gen_ai_hub.proxy.langchain` namespace re-exported OpenAI **and** Bedrock **and**
Google symbols from one module. Those provider adapters now live in
`sap_ai_sdk_amazon.langchain` / `sap_ai_sdk_google.langchain`. The shim forwards only
the OpenAI subset; re-aggregating the provider symbols would force `sap-ai-sdk-gen` to
depend on amazon+google and pull `boto3`/`google-genai` back into the base install.
A `TODO(compat)` in `gen_ai_hub/proxy/langchain/__init__.py` records exactly how to
complete it if full fidelity is later required.

**Not yet wired for release (intentional):** `packages/gen` is registered in the uv
workspace (`[tool.uv.sources]`) and builds/installs locally, but it is **deliberately
left out of CI and the release pipeline** — it is currently a local compatibility
convenience only. To actually publish `sap-ai-sdk-gen`, the following is needed:
- add `gen` to the `inputs.package.options` list in `.github/workflows/bump.yml`;
- add `gen` to the publish matrix / tag triggers in `.github/workflows/publish.yml`,
  `api-doc.yml`, `draft-release.yml`, and `snapshot-release.yml` (publishing last,
  after all six dependency packages, since it depends on them);
- optionally add a unit-test matrix entry in `.github/workflows/ci.yml` (the package
  has no tests of its own — it only forwards — so this is low value);
- register the `sap-ai-sdk-gen` PyPI project + Trusted Publisher environment
  (`pypi:sap-ai-sdk-gen`); the `publish.yml` environment name is already derived
  dynamically from the parsed tag.
