# Coding Tools

## Status

proposed

## Context

The Python SDK currently consists of the `base`, `core` and `gen` packages. The `gen` package has a large dependency footprint, which includes by default, for example, `openai`, `pandas` and `langchain`. Users asked for packages with a smaller dependency footprint for their use cases.

## Decision

Option C. Split the `gen` package into separate PyPI packages for the individual services (for example `sap-ai-sdk-rpt`, `sap-ai-sdk-orchestration` and so on). The `sap-ai-sdk-gen` package itself will stay for backwards compatibility as a meta package that distributes the individual packages in the `gen_ai_hub` namespace.

## Consequences

- The dependency footprint of the new packages will be minimal.
- There will be no breaking changes for current users because they can continue to use the `gen` package.
- There is a migration effort in creating the new packages and updating CI and release pipelines.

## Appendix

### Option A: Optional Dependencies

Move heavy dependencies into named extras (continuing the current approach).

Pros:

- Very small and easy change
- Keeps the current strategy

Cons:

- Making dependencies optional is a breaking change
- There is no clear mapping between the service used by the customer and installation command (some services need optional dependencies, others do not)
- Approach differs from other SDKs
- Are unused optional dependencies correctly ignored by security scanners? Currently this is the case, but it may be a risk in the future

### Option B: Namespace Packages

Distribute individual packages (`sap-ai-sdk-rpt`, `sap-ai-sdk-orchestration`, ...) but in the existing `gen_ai_hub` namespace. This keeps the current import paths and the `gen` meta package is for only assembling all package dependencies. See [this PoC](https://github.com/SAP/ai-sdk-python/tree/namespace-packages-poc) for more details.

Pros:

- Import paths in new packages stay as before
- Meta-package contains no code, just gathers all individual packages
- Independent releases and version numbers per package

Cons:

- Individual release pipeline per package (higher CI and release effort)
- To enable re-exports on the `gen` and `proxy` level, a [small hack](https://github.com/SAP/ai-sdk-python/blob/dfcf453a236a46dffb9ccc2f1763c97d37b3678e/packages/proxy/gen_ai_hub/__init__.py#L7) is needed. In a clean namespace package, these re-exports are not possible because `gen` and `proxy` are namespace without an `init.py`

### Option C: Separate Packages

Distribute separate packages for the different services, each in it's own namespace. The `gen` meta package alias the packages under the `gen_ai_hub` namespace for full backwards compatibility. See [this PoC](https://github.com/SAP/ai-sdk-python/tree/separate-packages-poc) for more details.

Pros:

- Mirrors existing `core` and `base` split and the approach in the other SDKs
- Independent releases and version numbers per package
- Less complex configuration compared to namespace packages (just a bunch of standard Python packages). Also more flexibility cause the old `gen` package and the new packages don't all write in the `gen_ai_hub` namespace.

Cons:

- Individual release pipeline per package (higher CI and release effort)
