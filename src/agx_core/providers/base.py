from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class ProviderError(RuntimeError):
    """Raised when a provider request fails."""


@dataclass(frozen=True)
class ProviderRequest:
    model: str
    prompt: str
    max_output_tokens: int
    api_key: str
    base_url: str
    timeout_seconds: int


@dataclass(frozen=True)
class ProviderResponse:
    request_payload: dict[str, Any]
    raw_payload: dict[str, Any]
    text_output: str
    provider_model: str
    usage: dict[str, Any]


class ProviderAdapter(Protocol):
    name: str

    def list_models(self) -> tuple[list[str], str | None]:
        ...

    def invoke(self, request: ProviderRequest) -> ProviderResponse:
        ...

