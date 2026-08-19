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

# FEATURE PLAN

# Orchestration
# - completion --> with resource group and with fallback
# - stream completion --> also with json response and tools
# - template --> from registry
# - messages history
# - image

app.get("/orchestration/completion")(orchestration.completion)
app.get("/orchestration/completion-stream")(orchestration.completion_stream)
app.get("/orchestration/completion-template")(orchestration.completion_template)
app.get("/orchestration/message-history")(orchestration.message_history)
app.get("/orchestration/completion-image")(orchestration.completion_image)

# - reasoning
# - multi turn reasoning
# - stream reasoning
# - multi string
# - file input (url, local, base 64, other input formats?)
# - input filtering with multiple policies
# - output filtering with multiple policies
# - llama guard (why separate?)
# - masking anonymiyation/pseudonymization/regex (embedding with masking?)
# - grounding (sharepoint/helpsap/parameter)
# - response format json (schema/object)
# - translation
# - embedding
# - citations
# - config (?) from registry
# - from json (?)
# - SAP ABAP
# - cache control (?)

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

# Further native stuff...
