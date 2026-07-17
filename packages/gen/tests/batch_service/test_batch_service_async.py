"""
Unit tests for the BatchService client — async methods.
"""

import unittest
from unittest.mock import AsyncMock, patch

import httpx

from gen_ai_hub.batch_service.models.response import (
    BatchCreateResponse,
    BatchListResponse,
    BatchDetailResponse,
    BatchStatusResponse,
    BatchCancelResponse,
    BatchDeleteResponse,
)
from gen_ai_hub.batch_service.service import BatchService
from tests.mock import (
    BATCH_ID,
    BATCH_CREATE_RESPONSE as CREATE_RESPONSE,
    batch_create_mocker_async,
    batch_list_mocker_async,
    batch_get_mocker_async,
    batch_status_mocker_async,
    batch_cancel_mocker_async,
    batch_delete_mocker_async,
    get_mocked_ai_core_client
)


class TestBatchServiceAsync(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='test')
        self.client = BatchService(proxy_client=self.proxy_client)

    async def test_acreate_returns_create_response(self):
        async with batch_create_mocker_async():
            resp = await self.client.acreate(
                input_uri="ai://store/input.jsonl",
                output_uri="ai://store/output/",
                provider="azure-openai",
                model="gpt-4.1-mini",
            )
        self.assertIsInstance(resp, BatchCreateResponse)
        self.assertEqual(resp.id, BATCH_ID)
        self.assertEqual(resp.status, "PENDING")

    async def test_alist_returns_list_response(self):
        async with batch_list_mocker_async():
            resp = await self.client.alist()
        self.assertIsInstance(resp, BatchListResponse)
        self.assertEqual(resp.count, 2)
        self.assertEqual(len(resp.resources), 2)

    async def test_aget_returns_detail_response(self):
        async with batch_get_mocker_async():
            resp = await self.client.aget(BATCH_ID)
        self.assertIsInstance(resp, BatchDetailResponse)
        self.assertEqual(resp.id, BATCH_ID)
        self.assertEqual(resp.status.current_status, "COMPLETED")

    async def test_aget_status_returns_status_response(self):
        async with batch_status_mocker_async():
            resp = await self.client.aget_status(BATCH_ID)
        self.assertIsInstance(resp, BatchStatusResponse)
        self.assertEqual(resp.current_status, "RUNNING")
        self.assertIsNone(resp.message)

    async def test_acancel_returns_cancel_response(self):
        async with batch_cancel_mocker_async():
            resp = await self.client.acancel(BATCH_ID)
        self.assertIsInstance(resp, BatchCancelResponse)
        self.assertEqual(resp.id, BATCH_ID)

    async def test_adelete_returns_delete_response(self):
        async with batch_delete_mocker_async():
            resp = await self.client.adelete(BATCH_ID)
        self.assertIsInstance(resp, BatchDeleteResponse)
        self.assertEqual(resp.id, BATCH_ID)

    async def test_async_timeout_no_timeout_set(self):
        captured = {}

        async def capture_post(url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            return httpx.Response(202, json=CREATE_RESPONSE)

        with patch.object(self.client.async_client, "post", new=AsyncMock(side_effect=capture_post)):
            await self.client.acreate(input_uri="ai://x", output_uri="ai://y", provider="p", model="m")

        self.assertEqual(captured["timeout"], httpx.USE_CLIENT_DEFAULT)

    async def test_async_timeout_service_default(self):
        client = BatchService(proxy_client=self.proxy_client, timeout=55.0)
        captured = {}

        async def capture_post(url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            return httpx.Response(202, json=CREATE_RESPONSE)

        with patch.object(client.async_client, "post", new=AsyncMock(side_effect=capture_post)):
            await client.acreate(input_uri="ai://x", output_uri="ai://y", provider="p", model="m")

        self.assertEqual(captured["timeout"], 55.0)

    async def test_async_timeout_per_request_overrides_default(self):
        client = BatchService(proxy_client=self.proxy_client, timeout=55.0)
        captured = {}

        async def capture_post(url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            return httpx.Response(202, json=CREATE_RESPONSE)

        with patch.object(client.async_client, "post", new=AsyncMock(side_effect=capture_post)):
            await client.acreate(input_uri="ai://x", output_uri="ai://y", provider="p", model="m", timeout=33.0)

        self.assertEqual(captured["timeout"], 33.0)

    async def test_async_client_is_reused(self):
        
        original_async_client = self.client.async_client
        async with batch_create_mocker_async():
            await self.client.acreate(input_uri="ai://x", output_uri="ai://y", provider="p", model="m")
        async with batch_list_mocker_async():
            await self.client.alist()
        self.assertIs(self.client.async_client, original_async_client)
        self.assertFalse(original_async_client.is_closed)

    async def test_aclose_http_connection(self):
        
        async_client_ref = self.client.async_client
        await self.client.aclose_http_connection()
        self.assertTrue(async_client_ref.is_closed)
