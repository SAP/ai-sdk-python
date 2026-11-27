# Coding Tools

## Status

agreed

## Context

The Python SDK currently uses Pylint for CI linting checks. There is no formatter or type checker as part of the CI checks. Therefore, the code base is inconsistently formatted and there are incorrect or missing type annotations.

## Decision

Drop Pylint and use Ruff as both a formatter and a linter. Use pyright for type checking. Ruff and pyright are run in CI.

## Consequences

- Using a formatter consistently enables a readable code base and clean commit diffs
- Using Ruff both as linter and formatter avoids formatting-based linter warnings
- Type checking improves the code quality and may catch bugs
- Initially, there is a cost in introducing the coding tools. The formatter needs to be run over the whole code base and linter/type checker warnings/errors need to be fixed.
- pyright needs Node to run, adding a CI dependency

## Appendix

### Formatter

Ruff is at the time of writing (October 2026) the standard choice of formatter for Python. It is a drop-in replacement for Black but is significantly faster.

### Linter

Ruff and Pylint are the standard choices for linters at the time of writing (October 2026). The main argument for switching to Ruff from Pylint was increased speed and simplification by using one tool for linting and formatting.

### Type Checker

The type checking landscape is more diverse.

- mypy is the oldest type checker, it is however less-used nowadays because there are faster alternatives
- Pyright is a TypeScript-based type checker that is faster than mypy. It is well-integrated into editors and IDEs and is the most common choice for a type checker.
- ty is a newer type checker from Astral (the company that develops uv and ruff). It is significantly faster than Pyright but currently still in beta. It is a less aggressive type checker (removing a type annotation should not lead to type checking errors).
- Pyrefly is a new type checker from Meta (made available in 2025). It is as fast as ty and version 1 is already released. It is currently less-used compared to Pyright and the type checking is aggressive (making switching to it more time-consuming).

Pyright is the most commonly used and most mature type checker. Both ty and Pyrefly are faster though and directly installable from pip. This may make them a better option in the future when they are more established and stable.
