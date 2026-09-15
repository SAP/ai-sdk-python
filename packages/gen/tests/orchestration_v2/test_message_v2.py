import unittest

from gen_ai_hub.orchestration_v2.models.message import (
    AssistantMessage,
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
        self.assertIsNotNone(msg.reasoning_content)
        self.assertIsInstance(msg.reasoning_content[0], ReasoningBlock)

    def test_reasoning_content_optional(self):
        msg = ResponseChatMessage.model_validate({"role": "assistant", "content": "Hello"})
        self.assertIsNone(msg.reasoning_content)


class TestAssistantMessageValidation(unittest.TestCase):

    def test_reasoning_content_deserialized_from_dict(self):
        msg = AssistantMessage.model_validate({
            "role": "assistant",
            "content": "Paris",
            "reasoning_content": [{"content": "France's capital is Paris.", "signature": "sig"}],
        })
        self.assertIsNotNone(msg.reasoning_content)
        self.assertIsInstance(msg.reasoning_content[0], ReasoningBlock)
        self.assertEqual(msg.reasoning_content[0].content, "France's capital is Paris.")
        self.assertEqual(msg.reasoning_content[0].signature, "sig")

    def test_reasoning_content_optional(self):
        msg = AssistantMessage.model_validate({"role": "assistant", "content": "Hello"})
        self.assertIsNone(msg.reasoning_content)

