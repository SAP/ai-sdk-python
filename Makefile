.PHONY: install docs lint license-check test test-integration test-pkg test-pkg-integration

install:
	uv sync --all-packages --all-extras

docs:
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen \
		packages/base/ai_api_client_sdk \
		packages/base/ai_api_client_sdk/helpers
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen \
		packages/core/ai_core_sdk \
		packages/core/ai_core_sdk/helpers \
		packages/core/ai_core_sdk/cli.py
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen \
		packages/gen/gen_ai_hub \
		packages/gen/gen_ai_hub/evaluations/_internal
	uv run sphinx-build -b html docs/sphinx api-docs/

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
