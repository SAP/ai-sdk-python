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
		-o docs/sphinx/_autogen/proxy \
		packages/proxy/sap_ai_sdk_proxy
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/langchain \
		packages/langchain/sap_ai_sdk_langchain
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/amazon \
		packages/amazon/sap_ai_sdk_amazon
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/google \
		packages/google/sap_ai_sdk_google
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/orchestration \
		packages/orchestration/sap_ai_sdk_orchestration
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/prompt-registry \
		packages/prompt-registry/sap_ai_sdk_prompt_registry
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/document-grounding \
		packages/document-grounding/sap_ai_sdk_document_grounding
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/batch \
		packages/batch/sap_ai_sdk_batch
	uv run sphinx-apidoc -e -M -f -T \
		-o docs/sphinx/_autogen/evaluations \
		packages/evaluations/sap_ai_sdk_evaluations \
		packages/evaluations/sap_ai_sdk_evaluations/_internal \
		packages/evaluations/sap_ai_sdk_evaluations/helpers
	uv run sphinx-build -b html docs/sphinx api-docs/

lint:
	uv run pylint ai_api_client_sdk ai_core_sdk sap_ai_sdk_proxy sap_ai_sdk_langchain sap_ai_sdk_amazon sap_ai_sdk_google sap_ai_sdk_orchestration sap_ai_sdk_prompt_registry sap_ai_sdk_document_grounding sap_ai_sdk_batch sap_ai_sdk_evaluations --errors-only --output-format=colorized

license-check:
	uv run pip-licenses

sample-code-server:
	uv run uvicorn sample_code.server:app --env-file sample-code/.env --reload

test:
	uv run pytest packages/base/tests
	uv run pytest packages/core/tests
	uv run pytest packages/proxy/tests
	uv run pytest packages/langchain/tests
	uv run pytest packages/amazon/tests
	uv run pytest packages/google/tests
	uv run pytest packages/orchestration/tests
	uv run pytest packages/prompt-registry/tests
	uv run pytest packages/document-grounding/tests
	uv run pytest packages/batch/tests
	uv run pytest packages/evaluations/tests

test-integration:
	uv run pytest packages/base/integration_tests
	uv run pytest packages/core/integration_tests
	uv run pytest packages/proxy/integration_tests
	uv run pytest packages/langchain/integration_tests
	uv run pytest packages/amazon/integration_tests
	uv run pytest packages/google/integration_tests
	uv run pytest packages/orchestration/integration_tests
	uv run pytest packages/prompt-registry/integration_tests
	uv run pytest packages/document-grounding/integration_tests
	uv run pytest packages/batch/integration_tests
	uv run pytest packages/evaluations/integration_tests

test-pkg:
	uv run pytest packages/$(pkg)/tests

test-pkg-integration:
	uv run pytest packages/$(pkg)/integration_tests
