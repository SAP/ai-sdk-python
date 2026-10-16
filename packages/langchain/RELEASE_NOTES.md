# Release Notes
## langchain-v1.0.0

### Features
- Initial release of `sap-ai-sdk-langchain`, split out from `sap-ai-sdk-gen`. Contains `init_llm` / `init_embedding_model` and the OpenAI langchain adapters. Provider adapters (Amazon, Google) moved to their provider packages and are dispatched lazily.
