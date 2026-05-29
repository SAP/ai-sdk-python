install:
	uv sync --all-packages --all-extras

lint:
	uv run pylint ai_api_client_sdk ai_core_sdk gen_ai_hub --errors-only --output-format=colorized

license-check:
	uv run pip-licenses

test:
	uv run pytest packages/ai-api-client-sdk/tests
	uv run pytest packages/ai-core-sdk/tests
	uv run pytest packages/generative-ai-hub-sdk/tests

test-integration:
	uv run pytest packages/ai-api-client-sdk/integration_tests
	uv run pytest packages/ai-core-sdk/integration_tests
	uv run pytest packages/generative-ai-hub-sdk/integration_tests

test-pkg:
	uv run pytest packages/$(pkg)/tests

test-pkg-integration:
	uv run pytest packages/$(pkg)/integration_tests
