from __future__ import annotations

from dataclasses import dataclass
import json
import os
from urllib.parse import urlparse


DEFAULT_BASE_URLS = {
    "anthropic": "https://api.anthropic.com",
    "openai-compatible": "https://api.openai.com/v1",
}


@dataclass(frozen=True)
class Settings:
    provider: str
    base_url: str
    api_key: str
    timeout_seconds: int
    auth_mode: str = "explicit"


def _normalize_provider(value: str | None) -> str:
    provider = (value or "anthropic").strip().lower()
    if provider not in DEFAULT_BASE_URLS:
        raise ValueError(f"Unsupported provider: {provider}")
    return provider


def is_localhost_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"127.0.0.1", "localhost"}


def load_settings(*, provider_override: str | None = None) -> Settings:
    provider = _normalize_provider(provider_override or os.environ.get("AGX_PROVIDER"))
    base_url = (os.environ.get("AGX_BASE_URL") or DEFAULT_BASE_URLS[provider]).rstrip("/")
    api_key = os.environ.get("AGX_API_KEY", "").strip()
    auth_mode = "explicit"
    if not api_key and provider == "anthropic" and is_localhost_url(base_url):
        # Local Anthropic-compatible proxies often ignore auth but still expect the header shape.
        api_key = "dummy"
        auth_mode = "local_proxy_dummy"
    timeout_seconds = int(os.environ.get("AGX_TIMEOUT_SECONDS", "300"))
    return Settings(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
        auth_mode=auth_mode,
    )


def settings_with_provider(settings: Settings, provider: str) -> Settings:
    normalized = _normalize_provider(provider)
    if normalized == settings.provider:
        return settings
    return load_settings(provider_override=normalized)


def current_model_aliases() -> dict[str, str]:
    raw = os.environ.get("AGX_MODEL_ALIASES_JSON", "").strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("AGX_MODEL_ALIASES_JSON must decode to a JSON object.")
    return {
        key: value
        for key, value in parsed.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def current_fallbacks() -> dict[str, list[str]]:
    raw = os.environ.get("AGX_DEFAULT_FALLBACKS_JSON", "").strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("AGX_DEFAULT_FALLBACKS_JSON must decode to a JSON object.")
    return {
        key: [item for item in value if isinstance(item, str)]
        for key, value in parsed.items()
        if isinstance(key, str) and isinstance(value, list)
    }


def resolve_model(name: str) -> str:
    return current_model_aliases().get(name, name)


def fallback_chain(primary: str, requested: list[str] | None = None) -> list[str]:
    chain = [primary]
    extras = requested if requested is not None else current_fallbacks().get(primary, [])
    for model in extras:
        if model not in chain:
            chain.append(model)
    return chain
