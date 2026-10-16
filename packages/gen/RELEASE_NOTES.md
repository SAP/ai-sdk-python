# Release Notes
## gen-v1.0.0

### Features
- Compatibility meta package for the post-split `sap-ai-sdk-*` ecosystem. Depends on the new packages and re-exposes the legacy `gen_ai_hub.*` import paths as thin forwarders so existing code keeps working. Provider native clients (`[amazon]`, `[google]`) and the LangChain adapter (`[langchain]`) are available via extras; `[all]` pulls everything.

### Known gaps
- `gen_ai_hub.proxy.langchain` submodule paths (`.openai`, `.init_models`, `.amazon`, `.google_genai`) all forward (the provider ones behind the `[amazon]`/`[google]` extras), but the merged *top-level* re-export forwards only the OpenAI subset. Import the Bedrock/Google adapters via the submodule (`gen_ai_hub.proxy.langchain.amazon`) or their new home (`sap_ai_sdk_amazon.langchain` / `sap_ai_sdk_google.langchain`).
