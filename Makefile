install:
	uv sync --all-packages --all-extras

test:
	uv run pytest

test-pkg:
	uv run pytest packages/$(pkg)/tests
