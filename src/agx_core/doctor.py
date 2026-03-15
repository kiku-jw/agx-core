from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import Settings, current_fallbacks, current_model_aliases
from .providers import provider_from_settings
from .providers.base import ProviderAdapter


@dataclass(frozen=True)
class DoctorReport:
    status: str
    provider: str
    base_url: str
    api_key_configured: bool
    auth_mode: str
    model_count: int
    models: list[str]
    model_fetch_error: str | None
    model_aliases: dict[str, str]
    default_fallbacks: dict[str, list[str]]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_doctor(settings: Settings, *, adapter: ProviderAdapter | None = None) -> DoctorReport:
    aliases = current_model_aliases()
    fallbacks = current_fallbacks()
    notes: list[str] = []

    if not settings.api_key:
        return DoctorReport(
            status="failed",
            provider=settings.provider,
            base_url=settings.base_url,
            api_key_configured=False,
            auth_mode=settings.auth_mode,
            model_count=0,
            models=[],
            model_fetch_error="AGX_API_KEY is not configured.",
            model_aliases=aliases,
            default_fallbacks=fallbacks,
            notes=["Set AGX_API_KEY before running provider checks."],
        )

    effective_adapter = adapter or provider_from_settings(settings)
    models, model_fetch_error = effective_adapter.list_models()
    if model_fetch_error:
        notes.append(model_fetch_error)
    if settings.auth_mode == "local_proxy_dummy":
        notes.append(
            "Using local proxy auth mode: no AGX_API_KEY was provided, so agx-core supplied a dummy header for localhost."
        )

    missing_alias_targets = sorted({value for value in aliases.values() if value not in models})
    if missing_alias_targets:
        notes.append(
            "Some AGX model aliases are not advertised by the current backend: "
            + ", ".join(missing_alias_targets)
        )

    status = "healthy"
    if model_fetch_error and not models:
        status = "failed"
    elif missing_alias_targets or model_fetch_error:
        status = "warning"

    return DoctorReport(
        status=status,
        provider=settings.provider,
        base_url=settings.base_url,
        api_key_configured=True,
        auth_mode=settings.auth_mode,
        model_count=len(models),
        models=models,
        model_fetch_error=model_fetch_error,
        model_aliases=aliases,
        default_fallbacks=fallbacks,
        notes=notes,
    )
