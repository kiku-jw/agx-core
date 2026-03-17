# Build Diary Tracker

## Status

- artifact type: build diary
- current phase: Complete
- public-safe gate: passed
- draft path: /Users/nick/myprojects/agx-core/docs/blog/agx-core-public-spinout-draft.md
- canonical post path: /Users/nick/myprojects/kikuai-blog/content/blog/2026-03-17-agx-core-public-execution-lane.md
- review status: final draft packaged, saved to the blog repo, and ready as the canonical public artifact

## Checklist

- [x] Phase 1: Questions
- [x] Phase 2: Research / Evidence
- [x] Phase 2.5: Related Assets
- [x] Phase 2.7: Brief
- [x] Phase 3: Draft
- [x] Phase 4: Critique / Deaify
- [x] Phase 5: Title / Packaging
- [x] Phase 6: Publish Prep

## Phase 1: Questions

- angle: extract the useful public kernel from a private agent workflow without shipping the baggage.
- audience: builders using Codex, Claude Code, or similar tools who want bounded execution lanes instead of framework theater.
- takeaway: keep planning and final judgment in the main agent, dispatch only narrow packets, and save durable execution artifacts.
- exclusions: no Telegram runtime, no Hetzner walkthrough, no OpenClaw migration details, no fake traction claims.

## Phase 2: Research / Evidence

- sources: https://github.com/kiku-jw/agx-core ; commits 933a1da and acabb42 ; https://github.com/kiku-jw/awesome-ai-skills-by-kiku commit 7ec28c8.
- screenshots or demos: local agx-core doctor against proxy; disposable-repo smoke with apply and verify passing; public skill path in agx-core.
- unverified claims: no public adoption numbers; no direct vendor API smoke yet.
- missing evidence: benchmark against full-chat workflow; second provider smoke; screenshot packaging.

## Phase 2.5: Related Assets

- internal links: README.md ; QUICKSTART.md ; skills/agx-orchestrator/SKILL.md ; examples/live2reels-first-slice/README.md.
- prior posts: none yet for this public spinout.
- visuals: terminal screenshot of proxy doctor and smoke result would help; simple Codex -> agx-core -> verify diagram later.

## Phase 2.7: Brief

- thesis: the useful part of an agent mini-corp is a small durable kernel, not the private operator surface around it.
- structure: awkward private repo -> what got cut -> what shipped -> proof via tests and smoke -> lesson about requested vs reported model.
- proof points: public repo, public skill, awesome listing, 21 passing tests, live proxy smoke, localhost proxy mode without manual dummy key, explicit inspiration note.
- excluded material: Telegram control, Hetzner deployment, OpenClaw migration, fake adoption or performance claims.

## Phase 3: Draft

- draft path: /Users/nick/myprojects/agx-core/docs/blog/agx-core-public-spinout-draft.md
- evidence pack used: public repo commits 933a1da and acabb42, awesome commit 7ec28c8, test run 21 passed, local proxy smoke with apply and verify passed.

## Phase 4: Critique / Deaify

- issues found: the first title was too generic; some phrasing still leaned too close to "framework" talk; direct vendor API smoke is still not in the evidence pack.
- fixes applied: tightened the title around the real cut, reduced vague "agent stack" language, kept claims bounded to repo/tests/proxy smoke, and kept the attribution section explicit.

## Phase 5: Title / Packaging

- title: AGX Core: Shipping the Execution Lane Without the Private Baggage
- slug: agx-core-public-execution-lane
- short description: How I split a small public execution kernel out of a messier private agent stack and validated it with tests plus a live proxy smoke.

## Phase 6: Publish Prep

- save location: /Users/nick/myprojects/kikuai-blog/content/blog/2026-03-17-agx-core-public-execution-lane.md
- review queue: none; the canonical copy is the blog repo article and the evidence pack remains in this repo
- announcement TODOs: keep AGX listed in the public awesome repo; optional follow-up post about the wider mini-corp lane after direct-vendor smoke and a second example run
