# Contribution Guidelines

These guidelines are maintained by repo owners and distilled from real PR feedback. They cover review conventions, coding conventions, and best practices that apply broadly across this codebase.

---

## Code Review Comment Labels

Use a prefix tag on every review comment to signal its weight:

| Tag | Meaning |
|-----|---------|
| `req` | Request changes — this must be addressed before merge |
| `pp` | Personal preference — nice to have, not a blocker |
| `q` | Question — something unclear, may or may not require a change |

Tags can be combined, e.g. `[q/pp]`.

---

## Naming Conventions

### Environment variable constants

Name constants after the variable they hold, not after their role. Prefer the pattern `ENV_VAR_<NAME>` so that the name is self-describing and autocomplete is unambiguous.

```python
# preferred
ENV_VAR_AICORE_HOME = f'{AI_CORE_PREFIX}_HOME'
ENV_VAR_AICORE_PROFILE = f'{AI_CORE_PREFIX}_PROFILE'
ENV_VAR_AICORE_SERVICE_KEY = f'{AI_CORE_PREFIX}_SERVICE_KEY'

# avoid
HOME_PATH_ENV_VAR = f'{AI_CORE_PREFIX}_HOME'
```

### Functions

A function's name must match what it returns. A function named `_parse_x` must return parsed data, not a callable. If the return type is a callable, reflect that in the name (e.g. `_create_x_getter`).

### Variables

Avoid generic names. Prefer descriptive names that reflect the content:

```python
# preferred
service_key_json_string = os.environ.get(ENV_VAR_AICORE_SERVICE_KEY)

# avoid
raw = os.environ.get(ENV_VAR_AICORE_SERVICE_KEY)
```

---

## Coding Conventions

### Keep changes in scope

Do not include changes unrelated to the PR's stated purpose. Unrelated changes (e.g. adding a new dependency group to `pyproject.toml`) belong in a separate PR.

### Do not make unnecessary changes

Avoid touching lines, files, or formatting that are not required for the change. Unnecessary diffs obscure intent and inflate review effort.

### Always leave a newline at the end of a file

This is a Unix convention. New files and modified files must end with a trailing newline.

### Separate concerns into separate functions

If a function has a parsing/validation step and a logic step, split them. Callers should be able to reuse the parsing step independently.

### Prefer inline over intermediate variables where it aids clarity

When an intermediate variable is only used once and its meaning is clear from the call site, prefer inlining. This is especially useful for default argument captures in lambdas:

```python
# preferred — service_key is captured once at definition time
Source("service key",
       lambda cv, service_key=_load_service_key(): ...)

# avoid — extra assignment with no added clarity
service_key = _load_service_key()
Source("service key",
       lambda cv: ...)
```

### Do not silently swallow exceptions

If an exception is caught and suppressed, log it. Use `debug` level when the suppressed case is expected in normal operation (e.g. an optional field being absent). Use `warning` only when the absence is unusual or worth operator attention.

---

## Comments and Documentation

### Comments must be precise

A comment on a tuple access path must say clearly that the value is a tuple, that it represents an access path, and what the leading element is. Vague references like "drop the prefix" are not sufficient.

```python
# preferred
# `vcap_key` is a tuple representing the access path to properties such as
# `clientid` in the `aicore` service binding, e.g. `('credentials', 'clientid')`.
# Skip the leading `credentials` element to access the nested value directly.

# avoid
# vcap_key is e.g. ('credentials', 'clientid') — drop the 'credentials' prefix
```

### Add inline comments on non-obvious source entries

When building a list of `Source` entries with lambda accessors, add a short inline comment explaining any non-obvious transformation, such as path stripping.

---

## Testing

### Use the constant, not the string

In tests, patch environment variables using the imported constant, not a hardcoded string. This ensures the test stays correct if the constant's value changes:

```python
# preferred
with patch.dict(os.environ, {ENV_VAR_AICORE_SERVICE_KEY: json.dumps(service_key)}):

# avoid
with patch.dict(os.environ, {"AICORE_SERVICE_KEY": json.dumps(service_key)}):
```

### Do not add test env vars that are not asserted

If a test patches an environment variable but never asserts on the value it provides, remove it. Unused setup adds noise and misleads future readers.

### Unit tests must not depend on a local `.env` file

Unit tests must pass without any `.env` present. If `pytest-dotenv` is installed, disable auto-loading explicitly in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
env_files = []
```

Integration tests may load `.env` explicitly via `conftest.py`.

---

## Scope Management

If a review surfaces a valid issue that is clearly outside the scope of the current PR, do not fix it inline. Instead:

1. Note it explicitly in the review thread.
2. Open a follow-up issue or backlog item.
3. Reference it from the PR thread.

This keeps PRs focused and avoids scope creep.
