# Versioning and Release Strategy

## Status

proposed

## Context

The monorepo contains three separately published PyPI packages with a strict dependency chain: `sap-ai-sdk-base` ← `sap-ai-sdk-core` ← `sap-ai-sdk-gen`. Each package has an independent version today (`base` at 3.4.0, `core` at 3.3.0, `gen` at 7.0.0).

Requirements:

### Must haves

- Publish packages in the correct topological order (base → core → gen)
- Update cross-package dependencies to latest (compatible) version

### Nice to haves

- Keep cross-package version constraints as wide as possible

## Decision

Pending. The options below are under evaluation.

## Consequences

To be filled in once a decision is made.

# Appendix

## Option A — Per-package independent releases with commitizen + orchestration scripts

`commitizen` (`cz bump`) reads conventional commits since the last tag and derives a semver bump per package. The topological ordering and downstream constraint updates require bespoke orchestration scripts on top.

**How it works in practice:**

1. On release, a script determines which packages have unreleased commits.
2. Packages are processed in topological order (base → core → gen). For each changed package, `cz bump` writes the new version to `pyproject.toml` and generates a changelog entry.
3. If an upstream package bumped, the script updates the lower bound of the downstream constraint (e.g. `sap-ai-sdk-core>=3.3` → `>=3.4`) before bumping the downstream package, then publishes each in order.

**Pros:**

- Independent versions — only changed packages get a new version.
- Per-package changelogs and tags give a clear release history for each package independently.

**Cons:**

- Commitizen has no native monorepo mode — per-package scoping requires per-package tag prefixes and configuration.
- Downstream constraint updates and topological ordering must be scripted manually.
- A commit touching multiple packages is counted in each package's bump calculation independently, which can lead to over-bumping.

---
