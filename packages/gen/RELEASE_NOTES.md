# Release Notes
## gen-v1.0.0

### Features
- Compatibility meta package for the post-split `sap-ai-sdk-*` ecosystem. Depends on the new packages and re-exposes the legacy `gen_ai_hub.*` import paths as thin forwarders so existing code keeps working. Provider native clients (`[amazon]`, `[google]`) and the LangChain adapter (`[langchain]`) are available via extras; `[all]` pulls everything.

### Known gaps
- `gen_ai_hub.proxy.langchain` forwards only the OpenAI subset. The Bedrock/Google LangChain adapters moved to `sap_ai_sdk_amazon.langchain` / `sap_ai_sdk_google.langchain`; import them from there for now.
