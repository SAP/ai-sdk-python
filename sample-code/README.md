# Sample Code - Work in Progress

Sample code to demonstrate the usage of the SAP Cloud SDK for AI.

## Local Deployment

Create a .env file in the sample-code directory with the complete content of your AI core service key by adding the following lines:

```bash
AICORE_CLIENT_ID="..."
AICORE_CLIENT_SECRET="..."
AICORE_AUTH_URL="..."
AICORE_BASE_URL="..."
```

The server can be started with 
```bash
uv run uvicorn sample_code.server:app --app-dir src --env-file .env --reload
```
or by running ```make```.

## Usage

TODO: overview
