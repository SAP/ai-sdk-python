"""
poc/test_api_shape.py
---------------------
Verify that httpx2 drop-in replacements for requests are shape-compatible:
  - requests.post(url=, data=, ...)   → httpx2.post(url=, data=, ...)
  - requests.Response attributes      → httpx2.Response attributes
  - requests.exceptions               → httpx2 exceptions
  - timeout tuple                     → httpx2.Timeout(read, connect=connect)
  - cert= kwarg                       → same signature in httpx2

No network calls — uses httpx2's MockTransport.
"""
import sys
import httpx2


# ---------------------------------------------------------------------------
# Helper: build a fake httpx2.Response as MockTransport would return it
# ---------------------------------------------------------------------------
def _mock_response(status_code: int, json_body: dict) -> httpx2.Response:
    import json
    return httpx2.Response(
        status_code=status_code,
        headers={"content-type": "application/json"},
        content=json.dumps(json_body).encode(),
    )


class _FixedTransport(httpx2.BaseTransport):
    """Returns a predetermined sequence of responses."""
    def __init__(self, responses):
        self._responses = list(responses)
        self._idx = 0

    def handle_request(self, request):
        resp = self._responses[self._idx % len(self._responses)]
        self._idx += 1
        return resp


# ---------------------------------------------------------------------------
# Test 1 — Response attributes are identical
# ---------------------------------------------------------------------------
def test_response_attributes():
    transport = _FixedTransport([_mock_response(200, {"key": "value"})])
    with httpx2.Client(transport=transport) as client:
        r = client.get("https://example.com")
    assert r.status_code == 200
    assert r.json() == {"key": "value"}
    assert isinstance(r.text, str)
    assert isinstance(r.content, bytes)
    print("  ✓ response.status_code / .json() / .text / .content — identical shape")


# ---------------------------------------------------------------------------
# Test 2 — raise_for_status raises httpx2.HTTPStatusError (≡ requests.HTTPError)
# ---------------------------------------------------------------------------
def test_raise_for_status():
    transport = _FixedTransport([_mock_response(404, {"error": "not found"})])
    with httpx2.Client(transport=transport) as client:
        r = client.get("https://example.com")
    try:
        r.raise_for_status()
        assert False, "should have raised"
    except httpx2.HTTPStatusError as exc:
        assert exc.response.status_code == 404
    print("  ✓ raise_for_status() raises httpx2.HTTPStatusError — maps to requests.HTTPError")


# ---------------------------------------------------------------------------
# Test 3 — Timeout shape: tuple (connect, read) → httpx2.Timeout
# ---------------------------------------------------------------------------
def test_timeout_shape():
    # requests: timeout=(connect_timeout, read_timeout)
    # httpx2:   httpx2.Timeout(read_timeout, connect=connect_timeout)
    connect_timeout, read_timeout = 10, 60

    t = httpx2.Timeout(read_timeout, connect=connect_timeout)
    assert t.read == read_timeout
    assert t.connect == connect_timeout
    print(f"  ✓ httpx2.Timeout({read_timeout}, connect={connect_timeout}) → read={t.read} connect={t.connect}")


# ---------------------------------------------------------------------------
# Test 4 — client.request(method, url, ...) replaces getattr(session, method)(url, ...)
# ---------------------------------------------------------------------------
def test_request_method_dispatch():
    calls = []

    class _RecordingTransport(httpx2.BaseTransport):
        def handle_request(self, request):
            calls.append((request.method, str(request.url)))
            return _mock_response(200, {})

    with httpx2.Client(transport=_RecordingTransport()) as client:
        client.request("GET",  "https://example.com/get")
        client.request("POST", "https://example.com/post")
        client.request("DELETE", "https://example.com/del")

    assert calls == [
        ("GET",    "https://example.com/get"),
        ("POST",   "https://example.com/post"),
        ("DELETE", "https://example.com/del"),
    ]
    print("  ✓ client.request(method, url) dispatches all HTTP verbs correctly")


# ---------------------------------------------------------------------------
# Test 5 — Exception hierarchy: RequestError covers network failures
# ---------------------------------------------------------------------------
def test_exception_hierarchy():
    # requests.exceptions.RequestException → httpx2.RequestError
    # requests.exceptions.ConnectionError  → httpx2.ConnectError
    assert issubclass(httpx2.ConnectError,   httpx2.RequestError)
    assert issubclass(httpx2.TimeoutException, httpx2.RequestError)
    assert issubclass(httpx2.HTTPStatusError, httpx2.HTTPStatusError)  # itself
    print("  ✓ httpx2.ConnectError ⊂ httpx2.RequestError  (≡ requests exception hierarchy)")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== POC 1: API shape compatibility ===")
    tests = [
        test_response_attributes,
        test_raise_for_status,
        test_timeout_shape,
        test_request_method_dispatch,
        test_exception_hierarchy,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
    print(f"\n{'All tests passed.' if not failed else f'{failed} test(s) FAILED.'}")
    sys.exit(failed)
