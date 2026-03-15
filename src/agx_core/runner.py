from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError, JSONDecoder
from pathlib import Path
from typing import Any

from .apply import LocalOperationError, apply_run_patch, assess_patch_quality
from .config import Settings, fallback_chain, resolve_model, settings_with_provider
from .providers import provider_from_settings
from .providers.base import ProviderError, ProviderRequest, ProviderResponse
from .storage import read_json, result_path, run_path, slugify, utc_iso, write_json
from .verify import verify_run


RESULT_INSTRUCTIONS = """You are an execution worker inside a supervised orchestration loop.

Return exactly one JSON object and nothing else.
Do not wrap it in markdown fences.
Do not include explanations before or after the JSON.

The JSON object must have these keys:
- task_id: string
- status: "completed" | "partial" | "failed"
- summary: short string
- changed_files: array of strings
- commands_run: array of strings
- verification: object with keys "passed" and "failed", both arrays of strings
- risks: array of strings
- notes: array of strings

The JSON object may also include:
- patch: unified diff string relative to repo_path, or an empty string when no patch is provided
"""


PATCH_INSTRUCTIONS = """Patch requirements:
- Return a valid unified diff in the `patch` field.
- Use `diff --git a/<path> b/<path>` headers.
- Include `--- a/...`, `+++ b/...`, and `@@ ... @@` hunks.
- Only touch files inside `allowed_paths`.
- Make `changed_files` exactly match the file paths modified in `patch`.
- Base the patch on the exact file contents provided in `context_files`.
- If you cannot produce a safe valid patch, return `status` as `partial` or `failed`, set `patch` to an empty string, and explain why in `risks` or `notes`.
"""


@dataclass(frozen=True)
class RunOnceResult:
    response: ProviderResponse
    normalized_result: dict[str, Any]


@dataclass(frozen=True)
class DispatchResult:
    final_result: dict[str, Any]
    attempts: list[dict[str, Any]]


def task_requires_patch(task: dict[str, Any]) -> bool:
    return bool(task.get("patch_required"))


def _render_context(task: dict[str, Any]) -> str:
    sections: list[str] = []
    notes = task.get("context_notes", [])
    if notes:
        sections.append("Context notes:")
        sections.extend(f"- {note}" for note in notes)

    context_files = task.get("context_files", [])
    if context_files:
        sections.append("Context files:")
        for item in context_files:
            path = item.get("path", "")
            content = item.get("content", "")
            sections.append(f"Path: {path}")
            sections.append("```text")
            sections.append(content.rstrip("\n"))
            sections.append("```")

    return "\n".join(section for section in sections if section)


def build_prompt(task: dict[str, Any]) -> str:
    task_view = {
        "id": task["id"],
        "title": task["title"],
        "goal": task["goal"],
        "repo_path": task["repo_path"],
        "allowed_paths": task["allowed_paths"],
        "constraints": task["constraints"],
        "deliverables": task["deliverables"],
        "verification": task["verification"],
        "patch_required": task.get("patch_required", False),
    }
    prompt_sections = [RESULT_INSTRUCTIONS]
    if task_requires_patch(task):
        prompt_sections.append(PATCH_INSTRUCTIONS)
    prompt_sections.extend(
        [
            "Here is the task bundle:",
            __import__("json").dumps(task_view, indent=2),
        ]
    )
    context_section = _render_context(task)
    if context_section:
        prompt_sections.extend(["", context_section])
    return "\n".join(prompt_sections) + "\n"


def _extract_json_object(text: str) -> dict[str, Any]:
    decoder = JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise JSONDecodeError("No JSON object found in model output", text, 0)


def _normalize_result(
    *,
    parsed_result: dict[str, Any] | None,
    text_output: str,
    task_id: str,
    model: str,
    patch_required: bool,
) -> dict[str, Any]:
    if parsed_result is None:
        return {
            "task_id": task_id,
            "status": "failed",
            "summary": "Model output was not valid JSON.",
            "changed_files": [],
            "commands_run": [],
            "verification": {"passed": [], "failed": []},
            "risks": ["Result parser could not extract a JSON object from the model output."],
            "notes": [text_output] if text_output else [],
            "model": model,
            "received_at": utc_iso(),
            "parse_error": True,
            "patch_missing": patch_required,
            "patch": "",
        }

    patch = parsed_result.get("patch", "")
    patch_missing = bool(patch_required and not patch)
    status = parsed_result.get("status", "completed")
    notes = parsed_result.get("notes", [])
    if patch_missing:
        if status == "completed":
            status = "partial"
        notes = [*notes, "Task required a patch, but the model did not return one."]

    return {
        "task_id": parsed_result.get("task_id", task_id),
        "status": status,
        "summary": parsed_result.get("summary", ""),
        "changed_files": parsed_result.get("changed_files", []),
        "commands_run": parsed_result.get("commands_run", []),
        "verification": parsed_result.get("verification", {"passed": [], "failed": []}),
        "risks": parsed_result.get("risks", []),
        "notes": notes,
        "model": model,
        "received_at": utc_iso(),
        "parse_error": False,
        "patch_missing": patch_missing,
        "patch": patch,
    }


def run_task_once(
    *,
    settings: Settings,
    task: dict[str, Any],
    run_dir: Path,
    model_override: str | None = None,
    max_output_tokens: int = 4000,
) -> RunOnceResult:
    provider_name = task.get("provider") or settings.provider
    effective_settings = settings_with_provider(settings, provider_name)
    adapter = provider_from_settings(effective_settings)
    model = resolve_model(model_override or task.get("model_hint", ""))
    if not model:
        raise ValueError("Task must declare a model or alias.")
    prompt = build_prompt(task)
    provider_request = ProviderRequest(
        model=model,
        prompt=prompt,
        max_output_tokens=max_output_tokens,
        api_key=effective_settings.api_key,
        base_url=effective_settings.base_url,
        timeout_seconds=effective_settings.timeout_seconds,
    )
    response = adapter.invoke(provider_request)
    write_json(run_dir / "request.json", response.request_payload)
    write_json(run_dir / "raw-response.json", response.raw_payload)
    try:
        parsed_result = _extract_json_object(response.text_output)
    except JSONDecodeError:
        parsed_result = None
    normalized = _normalize_result(
        parsed_result=parsed_result,
        text_output=response.text_output,
        task_id=task["id"],
        model=response.provider_model or model,
        patch_required=task_requires_patch(task),
    )
    write_json(run_dir / "result.json", normalized)
    return RunOnceResult(response=response, normalized_result=normalized)


def _attempt_dir(run_dir: Path, index: int, model: str) -> Path:
    return run_dir / "attempts" / f"{index:02d}-{slugify(model)}"


def _retryable(result: dict[str, Any]) -> bool:
    return bool(result.get("parse_error") or result.get("patch_missing"))


def _attempt_record(
    *,
    index: int,
    model: str,
    status: str,
    attempt_dir: Path,
    summary: str = "",
    error_text: str | None = None,
) -> dict[str, Any]:
    return {
        "attempt": index,
        "model": model,
        "status": status,
        "summary": summary,
        "error": error_text,
        "path": str(attempt_dir),
        "recorded_at": utc_iso(),
    }


def run_task_with_fallbacks(
    *,
    settings: Settings,
    task: dict[str, Any],
    run_dir: Path,
    primary_override: str | None = None,
    fallback_overrides: list[str] | None = None,
    max_output_tokens: int = 4000,
) -> DispatchResult:
    primary = primary_override or task.get("model_hint", "")
    if not primary:
        raise ValueError("Task does not declare a primary model.")
    requested_fallbacks = fallback_overrides if fallback_overrides is not None else task.get("fallback_models", [])
    chain = [resolve_model(model) for model in fallback_chain(primary, requested_fallbacks)]
    attempts: list[dict[str, Any]] = []
    last_result: RunOnceResult | None = None

    for index, model in enumerate(chain, start=1):
        attempt_dir = _attempt_dir(run_dir, index, model)
        attempt_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = run_task_once(
                settings=settings,
                task=task,
                run_dir=attempt_dir,
                model_override=model,
                max_output_tokens=max_output_tokens,
            )
        except ProviderError as exc:
            error_payload = {
                "task_id": task["id"],
                "model": model,
                "status": "request_error",
                "error": str(exc),
                "recorded_at": utc_iso(),
            }
            write_json(attempt_dir / "error.json", error_payload)
            attempts.append(
                _attempt_record(
                    index=index,
                    model=model,
                    status="request_error",
                    attempt_dir=attempt_dir,
                    error_text=str(exc),
                )
            )
            continue

        last_result = result
        attempts.append(
            _attempt_record(
                index=index,
                model=model,
                status=result.normalized_result.get("status", "completed"),
                attempt_dir=attempt_dir,
                summary=result.normalized_result.get("summary", ""),
            )
        )
        if not _retryable(result.normalized_result):
            break

    if last_result is None:
        final_result = {
            "task_id": task["id"],
            "status": "failed",
            "summary": "All provider attempts failed before a parseable result was returned.",
            "changed_files": [],
            "commands_run": [],
            "verification": {"passed": [], "failed": []},
            "risks": ["All models in the dispatch chain failed to return a usable response."],
            "notes": [],
            "model": chain[-1] if chain else resolve_model(primary),
            "attempt_count": len(attempts),
            "attempted_models": [attempt["model"] for attempt in attempts],
            "attempts": attempts,
            "received_at": utc_iso(),
            "parse_error": False,
            "patch_missing": bool(task.get("patch_required")),
            "patch": "",
        }
    else:
        final_result = dict(last_result.normalized_result)
        final_result["attempt_count"] = len(attempts)
        final_result["attempted_models"] = [attempt["model"] for attempt in attempts]
        final_result["attempts"] = attempts

    write_json(run_dir / "attempts.json", {"attempts": attempts})
    write_json(run_dir / "result.json", final_result)
    return DispatchResult(final_result=final_result, attempts=attempts)


def run_followups(
    *,
    repo_path: Path,
    run_id: str,
    apply_mode: str = "none",
    verify: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    indexed = assess_patch_quality(repo_path=repo_path, run_id=run_id, force=force)
    quality_status = indexed.get("patch_quality", {}).get("status", "")

    if apply_mode != "none":
        if quality_status == "ready":
            indexed = apply_run_patch(
                repo_path=repo_path,
                run_id=run_id,
                check_only=apply_mode == "check",
                force=force,
            )
        else:
            apply_payload = {
                "status": "skipped_no_patch" if quality_status == "no_patch" else "blocked_by_patch_quality",
                "reason": quality_status,
                "issues": indexed.get("patch_quality", {}).get("issues", []),
            }
            write_json(run_path(repo_path, run_id) / "apply.json", apply_payload)
            indexed = read_json(result_path(repo_path, run_id))
            indexed["local_apply"] = apply_payload
            write_json(result_path(repo_path, run_id), indexed)
            write_json(run_path(repo_path, run_id) / "result.json", indexed)

    if verify:
        indexed = verify_run(repo_path=repo_path, run_id=run_id)

    return indexed

