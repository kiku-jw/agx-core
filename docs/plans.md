# AGX Core Plan

## Goal

Ship a public, API-first AGX kernel that proves the bounded execution lane without private control-surface baggage.

## Scope

- [x] Create standalone public repo scaffold
- [x] Add durable execution docs
- [x] Port task bundle and local runtime storage
- [x] Port local patch gating, apply, and verification
- [x] Replace proxy-first transport with provider adapters
- [x] Add API-first `doctor`
- [x] Add public `agx-orchestrator` skill
- [x] Add basic unit tests for storage, runner, apply, and doctor
- [ ] Add richer examples and release packaging

## Milestones

### M1. Public repo scaffold

Status: `done`

Definition of done:

- repo has README, QUICKSTART, docs, package layout, tests, and skill

Validation:

- `find /Users/nick/myprojects/agx-core -maxdepth 3 | sort | sed -n '1,200p'`

### M2. Kernel extraction

Status: `done`

Definition of done:

- task bundle, run result storage, apply, and verify work without Telegram or Hetzner code

Validation:

- `cd /Users/nick/myprojects/agx-core && PYTHONPATH=src python3 -m pytest tests/test_storage.py tests/test_apply.py`

### M3. API-first provider layer

Status: `done`

Definition of done:

- `anthropic` and `openai-compatible` adapters exist behind one runner interface

Validation:

- `cd /Users/nick/myprojects/agx-core && PYTHONPATH=src python3 -m pytest tests/test_runner.py tests/test_doctor.py`

### M4. Public routing surface

Status: `done`

Definition of done:

- public skill teaches bounded dispatch without private assumptions

Validation:

- read [SKILL.md](/Users/nick/myprojects/agx-core/skills/agx-orchestrator/SKILL.md)

## Assumptions

- provider credentials will be supplied by env vars
- public v1 can use explicit model ids or user-defined aliases
- patch repair, Telegram control, and deployment profiles can stay out of the first public release

## Stop-And-Fix Rule

If the repo drifts back toward private runtime assumptions, cut scope instead of carrying the baggage forward.

