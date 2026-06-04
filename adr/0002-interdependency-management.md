# Interdependency management

## Status

proposed

## Context

The monorepo contains three separately published packages: `sap-ai-sdk-base`, `sap-ai-sdk-core`, and `sap-ai-sdk-gen`. When the packages were merged from separate repositories into this monorepo, the question arose whether `sap-ai-sdk-gen` should continue to declare `sap-ai-sdk-core` as a runtime dependency or instead inline the core source code into the gen package at publish time.

The packages were previously maintained as independent repositories and have distinct PyPI identities. Users interact with `sap-ai-sdk-core` directly — for example, by instantiating `AICoreV2Client` from `ai_core_sdk` — independently of whether they also use `sap-ai-sdk-gen`.

## Decision

`sap-ai-sdk-gen` declares `sap-ai-sdk-core` as a regular runtime dependency in its `pyproject.toml`. The core source code is not inlined or vendored into the gen package. During development, uv workspace sources resolve the dependency locally (`[tool.uv.sources] sap-ai-sdk-core = { workspace = true }`); at publish time, the dependency resolves from PyPI.

## Consequences

- Users who install `sap-ai-sdk-gen` automatically get a compatible version of `sap-ai-sdk-core` via pip's dependency resolution
- `sap-ai-sdk-core` can be installed and used independently without `sap-ai-sdk-gen`
- Types and classes from `ai_core_sdk` (e.g. `AICoreV2Client`) are the same objects regardless of whether the user reached them via `sap-ai-sdk-core` or `sap-ai-sdk-gen` — `isinstance` checks and type annotations work correctly across both packages
- Version constraints must be kept in sync when core introduces breaking changes
- Both packages must be released and published separately, in the correct order (core before gen) when there are cross-package changes

# Appendix

## Option A — Keep `sap-ai-sdk-core` as a declared dependency (chosen)

`sap-ai-sdk-gen` lists `sap-ai-sdk-core>=x.y.z` in its `dependencies`. The monorepo uses `[tool.uv.sources]` to point at the local workspace copy during development.

**Pros:**

- Single source of truth for core code — no duplication, no drift
- Users installing only `sap-ai-sdk-core` get a standalone package with its own release cadence
- Object identity is preserved: a type imported from `ai_core_sdk` is the same type everywhere in a user's environment, so `isinstance` checks, type narrowing, and `typing.cast` all behave correctly
- Standard Python packaging convention; pip, uv, and other tools handle the transitive install automatically

**Cons:**

- Coordinated releases required: a breaking core change forces a gen release as well
- Version constraint management adds maintenance overhead over time

## Option B — Inline (vendor) core source into gen at publish time

Copy the `ai_core_sdk` source tree into the gen package wheel. Remove the `sap-ai-sdk-core` dependency from gen's metadata.

**Pros:**

- Gen ships as a single self-contained wheel with no same-org transitive dependency

**Cons:**

- Two copies of the same code on the user's system if they install both packages — leads to two separate `ai_core_sdk` namespaces and broken `isinstance` checks
- `sap-ai-sdk-core` is a public, user-facing package; inlining it into gen would create a hidden fork that silently diverges from the published version
- The vendoring step adds build complexity and is non-standard for first-party packages
- `sap-ai-sdk-core` itself depends on `sap-ai-sdk-base`, so the inline would need to be recursive or leave a dangling dependency
