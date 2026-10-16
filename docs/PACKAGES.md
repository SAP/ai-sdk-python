# Packages Overview

The SAP Cloud SDK for AI (Python) is published as several independent packages, each
with its own distribution name (`sap-ai-sdk-*`) and flat import root (`sap_ai_sdk_*`).
Install only the packages you need — heavy dependencies (`pandas`, `boto3`,
`google-genai`, the `langchain` stack) are isolated to the packages that require them.

## At a glance

| Install (`pip install …`) | Import root | What it provides |
|---|---|---|
| `sap-ai-sdk-proxy` | `sap_ai_sdk_proxy` | Proxy client + native OpenAI & SAP (RPT) clients. The mandatory base every other package builds on. |
| `sap-ai-sdk-langchain` | `sap_ai_sdk_langchain` | LangChain adapters for OpenAI + `init_llm` / `init_embedding_model`. |
| `sap-ai-sdk-amazon` | `sap_ai_sdk_amazon` | Native Amazon Bedrock client. LangChain adapter via the `[langchain]` extra. |
| `sap-ai-sdk-google` | `sap_ai_sdk_google` | Native Google GenAI client. LangChain adapter via the `[langchain]` extra. |
| `sap-ai-sdk-orchestration` | `sap_ai_sdk_orchestration` | Orchestration service (v2). |
| `sap-ai-sdk-prompt-registry` | `sap_ai_sdk_prompt_registry` | Prompt template & orchestration-config registry clients. |
| `sap-ai-sdk-document-grounding` | `sap_ai_sdk_document_grounding` | Document grounding: pipeline, retrieval, vector clients. |
| `sap-ai-sdk-batch` | `sap_ai_sdk_batch` | Batch inference service. |
| `sap-ai-sdk-evaluations` | `sap_ai_sdk_evaluations` | Evaluation runs & metrics (pulls `pandas`). S3 support via the `[amazon]` extra. |

All packages depend (directly or transitively) on `sap-ai-sdk-proxy`, so installing any
of them gives you the proxy client too.

---

## `sap-ai-sdk-proxy`

```bash
pip install sap-ai-sdk-proxy
```

```python
from sap_ai_sdk_proxy import (
    get_proxy_client, GenAIHubProxyClient,
    set_proxy_version, get_proxy_version,
)

# native OpenAI client
from sap_ai_sdk_proxy.native.openai import OpenAI, AsyncOpenAI, chat, embeddings, responses

# native SAP (RPT) client
from sap_ai_sdk_proxy.native.sap.client import RPTClient
from sap_ai_sdk_proxy.native.sap.models import RPTRequest, TargetColumn, PredictionConfig, DataType
```

## `sap-ai-sdk-langchain`

```bash
pip install sap-ai-sdk-langchain
```

```python
from sap_ai_sdk_langchain import init_llm, init_embedding_model
from sap_ai_sdk_langchain.openai import ChatOpenAI, OpenAIEmbeddings, OpenAIClient, AsyncOpenAIClient, OpenAI
```

## `sap-ai-sdk-amazon`

```bash
pip install sap-ai-sdk-amazon            # native client only
pip install "sap-ai-sdk-amazon[langchain]"   # + LangChain Bedrock adapters
```

```python
# native
from sap_ai_sdk_amazon import Session, AsyncSession, ClientWrapper, AsyncClientWrapper

# LangChain adapters (requires the [langchain] extra)
from sap_ai_sdk_amazon.langchain import (
    ChatBedrock, ChatBedrockConverse, BedrockEmbeddings, AICoreBedrockBaseModel,
)
```

## `sap-ai-sdk-google`

```bash
pip install sap-ai-sdk-google
pip install "sap-ai-sdk-google[langchain]"   # + LangChain Google adapters
```

```python
# native
from sap_ai_sdk_google import Client, AICoreDynamicTransport, AsyncAICoreDynamicTransport

# LangChain adapters (requires the [langchain] extra)
from sap_ai_sdk_google.langchain import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
```

## `sap-ai-sdk-orchestration`

```bash
pip install sap-ai-sdk-orchestration
```

```python
from sap_ai_sdk_orchestration import OrchestrationService, OrchestrationConfig, ModuleConfig
from sap_ai_sdk_orchestration.models.template import Template, PromptTemplatingModuleConfig
from sap_ai_sdk_orchestration.models.llm_model_details import LLMModelDetails
from sap_ai_sdk_orchestration.models.message import UserMessage, SystemMessage, AssistantMessage
```

## `sap-ai-sdk-prompt-registry`

```bash
pip install sap-ai-sdk-prompt-registry
```

```python
from sap_ai_sdk_prompt_registry import PromptTemplateClient, OrchestrationConfigClient
from sap_ai_sdk_prompt_registry.models.prompt_template import PromptTemplate, PromptTemplateSpec
```

## `sap-ai-sdk-document-grounding`

```bash
pip install sap-ai-sdk-document-grounding
```

```python
from sap_ai_sdk_document_grounding import PipelineAPIClient, RetrievalAPIClient, VectorAPIClient
from sap_ai_sdk_document_grounding.models.retrieval import RetrievalChunk, RetrievalDocument
```

## `sap-ai-sdk-batch`

```bash
pip install sap-ai-sdk-batch
```

```python
from sap_ai_sdk_batch import BatchService, BatchCreateRequest, BatchInput, BatchOutput, BatchSpec
```

## `sap-ai-sdk-evaluations`

```bash
pip install sap-ai-sdk-evaluations          # includes pandas
pip install "sap-ai-sdk-evaluations[amazon]"    # + S3 artifact support (boto3)
```

```python
from sap_ai_sdk_evaluations import (
    EvaluationClient, EvaluationConfig, EvaluationRun, Dataset, MetricConfig, MetricRef, Results,
)
```

---

## Compatibility: `sap-ai-sdk-gen`

Code written against the **pre-split** SDK used a single `sap-ai-sdk-gen` distribution
with the `gen_ai_hub.*` import root. For migration, `sap-ai-sdk-gen` is still available
as a thin **compatibility meta package**: it depends on the packages above and
re-exposes the old `gen_ai_hub.*` paths as forwarders (no logic of its own).

```bash
pip install sap-ai-sdk-gen                  # proxy + orchestration + prompt-registry
                                            # + document-grounding + batch + evaluations
pip install "sap-ai-sdk-gen[all]"           # + langchain + amazon + google
pip install "sap-ai-sdk-gen[langchain]"     # selective extras also work
pip install "sap-ai-sdk-gen[amazon,google]"
```

```python
# legacy imports keep working
from gen_ai_hub.proxy import get_proxy_client, GenAIHubProxyClient
from gen_ai_hub.orchestration_v2 import OrchestrationService
from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.document_grounding.client import PipelineAPIClient
from gen_ai_hub.batch_service import BatchService
from gen_ai_hub.evaluations import EvaluationClient
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI   # [langchain]
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock  # [amazon]
from gen_ai_hub.proxy.native.amazon import Session          # [amazon]
```

**Known migration gap.** The old `gen_ai_hub.proxy.langchain` namespace re-exported the
OpenAI **and** Bedrock **and** Google LangChain symbols at its *top level*. The submodule
paths still work (`gen_ai_hub.proxy.langchain.amazon` / `.google_genai`, behind the
`[amazon]` / `[google]` extras), but the merged **top-level** re-export forwards only the
OpenAI subset. Import the Bedrock/Google adapters from the submodule or their new home:

```python
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock          # legacy submodule path
from sap_ai_sdk_amazon.langchain import ChatBedrock, ChatBedrockConverse, BedrockEmbeddings
from sap_ai_sdk_google.langchain import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
```

**New projects should import the `sap_ai_sdk_*` packages directly** rather than depend on
`sap-ai-sdk-gen` — the compat package exists only to ease migration.
