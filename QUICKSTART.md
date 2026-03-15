# QUICKSTART

This is the shortest honest path to a first `agx-core` run.

## 1. Install

```bash
cd /Users/nick/myprojects/agx-core
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2. Pick a provider

### Anthropic

```bash
export AGX_PROVIDER=anthropic
export AGX_API_KEY=YOUR_ANTHROPIC_KEY
```

Optional:

```bash
export AGX_MODEL_ALIASES_JSON='{"sonnet":"YOUR_MODEL_ID","opus":"YOUR_REVIEW_MODEL_ID"}'
export AGX_DEFAULT_FALLBACKS_JSON='{"sonnet":["opus"]}'
```

### OpenAI-compatible

```bash
export AGX_PROVIDER=openai-compatible
export AGX_API_KEY=YOUR_API_KEY
export AGX_BASE_URL=https://api.openai.com/v1
```

Optional:

```bash
export AGX_MODEL_ALIASES_JSON='{"fast":"YOUR_FAST_MODEL","strong":"YOUR_STRONG_MODEL"}'
export AGX_DEFAULT_FALLBACKS_JSON='{"fast":["strong"]}'
```

## 3. Check connectivity

```bash
agx-core doctor
```

Healthy means:

- API key is configured
- model list can be fetched
- alias targets are visible or no aliases were configured

## 4. Create a disposable repo

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
git init -q
printf 'hello\n' > message.txt
git add message.txt
git -c user.name='AGX' -c user.email='agx@example.com' commit -q -m init
```

## 5. Submit a bounded task

```bash
cd /Users/nick/myprojects/agx-core
agx-core submit \
  --cwd "$tmpdir" \
  --title "Quickstart patch" \
  --goal "Update message.txt so its only line becomes exactly hello from agx core" \
  --allowed-path message.txt \
  --context-file message.txt \
  --context-note "Return a unified diff patch for message.txt only." \
  --constraint "Do not touch any other file." \
  --verify "grep -qx 'hello from agx core' message.txt" \
  --require-patch \
  --model YOUR_MODEL_ID
```

If you rely on aliases instead of exact model ids, replace `YOUR_MODEL_ID` with the alias you configured.

## 6. Run, apply, verify

```bash
task_path="$(find "$tmpdir/.agx/tasks" -name task.json | head -n 1)"
agx-core run "$task_path" --apply --verify
```

## 7. Read the saved result

```bash
run_id="$(ls "$tmpdir/.agx/results" | sed 's/\\.json$//' | head -n 1)"
agx-core result "$run_id" --cwd "$tmpdir"
```

## Stop And Fix First

Stop before real work if:

- `doctor` cannot fetch models
- your configured alias targets are missing
- the task cannot be expressed with explicit `allowed_paths`
- the task has no local verification command

## Next

- [quickstart-patch](/Users/nick/myprojects/agx-core/examples/quickstart-patch/README.md)
- [live2reels-first-slice](/Users/nick/myprojects/agx-core/examples/live2reels-first-slice/README.md)
- [agx-orchestrator skill](/Users/nick/myprojects/agx-core/skills/agx-orchestrator/SKILL.md)

