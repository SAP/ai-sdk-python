"""
Unit tests for batch service model serialization and validation.
"""

import unittest

from pydantic import ValidationError

from gen_ai_hub.batch_service.models.request import BatchCreateRequest, BatchInput, BatchOutput, BatchSpec
from gen_ai_hub.batch_service.models.response import (
    BatchCreateResponse,
    BatchSummary,
    BatchListResponse,
    BatchDetailResponse,
    BatchStatusResponse,
    BatchCancelResponse,
    BatchDeleteResponse,
    ErrorResponse,
)


class TestBatchCreateRequest(unittest.TestCase):

    def _make_request(self, **overrides):
        defaults = dict(
            type="llm-native",
            input=BatchInput(uri="ai://store/input.jsonl"),
            output=BatchOutput(uri="ai://store/output/"),
            spec=BatchSpec(provider="azure-openai", model="gpt-4.1-mini"),
        )
        defaults.update(overrides)
        return BatchCreateRequest(**defaults)

    def test_serialization_uses_snake_case_keys(self):
        req = self._make_request()
        payload = req.model_dump()
        self.assertEqual(payload["type"], "llm-native")
        self.assertEqual(payload["input"]["uri"], "ai://store/input.jsonl")
        self.assertEqual(payload["output"]["uri"], "ai://store/output/")
        self.assertEqual(payload["spec"]["provider"], "azure-openai")
        self.assertEqual(payload["spec"]["model"], "gpt-4.1-mini")

    def test_none_fields_excluded(self):
        req = self._make_request()
        payload = req.model_dump()
        # No None values should be present at any level
        for value in payload.values():
            self.assertIsNotNone(value)

    def test_extra_fields_forbidden(self):
        with self.assertRaises(ValidationError):
            BatchCreateRequest(
                type="llm-native",
                input=BatchInput(uri="ai://x"),
                output=BatchOutput(uri="ai://y"),
                spec=BatchSpec(provider="p", model="m"),
                unexpected="bad",
            )

    def test_type_must_be_llm_native(self):
        with self.assertRaises(ValidationError):
            BatchCreateRequest(
                type="not-valid",
                input=BatchInput(uri="ai://x"),
                output=BatchOutput(uri="ai://y"),
                spec=BatchSpec(provider="p", model="m"),
            )

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            BatchCreateRequest(type="llm-native")

    def test_batch_create_response(self):
        data = {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "created_at": "2026-04-30T10:00:00Z",
            "status": "PENDING",
            "message": "Batch job scheduled",
        }
        resp = BatchCreateResponse(**data)
        self.assertEqual(resp.id, data["id"])
        self.assertEqual(resp.status, "PENDING")
        self.assertEqual(resp.message, "Batch job scheduled")

    def test_batch_create_response_allows_extra_fields(self):
        data = {"id": "abc", "status": "PENDING", "future_field": "value"}
        resp = BatchCreateResponse(**data)
        self.assertEqual(resp.id, "abc")

    def test_batch_list_response(self):
        data = {
            "count": 2,
            "resources": [
                {"id": "id1", "type": "llm-native", "provider": "azure-openai",
                 "created_at": "2026-04-30T10:00:00Z", "status": "COMPLETED"},
                {"id": "id2", "type": "llm-native", "provider": "azure-openai",
                 "created_at": "2026-04-30T11:00:00Z", "status": "RUNNING"},
            ],
        }
        resp = BatchListResponse(**data)
        self.assertEqual(resp.count, 2)
        self.assertEqual(len(resp.resources), 2)
        self.assertIsInstance(resp.resources[0], BatchSummary)
        self.assertEqual(resp.resources[0].id, "id1")
        self.assertEqual(resp.resources[1].status, "RUNNING")

    def test_batch_detail_response_nested_status(self):
        data = {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "type": "llm-native",
            "provider": "azure-openai",
            "created_at": "2026-04-30T10:00:00Z",
            "input": {"uri": "ai://store/input.jsonl"},
            "output": {"uri": "ai://store/output/"},
            "spec": {"model": "gpt-4.1-mini"},
            "status": {
                "current_status": "COMPLETED",
                "target_status": "COMPLETED",
                "updated_at": "2026-04-30T12:00:00Z",
                "message": None,
            },
        }
        resp = BatchDetailResponse(**data)
        self.assertEqual(resp.id, data["id"])
        self.assertEqual(resp.status.current_status, "COMPLETED")
        self.assertIsNone(resp.status.message)
        self.assertEqual(resp.input.uri, "ai://store/input.jsonl")
        self.assertEqual(resp.output.uri, "ai://store/output/")

    def test_batch_status_response(self):
        data = {
            "current_status": "RUNNING",
            "target_status": "COMPLETED",
            "updated_at": "2026-04-30T11:30:00Z",
            "message": None,
        }
        resp = BatchStatusResponse(**data)
        self.assertEqual(resp.current_status, "RUNNING")
        self.assertEqual(resp.target_status, "COMPLETED")
        self.assertIsNone(resp.message)

    def test_batch_cancel_response(self):
        data = {
            "id": "a1b2c3d4",
            "created_at": "2026-04-30T10:00:00Z",
            "message": "Batch job scheduled for cancellation",
        }
        resp = BatchCancelResponse(**data)
        self.assertEqual(resp.message, "Batch job scheduled for cancellation")

    def test_batch_delete_response(self):
        data = {
            "id": "a1b2c3d4",
            "created_at": "2026-04-30T10:00:00Z",
            "message": "Batch job deleted successfully",
        }
        resp = BatchDeleteResponse(**data)
        self.assertEqual(resp.message, "Batch job deleted successfully")

    def test_error_response(self):
        data = {
            "request_id": "d4a67ea1-2bf9-4df7-8105-d48203ccff76",
            "message": "Batch job not found",
        }
        resp = ErrorResponse(**data)
        self.assertEqual(resp.request_id, data["request_id"])
        self.assertEqual(resp.message, "Batch job not found")
