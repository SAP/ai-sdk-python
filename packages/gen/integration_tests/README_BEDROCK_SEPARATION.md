# Bedrock Model Separation Guide

This document explains how to separate Bedrock models from standard models in your integration tests.

## Overview

The `setup_aicore.py` module now provides separate setup functions and mixins to handle different model types:

- **Bedrock models**: Amazon and Anthropic models available via AWS Bedrock
- **Standard models**: All other models (OpenAI, Google, IBM, etc.)

## Available Functions

### Setup Functions

1. **`setup_bedrock_models(client)`** - Sets up only Bedrock models
2. **`setup_standard_models(client)`** - Sets up only standard (non-Bedrock) models  
3. **`setup_aicore_instance(client)`** - Sets up all models (backward compatibility)

### Helper Functions

- **`get_bedrock_models()`** - Returns list of Bedrock model tuples
- **`get_standard_models()`** - Returns list of standard model tuples

### Test Mixins

1. **`TestCaseAICoreSetupMixin`** - Sets up all models (original behavior)
2. **`TestCaseBedrockSetupMixin`** - Sets up only Bedrock models
3. **`TestCaseStandardSetupMixin`** - Sets up only standard models

## Usage Examples

### For Bedrock Tests (marked with @pytest.mark.bedrock)

```python
import pytest
from integration_tests.setup_aicore import TestCaseBedrockSetupMixin

@pytest.mark.bedrock
class TestAmazonServices(TestCaseBedrockSetupMixin, unittest.TestCase):
    def test_bedrock_functionality(self):
        # This test will only have Bedrock models deployed
        # Access via self.aicore_deployments
        pass
```

### For Standard Tests

```python
from integration_tests.setup_aicore import TestCaseStandardSetupMixin

class TestOpenAIServices(TestCaseStandardSetupMixin, unittest.TestCase):
    def test_openai_functionality(self):
        # This test will only have standard models deployed
        # Access via self.aicore_deployments
        pass
```

### For Mixed Tests (Backward Compatible)

```python
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin

class TestAllServices(TestCaseAICoreSetupMixin, unittest.TestCase):
    def test_mixed_functionality(self):
        # This test will have all models deployed (original behavior)
        # Access via self.aicore_deployments
        pass
```

## Model Categories

### Bedrock Models
- `amazon--titan-embed-image`
- `amazon--titan-embed-text`
- `amazon--nova-micro`
- `amazon--nova-lite` 
- `amazon--nova-pro`
- `amazon--nova-premier`
- `anthropic--claude-3-haiku`
- `anthropic--claude-4-opus`
- `anthropic--claude-3.5-sonnet`
- `anthropic--claude-3.7-sonnet`
- `anthropic--claude-4-sonnet`

### Standard Models
- OpenAI models (`gpt-4o`, `gpt-4o-mini`, etc.)
- Google models (`gemini-2.0-flash`, etc.)
- Mistral models (`mistralai--mistral-small-instruct`, etc.)
- Embedding models (`text-embedding-3-small`, etc.)

## Running Tests

### Run only Bedrock tests
```bash
pytest -m bedrock
```

### Run only non-Bedrock tests
(credentials for US10 intprod required - see in main README.md section "Running Bedrock Tests")
```bash
pytest -m "not bedrock"
```

### Run all tests
```bash
pytest
```

## Benefits

1. **Faster Test Execution**: Bedrock tests only deploy Bedrock models
2. **Resource Optimization**: Reduced deployment overhead for specific test suites
3. **Environment Separation**: Clear separation between Bedrock and standard environments
4. **Backward Compatibility**: Existing tests continue to work unchanged
5. **Targeted Testing**: Easier to run specific test suites in different environments

## Migration Guide

To migrate existing Bedrock tests:

1. Import the new mixin: 
   ```python
   from integration_tests.setup_aicore import TestCaseBedrockSetupMixin
   ```

2. Replace `TestCaseAICoreSetupMixin` with `TestCaseBedrockSetupMixin` for classes marked with `@pytest.mark.bedrock`:
   ```python
   @pytest.mark.bedrock
   class TestBedrock(TestCaseBedrockSetupMixin, unittest.TestCase):  # Changed here
       # Your test methods remain the same
   ```

3. No changes needed to test methods - they'll continue to access `self.aicore_deployments` as before.
