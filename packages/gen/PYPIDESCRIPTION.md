# SAP Cloud SDK for AI (Python) - compatibility meta package

This package provides backward compatibility for code written against the pre-split
`sap-ai-sdk-gen` SDK. It depends on the newer, independently published packages
(`sap-ai-sdk-proxy`, `sap-ai-sdk-orchestration`, `sap-ai-sdk-prompt-registry`,
`sap-ai-sdk-document-grounding`, `sap-ai-sdk-batch`, `sap-ai-sdk-evaluations`) and
re-exposes the old `gen_ai_hub.*` import paths as thin forwarders to the new modules.

It contains **no logic of its own** — every import resolves to the corresponding new
package. New projects should depend on the specific `sap-ai-sdk-*` packages they need
instead of this meta package.

## Installation

Base install (restores `gen_ai_hub.proxy`, `gen_ai_hub.orchestration_v2`,
`gen_ai_hub.prompt_registry`, `gen_ai_hub.document_grounding`,
`gen_ai_hub.batch_service`, `gen_ai_hub.evaluations`):

    pip install sap-ai-sdk-gen

With everything (langchain adapter + Amazon + Google native clients):

    pip install "sap-ai-sdk-gen[all]"

Selective extras:

    pip install "sap-ai-sdk-gen[langchain]"
    pip install "sap-ai-sdk-gen[amazon,google]"

## Known migration gap

The old `gen_ai_hub.proxy.langchain` namespace re-exported OpenAI **and** Amazon
(`ChatBedrock`, …) **and** Google (`ChatGoogleGenerativeAI`, …) symbols at its *top
level*. The submodule paths are preserved — `gen_ai_hub.proxy.langchain.amazon` /
`.google_genai` forward to the new provider adapters (behind the `[amazon]` / `[google]`
extras) — but the merged **top-level** re-export forwards only the OpenAI subset. Import
the Bedrock/Google adapters from the submodule or their new home:

    from gen_ai_hub.proxy.langchain.amazon import ChatBedrock          # legacy submodule path
    from sap_ai_sdk_langchain.amazon import ChatBedrock, ChatBedrockConverse, BedrockEmbeddings
    from sap_ai_sdk_langchain.google import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
