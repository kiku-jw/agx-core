---
name: agx-orchestrator
description: Use when Codex should keep planning and final judgment, but a bounded coding or review packet should run through `agx-core` with explicit allowed paths, saved results, and local verification.
---

# AGX Orchestrator

## Metadata
- Trigger when: the blocked layer is execution, the artifact is explicit, and the task can be expressed as one bounded packet.
- Do not use when: the work is still strategy, architecture, MCP, secrets, merge judgment, or vague discovery.

## Skill Purpose

Keep planning, acceptance, and final judgment in Codex while routing one narrow execution slice through `agx-core` only after scope, writable paths, and local verification are explicit.

## Instructions
### 1. Gate the layer first

- Keep the task in Codex if the real blocker is planning, architecture, contracts, or acceptance.
- Dispatch only when the blocked layer is execution and the end artifact is concrete.
- Read `/Users/nick/myprojects/agx-core/skills/agx-orchestrator/references/layered-routing.md` if the routing boundary is fuzzy.

### 2. Build one bounded packet

- Name one goal.
- Require explicit `allowed_paths`.
- Include only the minimum `context_files` and `context_notes` needed.
- Add at least one local verification command when code is supposed to change.
- Use `agx-core submit` and choose either an exact model id or a configured alias.

### 3. Run, verify, and bring judgment back

- Use `agx-core doctor` before dispatch if provider health is uncertain.
- Run `agx-core run ... --apply --verify` when the task is patch-oriented and verification is ready.
- Review the saved result in Codex and decide accept or reject there.

## Non-Negotiable Acceptance Criteria
- Do not dispatch before the blocked layer and end artifact are explicit.
- Do not dispatch work that still depends on secrets, MCP-only context, or merge judgment.
- Do not send a packet without `allowed_paths`.
- Do not treat provider choice as product identity.
- Do not skip local verification when the task is meant to change code.
- Do not leave the final accept-or-reject decision outside Codex.

## Output
- `layer`: strategy | truth | acceptance | execution
- `decision`: keep_in_codex | dispatch_via_agx_core
- `artifact`: required end artifact
- `packet`: task bundle path or short packet description
- `provider`: anthropic | openai-compatible | n/a
- `model`: exact model id, alias, or `n/a`
- `validation`: local checks that will prove success
- `review_lane`: codex | adversarial_review | n/a

