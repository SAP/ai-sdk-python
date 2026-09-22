#!/usr/bin/env bash
# =============================================================================
# poc2.sh — PoC 2: Minor version migration — prefer httpx2, fall back to httpx
#
# Strategy: inline try/except in every module. Code always reads httpx2.X.
#   On import, the try/except establishes 'httpx2' as the module name:
#
#     Files with "import httpx":
#       try:
#           import httpx2
#       except ModuleNotFoundError:
#           import httpx as httpx2  # type: ignore[no-redef]
#           import warnings
#           warnings.warn("httpx is deprecated; install httpx2 instead.",
#                         DeprecationWarning, stacklevel=1)
#
#     Files with "from httpx import X, Y" only:
#       try:
#           from httpx2 import X, Y
#       except ModuleNotFoundError:
#           import warnings
#           warnings.warn(...)
#           from httpx import X, Y  # type: ignore[no-redef]
#
#     Files with BOTH "import httpx" AND "from httpx import X":
#       → bare import gets the try/except block (as above)
#       → from-import becomes "X = httpx2.X" (uses the resolved name)
#
#   Body references: httpx.X → httpx2.X everywhere.
#   ssl/certifi: regular top-level imports (not inside try/except).
#   @patch: @patch('httpx.X') → @patch('httpx2.X').
#   respx: same migration as PoC 1 (respx → httpx2-pytest; mock.py: _HTTPXMock wrapper; e2e: import from tests.mock).
#
# Usage: bash poc2.sh   (idempotent — resets branch if it already exists)
# =============================================================================
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
BRANCH="poc/httpx2-minor"
GEN="$REPO/packages/gen"
PYPROJECT="$GEN/pyproject.toml"

echo "======================================================"
echo " PoC 2 — httpx2 minor migration (try/except fallback)"
echo " repo   : $REPO"
echo " branch : $BRANCH"
echo "======================================================"

# ── 1. Clean state guarantee ─────────────────────────────────────────────────
cd "$REPO"

# ── 3 & 4. Python transformation ─────────────────────────────────────────────
echo "--- Transforming Python source files ---"
export GEN
python3 << 'PYEOF'
import re, os, sys, textwrap

GEN = os.environ["GEN"]

# ── SSL utility module (identical to PoC 1) ───────────────────────────────────
SSL_MODULE = os.path.join(GEN, "gen_ai_hub/_ssl.py")
SSL_CONTENT = textwrap.dedent("""\
    \"\"\"
    Shared SSL context factory for httpx2 clients.

    httpx2 defaults to the OS trust store (truststore). This module preserves
    the pre-migration behaviour of using certifi's CA bundle so existing
    deployments are not affected. Switch callers to verify=True to adopt the
    httpx2 default when ready.
    \"\"\"
    import ssl
    import certifi


    def default_ssl_context() -> ssl.SSLContext:
        \"\"\"Return an SSL context backed by certifi's CA bundle.\"\"\"
        return ssl.create_default_context(cafile=certifi.where())
""")
with open(SSL_MODULE, "w") as f:
    f.write(SSL_CONTENT)
print(f"  ✓ created gen_ai_hub/_ssl.py")

# ── Config ────────────────────────────────────────────────────────────────────
CLIENT_FILES = {
    os.path.join(GEN, "gen_ai_hub/proxy/native/sap/client.py"),
    os.path.join(GEN, "gen_ai_hub/batch_service/service.py"),
    os.path.join(GEN, "gen_ai_hub/orchestration_v2/service.py"),
    os.path.join(GEN, "gen_ai_hub/orchestration/service.py"),
}

RESPX_FILES = {
    os.path.join(GEN, "tests/mock.py"),
    os.path.join(GEN, "tests/proxy/gen_ai_hub_proxy/test_additional_header_e2e.py"),
}

# ── try/except blocks ─────────────────────────────────────────────────────────
IMPORT_BLOCK = textwrap.dedent("""\
    try:
        import httpx2
    except ModuleNotFoundError:
        import httpx as httpx2  # type: ignore[no-redef]
        import warnings
        warnings.warn(
            "httpx is deprecated; install httpx2 instead.",
            DeprecationWarning,
            stacklevel=1,
        )""")


def from_block(names_str):
    """try/except block for 'from httpx import <names_str>'."""
    return textwrap.dedent(f"""\
        try:
            from httpx2 import {names_str}
        except ModuleNotFoundError:
            import warnings
            warnings.warn(
                "httpx is deprecated; install httpx2 instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            from httpx import {names_str}  # type: ignore[no-redef]""")


# ── respx helpers (shared with PoC 1) ────────────────────────────────────────
def find_close(s, start):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1


def transform_respx_stmt(full_stmt, indent):
    stmt = full_stmt.strip()
    m = re.match(r'(?:\w+\s*=\s*)?respx\.(post|get|put|patch|delete|head)\(', stmt)
    if not m:
        return indent + stmt

    method = m.group(1).upper()
    url_open = m.end() - 1
    url_close = find_close(stmt, url_open)
    if url_close == -1:
        return indent + "# TODO(respx→httpx2): " + stmt
    url = stmt[url_open + 1:url_close].strip()

    rest = stmt[url_close + 1:]
    mock_m = re.match(r'\s*\.mock\(', rest)
    if not mock_m:
        return indent + "# TODO(respx→httpx2): " + stmt

    mock_open = len(rest[:mock_m.end()]) - 1
    mock_close = find_close(rest, mock_open)
    if mock_close == -1:
        return indent + "# TODO(respx→httpx2): " + stmt
    mock_inner = rest[mock_m.end():mock_close].strip()

    rv_m = re.match(r'return_value\s*=\s*Response\(', mock_inner)
    if rv_m:
        resp_open = rv_m.end() - 1
        resp_close = find_close(mock_inner, resp_open)
        if resp_close == -1:
            return indent + "# TODO(respx→httpx2): " + stmt
        resp_inner = mock_inner[resp_open + 1:resp_close]

        depth = 0
        first_comma = -1
        for i, ch in enumerate(resp_inner):
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            elif ch == ',' and depth == 0:
                first_comma = i
                break

        if first_comma == -1:
            status = resp_inner.strip()
            extra = ''
        else:
            status = resp_inner[:first_comma].strip()
            extra = resp_inner[first_comma + 1:].strip()

        # Wrap bare sync generators passed as stream= in IteratorStream so
        # that pytest_httpx2/httpx2.Response can consume them correctly.
        if extra:
            extra = re.sub(
                r'stream=(?!\w*[Ss]tream\()(.+)',
                lambda mo: 'stream=IteratorStream(' + mo.group(1) + ')',
                extra,
            )

        args = f'url={url}, method="{method}", status_code={status}'
        if extra:
            args += f', {extra}'
        return f'{indent}_mock.add_response({args})'

    se_m = re.match(r'side_effect\s*=\s*(.+)', mock_inner)
    if se_m:
        return f'{indent}_mock.add_callback({se_m.group(1).strip()}, url={url}, method="{method}")'

    return indent + "# TODO(respx→httpx2): " + stmt


def transform_respx(content, path):
    lines = content.splitlines(keepends=True)
    result = []
    _route_vars = set()  # variable names assigned from respx route calls
    i = 0
    while i < len(lines):
        line = lines[i]
        raw = line.rstrip('\n')

        if re.match(r'^\s*import respx\s*$', raw):
                ind = re.match(r'^(\s*)', raw).group(1)
                if path == os.path.join(GEN, 'tests/mock.py'):
                    # mock.py: emit the full standalone _HTTPXMock context-manager class.
                    # It wraps pytest_httpx2.HTTPXMock (from the httpx2-pytest package)
                    # so that unittest.TestCase helpers can use it without a pytest fixture.
                    wrapper = textwrap.dedent('''
                        import httpx2 as _httpx2_mod
                        from pytest_httpx2 import HTTPXMock as _HTTPXMockBase
                        from pytest_httpx2._options import _HTTPXMockOptions
                        from pytest_httpx2._httpx_internals import IteratorStream


                        class _HTTPXMock:
                            """
                            Standalone context manager wrapping HTTPXMock for use inside
                            unittest.TestCase and @contextmanager helpers that cannot receive
                            pytest fixtures.

                            Patches httpx2.HTTPTransport / httpx2.AsyncHTTPTransport for the
                            duration of the ``with`` block, then restores the originals and
                            asserts all registered responses were consumed (matching the
                            default fixture behaviour).
                            """

                            def __init__(
                                self,
                                *,
                                assert_all_responses_were_requested: bool = True,
                                assert_all_requests_were_expected: bool = True,
                                can_send_already_matched_responses: bool = True,
                            ) -> None:
                                options = _HTTPXMockOptions(
                                    assert_all_responses_were_requested=assert_all_responses_were_requested,
                                    assert_all_requests_were_expected=assert_all_requests_were_expected,
                                    can_send_already_matched_responses=can_send_already_matched_responses,
                                )
                                self._mock = _HTTPXMockBase(options)
                                self._real_handle_request = None
                                self._real_handle_async_request = None

                            # --- public API (delegated to _HTTPXMockBase) ---

                            def add_response(self, **kwargs):
                                self._mock.add_response(**kwargs)

                            def add_callback(self, callback, **kwargs):
                                self._mock.add_callback(callback, **kwargs)

                            # --- context manager ---

                            def __enter__(self):
                                mock = self._mock
                                options = mock._options
                                self._real_handle_request = _httpx2_mod.HTTPTransport.handle_request
                                self._real_handle_async_request = _httpx2_mod.AsyncHTTPTransport.handle_async_request
                                _real_sync = self._real_handle_request
                                _real_async = self._real_handle_async_request

                                def _mocked_sync(transport, request):
                                    if options.should_mock(request):
                                        return mock._handle_request(transport, request)
                                    return _real_sync(transport, request)

                                async def _mocked_async(transport, request):
                                    if options.should_mock(request):
                                        return await mock._handle_async_request(transport, request)
                                    return await _real_async(transport, request)

                                _httpx2_mod.HTTPTransport.handle_request = _mocked_sync
                                _httpx2_mod.AsyncHTTPTransport.handle_async_request = _mocked_async
                                return self

                            def __exit__(self, *exc_info):
                                _httpx2_mod.HTTPTransport.handle_request = self._real_handle_request
                                _httpx2_mod.AsyncHTTPTransport.handle_async_request = self._real_handle_async_request
                                if exc_info[0] is None:
                                    self._mock._assert_options()
                                self._mock.reset()
                    ''').strip()
                    # Indent the entire class block to match the surrounding heredoc indentation
                    indented = '\n'.join((ind + line).rstrip() if line else '' for line in wrapper.splitlines())
                    result.append(indented + '\n')
                else:
                    # Other RESPX_FILES: import _HTTPXMock from tests.mock (defined there).
                    result.append(ind + 'from tests.mock import _HTTPXMock as _HTTPXMock\n')
                i += 1
                continue

        if re.match(r'^(\s*)with respx\.mock:\s*$', raw):
            ind = re.match(r'^(\s*)', raw).group(1)
            result.append(f'{ind}with _HTTPXMock() as _mock:\n')
            i += 1
            continue

        if re.search(r'\brespx\.(post|get|put|patch|delete|head)\(', raw):
            stmt_lines = [raw]
            open_parens = raw.count('(') - raw.count(')')
            while open_parens > 0 and i + 1 < len(lines):
                i += 1
                nxt = lines[i].rstrip('\n')
                stmt_lines.append(nxt)
                open_parens += nxt.count('(') - nxt.count(')')
            full = ' '.join(l.strip() for l in stmt_lines)
            indent = re.match(r'^(\s*)', stmt_lines[0]).group(1)
            var_m = re.match(r'\s*(\w+)\s*=\s*respx\.', full)
            if var_m:
                _route_vars.add(var_m.group(1))
            result.append(transform_respx_stmt(full, indent) + '\n')
            i += 1
            continue

        # Replace 'yield <var>' ONLY when <var> was a respx route variable
        # (tracked when we strip 'var = respx.METHOD(...)' assignments).
        m_yield = re.match(r'^(\s*)yield\s+(\w+)\s*$', raw)
        if m_yield and m_yield.group(2) in _route_vars:
            result.append(f'{m_yield.group(1)}yield _mock\n')
            i += 1
            continue
        result.append(line)
        i += 1
    return ''.join(result)


def has_import(content, name):
    """True if 'import <name>' or 'from <name> import' already present."""
    return bool(re.search(rf'^\s*(?:import {re.escape(name)}|from {re.escape(name)} import)',
                          content, re.MULTILINE))


# ── Main file transformer ─────────────────────────────────────────────────────
def transform_file(path):
    with open(path) as f:
        original = f.read()
    content = original

    # ── respx → httpx2-pytest ─────────────────────────────────────────────────
    if path in RESPX_FILES:
        content = transform_respx(content, path)

    # ── openai/cohere mockers: regex URL to ignore query params ──────────────
    # pytest_httpx2 does strict query-param matching (unlike respx which was
    # URL-permissive). The OpenAI proxy appends ?api-version=... (and potentially
    # other params) to every request. Using re.compile matches the base URL and
    # ignores any query string, keeping tests future-proof with no hardcoded version.
    if path == os.path.join(GEN, 'tests/mock.py'):
        content = re.sub(
            r'(def (?:openai|cohere)_\w+_mocker\([^)]*\):.*?_mock\.add_response\()url=deployment_url,',
            lambda m: m.group(1) + r"url=(re.compile(re.escape(deployment_url) + r'(\?.*)?$') if deployment_url else None),",
            content,
            flags=re.DOTALL,
        )
        if not has_import(content, 're'):
            content = re.sub(r'^(import asyncio\n)', r'import re\n\1', content, flags=re.MULTILINE)


    # Detect import patterns in the (possibly respx-transformed) content
    has_bare_import = bool(re.search(r'^import httpx$', content, re.MULTILINE))
    from_imports = re.findall(r'^from httpx import (.+)$', content, re.MULTILINE)

    # ── import httpx → try/except block ───────────────────────────────────────
    if has_bare_import:
        content = re.sub(r'^import httpx$', IMPORT_BLOCK, content, flags=re.MULTILINE)
        # from httpx import X → X = httpx2.X  (httpx2 is now defined above)
        for names_str in from_imports:
            names = [n.strip() for n in names_str.split(',')]
            assignments = '\n'.join(f'{n} = httpx2.{n}' for n in names)
            content = re.sub(
                rf'^from httpx import {re.escape(names_str)}$',
                assignments,
                content,
                flags=re.MULTILINE,
            )
    elif from_imports:
        # Only from-imports, no bare import httpx
        for names_str in from_imports:
            content = re.sub(
                rf'^from httpx import {re.escape(names_str)}$',
                from_block(names_str),
                content,
                flags=re.MULTILINE,
            )

    # ── httpx. in body → httpx2. ─────────────────────────────────────────────
    # \bhttpx\. matches 'httpx.' but NOT 'httpx2.' (word boundary stops at digits)
    content = re.sub(r'\bhttpx\.', 'httpx2.', content)

    # ── Client files: ssl utility + verify= ───────────────────────────────────
    if path in CLIENT_FILES:
        ssl_import = 'from gen_ai_hub._ssl import default_ssl_context'
        if ssl_import not in content:
            # ssl/certifi are NOT needed directly — the utility handles them.
            # Remove if already present at top level to avoid confusion.
            content = re.sub(r'^import ssl\n', '', content, flags=re.MULTILINE)
            content = re.sub(r'^import certifi\n', '', content, flags=re.MULTILINE)
            # Insert ssl_import right after the IMPORT_BLOCK we just inserted.
            # Anchor on the last two lines of IMPORT_BLOCK (8-space / 4-space indentation).
            anchor = '        stacklevel=1,\n    )\n'
            idx = content.find(anchor)
            if idx != -1:
                insert_at = idx + len(anchor)
                content = content[:insert_at] + ssl_import + '\n' + content[insert_at:]
            else:
                # Fallback: insert after 'import httpx2' (bare, non-indented)
                content = re.sub(
                    r'^(import httpx2)$',
                    rf'\1\n{ssl_import}',
                    content, count=1, flags=re.MULTILINE
                )

        verify = 'verify=default_ssl_context()'
        content = re.sub(
            r'httpx2\.Client\(timeout=self\.timeout\)',
            f'httpx2.Client(timeout=self.timeout, {verify})',
            content
        )
        content = re.sub(
            r'httpx2\.AsyncClient\(timeout=self\.timeout\)',
            f'httpx2.AsyncClient(timeout=self.timeout, {verify})',
            content
        )

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        rel = path.replace(os.path.expanduser('~'), '~')
        print(f"  ✓ {rel}")


count = 0
for dirpath, dirnames, filenames in os.walk(GEN):
    dirnames[:] = [d for d in dirnames if d not in ('__pycache__', '.venv', 'api-docs')]
    for fname in filenames:
        if fname.endswith('.py'):
            transform_file(os.path.join(dirpath, fname))
            count += 1

print(f"  Scanned {count} .py files.")
PYEOF

# ── 5. pyproject.toml ────────────────────────────────────────────────────────
echo ""
echo "--- Updating pyproject.toml ---"

sed -i '' 's|"httpx>=0.27.0"|"httpx2>=2.0.0"|' "$PYPROJECT"

if ! grep -q '"certifi"' "$PYPROJECT"; then
    sed -i '' 's|"httpx2>=2.0.0",|"httpx2>=2.0.0",\n    "certifi",|' "$PYPROJECT"
fi

sed -i '' 's|"openai>=1\.66\.0"|"openai>=3.0.0"|' "$PYPROJECT"
sed -i '' 's|"respx==0\.23\.1"|"httpx2-pytest"|' "$PYPROJECT"

echo "  ✓ packages/gen/pyproject.toml"

# ── 6. py_compile check ──────────────────────────────────────────────────────
echo ""
echo "--- Syntax check (py_compile) ---"
SYNTAX_ERRORS=0
while IFS= read -r -d '' pyfile; do
    if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo "  ✗ $pyfile"
        python3 -m py_compile "$pyfile" 2>&1 | sed 's/^/    /'
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done < <(find "$GEN" -name "*.py" -not -path "*/__pycache__/*" -print0)

if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo "  ✓ All .py files pass py_compile."
else
    echo "  ✗ $SYNTAX_ERRORS file(s) with syntax errors."
fi

# ── 7. uv lock ───────────────────────────────────────────────────────────────
echo ""
echo "--- uv lock ---"
cd "$REPO"
uv lock && echo "  ✓ uv.lock updated" || echo "  ⚠ uv lock failed (check deps manually)"

# ── Verification summary ─────────────────────────────────────────────────────
echo ""
echo "=== Verification ==="
REMAINING=$(grep -rEn \
    --exclude-dir=__pycache__ --exclude="*.pyc" \
    '(^import httpx$)|(^from httpx import)' \
    "$GEN" 2>/dev/null || true)
if [ -z "$REMAINING" ]; then
    echo "  ✓ No bare httpx imports remaining."
else
    echo "  ⚠ Remaining:"
    echo "$REMAINING"
fi

echo ""
echo "======================================================"
echo " PoC 2 complete — branch: $BRANCH"
echo " Review: git diff main"
echo "======================================================"
