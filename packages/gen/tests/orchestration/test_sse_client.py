import json
import unittest
from unittest.mock import Mock

from httpx import Response

from gen_ai_hub.orchestration.sse_client import AsyncSSEClient


def create_valid_event(token="test"):
    """
    Create a valid event structure matching the actual SSE response format.

    See tests/mock.py for structure details.
    """
    return {
        "request_id": "test-request-id",
        "module_results": {
            "input_filtering": None,
            "output_filtering": None,
            "input_masking": None,
            "llm": {
                "id": "test-id",
                "object": "chat.completion.chunk",
                "created": 1738573708,
                "model": "gemini-2.0-flash",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": token, "role": "assistant"},
                        "finish_reason": None,
                        "logprobs": None
                    }
                ],
                "system_fingerprint": None
            },
            "templating": None,
            "output_unmasking": None
        },
        "orchestration_result": {
            "id": "test-id",
            "object": "chat.completion.chunk",
            "created": 1738573708,
            "model": "gemini-2.0-flash",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": token, "role": "assistant"},
                    "finish_reason": None,
                    "logprobs": None
                }
            ],
            "system_fingerprint": None
        }
    }


class TestSSEClientBuffering(unittest.IsolatedAsyncioTestCase):
    """Tests for AsyncSSEClient with manual buffering using aiter_text()."""

    def setUp(self):
        """Set up test fixtures."""
        self.event_prefix = "data: "
        self.final_message = "[DONE]"

    async def test_simple_complete_lines(self):
        """Test that complete lines are processed correctly."""
        event1 = create_valid_event("test1")
        event2 = create_valid_event("test2")

        chunks = [
            f"data: {json.dumps(event1)}\n",
            f"data: {json.dumps(event2)}\n",
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].request_id, "test-request-id")
        self.assertEqual(results[1].request_id, "test-request-id")

    async def test_json_split_across_chunks(self):
        """Test that JSON split across multiple chunks is handled correctly."""
        event = create_valid_event("split test")
        event_str = json.dumps(event)

        # Split the JSON in the middle
        mid = len(event_str) // 2
        part1 = event_str[:mid]
        part2 = event_str[mid:]

        chunks = [
            f"data: {part1}",  # First part without newline
            f"{part2}\n",  # Second part with newline
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].request_id, "test-request-id")
        self.assertEqual(results[0].module_results.llm.choices[0].delta.content, "split test")

    async def test_multiple_events_in_single_chunk(self):
        """Test that multiple events in a single chunk are processed correctly."""
        event1 = create_valid_event("first")
        event2 = create_valid_event("second")

        chunks = [
            f"data: {json.dumps(event1)}\ndata: {json.dumps(event2)}\n",
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].module_results.llm.choices[0].delta.content, "first")
        self.assertEqual(results[1].module_results.llm.choices[0].delta.content, "second")

    async def test_final_message_stops_iteration(self):
        """Test that [DONE] message stops iteration."""
        event1 = create_valid_event("before done")

        chunks = [
            f"data: {json.dumps(event1)}\n",
            f"data: {self.final_message}\n",
            f"data: {json.dumps(event1)}\n",  # This should not be processed
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        # Should only have one result before [DONE]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].module_results.llm.choices[0].delta.content, "before done")

    async def test_empty_lines_ignored(self):
        """Test that empty lines are ignored."""
        event = create_valid_event("test")

        chunks = [
            "\n",
            f"data: {json.dumps(event)}\n",
            "\n",
            "\n",
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].request_id, "test-request-id")

    async def test_lines_without_event_prefix_ignored(self):
        """Test that lines without the event prefix are ignored."""
        event = create_valid_event("test")

        chunks = [
            "invalid line\n",
            f"data: {json.dumps(event)}\n",
            "another invalid line\n",
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].request_id, "test-request-id")

    async def test_partial_line_at_end_of_stream(self):
        """Test that a partial line at the end of the stream is processed."""
        event = create_valid_event("final")

        # Last chunk has no newline
        chunks = [
            f"data: {json.dumps(event)}",
        ]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].request_id, "test-request-id")
        self.assertEqual(results[0].module_results.llm.choices[0].delta.content, "final")

    async def test_very_small_chunks(self):
        """Test handling of very small chunks (simulating slow network)."""
        event = create_valid_event("test")
        event_str = f"data: {json.dumps(event)}\n"

        # Split into very small chunks (2 characters each)
        chunks = [event_str[i:i + 2] for i in range(0, len(event_str), 2)]

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].request_id, "test-request-id")

    async def test_complex_json_with_nested_objects(self):
        """Test handling of complex nested JSON objects split across chunks."""
        event = create_valid_event("Hello")
        event_str = json.dumps(event)

        # Split the JSON across multiple chunks
        chunk_size = 20
        parts = [event_str[i:i + chunk_size] for i in range(0, len(event_str), chunk_size)]

        chunks = [f"data: {parts[0]}"]
        for part in parts[1:-1]:
            chunks.append(part)
        chunks.append(f"{parts[-1]}\n")

        mock_response = Mock(spec=Response)
        mock_response.aiter_text = Mock(return_value=self._async_generator(chunks))

        client = AsyncSSEClient(mock_response, self.event_prefix, self.final_message)
        client._response = mock_response
        results = []
        async for result in client._internal_iterator():
            results.append(result)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].request_id, "test-request-id")
        self.assertEqual(results[0].module_results.llm.choices[0].delta.content, "Hello")

    async def _async_generator(self, items):
        """Helper to create async generator from list."""
        for item in items:
            yield item


if __name__ == '__main__':
    unittest.main()
