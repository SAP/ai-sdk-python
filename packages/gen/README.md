# sap-ai-sdk-gen (meta-package)

The SDK formerly known as *generative AI Hub SDK* was rebranded.
With this SDK you can leverage the power of Large Language Models available in SAP's Generative AI Hub.

`sap-ai-sdk-gen` is a **meta-package**: it ships no code of its own and simply
depends on every subsystem and provider distribution of the SDK. All of them
contribute to the shared **`gen_ai_hub` namespace**
([PEP 420](https://peps.python.org/pep-0420/) implicit namespace packages), so
the `gen_ai_hub.*` import paths work the same regardless of which distributions
are installed — none of them ship a `gen_ai_hub/__init__.py`.

## Installing and Using the SDK

Install everything (all providers **with** their LangChain wrappers):

```bash
pip install "sap-ai-sdk-gen[all]"
```

Install everything without the provider LangChain wrappers:

```bash
pip install sap-ai-sdk-gen
```

If you only need part of the SDK, install just the distributions you want instead
of the meta-package — this keeps the dependency footprint small (e.g. no
boto3/google-genai/LangChain unless you ask for them):

```bash
# orchestration against OpenAI, no Amazon/Google/LangChain pulled in
pip install sap-ai-sdk-orchestration sap-ai-sdk-openai
```

The import paths and class names are unchanged, **except** that the top-level
proxy-client re-export moved to its submodule:

```python
# before:  from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy.gen_ai_hub_proxy import GenAIHubProxyClient
```

### Distributions

| Distribution | Namespace it ships | Install README |
|---|---|---|
| `sap-ai-sdk-proxy` | `gen_ai_hub.proxy.{core,gen_ai_hub_proxy,langchain}` | [proxy](../proxy/README.md) |
| `sap-ai-sdk-openai` | `gen_ai_hub.proxy.native.openai` | [openai](../openai/README.md) |
| `sap-ai-sdk-amazon` | `gen_ai_hub.proxy.native.amazon` | [amazon](../amazon/README.md) |
| `sap-ai-sdk-google` | `gen_ai_hub.proxy.native.google_genai` | [google](../google/README.md) |
| `sap-ai-sdk-rpt` | `gen_ai_hub.proxy.native.sap` | [rpt](../rpt/README.md) |
| `sap-ai-sdk-orchestration` | `gen_ai_hub.orchestration_v2` | [orchestration](../orchestration/README.md) |
| `sap-ai-sdk-prompt-registry` | `gen_ai_hub.prompt_registry` | [prompt-registry](../prompt-registry/README.md) |
| `sap-ai-sdk-document-grounding` | `gen_ai_hub.document_grounding` | [document-grounding](../document-grounding/README.md) |
| `sap-ai-sdk-batch` | `gen_ai_hub.batch_service` | [batch](../batch/README.md) |
| `sap-ai-sdk-evaluations` | `gen_ai_hub.evaluations` | [evaluations](../evaluations/README.md) |

> [!NOTE]  
> Please refer to the [Generative AI Hub SDK Documentation](https://github.wdf.sap.corp/pages/AI/generative-ai-hub-sdk)

## Development

Each distribution keeps its code under the real `gen_ai_hub/...` tree inside its
own `packages/<name>/` directory. The proxy distribution holds the core modules:

- `gen_ai_hub/proxy/gen_ai_hub_proxy` — the proxy client
- `gen_ai_hub/proxy/langchain` — provider-agnostic LangChain factories (`init_llm`, `init_embedding_model`)
- `gen_ai_hub/proxy/native` — provider clients, each shipped by its own distribution

### Docstring Convention
In this project, we use the `reStructuredText` format for all Python docstrings, following the guidelines outlined in [PEP 257](https://peps.python.org/pep-0257/) and the [Sphinx documentation style guide](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).
This ensures consistency and compatibility with other SDKs in the same namespace.

Please follow these conventions when contributing to the codebase.

## Renovate Setup

Renovate is set up for this repository. For further information, take a look at the [documentation in ml-api-facade](https://github.wdf.sap.corp/AI/ml-api-facade/blob/master/docs/renovate.md).

## Integration Tests

This project utilizes integration tests to verify the system’s behavior across its various components. The tests are split into two primary groups:

1. **Main Integration Tests:** Most of the integration tests are executed against the main cluster, ensuring that the major functionalities and interactions in the system behave as expected.

2. **Bedrock Integration Tests:** A targeted subset of integration tests, known as the Bedrock tests, are executed in a separate cluster US10 (prod). These tests focus specifically on the Bedrock portions of the system and are annotated with `@pytest.mark.bedrock` within the test classes. This separation allows for targeted testing of Bedrock-specific features without interference from the broader system functionalities.

### Running Bedrock Tests

To facilitate the execution of the Bedrock integration tests, the `Makefile` includes the command `run-acceptance-test-us10`. This command specifically triggers the execution of the Bedrock tests, enabling the CI system to verify the Bedrock integrations in isolation (separate step).

The mechanism of splitting the tests into distinct clusters and utilizing specialized commands for targeted testing helps in achieving more organized, efficient, and effective testing processes.

Additional details regarding custom test stages and configuration specific to the cumulus can be found in the `customTestStages` section of the `config.yaml` in the `.pipeline` folder.

## Documentation

### Overview

Our project includes an extensive internal documentation to assist developers and users in understanding the architecture, usage, and development of the project. The documentation is built automatically via our continuous integration workflows using [Sphinx](http://www.sphinx-doc.org/), a robust documentation framework that converts [reStructuredText](http://docutils.sourceforge.net/rst.html) files into various output formats.

### Building Documentation Locally

If you wish to build the documentation on your local machine, follow these steps:

1. Navigate to the docs/ directory of the project.
2. Make sure you have Sphinx installed. If not, install it using `pip install sphinx` or `pip install -r requirements.txt`
3. Build the documentation by running `make preview_html`. This command will generate HTML output for the documentation and allow you to preview it in a web browser.

### Automated Documentation Builds with GitHub Actions

Our project leverages GitHub Actions to automate the documentation building process. The workflow is defined in `.github/workflows/documentation.yml`. It is triggered each time a pull request (PR) is merged into the `main` branch. Here's a rough sequence of the automated process:

1. GitHub Actions selects several important files within the project required for generating the documentation.
2. Using the Sphinx framework, GitHub Actions compiles these files into HTML format.
3. Upon successful build, the compiled documentation is pushed to the `gh-pages` branch of the repository.

### Documentation Location

Once the documentation is built by GitHub Actions, it is hosted and available for viewing at the GitHub Pages site. You can access the latest version of the internal documentation at the following URL:

[SAP Cloud SDK for AI (Python) - generative](https://github.wdf.sap.corp/pages/AI/generative-ai-hub-sdk/)

Note that the content on this site reflects the most recent documentation build from the `gh-pages` branch.

### Contributing to this Project

This project is Innersource and if you wish to contribute to this project please request write access to the repository by requesting CAM profile `AI Github AI SDK-Contributors`. More details on contributing to this project can be found in the [CONTRIBUTING.md](https://github.wdf.sap.corp/AI/generative-ai-hub-sdk/blob/main/CONTRIBUTING.md) file.

## Kudos

The code for this SDK is originated from [llm-commons](https://github.tools.sap/AI-Playground-Projects/llm-commons).

Kudos to the authors (especially Mathis Börner). 
