# API-First Layered Routing

This is the public shape of the mini-corp pattern.

Keep only the reusable part:

- separate planning from execution
- keep one source of truth per layer
- dispatch only bounded packets
- keep review independent from implementation

## Layer Map

| Layer | Main question | Source of truth | Default lane | Dispatch through `agx-core`? |
| --- | --- | --- | --- | --- |
| Operator | What outcome matters and what are the rules? | user request and local instructions | Codex | no |
| Strategy | What should be built and why? | validation, product notes, spec bundle | Codex | no |
| Project truth | What is true about the system right now? | repo code, contracts, tests | Codex | usually no |
| Execution | What bounded change should happen next? | task bundle with explicit paths and verification | `agx-core` | yes, when scoped |
| Review | Is the result real and good enough? | local tests, diff, saved run result | Codex or adversarial review | only as a bounded second pass |

## Trigger Protocol

Use this order:

1. find the blocked layer
2. name the work type
3. name the required artifact
4. only then decide whether to dispatch

## Keep-Vs-Dispatch Rule

Keep the task inside Codex when:

- the work is still ambiguous
- contracts or architecture are still moving
- the output is judgment, not a bounded artifact
- local verification does not exist yet

Dispatch through `agx-core` when:

- the task is already at the execution layer
- writable paths can be named
- verification exists or can be written now
- failure is repairable without hidden manual theater

## Packet Rule

One packet should carry:

- one goal
- explicit allowed paths
- minimum context files
- local verification commands
- constraints and non-goals

If that packet cannot be written cleanly, the task is not ready to leave Codex.

