# sap-ai-sdk-amazon

Amazon Bedrock provider for the SAP Cloud SDK for AI (Python). Ships the
boto3-based clients that route through the generative AI Hub proxy of SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.proxy.native.amazon`.

## Installation

```bash
# Native Bedrock session/clients only
pip install sap-ai-sdk-amazon
```

Installing this package automatically pulls `sap-ai-sdk-proxy`, `boto3`,
`aiobotocore`, and `botocore`. This package ships only the native
Amazon/Bedrock client.

If you want the LangChain Amazon Bedrock wrappers (`ChatBedrock`,
`ChatBedrockConverse`, `BedrockEmbeddings`), install
`pip install "sap-ai-sdk-langchain[amazon]"` instead (see
../langchain/README.md).

## Imports

```python
# Native clients (always available with sap-ai-sdk-amazon)
from gen_ai_hub.proxy.native.amazon import Session, AsyncSession, ClientWrapper
```

The LangChain wrappers are importable from `gen_ai_hub.proxy.langchain.amazon`
once `sap-ai-sdk-langchain[amazon]` is installed.

`init_llm("amazon--nova-micro")` from `sap-ai-sdk-proxy` resolves to the
LangChain wrappers once `sap-ai-sdk-langchain[amazon]` is installed; if it is
not, that call raises an `ImportError` telling you to install it.

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
