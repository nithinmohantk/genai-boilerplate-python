"""
AI Models Configuration
Support for the latest AI models from OpenAI, Anthropic, Google, and other providers.
"""

from enum import Enum
from typing import Any


class ModelProvider(str, Enum):
    """AI model providers enum."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class ModelCapability(str, Enum):
    """Model capabilities."""

    TEXT = "text"
    VISION = "vision"
    CODE = "code"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"
    STREAMING = "streaming"


# OpenAI Models Configuration
OPENAI_MODELS: dict[str, dict[str, Any]] = {
    # GPT-4 Models
    "gpt-4": {
        "name": "GPT-4",
        "provider": ModelProvider.OPENAI,
        "context_window": 8192,
        "max_tokens": 4096,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.03,
        "cost_per_1k_output": 0.06,
        "supports_streaming": True,
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "provider": ModelProvider.OPENAI,
        "context_window": 128000,
        "max_tokens": 4096,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.01,
        "cost_per_1k_output": 0.03,
        "supports_streaming": True,
    },
    "gpt-4o": {
        "name": "GPT-4o",
        "provider": ModelProvider.OPENAI,
        "context_window": 128000,
        "max_tokens": 4096,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.015,
        "supports_streaming": True,
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": ModelProvider.OPENAI,
        "context_window": 128000,
        "max_tokens": 16384,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
        "supports_streaming": True,
    },
    "gpt-4.1": {
        "name": "GPT-4.1",
        "provider": ModelProvider.OPENAI,
        "context_window": 200000,
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.008,
        "cost_per_1k_output": 0.024,
        "supports_streaming": True,
    },
    "gpt-4.1-mini": {
        "name": "GPT-4.1 Mini",
        "provider": ModelProvider.OPENAI,
        "context_window": 200000,
        "max_tokens": 16384,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.0001,
        "cost_per_1k_output": 0.0004,
        "supports_streaming": True,
    },
    "gpt-4.1-nano": {
        "name": "GPT-4.1 Nano",
        "provider": ModelProvider.OPENAI,
        "context_window": 128000,
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.00005,
        "cost_per_1k_output": 0.0002,
        "supports_streaming": True,
    },
    # GPT-3.5 Models
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "provider": ModelProvider.OPENAI,
        "context_window": 16385,
        "max_tokens": 4096,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.0015,
        "cost_per_1k_output": 0.002,
        "supports_streaming": True,
    },
    "gpt-3.5-turbo-16k": {
        "name": "GPT-3.5 Turbo 16K",
        "provider": ModelProvider.OPENAI,
        "context_window": 16385,
        "max_tokens": 4096,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.004,
        "supports_streaming": True,
    },
    # GPT-5 Models (Production Ready - Released)
    "gpt-5": {
        "name": "GPT-5",
        "provider": ModelProvider.OPENAI,
        "context_window": 1000000,
        "max_tokens": 32768,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.01,
        "cost_per_1k_output": 0.03,
        "supports_streaming": True,
    },
    "gpt-5.0-mini": {
        "name": "GPT-5.0 Mini",
        "provider": ModelProvider.OPENAI,
        "context_window": 500000,
        "max_tokens": 16384,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.001,
        "cost_per_1k_output": 0.003,
        "supports_streaming": True,
    },
    "gpt-5.0-nano": {
        "name": "GPT-5.0 Nano",
        "provider": ModelProvider.OPENAI,
        "context_window": 200000,
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
        ],
        "cost_per_1k_input": 0.0001,
        "cost_per_1k_output": 0.0003,
        "supports_streaming": True,
    },
    # Open Source Models
    "gpt-oss-20b": {
        "name": "GPT-OSS 20B",
        "provider": ModelProvider.OPENAI,
        "context_window": 4096,
        "max_tokens": 2048,
        "capabilities": [ModelCapability.TEXT],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": True,
        "open_source": True,
    },
}


# Anthropic Models Configuration
ANTHROPIC_MODELS: dict[str, dict[str, Any]] = {
    # Claude 3 Models
    "claude-3-haiku-20240307": {
        "name": "Claude 3 Haiku",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 200000,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.VISION],
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.00125,
        "supports_streaming": True,
    },
    "claude-3-sonnet-20240229": {
        "name": "Claude 3 Sonnet",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 200000,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.VISION],
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
        "supports_streaming": True,
    },
    "claude-3-opus-20240229": {
        "name": "Claude 3 Opus",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 200000,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.VISION],
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
        "supports_streaming": True,
    },
    # Claude 3.5 Models
    "claude-3-5-sonnet-20241022": {
        "name": "Claude 3.5 Sonnet",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 200000,
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
        ],
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
        "supports_streaming": True,
    },
    "claude-3-5-haiku-20241022": {
        "name": "Claude 3.5 Haiku",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 200000,
        "max_tokens": 8192,
        "capabilities": [ModelCapability.TEXT, ModelCapability.VISION],
        "cost_per_1k_input": 0.0008,
        "cost_per_1k_output": 0.004,
        "supports_streaming": True,
    },
    # Claude 3.7 Models (Production Ready - Released)
    "claude-3-7-sonnet": {
        "name": "Claude 3.7 Sonnet",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 500000,
        "max_tokens": 16384,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
        ],
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.025,
        "supports_streaming": True,
    },
    # Claude 4.0 Models (Production Ready - Released)
    "claude-4-0-opus": {
        "name": "Claude 4.0 Opus",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 1000000,
        "max_tokens": 32768,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
        ],
        "cost_per_1k_input": 0.02,
        "cost_per_1k_output": 0.1,
        "supports_streaming": True,
    },
    "claude-4-0-sonnet": {
        "name": "Claude 4.0 Sonnet",
        "provider": ModelProvider.ANTHROPIC,
        "context_window": 1000000,
        "max_tokens": 16384,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
        ],
        "cost_per_1k_input": 0.01,
        "cost_per_1k_output": 0.05,
        "supports_streaming": True,
    },
}


# Google Models Configuration
GOOGLE_MODELS: dict[str, dict[str, Any]] = {
    # Gemini 1.5 Models
    "gemini-1.5-flash": {
        "name": "Gemini 1.5 Flash",
        "provider": ModelProvider.GOOGLE,
        "context_window": 1048576,  # 1M tokens
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
        ],
        "cost_per_1k_input": 0.00035,
        "cost_per_1k_output": 0.0014,
        "supports_streaming": True,
    },
    "gemini-1.5-pro": {
        "name": "Gemini 1.5 Pro",
        "provider": ModelProvider.GOOGLE,
        "context_window": 2097152,  # 2M tokens
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
        ],
        "cost_per_1k_input": 0.0035,
        "cost_per_1k_output": 0.014,
        "supports_streaming": True,
    },
    # Gemini 2.5 Models (Latest)
    "gemini-2.5-flash": {
        "name": "Gemini 2.5 Flash",
        "provider": ModelProvider.GOOGLE,
        "context_window": 1048576,  # 1M tokens
        "max_tokens": 8192,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
        ],
        "cost_per_1k_input": 0.0003,
        "cost_per_1k_output": 0.0012,
        "supports_streaming": True,
    },
    "gemini-2.5-pro": {
        "name": "Gemini 2.5 Pro",
        "provider": ModelProvider.GOOGLE,
        "context_window": 2097152,  # 2M tokens
        "max_tokens": 16384,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
        ],
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.012,
        "supports_streaming": True,
    },
    # Legacy Gemini Models
    "gemini-pro": {
        "name": "Gemini Pro",
        "provider": ModelProvider.GOOGLE,
        "context_window": 32000,
        "max_tokens": 2048,
        "capabilities": [ModelCapability.TEXT],
        "cost_per_1k_input": 0.0005,
        "cost_per_1k_output": 0.0015,
        "supports_streaming": True,
    },
    "gemini-pro-vision": {
        "name": "Gemini Pro Vision",
        "provider": ModelProvider.GOOGLE,
        "context_window": 16000,
        "max_tokens": 2048,
        "capabilities": [ModelCapability.TEXT, ModelCapability.VISION],
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.0005,
        "supports_streaming": True,
    },
}


# Azure OpenAI Models Configuration
AZURE_OPENAI_MODELS: dict[str, dict[str, Any]] = {
    "gpt-4": {
        "name": "GPT-4 (Azure)",
        "provider": ModelProvider.AZURE_OPENAI,
        "context_window": 8192,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.FUNCTION_CALLING],
        "supports_streaming": True,
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo (Azure)",
        "provider": ModelProvider.AZURE_OPENAI,
        "context_window": 128000,
        "max_tokens": 4096,
        "capabilities": [
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
        ],
        "supports_streaming": True,
    },
    "gpt-35-turbo": {
        "name": "GPT-3.5 Turbo (Azure)",
        "provider": ModelProvider.AZURE_OPENAI,
        "context_window": 16385,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.FUNCTION_CALLING],
        "supports_streaming": True,
    },
}


# Hugging Face Models Configuration
HUGGINGFACE_MODELS: dict[str, dict[str, Any]] = {
    "microsoft/DialoGPT-medium": {
        "name": "DialoGPT Medium",
        "provider": ModelProvider.HUGGINGFACE,
        "context_window": 1024,
        "max_tokens": 1024,
        "capabilities": [ModelCapability.TEXT],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": False,
        "open_source": True,
    },
    "microsoft/DialoGPT-large": {
        "name": "DialoGPT Large",
        "provider": ModelProvider.HUGGINGFACE,
        "context_window": 1024,
        "max_tokens": 1024,
        "capabilities": [ModelCapability.TEXT],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": False,
        "open_source": True,
    },
    "meta-llama/Llama-2-7b-chat-hf": {
        "name": "Llama 2 7B Chat",
        "provider": ModelProvider.HUGGINGFACE,
        "context_window": 4096,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.CODE],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": True,
        "open_source": True,
    },
    "meta-llama/Llama-2-13b-chat-hf": {
        "name": "Llama 2 13B Chat",
        "provider": ModelProvider.HUGGINGFACE,
        "context_window": 4096,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.CODE],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": True,
        "open_source": True,
    },
    "meta-llama/Llama-2-70b-chat-hf": {
        "name": "Llama 2 70B Chat",
        "provider": ModelProvider.HUGGINGFACE,
        "context_window": 4096,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.CODE],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": True,
        "open_source": True,
    },
    "mistralai/Mistral-7B-Instruct-v0.1": {
        "name": "Mistral 7B Instruct",
        "provider": ModelProvider.HUGGINGFACE,
        "context_window": 8192,
        "max_tokens": 4096,
        "capabilities": [ModelCapability.TEXT, ModelCapability.CODE],
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "supports_streaming": True,
        "open_source": True,
    },
}


# Combined models configuration
ALL_MODELS: dict[str, dict[str, Any]] = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **GOOGLE_MODELS,
    **AZURE_OPENAI_MODELS,
    **HUGGINGFACE_MODELS,
}


def get_models_by_provider(provider: ModelProvider) -> dict[str, dict[str, Any]]:
    """Get all models for a specific provider."""
    provider_models = {
        ModelProvider.OPENAI: OPENAI_MODELS,
        ModelProvider.ANTHROPIC: ANTHROPIC_MODELS,
        ModelProvider.GOOGLE: GOOGLE_MODELS,
        ModelProvider.AZURE_OPENAI: AZURE_OPENAI_MODELS,
        ModelProvider.HUGGINGFACE: HUGGINGFACE_MODELS,
    }
    return provider_models.get(provider, {})


def get_model_info(model_id: str) -> dict[str, Any] | None:
    """Get information about a specific model."""
    return ALL_MODELS.get(model_id)


def get_available_providers() -> list[str]:
    """Get list of available providers."""
    return [provider.value for provider in ModelProvider]


def get_models_with_capability(
    capability: ModelCapability,
) -> dict[str, dict[str, Any]]:
    """Get all models that support a specific capability."""
    return {
        model_id: model_info
        for model_id, model_info in ALL_MODELS.items()
        if capability in model_info.get("capabilities", [])
    }


def is_model_experimental(model_id: str) -> bool:
    """Check if a model is experimental/future."""
    model_info = get_model_info(model_id)
    return model_info.get("experimental", False) if model_info else False


def get_production_models() -> dict[str, dict[str, Any]]:
    """Get only production-ready (non-experimental) models."""
    return {
        model_id: model_info
        for model_id, model_info in ALL_MODELS.items()
        if not model_info.get("experimental", False)
    }


def get_open_source_models() -> dict[str, dict[str, Any]]:
    """Get only open source models."""
    return {
        model_id: model_info
        for model_id, model_info in ALL_MODELS.items()
        if model_info.get("open_source", False)
    }


def calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate the cost for using a model with given token counts."""
    model_info = get_model_info(model_id)
    if not model_info:
        return 0.0

    input_cost = model_info.get("cost_per_1k_input", 0) * (input_tokens / 1000)
    output_cost = model_info.get("cost_per_1k_output", 0) * (output_tokens / 1000)

    return input_cost + output_cost
