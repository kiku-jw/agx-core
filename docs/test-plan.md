# AGX Core Test Plan

## Test levels

- unit: config alias parsing, runtime path creation, fallback dispatch behavior
- local ops: patch parsing, allowed-path gating, apply check, verification command capture
- doctor: provider selection and alias mismatch warnings
- local proxy compatibility: Anthropic localhost proxy mode works without a manual fake API key
- doc smoke: quickstart and skill match the actual public boundary

## Critical behaviors

- `submit` writes one durable task bundle under repo-local `.agx/`
- `run` saves raw request, raw response, and normalized result
- parse failures stay first-class instead of silent
- patch-required tasks surface `patch_missing` cleanly
- `apply` refuses patches outside allowed paths by default
- `verify` stores per-command logs and status
- `doctor` checks provider config without hidden proxy startup
- localhost Anthropic-compatible proxy mode auto-supplies a dummy header when no `AGX_API_KEY` is set
- the public skill never assumes private paths or private infra

## Negative cases

- missing API key
- unknown alias
- non-JSON model output
- provider request error
- patch outside allowed paths
- changed-files mismatch against patch headers

## Acceptance gates

- `cd /Users/nick/myprojects/agx-core && PYTHONPATH=src python3 -m pytest`
- `cd /Users/nick/myprojects/agx-core && PYTHONPATH=src python3 -m compileall src`
- one disposable-repo live smoke succeeds against a direct provider

## Explicitly deferred

- Telegram control
- Hetzner deployment
- proxy startup
- provider quota introspection
- patch repair loop
