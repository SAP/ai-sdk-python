install:
	uv sync --all-packages --all-extras

test:
	uv run pytest packages/ai-api-client-sdk/tests
	uv run pytest packages/ai-core-sdk/tests
	uv run pytest packages/generative-ai-hub-sdk/tests

test-integration:
	uv run pytest -c pytest-integration.toml

test-pkg:
	uv run pytest packages/$(pkg)/tests

test-pkg-integration:
	uv run pytest packages/$(pkg)/integration_tests -c pytest-integration.toml
