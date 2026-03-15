from __future__ import annotations

from agx_core.config import Settings

from .anthropic import AnthropicAdapter
from .base import ProviderAdapter
from .openai_compatible import OpenAICompatibleAdapter


def provider_from_settings(settings: Settings) -> ProviderAdapter:
    if settings.provider == "anthropic":
        return AnthropicAdapter(
            base_url=settings.base_url,
            api_key=settings.api_key,
            timeout_seconds=settings.timeout_seconds,
        )
    if settings.provider == "openai-compatible":
        return OpenAICompatibleAdapter(
            base_url=settings.base_url,
            api_key=settings.api_key,
            timeout_seconds=settings.timeout_seconds,
        )
    raise ValueError(f"Unsupported provider: {settings.provider}")

