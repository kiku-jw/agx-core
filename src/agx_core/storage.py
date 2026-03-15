from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any


RUNTIME_DIRS = ("tasks", "runs", "results", "artifacts", "logs")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    compact = re.sub(r"[^a-z0-9]+", "-", lowered)
    compact = compact.strip("-")
    return compact or "task"


def ensure_runtime(repo_path: Path) -> Path:
    runtime_root = repo_path / ".agx"
    for name in RUNTIME_DIRS:
        (runtime_root / name).mkdir(parents=True, exist_ok=True)
    return runtime_root


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def task_path_from_ref(task_ref: str) -> Path:
    path = Path(task_ref).expanduser().resolve()
    if path.is_dir():
        path = path / "task.json"
    return path


def create_task(
    *,
    repo_path: Path,
    title: str,
    goal: str,
    allowed_paths: list[str],
    constraints: list[str],
    deliverables: list[str],
    verification: list[str],
    context_files: list[dict[str, str]],
    context_notes: list[str],
    patch_required: bool,
    provider: str,
    model_hint: str,
    fallback_models: list[str],
) -> tuple[dict[str, Any], Path]:
    runtime_root = ensure_runtime(repo_path)
    task_id = f"{utc_timestamp()}-{slugify(title)}"
    task_dir = runtime_root / "tasks" / task_id
    task = {
        "schema_version": 1,
        "id": task_id,
        "created_at": utc_iso(),
        "title": title,
        "goal": goal,
        "repo_path": str(repo_path),
        "allowed_paths": allowed_paths,
        "constraints": constraints,
        "deliverables": deliverables,
        "verification": verification,
        "context_files": context_files,
        "context_notes": context_notes,
        "patch_required": patch_required,
        "provider": provider,
        "model_hint": model_hint,
        "fallback_models": fallback_models,
        "status": "submitted",
    }
    task_path = task_dir / "task.json"
    write_json(task_path, task)
    return task, task_path


def create_run_dir(repo_path: Path, task_id: str) -> tuple[str, Path]:
    runtime_root = ensure_runtime(repo_path)
    run_id = f"{utc_timestamp()}-{task_id}"
    run_dir = runtime_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def result_path(repo_path: Path, run_id: str) -> Path:
    return ensure_runtime(repo_path) / "results" / f"{run_id}.json"


def run_result_path(repo_path: Path, run_id: str) -> Path:
    return ensure_runtime(repo_path) / "runs" / run_id / "result.json"


def run_path(repo_path: Path, run_id: str) -> Path:
    return ensure_runtime(repo_path) / "runs" / run_id


def patch_artifact_path(repo_path: Path, run_id: str) -> Path:
    return ensure_runtime(repo_path) / "artifacts" / f"{run_id}.patch"

