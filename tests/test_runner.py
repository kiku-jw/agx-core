from pathlib import Path

from agx_core.config import Settings
from agx_core.providers.base import ProviderError, ProviderResponse
from agx_core.runner import run_task_with_fallbacks


def test_dispatch_retries_after_request_error(tmp_path: Path, monkeypatch) -> None:
    task = {
        "id": "task-1",
        "provider": "anthropic",
        "model_hint": "sonnet",
        "fallback_models": ["opus"],
        "patch_required": False,
    }
    settings = Settings(
        provider="anthropic",
        base_url="https://api.anthropic.com",
        api_key="dummy",
        timeout_seconds=10,
    )
    calls: list[str] = []

    def fake_run_task_once(*, settings, task, run_dir, model_override, max_output_tokens):
        calls.append(model_override)
        if len(calls) == 1:
            raise ProviderError("boom")
        return type(
            "Result",
            (),
            {
                "response": ProviderResponse(
                    request_payload={},
                    raw_payload={},
                    text_output='{"task_id":"task-1","status":"completed","summary":"ok"}',
                    provider_model=model_override,
                    usage={},
                ),
                "normalized_result": {
                    "task_id": "task-1",
                    "status": "completed",
                    "summary": "ok",
                    "changed_files": [],
                    "commands_run": [],
                    "verification": {"passed": [], "failed": []},
                    "risks": [],
                    "notes": [],
                    "model": model_override,
                    "received_at": "2026-03-15T00:00:00Z",
                    "parse_error": False,
                    "patch_missing": False,
                    "patch": "",
                },
            },
        )()

    monkeypatch.setattr("agx_core.runner.run_task_once", fake_run_task_once)
    dispatched = run_task_with_fallbacks(settings=settings, task=task, run_dir=tmp_path)
    assert calls == ["sonnet", "opus"]
    assert dispatched.final_result["status"] == "completed"
    assert dispatched.final_result["attempt_count"] == 2


def test_dispatch_retries_when_patch_is_missing(tmp_path: Path, monkeypatch) -> None:
    task = {
        "id": "task-2",
        "provider": "anthropic",
        "model_hint": "sonnet",
        "fallback_models": ["opus"],
        "patch_required": True,
    }
    settings = Settings(
        provider="anthropic",
        base_url="https://api.anthropic.com",
        api_key="dummy",
        timeout_seconds=10,
    )
    calls: list[str] = []

    def fake_run_task_once(*, settings, task, run_dir, model_override, max_output_tokens):
        calls.append(model_override)
        if len(calls) == 1:
            return type(
                "Result",
                (),
                {
                    "response": ProviderResponse(
                        request_payload={},
                        raw_payload={},
                        text_output="{}",
                        provider_model=model_override,
                        usage={},
                    ),
                    "normalized_result": {
                        "task_id": "task-2",
                        "status": "partial",
                        "summary": "missing patch",
                        "changed_files": [],
                        "commands_run": [],
                        "verification": {"passed": [], "failed": []},
                        "risks": [],
                        "notes": [],
                        "model": model_override,
                        "received_at": "2026-03-15T00:00:00Z",
                        "parse_error": False,
                        "patch_missing": True,
                        "patch": "",
                    },
                },
            )()
        return type(
            "Result",
            (),
            {
                "response": ProviderResponse(
                    request_payload={},
                    raw_payload={},
                    text_output="{}",
                    provider_model=model_override,
                    usage={},
                ),
                "normalized_result": {
                    "task_id": "task-2",
                    "status": "completed",
                    "summary": "ok",
                    "changed_files": ["x.txt"],
                    "commands_run": [],
                    "verification": {"passed": [], "failed": []},
                    "risks": [],
                    "notes": [],
                    "model": model_override,
                    "received_at": "2026-03-15T00:00:00Z",
                    "parse_error": False,
                    "patch_missing": False,
                    "patch": "diff --git a/x.txt b/x.txt",
                },
            },
        )()

    monkeypatch.setattr("agx_core.runner.run_task_once", fake_run_task_once)
    dispatched = run_task_with_fallbacks(settings=settings, task=task, run_dir=tmp_path)
    assert calls == ["sonnet", "opus"]
    assert dispatched.final_result["patch_missing"] is False

