from pathlib import Path

from agx_core.storage import create_task, ensure_runtime, result_path, run_result_path, slugify


def test_slugify_normalizes_text() -> None:
    assert slugify("Refactor Auth Middleware!") == "refactor-auth-middleware"


def test_create_task_writes_task_bundle(tmp_path: Path) -> None:
    task, task_path = create_task(
        repo_path=tmp_path,
        title="Refactor auth middleware",
        goal="Isolate token parsing",
        allowed_paths=["src/auth"],
        constraints=["Do not change public API"],
        deliverables=["Patch"],
        verification=["pytest -q"],
        context_files=[{"path": "src/auth/middleware.py", "content": "print('x')\n"}],
        context_notes=["Keep behavior unchanged."],
        patch_required=True,
        provider="anthropic",
        model_hint="sonnet",
        fallback_models=["opus"],
    )

    assert task_path.exists()
    assert task["title"] == "Refactor auth middleware"
    assert task["allowed_paths"] == ["src/auth"]
    assert task["fallback_models"] == ["opus"]
    assert task["patch_required"] is True
    assert task["context_files"][0]["path"] == "src/auth/middleware.py"
    runtime_root = ensure_runtime(tmp_path)
    assert (runtime_root / "tasks").exists()
    assert (runtime_root / "runs").exists()


def test_result_paths_use_results_index_and_run_folder(tmp_path: Path) -> None:
    assert result_path(tmp_path, "run-1") == tmp_path / ".agx" / "results" / "run-1.json"
    assert run_result_path(tmp_path, "run-1") == tmp_path / ".agx" / "runs" / "run-1" / "result.json"

