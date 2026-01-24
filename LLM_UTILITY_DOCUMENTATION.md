# LLM Utility Module Documentation

## Overview
The LLM utility module (`src/utils/llm.py`) provides a centralized abstraction for LLM (Large Language Model) calls across the project, following the same pattern as the logger utility.

## Features

- **Centralized LLM Configuration**: All LLM configurations in one place
- **Factory Pattern**: Easy creation of different LLM provider instances
- **Test Mode Support**: Mock API keys for testing without real API calls
- **Consistent Error Handling**: Standardized validation and error messages
- **Extensible Architecture**: Easy to add new LLM providers
- **Project Standards Compliance**: Follows the same pattern as logger utility

## Usage Examples

### Basic Usage
```python
from utils.llm import get_llm

# Get default LLM instance (ZhipuAI glm-4-flash)
llm = get_llm()

# Get specific model with custom temperature
llm = get_llm(
    provider="zhipu",
    model="glm-4",
    temperature=0.7
)

# Get LLM in test mode (uses mock API key)
llm = get_llm(test_mode=True)
```

### Integration with WeatherAgent
```python
from utils.llm import get_llm

class WeatherAgent(AgentBase):
    def __init__(self, model="glm-4-flash", temperature=0, test_mode=False):
        super().__init__()
        # Use LLM utility instead of direct ChatZhipuAI instantiation
        self.llm = get_llm(
            provider="zhipu",
            model=model,
            temperature=temperature,
            test_mode=test_mode
        )
        self.tools = [get_current_weather, get_weather_forecast]
```

## Architecture

### `LLMFactory` Class
Factory class for creating different types of LLMs:

- `create_zhipu_llm()`: Creates configured ZhipuAI LLM instances
- Handles API key validation and test mode configuration

### `get_llm()` Function
Main entry point for getting LLM instances:

- Parameters:
  - `provider`: LLM provider (default: "zhipu")
  - `model`: Model name (default: "glm-4-flash")
  - `temperature`: Temperature parameter (default: 0.0)
  - `api_key`: Optional API key (uses environment variable if not provided)
  - `test_mode`: Enable test mode with mock API key
  - `**kwargs`: Additional provider-specific parameters

### `get_default_llm()` Function
Convenience function for getting the default LLM configuration.

## Error Handling

The LLM utility provides standardized error messages:

- API key not found in environment variables
- Unsupported LLM provider specified
- Invalid parameters for specific LLM providers

## Extending the Utility

To add a new LLM provider:

1. Update the `LLMFactory` class with a new creation method
2. Update the `get_llm()` function to handle the new provider
3. Add any necessary dependencies

Example:
```python
class LLMFactory:
    # Existing methods...
    
    @staticmethod
    def create_openai_llm(model="gpt-3.5-turbo", temperature=0.0, api_key=None, test_mode=False):
        # Implementation for OpenAI LLM creation
        pass

def get_llm(provider="zhipu", **kwargs):
    if provider.lower() == "zhipu":
        return LLMFactory.create_zhipu_llm(**kwargs)
    elif provider.lower() == "openai":
        return LLMFactory.create_openai_llm(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

## Configuration

### Environment Variables
- `ZHIPU_API_KEY`: ZhipuAI API key (required for non-test mode)

### Test Mode
Test mode can be enabled by setting `test_mode=True` when calling `get_llm()`. This uses a mock API key and bypasses validation, useful for testing without making real API calls.

## Logging

All LLM operations are logged with the `LLM_UTIL` source identifier, providing consistent logging across the project:

```
2026-01-24 21:34:31,981 - utils.llm - INFO - [LLM_UTIL] Getting LLM: provider=zhipu, model=glm-4-flash
2026-01-24 21:34:31,981 - utils.llm - INFO - [LLM_UTIL] Creating ZhipuAI LLM in test mode: glm-4-flash
```

## Testing

A test file is available at `test/test_llm_utility.py` that verifies the LLM utility functions correctly:

```bash
python test/test_llm_utility.py
```

## Migration Guide

### Before (Direct LLM Instantiation)
```python
from langchain_community.chat_models import ChatZhipuAI

class WeatherAgent:
    def __init__(self):
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("API key not found")
        self.llm = ChatZhipuAI(model="glm-4-flash", temperature=0, api_key=api_key)
```

### After (Using LLM Utility)
```python
from utils.llm import get_llm

class WeatherAgent:
    def __init__(self):
        self.llm = get_llm(provider="zhipu", model="glm-4-flash", temperature=0)
```

## Benefits

- **Reduced Code Duplication**: No more copying API key validation across agents
- **Easier Provider Switching**: Change LLM providers in one place
- **Consistent Configuration**: All LLM settings follow the same pattern
- **Better Testability**: Built-in test mode support
- **Improved Maintainability**: Centralized updates for LLM configurations

## Future Enhancements

- Support for additional LLM providers (OpenAI, Anthropic, etc.)
- Caching of LLM responses
- Rate limiting functionality
- Automatic retries for failed LLM calls
- Performance monitoring for LLM operations