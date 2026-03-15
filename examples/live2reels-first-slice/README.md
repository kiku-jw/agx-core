# Live2Reels First Slice

This is the first real implementation slice for the Live2Reels spec bundle.

It is intentionally smaller than the full product:

- no Whisper yet
- no cloud analysis yet
- no Remotion rendering yet

The goal is to prove one stable local workflow first:

`create project -> import transcript -> persist local state -> open transcript data`

## Why this slice first

From the provided bundle:

- the PRD already allows transcript import as a first-class path
- the contracts define `CreateProject`, `ImportSource`, and `GetTranscript`
- the schema already defines `project`, `source_asset`, `transcript`, and `transcript_token`
- the test plan already has transcript-import integration and e2e coverage

This is exactly the kind of slice that should be frozen in Codex and then dispatched as bounded packets through AGX.

## Definition of done

- a project can be created
- a transcript file can be imported
- local DB rows are persisted for `project`, `source_asset`, and `transcript`
- the transcript can be read back through the application contract
- the result survives app restart

## Suggested packet order

1. backend packet
2. transcript-import packet
3. UI/readback packet
4. skeptical review packet

See `packet-outline.md` for the bounded AGX packet shapes.
