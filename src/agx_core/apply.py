from __future__ import annotations

from pathlib import Path
import re
import subprocess
from typing import Any

from .storage import patch_artifact_path, read_json, result_path, run_path, write_json


PATCH_FILE_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$")
PATCH_OLD_RE = re.compile(r"^--- (?:a/)?(.+)$")
PATCH_NEW_RE = re.compile(r"^\+\+\+ (?:b/)?(.+)$")


class LocalOperationError(RuntimeError):
    """Raised when apply cannot be completed safely."""


def extract_patch_files(patch_text: str) -> list[str]:
    files: list[str] = []
    seen: set[str] = set()
    pending_old_path: str | None = None
    for line in patch_text.splitlines():
        match = PATCH_FILE_RE.match(line)
        if match:
            candidate = match.group(2).strip()
            if candidate == "/dev/null":
                candidate = match.group(1).strip()
            if candidate not in seen:
                seen.add(candidate)
                files.append(candidate)
            pending_old_path = None
            continue

        old_match = PATCH_OLD_RE.match(line)
        if old_match:
            pending_old_path = old_match.group(1).strip()
            continue

        new_match = PATCH_NEW_RE.match(line)
        if not new_match:
            continue
        candidate = new_match.group(1).strip()
        if candidate == "/dev/null":
            candidate = pending_old_path or candidate
        if candidate != "/dev/null" and candidate not in seen:
            seen.add(candidate)
            files.append(candidate)
        pending_old_path = None
    return files


def _normalize_rel_path(path_value: str) -> str:
    raw = path_value.strip().replace("\\", "/")
    if raw.startswith("b/"):
        raw = raw[2:]
    return raw.lstrip("./")


def is_allowed_path(path_value: str, allowed_paths: list[str]) -> bool:
    candidate = _normalize_rel_path(path_value)
    if not candidate or candidate.startswith("/") or candidate.startswith("../") or "/../" in candidate:
        return False
    if not allowed_paths:
        return False
    normalized_allowed = [_normalize_rel_path(path) for path in allowed_paths]
    return any(candidate == allowed or candidate.startswith(f"{allowed}/") for allowed in normalized_allowed)


def save_patch_artifact(*, repo_path: Path, run_id: str, patch_text: str) -> Path:
    artifact_path = patch_artifact_path(repo_path, run_id)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_patch = patch_text if patch_text.endswith("\n") else f"{patch_text}\n"
    artifact_path.write_text(normalized_patch, encoding="utf-8")
    return artifact_path


def _update_result(repo_path: Path, run_id: str, key: str, payload: dict[str, Any]) -> dict[str, Any]:
    indexed = read_json(result_path(repo_path, run_id))
    indexed[key] = payload
    write_json(result_path(repo_path, run_id), indexed)
    write_json(run_path(repo_path, run_id) / "result.json", indexed)
    return indexed


def assess_patch_quality(*, repo_path: Path, run_id: str, force: bool = False) -> dict[str, Any]:
    run_dir = run_path(repo_path, run_id)
    task = read_json(run_dir / "task.json")
    result = read_json(result_path(repo_path, run_id))
    patch_text = result.get("patch", "")
    allowed_paths = task.get("allowed_paths", [])
    changed_files = result.get("changed_files", [])
    issues: list[str] = []

    if not patch_text:
        payload = {
            "status": "no_patch",
            "issues": [],
            "patch_files": [],
            "changed_files_match": not changed_files,
            "allowed_paths_enforced": not force,
            "patch_path": None,
            "patch_required": bool(task.get("patch_required")),
        }
        write_json(run_dir / "patch-quality.json", payload)
        return _update_result(repo_path, run_id, "patch_quality", payload)

    patch_files = extract_patch_files(patch_text)
    if not patch_files:
        issues.append("Patch does not contain any valid unified diff file headers.")

    if changed_files:
        normalized_changed = sorted({_normalize_rel_path(path) for path in changed_files})
        normalized_patch = sorted({_normalize_rel_path(path) for path in patch_files})
        if normalized_patch != normalized_changed:
            issues.append("Patch files do not match the `changed_files` list from the model result.")

    if not force:
        if not allowed_paths:
            issues.append("Task does not declare allowed paths.")
        else:
            disallowed = [path for path in patch_files if not is_allowed_path(path, allowed_paths)]
            if disallowed:
                issues.append(f"Patch touches files outside allowed paths: {', '.join(disallowed)}")

    artifact_path = str(save_patch_artifact(repo_path=repo_path, run_id=run_id, patch_text=patch_text))
    payload = {
        "status": "ready" if not issues else "blocked",
        "issues": issues,
        "patch_files": patch_files,
        "changed_files_match": not changed_files
        or sorted({_normalize_rel_path(path) for path in changed_files})
        == sorted({_normalize_rel_path(path) for path in patch_files}),
        "allowed_paths_enforced": not force,
        "patch_path": artifact_path,
        "patch_required": bool(task.get("patch_required")),
    }
    write_json(run_dir / "patch-quality.json", payload)
    return _update_result(repo_path, run_id, "patch_quality", payload)


def apply_run_patch(*, repo_path: Path, run_id: str, check_only: bool = False, force: bool = False) -> dict[str, Any]:
    quality_result = assess_patch_quality(repo_path=repo_path, run_id=run_id, force=force)
    quality_payload = quality_result.get("patch_quality", {})
    run_dir = run_path(repo_path, run_id)
    if quality_payload.get("status") == "no_patch":
        raise LocalOperationError("Run result does not include a patch artifact.")
    if quality_payload.get("status") != "ready":
        issues = quality_payload.get("issues", [])
        issue_text = "; ".join(issues) if issues else "Patch quality gate blocked apply."
        raise LocalOperationError(issue_text)

    patch_files = quality_payload.get("patch_files", [])
    artifact_path = Path(quality_payload["patch_path"])
    check_proc = subprocess.run(
        ["git", "-C", str(repo_path), "apply", "--check", str(artifact_path)],
        capture_output=True,
        text=True,
    )
    apply_payload = {
        "status": "check_failed" if check_proc.returncode else "checked",
        "check_returncode": check_proc.returncode,
        "check_stdout": check_proc.stdout,
        "check_stderr": check_proc.stderr,
        "patch_files": patch_files,
        "patch_path": str(artifact_path),
    }
    if check_proc.returncode != 0 or check_only:
        write_json(run_dir / "apply.json", apply_payload)
        return _update_result(repo_path, run_id, "local_apply", apply_payload)

    apply_proc = subprocess.run(
        ["git", "-C", str(repo_path), "apply", "--whitespace=nowarn", str(artifact_path)],
        capture_output=True,
        text=True,
    )
    apply_payload.update(
        {
            "status": "applied" if apply_proc.returncode == 0 else "apply_failed",
            "apply_returncode": apply_proc.returncode,
            "apply_stdout": apply_proc.stdout,
            "apply_stderr": apply_proc.stderr,
        }
    )
    write_json(run_dir / "apply.json", apply_payload)
    return _update_result(repo_path, run_id, "local_apply", apply_payload)

