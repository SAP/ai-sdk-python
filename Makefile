.PHONY: install docs lint license-check test test-integration test-pkg test-pkg-integration

install:
	uv sync --all-packages --all-extras

docs:
	uv run pdoc \
		--template-directory docs/pdoc \
		ai_api_client_sdk \
		'!ai_api_client_sdk.helpers' \
		ai_core_sdk \
		'!ai_core_sdk.helpers' \
		'!ai_core_sdk.cli' \
		gen_ai_hub \
		gen_ai_hub.batch_service \
		gen_ai_hub.document_grounding \
		gen_ai_hub.evaluations \
		gen_ai_hub.orchestration \
		gen_ai_hub.orchestration_v2 \
		gen_ai_hub.prompt_registry \
		gen_ai_hub.proxy \
		-o api-docs/

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
