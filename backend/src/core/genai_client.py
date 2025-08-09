"""
GenAI client for AI model integration.
Provides a unified interface for different AI providers.
"""

import logging
from typing import Any, List, Dict

from config.settings import settings
from config.ai_models import (
    ALL_MODELS,
    ModelProvider,
    get_models_by_provider,
    get_model_info,
    get_available_providers,
    get_production_models,
)

logger = logging.getLogger(__name__)


class GenAIClient:
    """Client for AI model interactions."""

    def __init__(self, tenant_api_keys: dict[str, str] | None = None):
        self.tenant_api_keys = tenant_api_keys or {}
        self.default_model = settings.openai_model
        self.default_temperature = settings.openai_temperature
        self.default_max_tokens = settings.openai_max_tokens

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        document_context: str | None = None,
    ) -> str | None:
        """Generate AI response from messages."""
        try:
            # For now, return a mock response
            # TODO: Implement actual AI provider integration

            user_message = ""
            for msg in messages:
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break

            # Mock response with context awareness
            response_parts = []

            if document_context:
                response_parts.append("Based on the provided documents,")

            response_parts.append(
                f"I understand you're asking about: '{user_message}'."
            )

            if document_context:
                response_parts.append("Here's what I found in your documents:")
                response_parts.append(
                    document_context[:200] + "..."
                    if len(document_context) > 200
                    else document_context
                )

            response_parts.append(
                "This is a mock AI response. In production, this would connect to:"
            )
            response_parts.append("• OpenAI GPT models")
            response_parts.append("• Anthropic Claude models")
            response_parts.append("• Google Gemini models")
            response_parts.append("• Azure OpenAI models")
            response_parts.append("• Custom models via API")

            return " ".join(response_parts)

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."

    async def get_available_models(
        self, provider: str = "openai", include_experimental: bool = False
    ) -> list[dict[str, Any]]:
        """Get available models for a provider."""
        try:
            # Get models from configuration
            if provider == "all":
                models_dict = get_production_models() if not include_experimental else ALL_MODELS
            else:
                provider_enum = ModelProvider(provider)
                models_dict = get_models_by_provider(provider_enum)
                
                # Filter experimental models if not requested
                if not include_experimental:
                    models_dict = {
                        k: v for k, v in models_dict.items()
                        if not v.get("experimental", False)
                    }
            
            # Convert to list format expected by API
            models_list = []
            for model_id, model_info in models_dict.items():
                models_list.append({
                    "id": model_id,
                    "name": model_info["name"],
                    "provider": model_info["provider"].value,
                    "context_window": model_info["context_window"],
                    "max_tokens": model_info["max_tokens"],
                    "capabilities": [cap.value for cap in model_info.get("capabilities", [])],
                    "supports_streaming": model_info.get("supports_streaming", False),
                    "experimental": model_info.get("experimental", False),
                    "open_source": model_info.get("open_source", False),
                })
            
            return sorted(models_list, key=lambda x: (x["provider"], x["name"]))
            
        except ValueError:
            # Invalid provider, return empty list
            logger.warning(f"Invalid provider: {provider}")
            return []

    def format_messages(
        self,
        user_message: str,
        context_messages: list | None = None,
        system_prompt: str | None = None,
        document_context: str | None = None,
    ) -> list[dict[str, str]]:
        """Format messages for AI API."""
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif document_context:
            messages.append(
                {
                    "role": "system",
                    "content": f"You are a helpful AI assistant. Use the following context to answer questions: {document_context}",
                }
            )
        else:
            messages.append({"role": "system", "content": settings.system_message})

        # Add context messages
        if context_messages:
            for msg in context_messages[-10:]:  # Last 10 messages for context
                if msg.message_type == "user":
                    messages.append({"role": "user", "content": msg.message})
                elif msg.message_type == "assistant":
                    messages.append({"role": "assistant", "content": msg.message})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    async def count_tokens(self, text: str, model: str | None = None) -> int:
        """Count tokens in text (approximate)."""
        # Simple approximation - in production, use actual tokenizer
        return len(text.split()) * 1.3  # Rough approximation

    def validate_api_key(self, provider: str, api_key: str) -> bool:
        """Validate API key for a provider."""
        # Mock validation - in production, make test API call
        return len(api_key) > 10 and api_key.startswith(("sk-", "claude-", "AIza"))
    
    def get_model_details(self, model_id: str) -> Dict[str, Any] | None:
        """Get detailed information about a specific model."""
        return get_model_info(model_id)
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported AI providers."""
        return get_available_providers()
    
    def estimate_cost(self, model_id: str, input_text: str, output_text: str) -> float:
        """Estimate the cost for a model interaction."""
        from config.ai_models import calculate_cost
        
        # Rough token estimation
        input_tokens = int(len(input_text.split()) * 1.3)
        output_tokens = int(len(output_text.split()) * 1.3)
        
        return calculate_cost(model_id, input_tokens, output_tokens)
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if a model is available and not experimental."""
        model_info = self.get_model_details(model_id)
        return model_info is not None and not model_info.get("experimental", False)
    
    def is_model_experimental(self, model_id: str) -> bool:
        """Check if a model is experimental/future."""
        model_info = self.get_model_details(model_id)
        return model_info.get("experimental", False) if model_info else False
    
    def get_models_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Get models that support a specific capability."""
        from config.ai_models import get_models_with_capability, ModelCapability
        
        try:
            cap = ModelCapability(capability)
            models_dict = get_models_with_capability(cap)
            
            # Convert to list format
            models_list = []
            for model_id, model_info in models_dict.items():
                models_list.append({
                    "id": model_id,
                    "name": model_info["name"],
                    "provider": model_info["provider"].value,
                    "context_window": model_info["context_window"],
                    "max_tokens": model_info["max_tokens"],
                    "capabilities": [cap.value for cap in model_info.get("capabilities", [])],
                })
            
            return sorted(models_list, key=lambda x: (x["provider"], x["name"]))
            
        except ValueError:
            logger.warning(f"Invalid capability: {capability}")
            return []


# Global client instance
genai_client = GenAIClient()
