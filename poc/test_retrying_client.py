"""
poc/test_retrying_client.py
---------------------------
Validate that _RetryingClient(httpx2.Client) reproduces the exact retry
semantics of urllib3.Retry used in rest_client.py:

    Retry(
        total            = num_request_retries,
        status           = num_request_retries,
        backoff_factor   = 0.1,
        status_forcelist = [429, 500, 502, 503, 504],
    )

Scenarios:
  1. 200 on first attempt  → 1 call, response returned
  2. 500 then 200          → 2 calls, final 200 returned
  3. 429 × N then 200      → N+1 calls, final 200 returned
  4. 500 × (N+1)           → N+1 calls, last response returned (exhausted)
  5. ConnectError then 200 → 2 calls, response returned
  6. ConnectError × (N+1)  → N+1 calls, exception raised
  7. Backoff timing        → delays increase as backoff_factor * 2**attempt
"""
import sys
import time
import httpx2

# ---------------------------------------------------------------------------
# The class under test — exact copy of what will go into rest_client.py
# ---------------------------------------------------------------------------
_STATUS_FORCELIST = frozenset({429, 500, 502, 503, 504})
_BACKOFF_FACTOR   = 0.1


class _RetryingClient(httpx2.Client):
    """
    Drop-in replacement for requests.Session() + HTTPAdapter(max_retries=Retry(...)).

    Retries on:
      - HTTP status codes in status_forcelist  (≡ Retry.status_forcelist)
      - httpx2.RequestError (network / connect) (≡ Retry.connect / Retry.read)

    Backoff: backoff_factor * 2**attempt  (≡ urllib3 backoff_factor formula)
    """

    def __init__(self, *, num_retries: int, backoff_factor: float,
                 status_forcelist: frozenset, **kwargs):
        super().__init__(**kwargs)
        self._num_retries    = num_retries
        self._backoff_factor = backoff_factor
        self._status_forcelist = status_forcelist

    def request(self, method, url, **kwargs):
        last_response = None
        for attempt in range(self._num_retries + 1):
            try:
                response = super().request(method, url, **kwargs)
                if response.status_code in self._status_forcelist:
                    last_response = response
                    if attempt < self._num_retries:
                        time.sleep(self._backoff_factor * (2 ** attempt))
                        continue
                    return last_response      # exhausted — return final response
                return response               # success
            except httpx2.RequestError:
                if attempt == self._num_retries:
                    raise                     # exhausted — propagate
                time.sleep(self._backoff_factor * (2 ** attempt))
        return last_response                  # unreachable; satisfies type checker


# ---------------------------------------------------------------------------
# Transport helpers
# ---------------------------------------------------------------------------
import json as _json

def _resp(status: int, body: dict = None) -> httpx2.Response:
    body = body or {}
    return httpx2.Response(
        status_code=status,
        headers={"content-type": "application/json"},
        content=_json.dumps(body).encode(),
    )


class _SequenceTransport(httpx2.BaseTransport):
    """Serves responses from a fixed sequence, then raises on overrun."""
    def __init__(self, responses):
        self._seq   = list(responses)
        self._calls = 0

    def handle_request(self, request):
        if self._calls >= len(self._seq):
            raise AssertionError(f"Unexpected extra call #{self._calls + 1}")
        resp = self._seq[self._calls]
        self._calls += 1
        if isinstance(resp, Exception):
            raise resp
        return resp


def _make_client(responses, num_retries=3):
    return _RetryingClient(
        transport=_SequenceTransport(responses),
        num_retries=num_retries,
        backoff_factor=0,           # 0 so tests don't actually sleep
        status_forcelist=_STATUS_FORCELIST,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_success_no_retry():
    with _make_client([_resp(200)]) as c:
        r = c.request("GET", "https://x.com/")
    assert r.status_code == 200
    assert c._transport._calls == 1
    print("  ✓ 200 on first attempt → 1 call, no retry")


def test_retry_500_then_200():
    with _make_client([_resp(500), _resp(200)]) as c:
        r = c.request("GET", "https://x.com/")
    assert r.status_code == 200
    assert c._transport._calls == 2
    print("  ✓ 500 → 200 → 2 calls, final 200 returned")


def test_retry_429_then_200():
    with _make_client([_resp(429), _resp(429), _resp(200)]) as c:
        r = c.request("GET", "https://x.com/")
    assert r.status_code == 200
    assert c._transport._calls == 3
    print("  ✓ 429, 429 → 200 → 3 calls, final 200 returned")


def test_status_exhausted_returns_last_response():
    # 4 calls (1 + 3 retries), all 500 → return last response, don't raise
    with _make_client([_resp(500)] * 4, num_retries=3) as c:
        r = c.request("GET", "https://x.com/")
    assert r.status_code == 500
    assert c._transport._calls == 4
    print("  ✓ 500 × 4 (retries=3) → returns last 500 response, no exception")


def test_connect_error_then_200():
    with _make_client([httpx2.ConnectError("refused"), _resp(200)]) as c:
        r = c.request("GET", "https://x.com/")
    assert r.status_code == 200
    assert c._transport._calls == 2
    print("  ✓ ConnectError → 200 → 2 calls, recovered")


def test_connect_error_exhausted_raises():
    errors = [httpx2.ConnectError("refused")] * 4
    try:
        with _make_client(errors, num_retries=3) as c:
            c.request("GET", "https://x.com/")
        assert False, "should have raised"
    except httpx2.ConnectError:
        pass
    assert c._transport._calls == 4
    print("  ✓ ConnectError × 4 (retries=3) → raises ConnectError after exhaustion")


def test_non_forcelist_status_not_retried():
    # 404 is not in forcelist → returned immediately, no retry
    with _make_client([_resp(404)], num_retries=3) as c:
        r = c.request("GET", "https://x.com/")
    assert r.status_code == 404
    assert c._transport._calls == 1
    print("  ✓ 404 (not in forcelist) → returned immediately, 1 call")


def test_backoff_timing():
    """Verify delay = backoff_factor * 2**attempt."""
    delays = []
    _real_sleep = time.sleep

    def _fake_sleep(s):
        delays.append(s)

    import unittest.mock as mock
    factor = 0.1
    responses = [_resp(503), _resp(503), _resp(200)]

    with mock.patch("time.sleep", side_effect=_fake_sleep):
        client = _RetryingClient(
            transport=_SequenceTransport(responses),
            num_retries=3,
            backoff_factor=factor,
            status_forcelist=_STATUS_FORCELIST,
        )
        with client:
            client.request("GET", "https://x.com/")

    # attempt 0 → sleep(0.1 * 1 = 0.1), attempt 1 → sleep(0.1 * 2 = 0.2)
    assert delays == [factor * (2**0), factor * (2**1)], f"got {delays}"
    print(f"  ✓ backoff delays {delays} == [factor*2^0, factor*2^1] = [{factor*1}, {factor*2}]")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== POC 2: _RetryingClient semantics ===")
    tests = [
        test_success_no_retry,
        test_retry_500_then_200,
        test_retry_429_then_200,
        test_status_exhausted_returns_last_response,
        test_connect_error_then_200,
        test_connect_error_exhausted_raises,
        test_non_forcelist_status_not_retried,
        test_backoff_timing,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            import traceback
            print(f"  ✗ {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{'All tests passed.' if not failed else f'{failed} test(s) FAILED.'}")
    sys.exit(failed)
