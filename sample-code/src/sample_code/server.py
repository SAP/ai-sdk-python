from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sample_code import amazon, core, google, openai, orchestration

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

# Orchestration
app.get("/orchestration/completion")(orchestration.completion)
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
app.get("/orchestration/tool_call_decorator")(orchestration.tool_call_decorator)
app.get("/orchestration/tool_call_function_tool")(orchestration.tool_call_function_tool)
app.get("/orchestration/tool_call_json")(orchestration.tool_call_json)
