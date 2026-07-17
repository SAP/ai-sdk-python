"""
Integration tests for the BatchService client — synchronous methods.

These tests exercise the full lifecycle of a batch job against the live
SAP AI Core batch service endpoint:
  create → get → get_status → cancel → delete

Each test class that mutates state is responsible for cleaning up its job
in tearDown so the resource group stays tidy.

All tests are wrapped with the retry decorator to handle transient 429/503
responses from the live service.
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
class TestBatchServiceCreate(BatchServiceTestBase):
    """Tests for create and basic read-back of a newly created batch job."""

    created_batch_id: str | None = None

    def tearDown(self):
        if self.created_batch_id:
            try:
                self.service.cancel(self.created_batch_id)
                self.service.delete(self.created_batch_id)
            except Exception:
                pass
            self.created_batch_id = None

    def test_create_and_get_returns_detail(self):
        create_resp = self.service.create(
            type="llm-native",
            input_uri=self.input_uri,
            output_uri=self.output_uri,
            provider=self.provider,
            model=self.model,
        )
        self.assertIsInstance(create_resp, BatchCreateResponse)
        self.assertIsNotNone(create_resp.id)
        self.assertIn(create_resp.status, ("PENDING", "RUNNING"))
        self.created_batch_id = create_resp.id


        detail = self.service.get(create_resp.id)
        self.assertIsInstance(detail, BatchDetailResponse)
        self.assertEqual(detail.id, create_resp.id)
        self.assertIsNotNone(detail.status)
        self.assertIsNotNone(detail.input)
        self.assertIsNotNone(detail.output)

        status = self.service.get_status(create_resp.id)
        self.assertIsInstance(status, BatchStatusResponse)
        self.assertIsNotNone(status.current_status)
        self.assertIsNotNone(status.target_status)

        list_resp = self.service.list()
        self.assertIsInstance(list_resp, BatchListResponse)
        self.assertTrue(list_resp.count >= 1)
        for item in list_resp.resources:
            self.assertIsNotNone(item.id)
            self.assertIsNotNone(item.status)

        cancel_resp = self.service.cancel(create_resp.id)
        self.assertIsInstance(cancel_resp, BatchCancelResponse)
        self.assertEqual(cancel_resp.id, create_resp.id)
        self.assertIsNotNone(cancel_resp.message)

        self.wait_for_batch_to_be_deletable(create_resp.id)

        delete_resp = self.service.delete(self.created_batch_id)
        self.assertIsInstance(delete_resp, BatchDeleteResponse)
        self.assertEqual(delete_resp.id, create_resp.id)

    def test_get_nonexistent_job_raises_batch_service_error(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        with self.assertRaises(BatchServiceError) as ctx:
            self.service.get(fake_id)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_get_status_nonexistent_job_raises_batch_service_error(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        with self.assertRaises(BatchServiceError) as ctx:
            self.service.get_status(fake_id)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_cancel_nonexistent_job_raises_batch_service_error(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        with self.assertRaises(BatchServiceError) as ctx:
            self.service.cancel(fake_id)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_delete_nonexistent_job_raises_batch_service_error(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        with self.assertRaises(BatchServiceError) as ctx:
            self.service.delete(fake_id)
        self.assertEqual(ctx.exception.status_code, 404)
