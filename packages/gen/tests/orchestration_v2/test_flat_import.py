expected = {
    # azure_content_filter
    "AzureContentFilter", "AzureContentSafetyInput", "AzureContentSafetyOutput", "AzureThreshold",

    # config
    "ModuleConfig", "OrchestrationConfig", "OrchestrationConfigReference",
    "CompletionRequestConfigurationReferenceByIdConfigRef",
    "CompletionRequestConfigurationReferenceByNameScenarioVersionConfigRef",

    # content_filter
    "ContentFilterProvider", "ContentFilter", "LlamaGuard38bFilterConfig",
    "AzureContentSafetyInputFilterConfig", "AzureContentSafetyOutputFilterConfig", "FilteringStreamOptions",

    # content_filtering
    "InputFiltering", "OutputFiltering", "FilteringModuleConfig",

    # data_masking
    "DataMaskingProviderName", "MaskingMethod", "ProfileEntity", "DPIMethodConstant", "DPIMethodFabricatedData",
    "DPICustomEntity", "DPIStandardEntity", "MaskGroundingInput", "MaskingProviderConfig", "MaskingModuleConfig",

    # document_grounding
    "GroundingType", "DataRepositoryType", "DocumentGroundingFilter", "DocumentGroundingPlaceholders",
    "DocumentGroundingConfig", "GroundingModuleConfig", "KeyValueListPair", "DocumentMetadataKeyValueListPairs",
    "GroundingSearchConfig",

    # embeddings
    "EmbeddingsEncodingFormat", "EmbeddingsInputType", "EmbeddingsModelParams", "EmbeddingsModelDetails",
    "EmbeddingsModelConfig", "EmbeddingsModuleConfigs", "EmbeddingsOrchestrationConfig", "EmbeddingsInput",
    "EmbeddingsUsage", "EmbeddingResult", "EmbeddingsResponse", "EmbeddingsPostResponse", "EmbeddingsRequest",

    # llama_guard_3_filter
    "LlamaGuard38bFilter",

    # llm_model_details
    "LLMModelDetails",

    # message
    "SystemMessage", "UserMessage", "AssistantMessage", "ToolChatMessage", "DeveloperChatMessage",
    "ChatMessage", "ResponseChatMessage", "FunctionCall", "MessageToolCall",

    # multimodal_items
    "ImageDetailLevel", "TextPart", "ImageUrl", "ImagePart", "ContentPart", "ImageItem",

    # response
    "PromptTokensDetails", "CompletionTokensDetails", "TokenUsage", "GenericModuleResult", "TopLogprob",
    "ChatCompletionTokenLogprob", "ChoiceLogprobs", "LLMChoice", "StreamFunctionObject", "StreamToolCall",
    "StreamDelta", "StreamLLMChoice", "Citation", "LLMModuleResult", "StreamLLMModuleResult", "ModuleResults",
    "StreamModuleResults", "SAPAPIError", "SAPAPIErrorStreaming", "CompletionPostResponse",
    "StreamCompletionPostResponse", "ErrorResponse", "ErrorResponseStreaming", "OrchestrationResponseWithRetries",

    # response_format
    "ResponseFormatText", "ResponseFormatJsonObject", "ResponseFormatJsonSchema", "JSONResponseSchema",

    # streaming
    "GlobalStreamOptions",

    # template
    "Template", "PromptTemplatingModuleConfig",

    # template_ref
    "TemplateRef", "TemplateRefByID", "TemplateRefByScenarioNameVersion",

    # tools
    "python_type_to_json_type", "ChatCompletionTool", "FunctionObject", "FunctionTool", "function_tool",

    # translation
    "TranslationConfig", "SAPDocumentTranslation", "SAPDocumentTranslationApplyToSelector",
    "InputTranslationConfig", "OutputTranslationConfig", "SAPDocumentTranslationInput",
    "SAPDocumentTranslationOutput", "TranslationModuleConfig",

    # OrchestrationService
    "OrchestrationService",

    # Exceptions
    "OrchestrationError", "OrchestrationErrorList"
            }


def test_flat_import_all():
    import gen_ai_hub.orchestration_v2 as module
    assert set(module.__all__) == expected

def test_flat_and_not_flat_import_by_name():
    from gen_ai_hub.orchestration_v2 import OrchestrationService as service_flat
    from gen_ai_hub.orchestration_v2.service import OrchestrationService as service
    assert service_flat == service

    from gen_ai_hub.orchestration_v2 import EmbeddingsOrchestrationConfig as embed_config_flat
    from gen_ai_hub.orchestration_v2.models.embeddings import EmbeddingsOrchestrationConfig as embed_config
    assert embed_config_flat == embed_config

    from gen_ai_hub.orchestration_v2 import OrchestrationConfig as config_flat
    from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig as config
    assert config_flat == config

    from gen_ai_hub.orchestration_v2 import MaskingModuleConfig as masking_flat
    from gen_ai_hub.orchestration_v2.models.data_masking import MaskingModuleConfig as masking
    assert masking_flat == masking

    from gen_ai_hub.orchestration_v2 import PromptTemplatingModuleConfig as prompt_flat
    from gen_ai_hub.orchestration_v2.models.template import PromptTemplatingModuleConfig as prompt
    assert prompt_flat == prompt

    from gen_ai_hub.orchestration_v2 import TranslationModuleConfig as translation_flat
    from gen_ai_hub.orchestration_v2.models.translation import TranslationModuleConfig as translation
    assert translation_flat == translation

    from gen_ai_hub.orchestration_v2 import GroundingModuleConfig as grounding_flat
    from gen_ai_hub.orchestration_v2.models.document_grounding import GroundingModuleConfig as grounding
    assert grounding_flat == grounding

    from gen_ai_hub.orchestration_v2 import FilteringModuleConfig as filtering_flat
    from gen_ai_hub.orchestration_v2.models.content_filtering import FilteringModuleConfig as filtering
    assert filtering_flat == filtering
