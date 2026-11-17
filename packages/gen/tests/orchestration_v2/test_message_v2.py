import unittest

from gen_ai_hub.orchestration_v2.models.message import (
    AssistantMessage,
    ReasoningBlock,
    ResponseChatMessage,
)
from gen_ai_hub.orchestration_v2.models.response import (
    LLMChoice,
    StreamLLMChoice,
)


class TestResponseChatMessageValidation(unittest.TestCase):

    def test_deserialization_from_dict(self):
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

    def test_deserialization_from_dict(self):
        msg = AssistantMessage.model_validate({
            "content": "Hello",
            "reasoning_content": [{"content": "I think...", "signature": "sig123"}],
        })
        self.assertIsNotNone(msg.reasoning_content)
        self.assertIsInstance(msg.reasoning_content[0], ReasoningBlock)

    def test_reasoning_content_optional(self):
        msg = AssistantMessage.model_validate({"role": "assistant", "content": "Hello"})
        self.assertIsNone(msg.reasoning_content)


class TestLLMChoiceValidation(unittest.TestCase):
    """provider_specific_fields is a declared optional field on LLMChoice /
    StreamLLMChoice, so it must round-trip and default to None when absent."""

    def test_llm_choice_provider_specific_fields(self):
        choice = LLMChoice.model_validate({
            "index": 0,
            "message": {"role": "assistant", "content": "ok"},
            "finish_reason": "stop",
            "provider_specific_fields": {"finish_reason": "end_turn"},
        })
        self.assertEqual(choice.provider_specific_fields, {"finish_reason": "end_turn"})

    def test_llm_choice_provider_specific_fields_optional(self):
        choice = LLMChoice.model_validate({
            "index": 0,
            "message": {"role": "assistant", "content": "ok"},
            "finish_reason": "stop",
        })
        self.assertIsNone(choice.provider_specific_fields)

    def test_stream_llm_choice_provider_specific_fields(self):
        choice = StreamLLMChoice.model_validate({
            "index": 0,
            "delta": {"content": "hi"},
            "finish_reason": "stop",
            "provider_specific_fields": {"finish_reason": "end_turn"},
        })
        self.assertEqual(choice.provider_specific_fields, {"finish_reason": "end_turn"})

    def test_stream_llm_choice_provider_specific_fields_optional(self):
        choice = StreamLLMChoice.model_validate({
            "index": 0,
            "delta": {"content": "hi"},
        })
        self.assertIsNone(choice.provider_specific_fields)
