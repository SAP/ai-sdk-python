from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sample_code import amazon, core, google, grounding, langchain_openai, openai, orchestration, prompt_registry, sap_rpt

app = FastAPI(
    title="SAP AI Core Python SDK",
    description=(
        "Demo application showcasing SAP Gen AI Hub Python SDK capabilities: "
        "SAP RPT, Document Grounding, and Orchestration Service."
    ),
    version="1.0.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


# ── AI Core ────────────────────────────────────────────────────────
app.get("/core/configurations",        tags=["AI Core"])(core.get_configurations)
app.post("/core/configuration/create", tags=["AI Core"])(core.create_configuration)
app.get("/core/deployments",           tags=["AI Core"])(core.get_deployments)
app.post("/core/deployment/create",    tags=["AI Core"])(core.create_deployment)
app.get("/core/scenarios",             tags=["AI Core"])(core.get_scenarios)
app.get("/core/models",                tags=["AI Core"])(core.get_models)

# ── Azure / OpenAI ─────────────────────────────────────────────────
app.get("/openai/chat-completion",            tags=["OpenAI"])(openai.chat_completion)
app.get("/openai/chat-completion-stream",     tags=["OpenAI"])(openai.chat_completion_stream)
app.get("/openai/chat-completion-structured", tags=["OpenAI"])(openai.chat_completion_structured)
app.get("/openai/responses",                  tags=["OpenAI"])(openai.responses_simple)
app.get("/openai/responses-structured",       tags=["OpenAI"])(openai.responses_structured)
app.get("/openai/embedding",                  tags=["OpenAI"])(openai.embedding)

# ── Google ─────────────────────────────────────────────────────────
app.get("/google/generate",        tags=["Google"])(google.generate)
app.get("/google/generate-stream", tags=["Google"])(google.generate_stream)
app.get("/google/tool-call",       tags=["Google"])(google.tool_call)

# ── Amazon ─────────────────────────────────────────────────────────
app.get("/amazon/converse", tags=["Amazon"])(amazon.converse)

# ── LangChain ──────────────────────────────────────────────────────
app.get("/langchain/invoke",                          tags=["LangChain"])(langchain_openai.invoke)
app.get("/langchain/invoke_chain",                    tags=["LangChain"])(langchain_openai.invoke_chain)
app.get("/langchain/structured-output-json-schema",   tags=["LangChain"])(langchain_openai.invoke_with_structured_output_json_schema)
app.get("/langchain/tool-chain",                      tags=["LangChain"])(langchain_openai.invoke_tool_chain)
app.get("/langchain/rag-chain",                       tags=["LangChain"])(langchain_openai.invoke_rag_chain)
app.get("/langchain/stream-chain",                    tags=["LangChain"])(langchain_openai.stream_chain)

# ── SAP RPT ────────────────────────────────────────────────────────
# POST because the request body carries the tabular input data.
# All fields have defaults — omit the body to run the built-in sample data.
app.post("/sap-rpt/predict-by-rows",    tags=["SAP RPT"])(sap_rpt.predict_by_rows)
app.post("/sap-rpt/predict-by-columns", tags=["SAP RPT"])(sap_rpt.predict_by_columns)
app.post("/sap-rpt/predict-regression", tags=["SAP RPT"])(sap_rpt.regression)

# ── Orchestration ──────────────────────────────────────────────────
app.get("/orchestration/completion",               tags=["Orchestration"])(orchestration.completion)
app.get("/orchestration/completion-async",         tags=["Orchestration"])(orchestration.completion_async)
app.get("/orchestration/completion-stream",        tags=["Orchestration"])(orchestration.completion_stream)
app.get("/orchestration/completion-template",      tags=["Orchestration"])(orchestration.completion_template)
app.get("/orchestration/completion-json",          tags=["Orchestration"])(orchestration.completion_json)
app.get("/orchestration/completion-with-fallback", tags=["Orchestration"])(orchestration.completion_with_fallback)
app.get("/orchestration/completion-abap",          tags=["Orchestration"])(orchestration.completion_abap)
app.get("/orchestration/message-history",          tags=["Orchestration"])(orchestration.message_history)
app.get("/orchestration/completion-image",         tags=["Orchestration"])(orchestration.completion_image)
app.get("/orchestration/input-filtering",          tags=["Orchestration"])(orchestration.input_filtering)
app.get("/orchestration/output-filtering",         tags=["Orchestration"])(orchestration.output_filtering)
app.get("/orchestration/completion-masking",       tags=["Orchestration"])(orchestration.completion_masking)
app.get("/orchestration/reasoning-content",        tags=["Orchestration"])(orchestration.reasoning_content)
app.get("/orchestration/reasoning-content-stream", tags=["Orchestration"])(orchestration.reasoning_content_stream)
app.get("/orchestration/translation",              tags=["Orchestration"])(orchestration.translation)
app.get("/orchestration/citations",                tags=["Orchestration"])(orchestration.sonar_with_citations)
app.get("/orchestration/embedding",                tags=["Orchestration"])(orchestration.embedding)
app.get("/orchestration/embedding-batched",        tags=["Orchestration"])(orchestration.embedding_batched)
app.get("/orchestration/embedding-masked",         tags=["Orchestration"])(orchestration.embedding_masked)
app.get("/orchestration/tool-call-decorator",      tags=["Orchestration"])(orchestration.tool_call_decorator)
app.get("/orchestration/tool-call-function-tool",  tags=["Orchestration"])(orchestration.tool_call_function_tool)
app.get("/orchestration/tool-call-json",           tags=["Orchestration"])(orchestration.tool_call_json)

# ── Prompt Registry ────────────────────────────────────────────────
app.post("/prompt-registry/template/create",           tags=["Prompt Registry"])(prompt_registry.create_prompt_template)
app.get("/prompt-registry/templates",                  tags=["Prompt Registry"])(prompt_registry.get_prompt_templates)
app.post("/prompt-registry/template/fill",             tags=["Prompt Registry"])(prompt_registry.fill_prompt_template)
app.delete("/prompt-registry/template/{template_id}",  tags=["Prompt Registry"])(prompt_registry.delete_prompt_template)
app.post("/prompt-registry/config/create",             tags=["Prompt Registry"])(prompt_registry.create_orchestration_config)
app.get("/prompt-registry/configs",                    tags=["Prompt Registry"])(prompt_registry.get_orchestration_configs)

# ── Document Grounding ─────────────────────────────────────────────
app.get("/document-grounding/vector/get-collections",                   tags=["Document Grounding"])(grounding.get_collections)
app.post("/document-grounding/vector/create-collection",                tags=["Document Grounding"])(grounding.create_collection)
app.delete("/document-grounding/vector/delete-collection/{collection_id}", tags=["Document Grounding"])(grounding.delete_collection)
app.post("/document-grounding/vector/add-documents/{collection_id}",   tags=["Document Grounding"])(grounding.create_documents)
app.get("/document-grounding/pipeline/get-pipelines",                  tags=["Document Grounding"])(grounding.get_pipelines)
app.get("/document-grounding/retrieval/search",                        tags=["Document Grounding"])(grounding.retrieval_documents)
