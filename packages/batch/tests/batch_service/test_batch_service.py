"""
Unit tests for the BatchService client — synchronous methods.
"""

import unittest
from unittest.mock import patch

import httpx
from httpx import Response

from gen_ai_hub.batch_service.exceptions import BatchServiceError
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
    batch_create_mocker,
    batch_list_mocker,
    batch_get_mocker,
    batch_status_mocker,
    batch_cancel_mocker,
    batch_delete_mocker,
    batch_not_found_mocker,
    batch_create_error_mocker,
    get_mocked_ai_core_client
)


class TestBatchService(unittest.TestCase):

    def setUp(self):
        self.proxy_client = get_mocked_ai_core_client(client_id='test')
        self.client = BatchService(proxy_client=self.proxy_client)

    def test_create_returns_create_response(self):
        with batch_create_mocker():
            resp = self.client.create(
                type="llm-native",
                input_uri="ai://store/input.jsonl",
                output_uri="ai://store/output/",
                provider="azure-openai",
                model="gpt-4.1-mini",
            )
        self.assertIsInstance(resp, BatchCreateResponse)
        self.assertEqual(resp.id, BATCH_ID)
        self.assertEqual(resp.status, "PENDING")

    def test_create_sends_correct_payload(self):
        captured = {}

        def capture_post(url, **kwargs):
            captured["json"] = kwargs.get("json")
            return Response(202, json=CREATE_RESPONSE)

        with patch.object(self.client.client, "post", side_effect=capture_post):
            self.client.create(
                type="llm-native",
                input_uri="ai://store/input.jsonl",
                output_uri="ai://store/output/",
                provider="azure-openai",
                model="gpt-4.1-mini",
            )

        payload = captured["json"]
        self.assertEqual(payload["type"], "llm-native")
        self.assertEqual(payload["input"]["uri"], "ai://store/input.jsonl")
        self.assertEqual(payload["output"]["uri"], "ai://store/output/")
        self.assertEqual(payload["spec"]["provider"], "azure-openai")
        self.assertEqual(payload["spec"]["model"], "gpt-4.1-mini")

    def test_with_resource_group_header(self):
        test_resource_group = 'test-resource-group'
        client = BatchService(proxy_client=self.proxy_client, resource_group=test_resource_group)
        captured_headers = {}

        def capture_post(url, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            return Response(202, json=CREATE_RESPONSE)

        with patch.object(client.client, "post", side_effect=capture_post):
            client.create(
                type="llm-native",
                input_uri="ai://x",
                output_uri="ai://y",
                provider="p",
                model="m",
            )

        self.assertEqual(captured_headers.get("AI-Resource-Group"), test_resource_group)

    def test_create_raises_batch_service_error_on_400(self):
        
        with batch_create_error_mocker():
            with self.assertRaises(BatchServiceError) as ctx:
                self.client.create(
                    type="llm-native",
                    input_uri="ai://bad.txt",
                    output_uri="ai://y",
                    provider="p",
                    model="m",
                )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("not found", ctx.exception.message.lower())

    def test_list_returns_list_response(self):
        
        with batch_list_mocker():
            resp = self.client.list()
        self.assertIsInstance(resp, BatchListResponse)
        self.assertEqual(resp.count, 2)
        self.assertEqual(len(resp.resources), 2)
        self.assertEqual(resp.resources[0].id, BATCH_ID)

    def test_get_returns_detail_response(self):
        
        with batch_get_mocker():
            resp = self.client.get(BATCH_ID)
        self.assertIsInstance(resp, BatchDetailResponse)
        self.assertEqual(resp.id, BATCH_ID)
        self.assertEqual(resp.status.current_status, "COMPLETED")
        self.assertEqual(resp.input.uri, "ai://my-store/input/batch-input.jsonl")

    def test_get_raises_on_404(self):
        
        with batch_not_found_mocker():
            with self.assertRaises(BatchServiceError) as ctx:
                self.client.get(BATCH_ID)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("not found", ctx.exception.message.lower())

    def test_get_status_returns_status_response(self):
        
        with batch_status_mocker():
            resp = self.client.get_status(BATCH_ID)
        self.assertIsInstance(resp, BatchStatusResponse)
        self.assertEqual(resp.current_status, "RUNNING")
        self.assertEqual(resp.target_status, "COMPLETED")
        self.assertIsNone(resp.message)

    def test_cancel_returns_cancel_response(self):
        
        with batch_cancel_mocker():
            resp = self.client.cancel(BATCH_ID)
        self.assertIsInstance(resp, BatchCancelResponse)
        self.assertEqual(resp.id, BATCH_ID)
        self.assertIn("cancellation", resp.message.lower())

    def test_delete_returns_delete_response(self):
        
        with batch_delete_mocker():
            resp = self.client.delete(BATCH_ID)
        self.assertIsInstance(resp, BatchDeleteResponse)
        self.assertEqual(resp.id, BATCH_ID)
        self.assertIn("deleted", resp.message.lower())

    def test_timeout_priority_no_timeout_set(self):
        
        captured = {}

        def capture_post(url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            return Response(202, json=CREATE_RESPONSE)

        with patch.object(self.client.client, "post", side_effect=capture_post):
            self.client.create(type="llm-native", input_uri="ai://x", output_uri="ai://y", provider="p", model="m")

        self.assertEqual(captured["timeout"], httpx.USE_CLIENT_DEFAULT)

    def test_timeout_priority_service_default(self):
        client = BatchService(proxy_client=self.proxy_client, timeout=99.0)
        captured = {}

        def capture_post(url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            return Response(202, json=CREATE_RESPONSE)

        with patch.object(client.client, "post", side_effect=capture_post):
            client.create(type="llm-native", input_uri="ai://x", output_uri="ai://y", provider="p", model="m")

        self.assertEqual(captured["timeout"], 99.0)

    def test_timeout_priority_per_request_overrides_default(self):
        client = BatchService(proxy_client=self.proxy_client, timeout=99.0)
        captured = {}

        def capture_post(url, **kwargs):
            captured["timeout"] = kwargs.get("timeout")
            return Response(202, json=CREATE_RESPONSE)

        with patch.object(client.client, "post", side_effect=capture_post):
            client.create(type="llm-native", input_uri="ai://x", output_uri="ai://y", provider="p", model="m", timeout=77.0)

        self.assertEqual(captured["timeout"], 77.0)

    def test_http_client_is_reused_across_requests(self):
        
        original_client = self.client.client
        with batch_create_mocker():
            self.client.create(type="llm-native", input_uri="ai://x", output_uri="ai://y", provider="p", model="m")
        with batch_list_mocker():
            self.client.list()
        self.assertIs(self.client.client, original_client)
        self.assertFalse(original_client.is_closed)

    def test_close_http_connection(self):
        
        client_ref = self.client.client
        self.client.close_http_connection()
        self.assertTrue(client_ref.is_closed)
