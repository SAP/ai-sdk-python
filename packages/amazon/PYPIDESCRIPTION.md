# SAP Cloud SDK for AI (Python) - Amazon Bedrock

Amazon Bedrock integration for the SAP generative AI SDK. Provides the native
Bedrock client wrappers (`Session`, `AsyncSession`, `ClientWrapper`) that route
`boto3`/`aiobotocore` calls through the generative AI Hub of SAP AI Core.

Looking for the langchain adapters (`ChatBedrock`, `ChatBedrockConverse`,
`BedrockEmbeddings`)? They now ship with the langchain package — install
`sap-ai-sdk-langchain[amazon]`.

## Installation

    pip install sap-ai-sdk-amazon

## Usage

```python
from sap_ai_sdk_amazon import Session

session = Session()
client = session.client("bedrock-runtime", model="anthropic--claude-4-sonnet")
```

## Documentation

See the project documentation for full usage details.
