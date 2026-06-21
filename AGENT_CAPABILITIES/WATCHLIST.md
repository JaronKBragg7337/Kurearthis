# WATCHLIST.md
Last updated: 2026-06-21
Updated by: Codex (corrected)

This file tracks new tools, MCPs, model updates, TOS changes, and experiments to revisit.
Anything that could change what's possible belongs here.

---

## Corrections + fixes (2026-06-20)
| Item | Reality / fix |
|---|---|
| "Unreal Engine MCP now available/active" | [CLAUDE-ENV] **Not loaded for Claude** — editor driven via console + GUI. Agent/session-specific; Codex checks its own. |
| "gh confirmed authenticated" | Was NOT authed → **FIXED**: now logged in as JaronKBragg7337 (machine keyring). |
| "Docker installed" | Was daemon-off → **FIXED**: Docker Desktop started, daemon up (29.5.3). |
| "Codex environment parity unknown" | **PARTIALLY RESOLVED:** Codex verified filesystem/shell, remote Unreal execution, Scoop, Go/Rust/Java/Git LFS, visual file inspection, and the OCR/PDF stack. MCP/app availability remains session-specific. |

## To verify / investigate
| Item | Why it matters | Priority |
|---|---|---|
| Local collision chunk + radial controller | The proven-necessary next architecture layer (Proof 2c). Build it. | High |
| Codex environment parity | Continue recording session-specific MCP/app discoveries; machine-level CLI parity is now verified | Medium |
| Blender 5.1.2 Python API | **Resolved:** `pipeline_smoketest.py` passes Blender 5.1.2 → UE 5.8 | Done |
| Unreal MCP (if one becomes available/loadable) | Would replace console+GUI driving with structured calls | Medium |
| Blender MCP | Could augment the headless CLI pipeline | Low |

## Rule
When Claude or Codex hits a limit or finishes research, check here before concluding
something is impossible — and use ToolSearch to confirm what is actually loaded rather
than trusting these notes. Record discoveries in CHANGELOG_CAPABILITIES.md.
