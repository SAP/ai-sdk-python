from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sample_code import core, openai

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
