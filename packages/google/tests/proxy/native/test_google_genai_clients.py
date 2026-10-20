import unittest
from unittest.mock import MagicMock, patch
import httpx
from gen_ai_hub.proxy.native.google_genai.clients import (
    _rewrite_request,
    AICoreDynamicTransport,
    AsyncAICoreDynamicTransport,
)

class TestRewriteRequest(unittest.TestCase):
    def setUp(self):
        self.transport_instance = MagicMock()
        self.transport_instance.proxy_client.request_header = {
            "Authorization": "Bearer test-token",
            "Custom-Header": "CustomValue"
        }
        self.transport_instance.proxy_client.select_deployment.return_value = MagicMock(
            url="https://base_url.com/deployment"
        )
        self.transport_instance.get_selector_kwargs.return_value = {}

    def test_rewrite_request_with_valid_model(self):
        request = httpx.Request(
            method="POST",
            url=httpx.URL("https://api.base_url.com/models/test-model:generateContent"),
        )
        modified_request = _rewrite_request(self.transport_instance, request)

        self.assertEqual(modified_request.url.host, "base_url.com")
        self.assertIn("/models/test-model:generateContent", modified_request.url.path)
        self.assertEqual(modified_request.headers["Authorization"], "Bearer test-token")
        self.assertEqual(modified_request.headers["Custom-Header"], "CustomValue")

    def test_rewrite_request_with_discovery_call(self):
        request = httpx.Request(
            method="GET",
            url=httpx.URL("https://api.base_url.com/models/"),
        )
        modified_request = _rewrite_request(self.transport_instance, request)

        self.assertEqual(modified_request.url.host, "api.base_url.com")
        self.assertEqual(modified_request.url.path, "/models/")

class TestAICoreDynamicTransport(unittest.TestCase):
    def setUp(self):
        self.proxy_client = MagicMock()
        self.transport = AICoreDynamicTransport(proxy_client=self.proxy_client)
        self.transport.proxy_client.select_deployment.return_value = MagicMock(
            url="https://base_url.com/deployment"
        )

    @patch("httpx.HTTPTransport.handle_request")
    def test_handle_request(self, mock_handle_request):
        request = httpx.Request(
            method="POST",
            url=httpx.URL("https://api.base_url.com/models/test-model:generateContent"),
        )
        mock_response = httpx.Response(200, text="Success")
        mock_handle_request.return_value = mock_response

        response = self.transport.handle_request(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Success")
        mock_handle_request.assert_called_once()

    def test_close(self):
        with patch.object(self.transport._inner_transport, "close") as mock_close:
            self.transport.close()
            mock_close.assert_called_once()

class TestAsyncAICoreDynamicTransport(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.proxy_client = MagicMock()
        self.transport = AsyncAICoreDynamicTransport(proxy_client=self.proxy_client)
        self.transport.proxy_client.select_deployment.return_value = MagicMock(
            url="https://base_url.com/deployment"
        )

    @patch("httpx.AsyncHTTPTransport.handle_async_request")
    async def test_handle_async_request(self, mock_handle_async_request):
        request = httpx.Request(
            method="POST",
            url=httpx.URL("https://api.base_url.com/models/test-model:generateContent"),
        )
        mock_response = httpx.Response(200, text="Success")
        mock_handle_async_request.return_value = mock_response

        response = await self.transport.handle_async_request(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Success")
        mock_handle_async_request.assert_called_once()

    async def test_aclose(self):
        with patch.object(self.transport._inner_transport, "aclose") as mock_aclose:
            await self.transport.aclose()
            mock_aclose.assert_called_once()

def test_flat_import_google_genai_clients():
    from gen_ai_hub.proxy.native.google_genai.clients import Client as client
    from gen_ai_hub.proxy.native.google_genai import Client as client_flat
    assert client == client_flat
