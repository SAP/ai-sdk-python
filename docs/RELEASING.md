# Releasing

This monorepo publishes three independent PyPI packages, each with its own version, tag prefix, and changelog. Publish in dependency order when several changed together: **base → core → gen**.

| Package | PyPI name | Tag prefix | Changelog |
| --- | --- | --- | --- |
| `base` | `sap-ai-sdk-base` | `base-v*` | `packages/base/RELEASE_NOTES.md` |
| `core` | `sap-ai-sdk-core` | `core-v*` | `packages/core/RELEASE_NOTES.md` |
| `gen`  | `sap-ai-sdk-gen`  | `gen-v*`  | `packages/gen/RELEASE_NOTES.md` |

## Flow


0. Commit with the package's scope → feat(base|core|gen): ... / fix(...): ...
1. Run the "bump" workflow      → Actions ▸ bump ▸ Run workflow ▸ pick the package
2. draft-release (automatic)    → notes auto-generated from commits, on the new tag
3. Review the draft release, then Publish → edits sync back to RELEASE_NOTES.md
4. publish-pypi (automatic)     → package lands on PyPI

Also on tag push: **api-doc.yml** (any package) regenerates the API docs and opens a PR in `SAP/ai-sdk`; **documentation.yml** (`gen` only) builds the Sphinx HTML.

## Commit scopes

Versions and changelog entries come **from commit messages**, not the diff — each package counts only commits matching its own scope (from `[tool.commitizen.customize]` in its `pyproject.toml`). `feat` → minor bump, `fix` → patch bump. Any other scope (`chore`, `test`, none) is **silently ignored**.

| Package | `bump_pattern` |
| --- | --- |
| `base` | `^(feat\|fix)\(base\)` |
| `core` | `^(feat\|fix)\(core\)` |
| `gen`  | `^(feat\|fix)\((gen\|prompt_registry\|evaluations)\)` |
