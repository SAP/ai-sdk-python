[![REUSE status](https://api.reuse.software/badge/github.com/SAP/ai-sdk-python)](https://api.reuse.software/info/github.com/SAP/ai-sdk-python)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SAP/ai-sdk-python)

# SAP Cloud SDK for AI (Python)

SAP Cloud SDK for AI is the official Software Development Kit (SDK) for SAP AI Core, SAP Generative AI Hub, and Orchestration Service.

The SDK formerly known as generative AI Hub SDK was rebranded.

## Installation

The SDK is published as several independently-installable distributions that all
contribute to the shared **`gen_ai_hub` namespace**
([PEP 420](https://peps.python.org/pep-0420/) implicit namespace packages), so the
`gen_ai_hub.*` import paths are the same no matter which subset you install.

Install everything via the `sap-ai-sdk-gen` meta-package (all providers **with**
their LangChain wrappers):

```bash
pip install "sap-ai-sdk-gen[all]"
```

Install everything without the provider LangChain wrappers:

```bash
pip install sap-ai-sdk-gen
```

Or install only the distributions you need, which keeps the dependency footprint
small (e.g. no boto3/google-genai/LangChain unless you ask for them):

```bash
# orchestration against OpenAI only — no Amazon/Google/LangChain pulled in
pip install sap-ai-sdk-orchestration sap-ai-sdk-openai
```

### Distributions

| Distribution | Namespace it ships | Install guide |
|---|---|---|
| `sap-ai-sdk-proxy` | `gen_ai_hub.proxy.{core,gen_ai_hub_proxy,langchain}` | [packages/proxy](packages/proxy/README.md) |
| `sap-ai-sdk-openai` | `gen_ai_hub.proxy.native.openai` | [packages/openai](packages/openai/README.md) |
| `sap-ai-sdk-amazon` | `gen_ai_hub.proxy.native.amazon` | [packages/amazon](packages/amazon/README.md) |
| `sap-ai-sdk-google` | `gen_ai_hub.proxy.native.google_genai` | [packages/google](packages/google/README.md) |
| `sap-ai-sdk-rpt` | `gen_ai_hub.proxy.native.sap` | [packages/rpt](packages/rpt/README.md) |
| `sap-ai-sdk-orchestration` | `gen_ai_hub.orchestration_v2` | [packages/orchestration](packages/orchestration/README.md) |
| `sap-ai-sdk-prompt-registry` | `gen_ai_hub.prompt_registry` | [packages/prompt-registry](packages/prompt-registry/README.md) |
| `sap-ai-sdk-document-grounding` | `gen_ai_hub.document_grounding` | [packages/document-grounding](packages/document-grounding/README.md) |
| `sap-ai-sdk-batch` | `gen_ai_hub.batch_service` | [packages/batch](packages/batch/README.md) |
| `sap-ai-sdk-evaluations` | `gen_ai_hub.evaluations` | [packages/evaluations](packages/evaluations/README.md) |
| `sap-ai-sdk-gen` | — (meta-package, no code) | [packages/gen](packages/gen/README.md) |

The three provider distributions (`openai`, `amazon`, `google`) expose their
LangChain wrappers under an optional `[langchain]` extra; `evaluations` exposes
Amazon Bedrock support under an `[amazon]` extra. The provider-agnostic
`init_llm` / `init_embedding_model` factories ship with `sap-ai-sdk-proxy` and
resolve each provider's wrapper lazily, so a model whose provider is not installed
raises an actionable error telling you which distribution to install.

> **Import note.** The namespace root has no `__init__.py`, so the old top-level
> re-export `from gen_ai_hub import GenAIHubProxyClient` no longer exists — import
> it from its submodule instead:
> `from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient`.

For detailed configuration and usage examples, see [README_sphynx.md](README_sphynx.md).

## Development

This repository is a [uv](https://docs.astral.sh/uv/) workspace. Each distribution
lives under `packages/<name>/` and keeps its code under the real `gen_ai_hub/...`
tree (none of them ship a `gen_ai_hub/__init__.py`). The core modules — the proxy
client, the proxy registry, and the LangChain factories — are in
[packages/proxy](packages/proxy).

Install the whole workspace into a single environment:

```bash
make install        # uv sync --all-packages --all-extras
```

Integration tests are split into two groups:

1. Standard integration tests.
2. Bedrock integration tests marked with the pytest marker bedrock.

Run tests across every package with the Makefile targets:

```bash
make test               # unit tests for every package
make test-integration   # integration tests for every package
make test-pkg pkg=proxy # unit tests for a single package
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
