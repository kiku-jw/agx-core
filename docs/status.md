# AGX Core Status

## Current phase

`Public kernel scaffold`

## Done

- created a separate `agx-core` repo next to the private `agx`
- wrote a public README and API-first quickstart
- added durable execution docs
- ported repo-local `.agx/` runtime storage
- ported patch gating, local apply, and local verification
- added provider adapters for `anthropic` and `openai-compatible`
- added a provider-agnostic `doctor`
- added a public `agx-orchestrator` skill and routing reference
- copied public Live2Reels example artifacts
- added base unit tests for config, storage, runner, apply, and doctor
- verified a real `agx-core` disposable-repo smoke through the local Antigravity proxy with `apply` and `verify` both passing
- added localhost proxy compatibility so `agx-core doctor` and the Anthropic transport do not require a manual `AGX_API_KEY=dummy`

## In progress

- none

## Next

- run a real disposable-repo smoke against one direct vendor API
- create the public GitHub repo and push the scaffold there
- tighten README examples after the first live run
- decide whether patch repair belongs in `agx-core` v1 or later
