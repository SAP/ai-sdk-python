[![REUSE status](https://api.reuse.software/badge/github.com/SAP/ai-sdk-python)](https://api.reuse.software/info/github.com/SAP/ai-sdk-python)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SAP/ai-sdk-python)

# SAP Cloud SDK for AI (Python)

SAP Cloud SDK for AI is the official Software Development Kit (SDK) for SAP AI Core, SAP Generative AI Hub, and Orchestration Service.

This repository contains three packages, formerly known as the AI API Client SDK (`sap-ai-sdk-base`), AI Core SDK (`sap-ai-sdk-core`), and Generative AI Hub SDK (`sap-ai-sdk-gen`).

## Installation

Install the SDK with support for all model providers:

```bash
pip install "sap-ai-sdk-gen[all]"
```

Install the default package (OpenAI support):

```bash
pip install sap-ai-sdk-gen
```

Install selected extras:

```bash
pip install "sap-ai-sdk-gen[google,amazon]"
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and provides a Makefile for common tasks.

### Setup

Install all packages and extras:

```bash
make install
```

### Code Quality

```bash
make format          # auto-format code with Ruff
make format-check    # check formatting without modifying files
make lint            # run Pylint (errors only) across all packages
make license-check   # list third-party license information
```

### Testing

Run unit tests for all packages:

```bash
make test
```

Run integration tests for all packages:

```bash
make test-integration
```

Run tests for a single package (`base`, `core`, or `gen`):

```bash
make test-pkg pkg=core
make test-pkg-integration pkg=core
```

### Sample Code Server

Start the local sample-code server (requires a `sample-code/.env` file):

```bash
make sample-code-server
```

## Documentation

For user-facing documentation, see the [AI SDK docs](https://github.com/SAP/ai-sdk/tree/main/docs-python).

To generate API reference docs locally:

```bash
make docs
```

## Support, Feedback, Contributing

This project is open to feature requests, suggestions, and bug reports via [GitHub issues](https://github.com/SAP/ai-sdk-python/issues).

Contribution and feedback are welcome. For contribution details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Security / Disclosure

If you find a potential security issue, please follow the process in [Security Policy](https://github.com/SAP/ai-sdk-python/security/policy).

Please do not create public GitHub issues for security-related reports.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](https://github.com/SAP/.github/blob/main/CODE_OF_CONDUCT.md).

## Licensing

Copyright 2026 SAP SE or an SAP affiliate company and ai-sdk-python contributors.

See [LICENSE](LICENSE) for license information. Detailed third-party licensing information is available via the [REUSE tool](https://api.reuse.software/info/github.com/SAP/ai-sdk-python).
