install:
	pip install \
		-e "packages/ai-api-client-sdk[dev]" \
		-e "packages/ai-core-sdk[dev]" \
		-e "packages/generative-ai-hub-sdk[all,dev]"

test:
	pytest

test-pkg:
	pytest packages/$(pkg)/tests
