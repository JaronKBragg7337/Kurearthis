# USAGE_AND_LIMITS.md
Last updated: 2026-06-21
Updated by: Claude

How the usage meters work and how to get the most build per token. This is
strategy knowledge for Jaron and the agents — not a hard rule.

---

## The three meters are different things
| Meter | Scope | Resets | What grows it | Lever |
|---|---|---|---|---|
| **Context window** (e.g. 56% / 1M) | THIS chat | a new chat → ~0 | every message + tool result in the conversation | start a fresh chat when it gets high (~80%+); the repo files reload context cheaply |
| **5-hour limit** | rolling 5h | every 5h | all work in the window | pace bursty work; it's a throttle, not the ceiling |
| **Weekly (all models)** | the week | weekly | sustained work | the real budget — watch this for big pushes |

## Worked example (2026-06-21, the four capability upgrades)
- Context: 50% → 56% (~6% for a big multi-step chunk)
- 5-hour: 18% → 30% (~12%)
- Weekly: 31% → 32% (~1%)
Takeaway: a substantial chunk barely touched the **weekly** budget; **context**
crept up the most. So context — not weekly — is usually what decides "fresh chat
or keep going."

## Decision rules
- **Keep going in this chat** while context < ~80% and the task is continuous.
- **Start a fresh chat** when context is high OR the task clearly changes. A fresh
  chat re-reads CHARTER / WORKFLOW / AUTHORIZATION / AGENT_CAPABILITIES / BUILDLOG
  and is productive within seconds — that's what those files are for.
- **Switch to Codex** for *parallelism* (two agents at once) or if the **weekly**
  meter is genuinely low — not just because one chat got long.
- **Hand off cleanly** before stopping: BUILDLOG "Next:" + `SESSION INCOMPLETE`
  so any agent/chat resumes mid-stream with zero lost work.

## Getting more build per token
- **Small committed chunks** — never lose progress; cheap to resume.
- **Right model for the step** — routine edits/inventory on a cheaper model;
  reserve the strongest model for hard reasoning.
- **Push work off the live budget** — background tasks, scheduled/cron agents, and
  CI do work without spending interactive turns.
- **Scriptable > manual** — remote exec + the physics harness mean one command
  instead of dozens of GUI tool-calls (each of which costs context + budget).
- **Two agents, shared via committed files** — Claude + Codex roughly double
  effective hours.
