# AUTOMATION_AND_AGENTS.md
Last updated: 2026-06-21
Updated by: Claude (research synthesis)

What people do with Claude Code + Codex (loops, autonomy, multi-agent), how this
project already lines up with best practice, and what to turn on — and when.
This is the "learn and document before doing loops" reference.

---

## The 5 Claude Code workflow patterns (least → most autonomous)
1. **Sequential** — one task at a time, human reviews each step. (What we do now.)
2. **Operator** — agent proposes, human approves before acting.
3. **Split-and-merge** — parallel subagents on independent sub-tasks, merged.
4. **Agent teams** — multiple specialized agents collaborating (3–4× token cost).
5. **Headless** — fully autonomous, triggered by event/schedule, runs to a stop
   condition, no human in the loop. Highest payoff, needs the most guardrails.

Recommended progression (industry + Anthropic): **start sequential, add headless
only for well-guarded CI-style tasks, reach for parallel/teams only when work is
genuinely independent.** Don't pay the parallel token cost without a reason.

## Anthropic's long-running-agent pattern == what we already built
Anthropic's guidance for agents that span many context windows: an **initializer
agent** that sets up the environment once, and a **coding agent** that makes
**incremental progress each session and leaves clear artifacts** for the next.
We already have this:
- Initializer = `CHARTER` + `AUTHORIZATION` + `SESSION_WARMUP` + `AGENT_CAPABILITIES/`
- Incremental + artifacts = small committed chunks + `BUILDLOG` "Next:" + `SESSION INCOMPLETE`
So turning on loops is mostly *wiring a trigger* onto a system that's already shaped right.

## Safeguards (do not skip when going autonomous)
- **Least privilege** — only the tools/permissions a task needs.
- **Prefer reversible actions**; commit before risky changes (already our rule).
- **Human checkpoints for high-stakes/irreversible/outward-facing steps** (matches
  `AUTHORIZATION.md`: installs/UAC, product-direction, anything hard to undo).

## Claude + Codex together (how others split the work)
- **Race**: run both on the same task, compare diffs, keep the better. Good for hard problems.
- **Route by strength**: Claude → multi-file refactors, architecture, contextual reasoning;
  Codex → targeted functions, test writing (esp. Python/JS).
- **Isolation**: each agent in its own **git worktree** so they don't collide; merge with review.
- **Shared state only through committed files** (already our cross-agent rule).
- For THIS project: Claude on engine/C++/architecture; Codex on test scripts, tooling,
  data/utility code — handing off via `BUILDLOG`.

## What we could turn on for THIS project (when ready)
| Loop | Trigger | Value | Guardrail |
|---|---|---|---|
| Physics regression | on push / schedule | run `run_physics_harness.py`, flag if a known-good result regresses | read-only report; no auto-edits |
| Trusted local build check | human-approved revision | compile C++ with the local engine | no persistent public-repo runner; exact clean revision/branch/remote gate; editor closed |
| Autonomous chunk loop | `/loop` or scheduled agent | do the next `BUILDLOG` item, verify, commit, write next | small chunks; stop on ambiguity/failure |
| Nightly capability re-verify | schedule | run `SESSION_WARMUP` checks, refresh anything down | report-only |

## Professions → capabilities map (and gaps to fill)
| Role | Tooling we have | Gap / add next |
|---|---|---|
| Build engineer | UE C++ build, CMake/Ninja | — |
| QA / test | physics harness, CI | more automated functional tests |
| 3D artist | Blender 5.1 | (re-verify 5.x scripts) |
| 2D/UI artist | ImageMagick, Inkscape, Krita | — |
| Sound designer | SoX, ffmpeg | — |
| Tech writer / docs | Pandoc, Graphviz | — |
| Level designer | **remote exec can build levels programmatically** | level-gen scripts |
| DevOps / release | GitHub Actions CI, gh, Agent Workbench trusted-build gate | UE packaging pipeline (local, gated; no persistent public-repo runner) |
| Data / telemetry analyst | Python | pandas/numpy/matplotlib (pip), a metrics sink |
| Security | `/security-review` skill | dependency/secret scanning in CI |
| Localization | — | text-extraction + po/gettext if/when needed |
| Producer / orchestrator | BUILDLOG, tasks, this doc | the loop trigger itself |

## Bottom line
The private cross-project Agent Workbench now supplies the loop infrastructure:
local Ollama routing, a ledger, constrained workers, scheduling, recovery, and
telemetry. Kurearthis is intentionally registered read/draft-only. The next safe
progression is to prove report-only and allowlisted regression loops before any
write or build permission is considered. Do it on a small, reversible loop first.
