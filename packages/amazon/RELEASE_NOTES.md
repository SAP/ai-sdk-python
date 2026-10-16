# Release Notes
## amazon-v1.0.0

### Features
- Initial release of `sap-ai-sdk-amazon`, split out from `sap-ai-sdk-gen`. Contains the native Amazon Bedrock client wrappers (`Session`, `AsyncSession`, `ClientWrapper`, `AsyncClientWrapper`). The langchain adapters (`ChatBedrock`, `ChatBedrockConverse`, `BedrockEmbeddings`) are available via the optional `[langchain]` extra.
