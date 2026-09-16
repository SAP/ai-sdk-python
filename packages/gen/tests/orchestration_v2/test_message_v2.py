import unittest

from gen_ai_hub.orchestration_v2.models.message import (
    ReasoningBlock,
    ResponseChatMessage,
)


class TestResponseChatMessageValidation(unittest.TestCase):

    def test_reasoning_content_deserialized_from_dict(self):
        msg = ResponseChatMessage.model_validate({
            "role": "assistant",
            "content": "Hello",
            "reasoning_content": [{"content": "I think...", "signature": "sig123"}],
        })
        assert msg.reasoning_content is not None
        self.assertIsInstance(msg.reasoning_content[0], ReasoningBlock)

    def test_reasoning_content_optional(self):
        msg = ResponseChatMessage.model_validate({"role": "assistant", "content": "Hello"})
        self.assertIsNone(msg.reasoning_content)
