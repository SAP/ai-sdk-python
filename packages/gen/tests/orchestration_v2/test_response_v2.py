import unittest

from gen_ai_hub.orchestration_v2.models.message import ReasoningBlock
from gen_ai_hub.orchestration_v2.models.response import StreamDelta


class TestStreamDeltaValidation(unittest.TestCase):

    def test_reasoning_content_deserialized_from_dict(self):
        delta = StreamDelta.model_validate({
            "content": "",
            "reasoning_content": [{"content": "I should respond politely.", "signature": ""}],
        })
        self.assertIsNotNone(delta.reasoning_content)
        self.assertIsInstance(delta.reasoning_content[0], ReasoningBlock)
        self.assertEqual(delta.reasoning_content[0].content, "I should respond politely.")

    def test_reasoning_content_optional(self):
        delta = StreamDelta.model_validate({"content": "Hello"})
        self.assertIsNone(delta.reasoning_content)

