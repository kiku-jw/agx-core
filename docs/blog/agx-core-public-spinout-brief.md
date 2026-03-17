# AGX Core Public Spinout Brief

Date: 2026-03-15

## Questions

- Angle: how to extract the useful public kernel from a private agent workflow without shipping the baggage.
- Audience: builders using Codex, Claude Code, or similar tools who want bounded execution lanes instead of “agent framework” theater.
- Takeaway: keep planning and final judgment in the main agent, dispatch only narrow packets, and save durable execution artifacts.
- Exclusions: no private Telegram runtime, no Hetzner deployment walkthrough, no OpenClaw migration details, no fake traction claims.

## Research / Evidence

- Public repo: [kiku-jw/agx-core](https://github.com/kiku-jw/agx-core)
- Initial public scaffold commit: `933a1da`
- Localhost proxy mode commit: `acabb42`
- Awesome list update: [kiku-jw/awesome-ai-skills-by-kiku](https://github.com/kiku-jw/awesome-ai-skills-by-kiku) commit `7ec28c8`
- Repo tests: `21 passed`
- Live local smoke through Antigravity-compatible proxy:
  `submit -> run --apply --verify -> result`
- Verified localhost proxy mode without exporting `AGX_API_KEY`
- Public `agx-orchestrator` skill published under the repo

## Related Assets

- [README.md](/Users/nick/myprojects/agx-core/README.md)
- [QUICKSTART.md](/Users/nick/myprojects/agx-core/QUICKSTART.md)
- [SKILL.md](/Users/nick/myprojects/agx-core/skills/agx-orchestrator/SKILL.md)
- [live2reels-first-slice example](/Users/nick/myprojects/agx-core/examples/live2reels-first-slice/README.md)

## Brief

- Thesis: the useful part of an agent “mini-corp” is usually a small durable kernel, not the private operator surface that grew around it.
- Structure:
  1. start with the embarrassment of a private repo mixing core and baggage
  2. explain what got cut and why
  3. show what the public kernel actually does
  4. prove it with tests and a live proxy smoke
  5. end with one non-obvious lesson from the smoke
- Proof points:
  - new public repo
  - public skill path
  - awesome list update
  - live smoke through local proxy
  - localhost proxy mode no longer needs `AGX_API_KEY=dummy`
  - explicit credit to Sereja Ris / AI Corp for the layer-separation inspiration
- Excluded material:
  - private infra specifics
  - any claim of adoption or performance that we did not measure
  - pretending this is a full framework or a hosted platform

