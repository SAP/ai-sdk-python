install:
	uv sync --all-packages --all-extras

lint:
	uv run pylint ai_api_client_sdk ai_core_sdk gen_ai_hub --errors-only --output-format=colorized

license-check:
	uv run pip-licenses

test:
	uv run pytest packages/base/tests
	uv run pytest packages/core/tests
	uv run pytest packages/gen/tests

test-integration:
	uv run pytest packages/base/integration_tests
	uv run pytest packages/core/integration_tests
	uv run pytest packages/gen/integration_tests

test-pkg:
	uv run pytest packages/$(pkg)/tests

test-pkg-integration:
	uv run pytest packages/$(pkg)/integration_tests
