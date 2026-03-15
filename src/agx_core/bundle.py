from __future__ import annotations

from pathlib import Path

from .config import Settings
from .storage import create_task


DEFAULT_DELIVERABLES = [
    "Patch or file edits",
    "Short rationale",
    "Verification notes",
]


def load_context_files(repo_path: Path, raw_paths: list[str]) -> list[dict[str, str]]:
    context_files: list[dict[str, str]] = []
    for raw_path in raw_paths:
        file_path = (repo_path / raw_path).resolve()
        try:
            file_path.relative_to(repo_path)
        except ValueError as exc:
            raise ValueError(f"Context file is outside repo root: {raw_path}") from exc
        if not file_path.is_file():
            raise FileNotFoundError(f"Context file not found: {file_path}")
        rel_path = file_path.relative_to(repo_path).as_posix()
        context_files.append(
            {
                "path": rel_path,
                "content": file_path.read_text(encoding="utf-8"),
            }
        )
    return context_files


def create_task_bundle(
    *,
    settings: Settings,
    repo_path: Path,
    title: str,
    goal: str,
    allowed_paths: list[str],
    constraints: list[str],
    deliverables: list[str] | None,
    verification: list[str],
    context_files: list[dict[str, str]],
    context_notes: list[str],
    patch_required: bool,
    provider: str | None,
    model_hint: str,
    fallback_models: list[str],
) -> tuple[dict, Path]:
    return create_task(
        repo_path=repo_path,
        title=title,
        goal=goal,
        allowed_paths=allowed_paths,
        constraints=constraints,
        deliverables=deliverables or list(DEFAULT_DELIVERABLES),
        verification=verification,
        context_files=context_files,
        context_notes=context_notes,
        patch_required=patch_required,
        provider=provider or settings.provider,
        model_hint=model_hint,
        fallback_models=fallback_models,
    )

