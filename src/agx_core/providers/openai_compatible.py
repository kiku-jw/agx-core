from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from .base import ProviderAdapter, ProviderError, ProviderRequest, ProviderResponse


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif item.get("type") == "text" and isinstance(item.get("content"), str):
                parts.append(item["content"])
        return "\n".join(parts).strip()
    return ""


class OpenAICompatibleAdapter(ProviderAdapter):
    name = "openai-compatible"

    def __init__(self, *, base_url: str, api_key: str, timeout_seconds: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

    def list_models(self) -> tuple[list[str], str | None]:
        req = request.Request(
            f"{self.base_url}/models",
            headers=self._headers(),
            method="GET",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return [], f"HTTP {exc.code}: {body}"
        except error.URLError as exc:
            return [], f"Could not reach provider: {exc.reason}"
        except ValueError:
            return [], "Provider returned invalid JSON for model list."

        data = payload.get("data", [])
        if not isinstance(data, list):
            return [], "Provider returned an invalid model list shape."
        models = [
            item.get("id", "")
            for item in data
            if isinstance(item, dict) and item.get("id")
        ]
        if not models:
            return [], "Provider returned no model ids."
        return sorted(set(models)), None

    def invoke(self, request_payload: ProviderRequest) -> ProviderResponse:
        payload = {
            "model": request_payload.model,
            "messages": [{"role": "user", "content": request_payload.prompt}],
            "max_tokens": request_payload.max_output_tokens,
        }
        req = request.Request(
            f"{request_payload.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=request_payload.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(f"Provider returned HTTP {exc.code}: {body}") from exc
        except error.URLError as exc:
            raise ProviderError(f"Could not reach provider: {exc.reason}") from exc
        except ValueError as exc:
            raise ProviderError("Provider returned invalid JSON.") from exc

        choices = raw.get("choices", [])
        message = choices[0].get("message", {}) if isinstance(choices, list) and choices else {}
        text_output = _content_to_text(message.get("content"))
        usage = raw.get("usage", {}) if isinstance(raw.get("usage"), dict) else {}
        return ProviderResponse(
            request_payload=payload,
            raw_payload=raw,
            text_output=text_output,
            provider_model=str(raw.get("model", request_payload.model)),
            usage=usage,
        )

