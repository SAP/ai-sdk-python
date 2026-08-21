from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sample_code import core, openai, orchestration

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

# OpenAI
app.get("/openai/chat-completion")(openai.chat_completion)
app.get("/openai/chat-completion-stream")(openai.chat_completion_stream)
app.get("/openai/chat-completion-structured")(openai.chat_completion_structured)
app.get("/openai/chat-completion-structured-stream")(
    openai.chat_completion_structured_stream
)
app.get("/openai/responses")(openai.responses_simple)
app.get("/openai/responses-structured")(openai.responses_structured)
app.get("/openai/embedding")(openai.embedding)

app.get("/orchestration/completion")(orchestration.completion)
app.get("/orchestration/completion-stream")(orchestration.completion_stream)
app.get("/orchestration/completion-template")(orchestration.completion_template)
app.get("/orchestration/completion-json")(orchestration.completion_json)
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

# PARTIALLY MISSING
# Orchestration
# - completion --> with resource group and with fallback
# - stream completion --> also with json response and tools
# - template --> from registry

# FULLY MISSING
# Orchestration
# - tool calling
# - async
# - config (?) from registry
# - from json (?)

# LangChain
# - max tokens
# - structured output
# - orchestration
# - input filter
# - output filter
# - masking
# - rag
# - toolchain
# - stateful chain
# - invoke dynamic model agent
# - prompt caching agent
# - retrieve documents
# - streaming

# Prompt Registry
# RPT Models
# Amazon and Google
