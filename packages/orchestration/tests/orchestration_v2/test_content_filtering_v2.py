import pytest
from pydantic import ValidationError
from gen_ai_hub.orchestration_v2.models.content_filtering import FilteringModuleConfig, InputFiltering, OutputFiltering
from gen_ai_hub.orchestration_v2.models.llama_guard_3_filter import LlamaGuard38bFilter
from gen_ai_hub.orchestration_v2.models.content_filter import (LlamaGuard38bFilterConfig, ContentFilter,
                                                               ContentFilterProvider)


def make_mock_content_filter():
    """Factory for minimal valid ContentFilter instance for tests."""
    return LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter())

def make_mock_content_filter_backward_compatibility():
    """Factory for minimal valid ContentFilter instance for tests."""
    return ContentFilter(type=ContentFilterProvider.LLAMA_GUARD_3_8B, config=None)

def test_filtering_module_config_min_properties_none():
    """Should raise ValidationError if both input and output are missing (enforced by model validator)."""
    with pytest.raises(ValidationError):
        FilteringModuleConfig()

def test_filtering_module_config_min_properties_input_only():
    """Should succeed with only input filters set."""
    input_filters = InputFiltering(filters=[make_mock_content_filter()])
    config = FilteringModuleConfig(input=input_filters)
    assert config.input is not None and config.output is None, "Output should be None when input is provided only"

def test_filtering_module_config_min_properties_output_only():
    """Should succeed with only output filters set."""
    output_filters = OutputFiltering(filters=[make_mock_content_filter()])
    config = FilteringModuleConfig(output=output_filters)
    assert config.output is not None and config.input is None, "Input should be None when output is provided only"

def test_filtering_module_config_min_properties_both():
    """Should succeed when both input and output filters are set."""
    input_filters = InputFiltering(filters=[make_mock_content_filter()])
    output_filters = OutputFiltering(filters=[make_mock_content_filter()])
    config = FilteringModuleConfig(input=input_filters, output=output_filters)
    assert config.input is not None, "Input should not be None"
    assert config.output is not None, "Output should not be None"

def test_filtering_module_config_min_properties_both_backward_compatibility():
    """Should succeed when both input and output filters are set."""
    input_filters = InputFiltering(filters=[make_mock_content_filter_backward_compatibility()])
    output_filters = OutputFiltering(filters=[make_mock_content_filter_backward_compatibility()])
    config = FilteringModuleConfig(input=input_filters, output=output_filters)
    assert config.input is not None, "Input should not be None"
    assert config.output is not None, "Output should not be None"
