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
Google symbols at its top level (`from gen_ai_hub.proxy.langchain import ChatBedrock`).
The submodule paths are fully restored (`gen_ai_hub.proxy.langchain.{openai,
init_models,amazon,google_genai}` all forward, the provider ones behind the `[amazon]`/
`[google]` extras), but the **merged top-level re-export** forwards only the OpenAI
subset: re-aggregating the provider symbols at that top level would force
`sap-ai-sdk-gen` to depend on amazon+google and pull `boto3`/`google-genai` into the
base install. A `TODO(compat)` in `gen_ai_hub/proxy/langchain/__init__.py` records
exactly how to complete it if full fidelity is later required.

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

## Addendum — native OpenAI and SAP/RPT clients split out of `sap-ai-sdk-proxy`

Two native clients that previously shipped inside `sap-ai-sdk-proxy` were extracted
into their own distributions, continuing the footprint-driven decomposition:

- **`sap-ai-sdk-openai`** (import root `sap_ai_sdk_openai`) — the native OpenAI client
  (`OpenAI`, `AsyncOpenAI`, and the module-level lazy `chat`/`embeddings`/`responses`/
  `completions` globals), moved from `sap_ai_sdk_proxy/native/openai/`.
- **`sap-ai-sdk-rpt`** (import root `sap_ai_sdk_rpt`) — the native SAP RPT client
  (`RPTClient` + pydantic request/response models), moved from
  `sap_ai_sdk_proxy/native/sap/`.

Both depend only on stable public proxy symbols (`get_proxy_client`,
`get_proxy_version`, `BaseProxyClient`, the `core.utils` helpers,
`GenAIHubProxyClient`), so they sit above proxy in the dependency DAG as siblings of
the amazon/google provider packages — no circular dependency. `langchain` gains an
edge to `openai` (its OpenAI adapter imports `AsyncOpenAI`/`OpenAI` and
`DEFAULT_API_VERSION` from `sap_ai_sdk_openai`).

**Clean break (no proxy compat shim):** the old `sap_ai_sdk_proxy.native.openai` and
`sap_ai_sdk_proxy.native.sap` paths were **removed outright**, not aliased — proxy no
longer has a `native/` package. All first-party consumers were repointed to the new
roots (langchain adapter, sample-code, the `gen_ai_hub.proxy.native.{openai,sap}`
forwarders in the `sap-ai-sdk-gen` compat package, which now alias to
`sap_ai_sdk_openai`/`sap_ai_sdk_rpt`). Any external code importing the old
`sap_ai_sdk_proxy.native.*` paths must migrate to the new distributions.

**Footprint win:** `openai` and `packaging` were dropped from `sap-ai-sdk-proxy`'s base
dependencies. The guarded `openai._types` import in `core/utils.py` stays (it is already
`try/except ImportError` with a local `NotGiven` fallback), so proxy functions fully
without `openai` installed. A base `sap-ai-sdk-proxy` install no longer pulls `openai`,
`packaging`, `sap_ai_sdk_openai`, or `sap_ai_sdk_rpt`. The proxy e2e header test
(`tests/gen_ai_hub_proxy/test_additional_header_e2e.py`) imports the native OpenAI
client, so `sap-ai-sdk-openai` is kept as a proxy **dev-only** dependency to preserve
that coverage — it is not a runtime dep.

**Not yet wired for release (intentional):** like `packages/gen`, the two new packages
are registered in the uv workspace and build/install/lint/test locally, but their CI and
release wiring is **deliberately left out**. To publish `sap-ai-sdk-openai` and
`sap-ai-sdk-rpt`:
- add `openai` and `rpt` to the `inputs.package.options` list in
  `.github/workflows/bump.yml`;
- add them to the publish matrix / tag triggers in `.github/workflows/publish.yml`,
  `api-doc.yml`, `draft-release.yml`, and `snapshot-release.yml` (publishing before
  `langchain`/`gen`, which now depend on `openai`);
- add unit-test matrix entries in `.github/workflows/ci.yml` (both have real test
  suites, moved over from proxy);
- register the `sap-ai-sdk-openai` / `sap-ai-sdk-rpt` PyPI projects + Trusted Publisher
  environments.

Unlike `sap-ai-sdk-gen` (which reuses an existing PyPI name last published at 7.4.1),
these are brand-new distribution names, so the 1.0.0 starting version has no
version-history conflict.
