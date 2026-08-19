# Sample Code - Work in Progress

Sample code to demonstrate the usage of the SAP Cloud SDK for AI.

## Prerequisites

Before running the application, ensure the following prerequisites are met:

- Python installation (3.10 or higher)
- uv installation (0.12)
- Credentials for [SAP AI Core](https://help.sap.com/docs/sap-ai-core/sap-ai-core-service-guide/what-is-sap-ai-core) service configured.
- Deployments of the orchestration service as well as the following models in the resource group specified in the `.env` file below:
  - `gpt-5.4-nano`
  - `text-embedding-3-small`
  - `anthropic--claude-4.6-sonnet`
  - `gemini-3.5-flash`

## Local Deployment

Create a `.env` file in the sample-code directory with the complete content of your AI core service key by adding the following lines:

```bash
AICORE_CLIENT_ID="..."
AICORE_CLIENT_SECRET="..."
AICORE_AUTH_URL="..."
AICORE_BASE_URL="..."
```

Optionally, you can add the `AICORE_RESOURCE_GROUP` environment variable to specify a resource group different from the `default` one.

The server can be started with

```bash
uv run uvicorn sample_code.server:app --app-dir src --env-file .env --reload
```

or by running ```make```.

## Usage

When the server is running, head to `http://localhost:8000/docs` to see all available endpoints.
