# Live2Reels Packet Outline

These are Codex-to-AGX packet shapes, not vague prompts.

Use them only after the implementation slice and paths are fixed in the actual Live2Reels repo.

## Packet 1: project creation + local persistence

- Goal: implement `CreateProjectRequest` and persist a `project` row
- Keep in Codex first: choose exact module boundaries and storage adapter shape
- Dispatch through AGX after that
- Suggested lane: `sonnet`

Required packet fields:

- allowed paths:
  - `src/main/ipc/projects.ts`
  - `src/main/db/projects.ts`
  - `tests/integration/projects.test.ts`
- context files:
  - current IPC handler
  - current DB adapter
  - `Project` contract excerpt
  - schema excerpt for `project`
- verify:
  - one integration command that proves `CreateProjectResponse.project`

## Packet 2: transcript import

- Goal: import `.txt` / `.srt` transcript into `source_asset`, `transcript`, and synthetic or timed transcript rows
- Suggested lane: `gemini-pro`, fallback `sonnet`

Required packet fields:

- allowed paths:
  - `src/main/ipc/import.ts`
  - `src/main/transcript/importers/*`
  - `src/main/db/transcripts.ts`
  - `tests/integration/transcript-import.test.ts`
- context files:
  - import contract excerpt
  - transcript contract excerpt
  - transcript-related schema excerpt
  - one fixture transcript file
- verify:
  - integration test for txt import
  - integration test for srt import if that support is included in the packet

## Packet 3: readback + transcript view

- Goal: implement `GetTranscriptRequest` readback and show transcript data in a narrow transcript view
- Suggested lane: `gemini-fast` for UI if readback is already stable, otherwise `sonnet`

Required packet fields:

- allowed paths:
  - `src/main/ipc/transcript.ts`
  - `src/renderer/transcript/*`
  - `tests/transcript-view.test.ts`
- context files:
  - `GetTranscript` contract
  - transcript DB reader
  - current transcript component
- verify:
  - one renderer/component test
  - one integration check for `GetTranscriptResponse`

## Packet 4: skeptical review

- Goal: review restart resilience, transcript integrity, and local-only data handling for this slice
- Suggested lane: `opus`

Review questions:

- does restart create duplicate rows?
- does txt import degrade safely without timings?
- do the persisted rows match the contracts bundle?
- is any cloud dependency accidentally required in this local-first slice?
