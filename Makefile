install:
	uv sync --all-packages --all-extras

test:
	uv run pytest -c pytest-unit.toml

test-integration:
	uv run pytest -c pytest-integration.toml

test-pkg:
	uv run pytest packages/$(pkg)/tests

test-pkg-integration:
	uv run pytest packages/$(pkg)/integration_tests
