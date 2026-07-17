"""
Integration tests for the BatchService client — async methods.

Mirrors test_service.py but exercises the acreate / alist / aget /
aget_status / acancel / adelete variants end-to-end.
"""

import unittest

from gen_ai_hub.batch_service import BatchDeleteResponse
from gen_ai_hub.batch_service.exceptions import BatchServiceError
from gen_ai_hub.batch_service.models.response import (
    BatchCreateResponse,
    BatchListResponse,
    BatchDetailResponse,
    BatchStatusResponse,
    BatchCancelResponse,
)
from integration_tests.batch_service.test_base import BatchServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class

@retry_on_429_or_503_class()
class TestBatchServiceAsync(BatchServiceTestBase, unittest.IsolatedAsyncioTestCase):

    created_batch_id: str | None = None

    async def asyncTearDown(self):
        if self.created_batch_id:
            try:
                await self.service.acancel(self.created_batch_id)
                await self.service.adelete(self.created_batch_id)
            except Exception:
                pass
            self.created_batch_id = None

    async def test_acreate_returns_pending_job(self):
        create_resp = await self.service.acreate(
            input_uri=self.input_uri,
            output_uri=self.output_uri,
            provider=self.provider,
            model=self.model,
        )
        self.created_batch_id = create_resp.id

        self.assertIsInstance(create_resp, BatchCreateResponse)
        self.assertIsNotNone(create_resp.id)
        self.assertIn(create_resp.status, ("PENDING", "RUNNING"))

        detail_resp = await self.service.aget(create_resp.id)
        self.assertIsInstance(detail_resp, BatchDetailResponse)
        self.assertEqual(detail_resp.id, create_resp.id)

        status_resp = await self.service.aget_status(create_resp.id)
        self.assertIsInstance(status_resp, BatchStatusResponse)
        self.assertIsNotNone(status_resp.current_status)

        list_resp = await self.service.alist()
        self.assertIsInstance(list_resp, BatchListResponse)
        self.assertIsNotNone(list_resp.count)

        cancel_resp = await self.service.acancel(create_resp.id)
        self.assertIsInstance(cancel_resp, BatchCancelResponse)
        self.assertEqual(cancel_resp.id, create_resp.id)

        delete_resp = await self.service.adelete(self.created_batch_id)
        self.assertIsInstance(delete_resp, BatchDeleteResponse)
        self.assertEqual(delete_resp.id, create_resp.id)

        self.created_batch_id = None  # tearDown should not re-cancel

    async def test_aget_nonexistent_raises_error(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        with self.assertRaises(BatchServiceError) as ctx:
            await self.service.aget(fake_id)
        self.assertEqual(ctx.exception.status_code, 404)
