from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any

from .storage import read_json, result_path, run_path, write_json


def _update_result(repo_path: Path, run_id: str, key: str, payload: dict[str, Any]) -> dict[str, Any]:
    indexed = read_json(result_path(repo_path, run_id))
    indexed[key] = payload
    write_json(result_path(repo_path, run_id), indexed)
    write_json(run_path(repo_path, run_id) / "result.json", indexed)
    return indexed


def verify_run(*, repo_path: Path, run_id: str) -> dict[str, Any]:
    run_dir = run_path(repo_path, run_id)
    task = read_json(run_dir / "task.json")
    commands = task.get("verification", [])
    logs_dir = run_dir / "verify-logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    passed: list[str] = []
    failed: list[str] = []

    for index, command in enumerate(commands, start=1):
        completed = subprocess.run(
            command,
            cwd=repo_path,
            shell=True,
            executable=os.environ.get("SHELL", "/bin/zsh"),
            capture_output=True,
            text=True,
        )
        stdout_path = logs_dir / f"{index:02d}.stdout.log"
        stderr_path = logs_dir / f"{index:02d}.stderr.log"
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        entry = {
            "command": command,
            "returncode": completed.returncode,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        entries.append(entry)
        if completed.returncode == 0:
            passed.append(command)
        else:
            failed.append(command)

    payload = {
        "status": "passed" if not failed else "failed",
        "commands": entries,
        "passed": passed,
        "failed": failed,
    }
    write_json(run_dir / "verify.json", payload)
    return _update_result(repo_path, run_id, "local_verification", payload)

