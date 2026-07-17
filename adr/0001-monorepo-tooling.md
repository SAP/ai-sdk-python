# Monorepo Tooling

## Status

proposed

## Context

The SDK ships multiple related packages (`base`, `core`, `gen`) that share dev tooling, CI, and cross-package dependencies. We need a way to manage them in a single repository with consistent dependency resolution and a single lockfile.

## Decision (preliminary)

Use uv workspaces to manage the monorepo. Each package lives under `packages/` with its own `pyproject.toml`. The root `pyproject.toml` declares the workspace and shared index configuration. `uv sync --all-packages` installs all packages and their dependencies into a single shared `.venv`.

## Consequences

- Single lockfile (`uv.lock`) covers all packages — reproducible installs across the repo
- Cross-package dependencies resolve locally without publishing to a registry
- CI installs the entire workspace in one step
- uv is a required tool for contributors; there is no pip-based fallback

# Appendix

## Option A — uv workspaces (chosen)

Root `pyproject.toml` declares `[tool.uv.workspace]` with `members = ["packages/*"]`. Each sub-package has its own `pyproject.toml` with its dependencies. `uv sync --all-packages --all-extras` installs everything.

**Pros:**

- Single lockfile, fast resolution
- Native cross-package local references via `[tool.uv.sources]`
- Only one tool needed (resolution, locking, venv, script running)

**Cons:**

- uv must be installed by all contributors and CI

**Note:** `uv run` has no equivalent of `--all-packages` for running commands across all packages. Tools that accept multiple paths (e.g. pylint) can still be invoked once with all package paths; this is not uv-specific.

## Option B — pip + virtual envs per package

Each package manages its own venv. A top-level script or Makefile coordinates installs across packages.

**Pros:**

- Standard tooling, no uv dependency

**Cons:**

- No shared lockfile — dependency drift between packages
- Cross-package local installs require `pip install -e` per package in the right order (base → core → gen)
- CI must repeat the install step for each package
