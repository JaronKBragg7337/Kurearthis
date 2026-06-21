# WATCHLIST.md
Last updated: 2026-06-20
Updated by: Claude (corrected)

This file tracks new tools, MCPs, model updates, TOS changes, and experiments to revisit.
Anything that could change what's possible belongs here.

---

## Corrections + fixes (2026-06-20)
| Item | Reality / fix |
|---|---|
| "Unreal Engine MCP now available/active" | [CLAUDE-ENV] **Not loaded for Claude** — editor driven via console + GUI. Agent/session-specific; Codex checks its own. |
| "gh confirmed authenticated" | Was NOT authed → **FIXED**: now logged in as JaronKBragg7337 (machine keyring). |
| "Docker installed" | Was daemon-off → **FIXED**: Docker Desktop started, daemon up (29.5.3). |

## To verify / investigate
| Item | Why it matters | Priority |
|---|---|---|
| Local collision chunk + radial controller | The proven-necessary next architecture layer (Proof 2c). Build it. | High |
| Codex environment parity | Confirm what MCP tools/paths Codex actually has — agent-specific items here ([CLAUDE-ENV]) may not apply to it | High |
| Blender 5.1.2 Python API | Blender jumped to 5.x; re-verify the FBX authoring scripts still run | Medium |
| Unreal MCP (if one becomes available/loadable) | Would replace console+GUI driving with structured calls | Medium |
| Blender MCP | Could augment the headless CLI pipeline | Low |

## Rule
When Claude or Codex hits a limit or finishes research, check here before concluding
something is impossible — and use ToolSearch to confirm what is actually loaded rather
than trusting these notes. Record discoveries in CHANGELOG_CAPABILITIES.md.
