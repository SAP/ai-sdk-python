expected = {
    # cache_control
    "CacheControl",

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
    "StreamCompletionPostResponse", "ErrorResponse", "ErrorResponseStreaming", "OrchestrationResponseWithRetries", "CacheCreationTokenDetails",

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
    "OrchestrationError", "OrchestrationErrorList",
        }


def test_flat_import_all():
    import sap_ai_sdk_orchestration as module
    assert set(module.__all__) == expected

def test_flat_and_not_flat_import_by_name():
    from sap_ai_sdk_orchestration import OrchestrationService as service_flat
    from sap_ai_sdk_orchestration.service import OrchestrationService as service
    assert service_flat == service

    from sap_ai_sdk_orchestration import EmbeddingsOrchestrationConfig as embed_config_flat
    from sap_ai_sdk_orchestration.models.embeddings import EmbeddingsOrchestrationConfig as embed_config
    assert embed_config_flat == embed_config

    from sap_ai_sdk_orchestration import OrchestrationConfig as config_flat
    from sap_ai_sdk_orchestration.models.config import OrchestrationConfig as config
    assert config_flat == config

    from sap_ai_sdk_orchestration import MaskingModuleConfig as masking_flat
    from sap_ai_sdk_orchestration.models.data_masking import MaskingModuleConfig as masking
    assert masking_flat == masking

    from sap_ai_sdk_orchestration import PromptTemplatingModuleConfig as prompt_flat
    from sap_ai_sdk_orchestration.models.template import PromptTemplatingModuleConfig as prompt
    assert prompt_flat == prompt

    from sap_ai_sdk_orchestration import TranslationModuleConfig as translation_flat
    from sap_ai_sdk_orchestration.models.translation import TranslationModuleConfig as translation
    assert translation_flat == translation

    from sap_ai_sdk_orchestration import GroundingModuleConfig as grounding_flat
    from sap_ai_sdk_orchestration.models.document_grounding import GroundingModuleConfig as grounding
    assert grounding_flat == grounding

    from sap_ai_sdk_orchestration import FilteringModuleConfig as filtering_flat
    from sap_ai_sdk_orchestration.models.content_filtering import FilteringModuleConfig as filtering
    assert filtering_flat == filtering
