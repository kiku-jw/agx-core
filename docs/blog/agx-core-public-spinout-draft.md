---
title: "AGX Core: Shipping the Execution Lane Without the Private Baggage"
slug: "agx-core-public-execution-lane"
status: "final-draft"
summary: "How I split a small public execution kernel out of a messier private agent stack and validated it with tests plus a live proxy smoke."
---

My private `agx` repo had started to annoy me.

Not because it was useless. The useful part was actually pretty small: take one narrow task packet, run it through an external model lane, save the result, apply a patch locally, and verify it.

The problem was everything that had grown around it.

Telegram control. Hetzner notes. OpenClaw migration glue. Proxy-specific habits. Parked runtime paths. Private operator baggage.

That mix is fine inside a private working repo. It is bad as a public artifact.

So instead of making the private repo public and pretending the whole thing was a product, I split out the part that actually deserved daylight.

The result is [`agx-core`](https://github.com/kiku-jw/agx-core): a small, API-first execution kernel for bounded agent work.

## The Public Cut

The public repo keeps the part I would actually recommend to another builder:

- one durable task bundle
- one bounded execution run
- saved request and response artifacts
- local patch gating
- local apply
- local verification
- one narrow `agx-orchestrator` skill that tells Codex when to dispatch and when not to

The operating model is deliberately boring:

`Codex plans -> agx-core runs one bounded packet -> local checks run -> Codex accepts or rejects`

That is the whole point.

I did not want to publish a bag of private conveniences and call it a framework. I wanted one execution lane that is explicit enough to trust.

## What I Cut

The private repo still has material that was useful for me personally, but wrong for a public v1:

- Telegram control
- Telegram-to-Codex job intake
- Hetzner deployment flow
- OpenClaw migration helpers
- proxy startup behavior
- vendor quota-log scraping

Those are not fake features. They are just not the kernel.

Public tooling gets muddy fast when you dump every private convenience into the first release. The repo starts telling a confusing story: is this a small execution lane, a remote control surface, a server deployment kit, or a proxy ops bundle?

I wanted the public answer to be clean: it is the execution lane.

## What The Repo Is For

`agx-core` is for the moment after planning is already done.

You have a real task. You can name the writable paths. You can give the minimum context files. You can write at least one local verification command. Now you want to hand that bounded packet to another model lane without turning chat history into the source of truth.

That is where the repo is useful.

The public `agx-orchestrator` skill follows the same rule. It does not tell Codex to throw big vague work into a worker swarm. It says:

- keep planning in Codex
- keep final judgment in Codex
- dispatch only bounded execution slices

That is a much smaller promise, but it is also a real one.

## The First Real Check

I wanted more than a repo skeleton and a nice README, so I pushed the public scaffold and then forced it through a real local smoke.

At the time of writing:

- the public repo exists: [`kiku-jw/agx-core`](https://github.com/kiku-jw/agx-core)
- the scaffold commit is `933a1da`
- the follow-up commit `acabb42` adds localhost proxy mode so the public quickstart does not require a fake `AGX_API_KEY=dummy`
- the repo test suite passes with `21 passed`
- localhost proxy mode now passes `agx-core doctor` without exporting `AGX_API_KEY`

Then I ran a disposable-repo smoke through my local Antigravity-compatible proxy:

1. create a tiny git repo with one file
2. submit one packet against `message.txt`
3. run `agx-core run --apply --verify`
4. inspect the saved result

The run finished with:

- `status=completed`
- `patch_quality=ready`
- `local_apply=applied`
- `local_verification=passed`

And the file really changed to the expected content.

That matters more than a long roadmap.

## One Non-Obvious Lesson

The smoke also surfaced something I am glad I caught in a public-friendly form.

I asked for `claude-sonnet-4-6`, but the proxy reported `gemini-2.5-flash` in the saved result.

In other words:

- the requested attempt lane was `claude-sonnet-4-6`
- the transport layer reported `gemini-2.5-flash`
- the run still succeeded

This is exactly why I care about durable execution artifacts.

If you only watch the terminal, you can tell yourself a neat story about what happened. If you save the packet, attempts, result, patch, and local verification, you can see what actually happened.

That is a better foundation for agent tooling than vibes about orchestration.

## Credit Where It Belongs

The public repo is mine, but the framing did not come out of nowhere.

The layer-separation part was strongly shaped by Sereja Ris and `ai-corp.sereja.tech`: keep one truth source per layer, separate planning from execution, and keep review independent.

What I added on top is the smaller local kernel:

- durable task bundles
- saved run artifacts
- local patch gating
- local verification
- a Codex-oriented bounded execution lane

I would rather name that influence directly than pretend every useful idea started in my own repo.

## What Happens Next

I also added `AGX Orchestrator` to my public awesome list of skills so the repo is discoverable from the skill side, not only as a standalone tool.

The next real checks are straightforward:

- run the same smoke against a direct vendor API instead of only a local proxy
- decide whether patch repair belongs in the public v1 or should stay out for now
- write the broader mini-corp post only after the smaller execution lane story stands on its own

For now, this feels like the right cut.

Not a framework dump. Not a private ops leak. Just the part that actually earned a public repo.
