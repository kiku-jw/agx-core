from pathlib import Path
import subprocess

from agx_core.apply import apply_run_patch, assess_patch_quality, extract_patch_files, is_allowed_path, save_patch_artifact
from agx_core.runner import run_followups
from agx_core.storage import create_run_dir, result_path, write_json
from agx_core.verify import verify_run


def test_extract_patch_files_reads_diff_headers() -> None:
    patch = """diff --git a/src/a.py b/src/a.py
index 1111111..2222222 100644
--- a/src/a.py
+++ b/src/a.py
@@ -1 +1 @@
-print("old")
+print("new")
"""
    assert extract_patch_files(patch) == ["src/a.py"]


def test_is_allowed_path_enforces_scope() -> None:
    assert is_allowed_path("src/a.py", ["src"]) is True
    assert is_allowed_path("../secrets.txt", ["src"]) is False
    assert is_allowed_path("tests/a.py", ["src"]) is False


def test_verify_run_executes_commands(tmp_path: Path) -> None:
    repo_path = tmp_path
    run_id, run_dir = create_run_dir(repo_path, "verify-task")
    write_json(
        run_dir / "task.json",
        {
            "id": "verify-task",
            "repo_path": str(repo_path),
            "allowed_paths": ["src"],
            "verification": ["python3 -c 'print(123)'", "python3 -c 'import sys; sys.exit(1)'"],
        },
    )
    write_json(
        result_path(repo_path, run_id),
        {
            "task_id": "verify-task",
            "status": "completed",
            "summary": "ready",
            "changed_files": [],
            "commands_run": [],
            "verification": {"passed": [], "failed": []},
            "risks": [],
            "notes": [],
            "model": "model-a",
            "received_at": "2026-03-15T00:00:00Z",
            "parse_error": False,
            "patch": "",
        },
    )
    payload = verify_run(repo_path=repo_path, run_id=run_id)
    assert payload["local_verification"]["status"] == "failed"
    assert payload["local_verification"]["passed"] == ["python3 -c 'print(123)'"]


def test_apply_run_patch_check_only(tmp_path: Path) -> None:
    repo_path = tmp_path
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True, text=True)
    readme = repo_path / "README.md"
    readme.write_text("old\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
        env={
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )

    run_id, run_dir = create_run_dir(repo_path, "apply-task")
    patch = """diff --git a/README.md b/README.md
index 3367afd..7e4fa2d 100644
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-old
+new
"""
    write_json(
        run_dir / "task.json",
        {
            "id": "apply-task",
            "repo_path": str(repo_path),
            "allowed_paths": ["README.md"],
            "verification": [],
        },
    )
    write_json(
        result_path(repo_path, run_id),
        {
            "task_id": "apply-task",
            "status": "completed",
            "summary": "ready",
            "changed_files": ["README.md"],
            "commands_run": [],
            "verification": {"passed": [], "failed": []},
            "risks": [],
            "notes": [],
            "model": "model-a",
            "received_at": "2026-03-15T00:00:00Z",
            "parse_error": False,
            "patch": patch,
        },
    )
    payload = apply_run_patch(repo_path=repo_path, run_id=run_id, check_only=True)
    assert payload["local_apply"]["status"] == "checked"


def test_assess_patch_quality_blocks_disallowed_paths(tmp_path: Path) -> None:
    repo_path = tmp_path
    run_id, run_dir = create_run_dir(repo_path, "quality-task")
    write_json(
        run_dir / "task.json",
        {
            "id": "quality-task",
            "repo_path": str(repo_path),
            "allowed_paths": ["src"],
            "verification": [],
        },
    )
    write_json(
        result_path(repo_path, run_id),
        {
            "task_id": "quality-task",
            "status": "completed",
            "summary": "ready",
            "changed_files": ["README.md"],
            "commands_run": [],
            "verification": {"passed": [], "failed": []},
            "risks": [],
            "notes": [],
            "model": "model-a",
            "received_at": "2026-03-15T00:00:00Z",
            "parse_error": False,
            "patch": """diff --git a/README.md b/README.md
index 3367afd..7e4fa2d 100644
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-old
+new
""",
        },
    )
    payload = assess_patch_quality(repo_path=repo_path, run_id=run_id)
    assert payload["patch_quality"]["status"] == "blocked"
    assert payload["patch_quality"]["issues"]


def test_run_followups_marks_apply_skip_when_no_patch(tmp_path: Path) -> None:
    repo_path = tmp_path
    run_id, run_dir = create_run_dir(repo_path, "followup-task")
    write_json(
        run_dir / "task.json",
        {
            "id": "followup-task",
            "repo_path": str(repo_path),
            "allowed_paths": ["src"],
            "verification": [],
        },
    )
    write_json(
        result_path(repo_path, run_id),
        {
            "task_id": "followup-task",
            "status": "completed",
            "summary": "ready",
            "changed_files": [],
            "commands_run": [],
            "verification": {"passed": [], "failed": []},
            "risks": [],
            "notes": [],
            "model": "model-a",
            "received_at": "2026-03-15T00:00:00Z",
            "parse_error": False,
            "patch": "",
        },
    )
    payload = run_followups(repo_path=repo_path, run_id=run_id, apply_mode="check", verify=False)
    assert payload["patch_quality"]["status"] == "no_patch"
    assert payload["local_apply"]["status"] == "skipped_no_patch"


def test_save_patch_artifact_appends_final_newline(tmp_path: Path) -> None:
    artifact = save_patch_artifact(repo_path=tmp_path, run_id="run-1", patch_text="diff --git a/x b/x")
    assert artifact.read_text(encoding="utf-8").endswith("\n")

