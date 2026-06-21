# WATCHLIST.md
Last updated: 2026-06-20
Updated by: Claude (corrected)

This file tracks new tools, MCPs, model updates, TOS changes, and experiments to revisit.
Anything that could change what's possible belongs here.

---

## Corrections to earlier assumptions (2026-06-20)
| Item | Reality (verified) |
|---|---|
| "Unreal Engine MCP now available/active" | **Not present** in the Claude environment. Editor is driven via Python console + GUI automation. If an Unreal MCP is added later, re-verify and update CONNECTED_TOOLS. |
| "gh confirmed working/authenticated" | `gh` installed but **NOT authenticated**. Git push/pull work via Credential Manager. |
| "Docker installed — potential services" | Installed but **daemon not running**. |

## To verify / investigate
| Item | Why it matters | Priority |
|---|---|---|
| Local collision chunk + radial controller | The proven-necessary next architecture layer (Proof 2c). Build it. | High |
| Blender 5.1.2 Python API | Blender jumped to 5.x; re-verify the FBX authoring scripts still run | Medium |
| Authenticate `gh` (or set GH_TOKEN) | Needed if we ever want `gh pr/issue/api`; not needed for push/pull | Low |
| Unreal MCP (if one becomes available) | Would replace console+GUI driving with structured calls | Medium |
| Blender MCP | Could augment the headless CLI pipeline | Low |
| Docker (start daemon) | Only if a containerized workflow is actually needed | Low |
| Codex environment parity | Confirm what tools/paths Codex actually has — may differ from this machine's Claude env | High |

## Rule
When Claude or Codex hits a limit or finishes research, check here before concluding
something is impossible — and use ToolSearch to confirm what is actually loaded rather
than trusting these notes. Record discoveries in CHANGELOG_CAPABILITIES.md.
