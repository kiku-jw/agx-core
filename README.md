# agx-core

`agx-core` is a small local dispatcher for bounded execution lanes.

It keeps planning, acceptance, and final judgment in your main coding agent, while moving narrow execution slices into durable task bundles with explicit path scope, saved results, and local verification.

## Public v1 Boundary

This repo intentionally includes only the public kernel:

- `submit` to create a durable task bundle
- `run` to send the bundle through a configured provider
- `result` to read saved results
- `apply` to gate and apply returned patches locally
- `verify` to run local verification commands
- `doctor` to sanity-check provider config and model visibility
- `install-skill` to copy the public `agx-orchestrator` skill into Codex

This repo intentionally does not include:

- Telegram control
- Hetzner deployment flows
- hidden proxy startup
- vendor quota scraping
- remote shell behavior

## Core Loop

`Codex plans -> agx-core runs one bounded packet -> local checks run -> Codex reviews and accepts or rejects`

The point is not “agent swarm theater”.
The point is a durable, replayable execution lane with clear scope and evidence.

## Why It Exists

When everything stays in one chat thread, narrow execution work often becomes expensive, noisy, or hard to verify.

`agx-core` makes that smaller job explicit:

- one goal
- explicit allowed paths
- minimal context files
- local verification commands
- one saved run result

## Provider Model

Public v1 is API-first.

Supported provider surfaces:

- `anthropic`
- `openai-compatible`

You can point `openai-compatible` at any gateway that speaks a normal chat-completions and models surface.

## Quick Start

See [QUICKSTART.md](/Users/nick/myprojects/agx-core/QUICKSTART.md).

Short version:

1. create a virtualenv and install the package
2. export `AGX_PROVIDER`, `AGX_API_KEY`, and optional `AGX_BASE_URL`
3. run `agx-core doctor`
4. create a tiny repo
5. run `agx-core submit`
6. run `agx-core run --apply --verify`

## Skill

The public Codex skill lives at [skills/agx-orchestrator/SKILL.md](/Users/nick/myprojects/agx-core/skills/agx-orchestrator/SKILL.md).

It teaches one routing rule:

- keep planning and acceptance in Codex
- dispatch only bounded execution slices

## Examples

- [quickstart-patch](/Users/nick/myprojects/agx-core/examples/quickstart-patch/README.md)
- [live2reels-first-slice](/Users/nick/myprojects/agx-core/examples/live2reels-first-slice/README.md)

## Origin

The layer-separation and control-plane framing here were inspired by Sereja Ris and [ai-corp.sereja.tech](https://ai-corp.sereja.tech/).

What `agx-core` adds on top is the local dispatcher kernel itself:

- durable task bundles
- saved run artifacts
- local patch gating
- local verification
- a Codex-oriented bounded execution lane

## Repo Truth

Durable execution docs for this scaffold live in:

- [plans.md](/Users/nick/myprojects/agx-core/docs/plans.md)
- [status.md](/Users/nick/myprojects/agx-core/docs/status.md)
- [test-plan.md](/Users/nick/myprojects/agx-core/docs/test-plan.md)

