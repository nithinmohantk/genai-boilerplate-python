"""
GenAI client for AI model integration.
Provides a unified interface for different AI providers.
"""

import logging
from typing import Any

from config.settings import settings

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
        self, provider: str = "openai"
    ) -> list[dict[str, Any]]:
        """Get available models for a provider."""
        # Mock model list - in production, fetch from actual providers
        mock_models = {
            "openai": [
                {"id": "gpt-4", "name": "GPT-4", "context_window": 8192},
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "context_window": 4096,
                },
                {
                    "id": "gpt-3.5-turbo-16k",
                    "name": "GPT-3.5 Turbo 16K",
                    "context_window": 16384,
                },
            ],
            "anthropic": [
                {
                    "id": "claude-3-haiku-20240307",
                    "name": "Claude 3 Haiku",
                    "context_window": 200000,
                },
                {
                    "id": "claude-3-sonnet-20240229",
                    "name": "Claude 3 Sonnet",
                    "context_window": 200000,
                },
                {
                    "id": "claude-3-opus-20240229",
                    "name": "Claude 3 Opus",
                    "context_window": 200000,
                },
            ],
            "google": [
                {"id": "gemini-pro", "name": "Gemini Pro", "context_window": 32000},
                {
                    "id": "gemini-pro-vision",
                    "name": "Gemini Pro Vision",
                    "context_window": 16000,
                },
            ],
        }

        return mock_models.get(provider, [])

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


# Global client instance
genai_client = GenAIClient()
