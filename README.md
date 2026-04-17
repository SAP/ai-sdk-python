[![REUSE status](https://api.reuse.software/badge/github.com/SAP/ai-sdk-python)](https://api.reuse.software/info/github.com/SAP/ai-sdk-python)

# SAP Cloud SDK for AI (Python)

SAP Cloud SDK for AI is the official Software Development Kit (SDK) for SAP AI Core, SAP Generative AI Hub, and Orchestration Service.

The SDK formerly known as generative AI Hub SDK was rebranded.

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

For detailed configuration and usage examples, see [README_sphynx.md](README_sphynx.md).

## Development

Main SDK modules are under [gen_ai_hub](gen_ai_hub).

Integration tests are split into two groups:

1. Standard integration tests.
2. Bedrock integration tests marked with the pytest marker bedrock.

Run tests with:

```bash
pytest tests -v
pytest integration_tests -m "not bedrock" -v
pytest integration_tests -m bedrock -v
```

You can also use the Makefile targets for acceptance test runs.

## Documentation

Documentation sources are in [docs](docs), and generated API docs are included there as well.

For local documentation workflows and SDK configuration details, see [README_sphynx.md](README_sphynx.md).

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
