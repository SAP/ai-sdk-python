.PHONY: install docs lint license-check test test-integration test-pkg test-pkg-integration

install:
	uv sync --all-packages --all-extras

docs:
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/base \
		packages/base/ai_api_client_sdk \
		packages/base/ai_api_client_sdk/helpers
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/core \
		packages/core/ai_core_sdk \
		packages/core/ai_core_sdk/helpers \
		packages/core/ai_core_sdk/cli.py
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/gen \
		packages/proxy/gen_ai_hub \
		packages/openai/gen_ai_hub \
		packages/amazon/gen_ai_hub \
		packages/google/gen_ai_hub \
		packages/rpt/gen_ai_hub \
		packages/orchestration/gen_ai_hub \
		packages/prompt-registry/gen_ai_hub \
		packages/document-grounding/gen_ai_hub \
		packages/batch/gen_ai_hub \
		packages/evaluations/gen_ai_hub \
		packages/evaluations/gen_ai_hub/evaluations/_internal \
		packages/evaluations/gen_ai_hub/evaluations/helpers
	uv run sphinx-build -b html docs/sphinx api-docs/

lint:
	uv run pylint ai_api_client_sdk ai_core_sdk gen_ai_hub --errors-only --output-format=colorized

license-check:
	uv run pip-licenses

sample-code-server:
	uv run uvicorn sample_code.server:app --env-file sample-code/.env --reload

PACKAGES = base core proxy openai amazon google rpt orchestration prompt-registry document-grounding batch evaluations gen

test:
	@for pkg in $(PACKAGES); do \
		echo "=== pytest packages/$$pkg/tests ==="; \
		uv run pytest packages/$$pkg/tests || exit $$?; \
	done

test-integration:
	@for pkg in $(PACKAGES); do \
		echo "=== pytest packages/$$pkg/integration_tests ==="; \
		uv run pytest packages/$$pkg/integration_tests || exit $$?; \
	done

test-pkg:
	uv run pytest packages/$(pkg)/tests

test-pkg-integration:
	uv run pytest packages/$(pkg)/integration_tests
