import unittest

from gen_ai_hub.orchestration_v2.models.message import (
    AssistantMessage,
    FunctionCall,
    MessageToolCall,
    ReasoningBlock,
    ResponseChatMessage,
)
from gen_ai_hub.orchestration_v2.models.response import (
    Citation,
    CompletionPostResponse,
    CompletionTokensDetails,
    ChoiceLogprobs,
    ChatCompletionTokenLogprob,
    ErrorResponse,
    ErrorResponseStreaming,
    GenericModuleResult,
    LLMChoice,
    LLMModuleResult,
    ModuleResults,
    OrchestrationResponseWithRetries,
    PromptTokensDetails,
    SAPAPIError,
    SAPAPIErrorStreaming,
    StreamCompletionPostResponse,
    StreamDelta,
    StreamFunctionObject,
    StreamLLMChoice,
    StreamLLMModuleResult,
    StreamModuleResults,
    StreamToolCall,
    TokenUsage,
    TopLogprob,
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

class TestExtraFieldsAllowed(unittest.TestCase):
    """Response-side models (ResponseBaseModel subclasses) must silently accept
    unknown fields so that new API attributes never break existing clients."""

    def test_response_chat_message_stores_extra_field(self):
        msg = ResponseChatMessage.model_validate({
            "role": "assistant",
            "content": "hi",
            "extra_field": "extra",
        })
        self.assertEqual(msg.extra_field, "extra")

    def test_function_call_stores_extra_field(self):
        fc = FunctionCall.model_validate({
            "name": "my_fn",
            "arguments": "{}",
            "extra_field": "extra",
        })
        self.assertEqual(fc.extra_field, "extra")

    def test_message_tool_call_stores_extra_field(self):
        tc = MessageToolCall.model_validate({
            "id": "call_1",
            "type": "function",
            "function": {"name": "fn", "arguments": "{}"},
            "extra_field": "extra",
        })
        self.assertEqual(tc.extra_field, "extra")

    def test_llm_choice_stores_extra_field(self):
        choice = LLMChoice.model_validate({
            "index": 0,
            "message": {"role": "assistant", "content": "ok"},
            "finish_reason": "stop",
            "extra_field": "extra",
        })
        self.assertEqual(choice.extra_field, "extra")

    def test_llm_module_result_stores_extra_field(self):
        result = LLMModuleResult.model_validate({
            "id": "chatcmpl-abc",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4o",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "hello"},
                "finish_reason": "stop",
            }],
            "usage": {"completion_tokens": 5, "prompt_tokens": 3, "total_tokens": 8},
            "extra_field": "extra",
        })
        self.assertEqual(result.extra_field, "extra")

    def test_completion_post_response_stores_extra_field(self):
        resp = CompletionPostResponse.model_validate({
            "request_id": "req-1",
            "intermediate_results": {},
            "final_result": {
                "id": "chatcmpl-abc",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4o",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "hello"},
                    "finish_reason": "stop",
                }],
                "usage": {"completion_tokens": 5, "prompt_tokens": 3, "total_tokens": 8},
            },
            "extra_field": "extra",
        })
        self.assertEqual(resp.extra_field, "extra")

    def test_prompt_tokens_details_stores_extra_field(self):
        details = PromptTokensDetails.model_validate({"extra_field": "extra"})
        self.assertEqual(details.extra_field, "extra")

    def test_completion_tokens_details_stores_extra_field(self):
        details = CompletionTokensDetails.model_validate({"extra_field": "extra"})
        self.assertEqual(details.extra_field, "extra")

    def test_token_usage_stores_extra_field(self):
        usage = TokenUsage.model_validate({
            "completion_tokens": 5, "prompt_tokens": 3, "total_tokens": 8,
            "extra_field": "extra",
        })
        self.assertEqual(usage.extra_field, "extra")

    def test_generic_module_result_stores_extra_field(self):
        result = GenericModuleResult.model_validate({"message": "ok", "extra_field": "extra"})
        self.assertEqual(result.extra_field, "extra")

    def test_top_logprob_stores_extra_field(self):
        lp = TopLogprob.model_validate({"token": "hi", "logprob": -0.5, "extra_field": "extra"})
        self.assertEqual(lp.extra_field, "extra")

    def test_chat_completion_token_logprob_stores_extra_field(self):
        lp = ChatCompletionTokenLogprob.model_validate({
            "token": "hi", "logprob": -0.5, "extra_field": "extra",
        })
        self.assertEqual(lp.extra_field, "extra")

    def test_choice_logprobs_stores_extra_field(self):
        lp = ChoiceLogprobs.model_validate({"extra_field": "extra"})
        self.assertEqual(lp.extra_field, "extra")

    def test_stream_function_object_stores_extra_field(self):
        fo = StreamFunctionObject.model_validate({"name": "fn", "arguments": "{}", "extra_field": "extra"})
        self.assertEqual(fo.extra_field, "extra")

    def test_stream_tool_call_stores_extra_field(self):
        tc = StreamToolCall.model_validate({"index": 0, "extra_field": "extra"})
        self.assertEqual(tc.extra_field, "extra")

    def test_stream_delta_stores_extra_field(self):
        delta = StreamDelta.model_validate({"content": "hi", "extra_field": "extra"})
        self.assertEqual(delta.extra_field, "extra")

    def test_stream_llm_choice_stores_extra_field(self):
        choice = StreamLLMChoice.model_validate({
            "index": 0, "delta": {"content": "hi"}, "extra_field": "extra",
        })
        self.assertEqual(choice.extra_field, "extra")

    def test_citation_stores_extra_field(self):
        citation = Citation.model_validate({
            "title": "Source A", "url": "https://example.com", "extra_field": "extra",
        })
        self.assertEqual(citation.extra_field, "extra")

    def test_stream_llm_module_result_stores_extra_field(self):
        result = StreamLLMModuleResult.model_validate({
            "id": "chatcmpl-abc", "object": "chat.completion.chunk",
            "created": 1234567890, "model": "gpt-4o",
            "choices": [{"index": 0, "delta": {"content": "hi"}}],
            "extra_field": "extra",
        })
        self.assertEqual(result.extra_field, "extra")

    def test_module_results_stores_extra_field(self):
        results = ModuleResults.model_validate({"extra_field": "extra"})
        self.assertEqual(results.extra_field, "extra")

    def test_stream_module_results_stores_extra_field(self):
        results = StreamModuleResults.model_validate({"extra_field": "extra"})
        self.assertEqual(results.extra_field, "extra")

    def test_sap_api_error_stores_extra_field(self):
        err = SAPAPIError.model_validate({
            "request_id": "r1", "code": 400, "message": "bad", "location": "svc",
            "extra_field": "extra",
        })
        self.assertEqual(err.extra_field, "extra")

    def test_sap_api_error_streaming_stores_extra_field(self):
        err = SAPAPIErrorStreaming.model_validate({
            "request_id": "r1", "code": 500, "message": "error", "location": "svc",
            "extra_field": "extra",
        })
        self.assertEqual(err.extra_field, "extra")

    def test_stream_completion_post_response_stores_extra_field(self):
        resp = StreamCompletionPostResponse.model_validate({
            "request_id": "req-1",
            "intermediate_results": None,
            "final_result": None,
            "extra_field": "extra",
        })
        self.assertEqual(resp.extra_field, "extra")

    def test_error_response_stores_extra_field(self):
        resp = ErrorResponse.model_validate({
            "error": {"request_id": "r1", "code": 400, "message": "bad", "location": "svc"},
            "extra_field": "extra",
        })
        self.assertEqual(resp.extra_field, "extra")

    def test_error_response_streaming_stores_extra_field(self):
        resp = ErrorResponseStreaming.model_validate({
            "error": {"request_id": "r1", "code": 500, "message": "error", "location": "svc"},
            "extra_field": "extra",
        })
        self.assertEqual(resp.extra_field, "extra")

    def test_orchestration_response_with_retries_stores_extra_field(self):
        resp = OrchestrationResponseWithRetries.model_validate({
            "request_id": "req-1",
            "intermediate_results": {},
            "final_result": {
                "id": "chatcmpl-abc", "object": "chat.completion",
                "created": 1234567890, "model": "gpt-4o",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "hi"}, "finish_reason": "stop"}],
                "usage": {"completion_tokens": 5, "prompt_tokens": 3, "total_tokens": 8},
            },
            "extra_field": "extra",
        })
        self.assertEqual(resp.extra_field, "extra")
