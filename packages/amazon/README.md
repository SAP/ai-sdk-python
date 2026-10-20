# sap-ai-sdk-amazon

Amazon Bedrock provider for the SAP Cloud SDK for AI (Python). Ships the
boto3-based clients that route through the generative AI Hub proxy of SAP AI Core.

This package contributes to the **`gen_ai_hub` namespace** (PEP 420). It ships no
`gen_ai_hub/__init__.py`; its code lives under `gen_ai_hub.proxy.native.amazon`.

## Installation

```bash
# Native Bedrock session/clients only
pip install sap-ai-sdk-amazon

# Including the LangChain wrappers (ChatBedrock, BedrockEmbeddings, …)
pip install "sap-ai-sdk-amazon[langchain]"
```

Installing this package automatically pulls `sap-ai-sdk-proxy`, `boto3`,
`aiobotocore`, and `botocore`. The `[langchain]` extra additionally pulls
`langchain`, `langchain-classic`, and `langchain-aws`.

## Imports

```python
# Native clients (always available with sap-ai-sdk-amazon)
from gen_ai_hub.proxy.native.amazon import Session, AsyncSession, ClientWrapper

# LangChain wrappers (require the [langchain] extra)
from gen_ai_hub.proxy.native.amazon.langchain import (
    ChatBedrock, ChatBedrockConverse, BedrockEmbeddings,
)
# Back-compat shim path (still works with the [langchain] extra installed):
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock, BedrockEmbeddings
```

`init_llm("amazon--nova-micro")` from `sap-ai-sdk-proxy` resolves to this
package's wrappers once `sap-ai-sdk-amazon[langchain]` is installed; if it is
not, that call raises an `ImportError` telling you to install it.

## Configuration, Usage

See the official documentation on
[help.sap.com](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html).
