# Quickstart Patch Example

This is the smallest honest `agx-core` job:

- one file
- one allowed path
- one verification command
- one patch result

Use it after [QUICKSTART.md](/Users/nick/myprojects/agx-core/QUICKSTART.md) proves that provider access is configured.

## Packet shape

- goal: change exactly one line
- allowed paths: `message.txt`
- context files: `message.txt`
- verify: one `grep -qx` command

This is the baseline pattern for any public demo.
If a task cannot be narrowed down to something this explicit, it probably should stay in Codex planning first.

