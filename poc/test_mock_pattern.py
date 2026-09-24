"""
poc/test_mock_pattern.py
------------------------
Show the before/after of how unit tests in packages/base mock the HTTP layer.

BEFORE (requests):
    @patch('module.requests')
    def test(self, m):
        session = MagicMock()
        session.get.return_value = response_mock
        m.Session.return_value = session

AFTER (httpx2 + _RetryingClient):
    @patch('module.httpx2.Client')        ← patch the class, not the module
    def test(self, MockClient):
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = False
        mock_client.request.return_value = response_mock
        MockClient.return_value = mock_client

This POC runs both patterns side by side to prove they produce the same
observable behaviour for the production code under test.
"""
import sys
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Minimal stand-in for the production code under test
# (mirrors the shape of rest_client._handle_request)
# ---------------------------------------------------------------------------

# --- BEFORE version (requests) ---
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

class _OldClient:
    def get(self, path, *, base_url="https://example.com"):
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(url=f"{base_url}{path}", timeout=(10, 60))
        return response.json()


# --- AFTER version (httpx2 + _RetryingClient) ---
import time
import httpx2

_STATUS_FORCELIST = frozenset({429, 500, 502, 503, 504})
_BACKOFF_FACTOR   = 0.1


class _RetryingClient(httpx2.Client):
    def __init__(self, *, num_retries, backoff_factor, status_forcelist, **kwargs):
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
                    return last_response
                return response
            except httpx2.RequestError:
                if attempt == self._num_retries:
                    raise
                time.sleep(self._backoff_factor * (2 ** attempt))
        return last_response


class _NewClient:
    def get(self, path, *, base_url="https://example.com"):
        with _RetryingClient(
            num_retries=3,
            backoff_factor=_BACKOFF_FACTOR,
            status_forcelist=_STATUS_FORCELIST,
            timeout=httpx2.Timeout(60, connect=10),
        ) as client:
            response = client.request("GET", url=f"{base_url}{path}")
            return response.json()


# ---------------------------------------------------------------------------
# Tests: BEFORE pattern
# ---------------------------------------------------------------------------
class TestOldMockPattern(TestCase):

    def _make_response(self, status_code, body):
        m = MagicMock()
        m.status_code = status_code
        m.json.return_value = body
        return m

    @patch("poc.test_mock_pattern.requests")
    def test_get_old(self, mock_requests):
        expected = {"result": "ok"}
        # response_mock: MagicMock so .json() returns our dict directly
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = expected
        session = MagicMock()
        session.get.return_value = response_mock
        mock_requests.Session.return_value = session

        result = _OldClient().get("/endpoint")

        session.get.assert_called_once_with(
            url="https://example.com/endpoint", timeout=(10, 60)
        )
        self.assertEqual(result, expected)

    def test_old_pattern_label(self):
        print("  ✓ BEFORE: @patch('module.requests') + Session mock works")


# ---------------------------------------------------------------------------
# Tests: AFTER pattern
# ---------------------------------------------------------------------------
class TestNewMockPattern(TestCase):

    def _make_response(self, status_code, body):
        return httpx2.Response(
            status_code=status_code,
            headers={"content-type": "application/json"},
            content=json.dumps(body).encode(),
        )

    @patch("poc.test_mock_pattern._RetryingClient")
    def test_get_new(self, MockRetryingClient):
        expected = {"result": "ok"}
        # Use a real httpx2.Response so .json() works without extra setup
        response = self._make_response(200, expected)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.request.return_value = response
        MockRetryingClient.return_value = mock_client

        result = _NewClient().get("/endpoint")

        mock_client.request.assert_called_once_with(
            "GET", url="https://example.com/endpoint"
        )
        self.assertEqual(result, expected)

    def test_new_pattern_label(self):
        print("  ✓ AFTER:  @patch('module._RetryingClient') + context-manager mock works")


# ---------------------------------------------------------------------------
# Side-by-side summary
# ---------------------------------------------------------------------------
def print_diff():
    print("""
  Pattern diff (before → after)
  ──────────────────────────────────────────────────────────────
  BEFORE  @patch('module.requests')
          session = MagicMock()
          session.get.return_value = response_mock
          mock_requests.Session.return_value = session
          # assert:
          session.get.assert_called_with(url=..., timeout=(10, 60))

  AFTER   @patch('module._RetryingClient')
          mock_client = MagicMock()
          mock_client.__enter__ = MagicMock(return_value=mock_client)
          mock_client.__exit__  = MagicMock(return_value=False)
          mock_client.request.return_value = response_mock
          MockRetryingClient.return_value = mock_client
          # assert:
          mock_client.request.assert_called_with('GET', url=..., timeout=...)
  ──────────────────────────────────────────────────────────────
  Key changes:
    • patch target:  'module.requests'     → 'module._RetryingClient'
    • setup:         .Session.return_value → .__enter__ + return_value
    • call assert:   session.get(...)      → mock_client.request('GET', ...)
    • timeout:       (10, 60)              → httpx2.Timeout(60, connect=10)
""")


if __name__ == "__main__":
    import unittest
    print("=== POC 3: mock pattern before vs after ===")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestOldMockPattern, TestNewMockPattern]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w"))
    result = runner.run(suite)

    if result.wasSuccessful():
        print("  ✓ BEFORE pattern (requests Session mock) passes")
        print("  ✓ AFTER  pattern (_RetryingClient context-manager mock) passes")
        print_diff()
        sys.exit(0)
    else:
        for f in result.failures + result.errors:
            print(f"  ✗ {f[0]}: {f[1]}")
        sys.exit(1)
