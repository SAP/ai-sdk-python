# SAP Cloud SDK for AI (Python) - generative

The SDK formerly known as *generative AI Hub SDK* was rebranded.
With this SDK you can leverage the power of Large Language Models available in SAP's Generative AI Hub.

## Installing and Using the SDK

Use the new package name to install the SDK:

```bash
pip install sap-ai-sdk-gen[all]
```

The class names have not changed i.e., you can continue to use existing code.

> [!NOTE]  
> Please refer to the [AI SDK Python Documentation](https://sap.github.io/ai-sdk/docs/python/overview)

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. All common tasks are available as Makefile targets from the **repository root**.

### Setup

```bash
make install
```

### Main Modules

The main modules are located in the subfolder [proxy](https://github.com/SAP/ai-sdk-python/tree/main/packages/gen/gen_ai_hub/proxy):

- [core](https://github.com/SAP/ai-sdk-python/tree/main/packages/gen/gen_ai_hub/proxy/core)
- [gen_ai_hub_proxy](https://github.com/SAP/ai-sdk-python/tree/main/packages/gen/gen_ai_hub/proxy/gen_ai_hub_proxy)
- [langchain](https://github.com/SAP/ai-sdk-python/tree/main/packages/gen/gen_ai_hub/proxy/langchain)
- [native](https://github.com/SAP/ai-sdk-python/tree/main/packages/gen/gen_ai_hub/proxy/native)

### Code Quality

```bash
make format          # auto-format code with Ruff
make format-check    # check formatting without modifying files
make lint            # run Pylint (errors only) across all packages
make license-check   # list third-party license information
```

### Docstring Convention

We use the `reStructuredText` format for all Python docstrings, following [PEP 257](https://peps.python.org/pep-0257/) and the [Sphinx documentation style guide](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html). This ensures consistency and compatibility with other SDKs in the same namespace.

## Testing

Run unit tests for this package:

```bash
make test-pkg pkg=gen
```

Run all unit tests across every package:

```bash
make test
```

### Integration Tests

Integration tests verify system behavior across components. They are split into two groups:

1. **Main Integration Tests**: executed against the main cluster.
2. **Bedrock Integration Tests**: a targeted subset annotated with `@pytest.mark.bedrock`, executed in a separate cluster (US10 prod).

```bash
make test-pkg-integration pkg=gen   # this package only
make test-integration                # all packages
```

## Documentation

For user-facing documentation, see the [AI SDK Python Documentation](https://sap.github.io/ai-sdk/docs/python/overview).

### Building Locally

Generate API reference docs from the repository root:

```bash
make docs
```

This runs Sphinx to produce HTML output in `api-docs/`.

## Kudos

Kudos to the authors (especially Mathis Börner).
