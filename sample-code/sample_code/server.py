from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sample_code import amazon, core, google, grounding, langchain_orchestration, openai, orchestration, prompt_registry, sap_rpt

app = FastAPI(title="SAP AI Core Python SDK Sample Application")


# no specific error handling, simply return error message
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


# NOTE: /docs contains an auto-generated overview of the routes


@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok"}


# AI Core (Configurations/Deployments)
app.get("/core/configurations")(core.get_configurations)
app.post("/core/configuration/create")(core.create_configuration)
app.get("/core/deployments")(core.get_deployments)
app.post("/core/deployment/create")(core.create_deployment)
app.get("/core/scenarios")(core.get_scenarios)
app.get("/core/models")(core.get_models)

# Azure/OpenAI
app.get("/openai/chat-completion")(openai.chat_completion)
app.get("/openai/chat-completion-stream")(openai.chat_completion_stream)
app.get("/openai/chat-completion-structured")(openai.chat_completion_structured)
app.get("/openai/responses")(openai.responses_simple)
app.get("/openai/responses-structured")(openai.responses_structured)
app.get("/openai/embedding")(openai.embedding)

# Google
app.get("/google/generate")(google.generate)
app.get("/google/generate-stream")(google.generate_stream)
app.get("/google/tool-call")(google.tool_call)

# Amazon/Anthropic
app.get("/amazon/converse")(amazon.converse)

# LangChain
app.get("/langchain/chat-completion")(langchain_orchestration.init_llm_chat_completion)
app.get("/langchain/embedding")(langchain_orchestration.init_embedding)
app.get("/langchain/chat-completion-with-fallback")(langchain_orchestration.invoke_chain_with_fallback_configs)
app.get("/langchain/dynamic-model-agent")(langchain_orchestration.invoke_dynamic_model_agent)
app.get("/langchain/tool-chain")(langchain_orchestration.tool_chain)
app.get("/langchain/structured-output")(langchain_orchestration.structured_output)
app.get("/langchain/langgraph/chat-completion")(langchain_orchestration.langgraph_chat_completion)
app.get("/langchain/langgraph/chat-completion-stream")(langchain_orchestration.langgraph_chat_completion_stream)

# SAP RPT-1
app.get("/sap-rpt/predict-by-rows")(sap_rpt.predict_by_rows)
app.get("/sap-rpt/predict-by-columns")(sap_rpt.predict_by_columns)
app.get("/sap-rpt/predict-regression")(sap_rpt.regression)

# Orchestration
app.get("/orchestration/completion")(orchestration.completion)
app.get("/orchestration/completion-async")(orchestration.completion_async)
app.get("/orchestration/completion-stream")(orchestration.completion_stream)
app.get("/orchestration/completion-template")(orchestration.completion_template)
app.get("/orchestration/completion-json")(orchestration.completion_json)
app.get("/orchestration/completion-with-fallback")(
    orchestration.completion_with_fallback
)
app.get("/orchestration/completion-abap")(orchestration.completion_abap)
app.get("/orchestration/message-history")(orchestration.message_history)
app.get("/orchestration/completion-image")(orchestration.completion_image)
app.get("/orchestration/input-filtering")(orchestration.input_filtering)
app.get("/orchestration/output-filtering")(orchestration.output_filtering)
app.get("/orchestration/completion-masking")(orchestration.completion_masking)
app.get("/orchestration/translation")(orchestration.translation)
app.get("/orchestration/citations")(orchestration.sonar_with_citations)
app.get("/orchestration/embedding")(orchestration.embedding)
app.get("/orchestration/embedding-batched")(orchestration.embedding_batched)
app.get("/orchestration/embedding-masked")(orchestration.embedding_masked)
app.get("/orchestration/tool-call-decorator")(orchestration.tool_call_decorator)
app.get("/orchestration/tool-call-function-tool")(orchestration.tool_call_function_tool)
app.get("/orchestration/tool-call-json")(orchestration.tool_call_json)

# Prompt Registry - Prompt Templates
app.post("/prompt-registry/template/create")(prompt_registry.create_prompt_template)
app.get("/prompt-registry/templates")(prompt_registry.get_prompt_templates)
app.post("/prompt-registry/template/fill")(prompt_registry.fill_prompt_template)
app.delete("/prompt-registry/template/{template_id}")(prompt_registry.delete_prompt_template)

# Prompt Registry - Orchestration Configs
app.post("/prompt-registry/config/create")(prompt_registry.create_orchestration_config)
app.get("/prompt-registry/configs")(prompt_registry.get_orchestration_configs)

# Document Grounding - Vector API
app.get("/document-grounding/vector/get-collections")(grounding.get_collections)
app.post("/document-grounding/vector/create-collection")(grounding.create_collection)
app.delete("/document-grounding/vector/delete-collection/{collection_id}")(grounding.delete_collection)
app.post("/document-grounding/vector/add-documents/{collection_id}")(grounding.create_documents)

# Document Grounding - Pipeline API
app.get("/document-grounding/pipeline/get-pipelines")(grounding.get_pipelines)

# Document Grounding - Retrieval API
app.get("/document-grounding/retrieval/search")(grounding.retrieval_documents)
