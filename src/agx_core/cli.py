from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from .apply import LocalOperationError, apply_run_patch
from .bundle import create_task_bundle, load_context_files
from .config import load_settings
from .doctor import run_doctor
from .runner import run_followups, run_task_with_fallbacks
from .storage import create_run_dir, read_json, result_path, task_path_from_ref, write_json
from .verify import verify_run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agx-core", description="Bounded execution lanes with durable task bundles.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit = subparsers.add_parser("submit", help="Create a task bundle.")
    submit.add_argument("--cwd", default=".", help="Target repository root.")
    submit.add_argument("--title", required=True, help="Short task title.")
    submit.add_argument("--goal", required=True, help="Task goal.")
    submit.add_argument("--allowed-path", action="append", default=[], help="Writable path scope.")
    submit.add_argument("--constraint", action="append", default=[], help="Execution constraint.")
    submit.add_argument("--deliverable", action="append", default=[], help="Expected deliverable.")
    submit.add_argument("--verify", action="append", default=[], help="Verification command.")
    submit.add_argument("--context-file", action="append", default=[], help="Repo-relative file to embed as worker context.")
    submit.add_argument("--context-note", action="append", default=[], help="Extra plain-text context for the worker.")
    submit.add_argument("--require-patch", action="store_true", help="Require the worker to return a unified diff patch.")
    submit.add_argument("--provider", help="Override the provider for this task bundle.")
    submit.add_argument("--model", required=True, help="Model id or configured alias.")
    submit.add_argument("--fallback-model", action="append", default=[], help="Fallback model id or alias.")

    run = subparsers.add_parser("run", help="Dispatch a task bundle.")
    run.add_argument("task_ref", help="Path to a task.json or its directory.")
    run.add_argument("--model", help="Override the task model.")
    run.add_argument("--fallback-model", action="append", default=[], help="Fallback model id or alias.")
    run.add_argument("--max-tokens", type=int, default=4000, help="Maximum provider output tokens.")
    run.add_argument("--apply-check", action="store_true", help="Run patch quality gate and `git apply --check` when a patch is returned.")
    run.add_argument("--apply", action="store_true", help="Run patch quality gate and apply the returned patch locally.")
    run.add_argument("--verify", action="store_true", help="Execute local verification commands after dispatch.")
    run.add_argument("--force-apply", action="store_true", help="Bypass allowed-path enforcement for automatic patch follow-up.")

    result = subparsers.add_parser("result", help="Read a saved run result.")
    result.add_argument("run_id", help="Run identifier created by `agx-core run`.")
    result.add_argument("--cwd", default=".", help="Target repository root.")

    apply = subparsers.add_parser("apply", help="Apply a patch artifact from a saved run.")
    apply.add_argument("run_id", help="Run identifier created by `agx-core run`.")
    apply.add_argument("--cwd", default=".", help="Target repository root.")
    apply.add_argument("--check-only", action="store_true", help="Only validate the patch.")
    apply.add_argument("--force", action="store_true", help="Bypass allowed-path enforcement.")

    verify = subparsers.add_parser("verify", help="Run local verification commands for a saved run.")
    verify.add_argument("run_id", help="Run identifier created by `agx-core run`.")
    verify.add_argument("--cwd", default=".", help="Target repository root.")

    doctor = subparsers.add_parser("doctor", help="Check provider config, model visibility, and alias sanity.")
    doctor.add_argument("--json", action="store_true", help="Print the full doctor report as JSON.")

    install_skill = subparsers.add_parser("install-skill", help="Install the public agx-orchestrator skill into Codex.")
    install_skill.add_argument("--codex-home", default=str(Path.home() / ".codex"), help="Target Codex home directory.")
    install_skill.add_argument("--json", action="store_true", help="Print the install report as JSON.")

    return parser


def _skill_source_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "skills" / "agx-orchestrator"


def _copy_skill_tree(source_dir: Path, dest_dir: Path) -> list[str]:
    changed: list[str] = []
    dest_dir.mkdir(parents=True, exist_ok=True)
    for source in source_dir.rglob("*"):
        relative = source.relative_to(source_dir)
        destination = dest_dir / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text(encoding="utf-8")
        if not destination.exists() or destination.read_text(encoding="utf-8") != content:
            destination.write_text(content, encoding="utf-8")
            changed.append(str(destination))
    return changed


def cmd_submit(args: argparse.Namespace) -> int:
    repo_path = Path(args.cwd).expanduser().resolve()
    settings = load_settings(provider_override=args.provider)
    context_files = load_context_files(repo_path, args.context_file)
    task, task_path = create_task_bundle(
        settings=settings,
        repo_path=repo_path,
        title=args.title,
        goal=args.goal,
        allowed_paths=args.allowed_path,
        constraints=args.constraint,
        deliverables=args.deliverable or None,
        verification=args.verify,
        context_files=context_files,
        context_notes=args.context_note,
        patch_required=args.require_patch,
        provider=args.provider,
        model_hint=args.model,
        fallback_models=args.fallback_model,
    )
    print(f"task_id={task['id']}")
    print(f"task_path={task_path}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    task_path = task_path_from_ref(args.task_ref)
    if not task_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_path}")

    task = read_json(task_path)
    repo_path = Path(task["repo_path"]).expanduser().resolve()
    run_id, run_dir = create_run_dir(repo_path, task["id"])
    settings = load_settings(provider_override=task.get("provider"))
    write_json(run_dir / "task.json", task)

    result = run_task_with_fallbacks(
        settings=settings,
        task=task,
        run_dir=run_dir,
        primary_override=args.model,
        fallback_overrides=args.fallback_model or None,
        max_output_tokens=args.max_tokens,
    )

    write_json(result_path(repo_path, run_id), result.final_result)
    final_payload = result.final_result
    apply_mode = "apply" if args.apply else "check" if args.apply_check else "none"
    if apply_mode != "none" or args.verify:
        final_payload = run_followups(
            repo_path=repo_path,
            run_id=run_id,
            apply_mode=apply_mode,
            verify=args.verify,
            force=args.force_apply,
        )

    print(f"run_id={run_id}")
    print(f"run_dir={run_dir}")
    print(f"status={final_payload['status']}")
    print(f"summary={final_payload['summary']}")
    print(f"attempt_count={final_payload.get('attempt_count', 0)}")
    print(f"model={final_payload['model']}")
    if "patch_quality" in final_payload:
        print(f"patch_quality={final_payload['patch_quality']['status']}")
    if "local_apply" in final_payload:
        print(f"local_apply={final_payload['local_apply']['status']}")
    if "local_verification" in final_payload:
        print(f"local_verification={final_payload['local_verification']['status']}")

    exit_code = 0 if final_payload["status"] != "failed" else 2
    if final_payload.get("patch_missing"):
        exit_code = 2
    if apply_mode != "none":
        local_apply_status = final_payload.get("local_apply", {}).get("status", "")
        if local_apply_status not in {"checked", "applied"}:
            exit_code = 2
    if args.verify and final_payload.get("local_verification", {}).get("status") != "passed":
        exit_code = 2
    return exit_code


def cmd_result(args: argparse.Namespace) -> int:
    repo_path = Path(args.cwd).expanduser().resolve()
    path = result_path(repo_path, args.run_id)
    if not path.exists():
        raise FileNotFoundError(f"Result file not found: {path}")
    payload = read_json(path)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    repo_path = Path(args.cwd).expanduser().resolve()
    try:
        payload = apply_run_patch(
            repo_path=repo_path,
            run_id=args.run_id,
            check_only=args.check_only,
            force=args.force,
        )
    except LocalOperationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload.get("local_apply", payload), indent=2))
    status = payload.get("local_apply", {}).get("status", "")
    return 0 if status in {"checked", "applied"} else 2


def cmd_verify(args: argparse.Namespace) -> int:
    repo_path = Path(args.cwd).expanduser().resolve()
    payload = verify_run(repo_path=repo_path, run_id=args.run_id)
    print(json.dumps(payload.get("local_verification", payload), indent=2))
    status = payload.get("local_verification", {}).get("status", "")
    return 0 if status == "passed" else 2


def cmd_doctor(args: argparse.Namespace) -> int:
    report = run_doctor(load_settings()).to_dict()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for key in ("status", "provider", "base_url", "auth_mode", "model_count"):
            print(f"{key}={report[key]}")
        if report["notes"]:
            print("notes:")
            for note in report["notes"]:
                print(f"- {note}")
    return 0 if report["status"] != "failed" else 2


def cmd_install_skill(args: argparse.Namespace) -> int:
    source_dir = _skill_source_dir()
    codex_home = Path(args.codex_home).expanduser().resolve()
    dest_dir = codex_home / "skills" / "agx-orchestrator"
    changed = _copy_skill_tree(source_dir, dest_dir)
    report = {
        "source_dir": str(source_dir),
        "dest_dir": str(dest_dir),
        "changed_count": len(changed),
        "changed_files": changed,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"dest_dir={dest_dir}")
        print(f"changed_count={len(changed)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "submit":
        return cmd_submit(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "result":
        return cmd_result(args)
    if args.command == "apply":
        return cmd_apply(args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.command == "doctor":
        return cmd_doctor(args)
    if args.command == "install-skill":
        return cmd_install_skill(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
