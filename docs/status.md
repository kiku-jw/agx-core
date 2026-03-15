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

## In progress

- none

## Next

- run a real disposable-repo smoke against one direct provider
- create the public GitHub repo and push the scaffold there
- tighten README examples after the first live run
- decide whether patch repair belongs in `agx-core` v1 or later

## Blockers

- no live provider smoke has been run from this scaffold yet

