def test_not_flat_and_flat_import_by_name():
    from sap_ai_sdk_prompt_registry import PromptTemplateClient as client_flat
    from sap_ai_sdk_prompt_registry.client import PromptTemplateClient as client
    assert client_flat == client

    from sap_ai_sdk_prompt_registry import PromptTemplateClient as client_flat_2
    from sap_ai_sdk_prompt_registry.client import PromptTemplateClient as client_2
    assert client_flat_2 == client_2

    from sap_ai_sdk_prompt_registry import PromptTemplate as prompt_flat
    from sap_ai_sdk_prompt_registry.models.prompt_template import PromptTemplate as prompt
    assert prompt_flat == prompt

    from sap_ai_sdk_prompt_registry import PromptTemplateSpec as prompt_spec_flat
    from sap_ai_sdk_prompt_registry.models.prompt_template import PromptTemplateSpec as prompt_spec
    assert prompt_spec_flat == prompt_spec

    from sap_ai_sdk_prompt_registry import OrchestrationConfigGetResponse as orchestration_config_get_response_flat
    from sap_ai_sdk_prompt_registry.models.orchestration_config import (OrchestrationConfigGetResponse
                                                                        as orchestration_config_get_response)
    assert orchestration_config_get_response_flat == orchestration_config_get_response
