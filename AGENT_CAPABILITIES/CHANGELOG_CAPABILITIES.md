# CHANGELOG_CAPABILITIES.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file is a dated log of capability changes — new tools discovered, limits found, integrations added or removed.
This is separate from BUILDLOG (which tracks what was BUILT).
This tracks what became POSSIBLE or IMPOSSIBLE.

---

## 2026-06-20 — Initial capability registry created
- Created by: Perplexity AI
- Reason: Prior sessions were assuming capabilities incorrectly, missing newly possible integrations, and repeating failing workflows without checking alternatives.
- Files created: SYSTEM_INVENTORY.md, CURRENT_STACK.md, CONNECTED_TOOLS.md, LOCAL_APPS_AND_SERVICES.md, TESTED_WORKFLOWS.md, KNOWN_LIMITS.md, WATCHLIST.md, CHANGELOG_CAPABILITIES.md
- Trigger rule added to WORKFLOW.md: agents must inspect local environment and consult AGENT_CAPABILITIES/ before assuming a tool is unavailable or repeating a failing path.

## 2026-06 (approx) — Unreal Engine MCP confirmed available
- Unreal MCP became available approximately one week before this entry.
- Prior to this, Unreal integration required manual scripting only.
- Now enables live actor enumeration, import, and editor control from Claude Code.

---

## Entry format (for future updates)
```
## YYYY-MM-DD — [What changed]
- Changed by: [Claude | Codex | Perplexity | Jaron]
- What is now possible: [description]
- What is now impossible or blocked: [description]
- Source: [link, TOS notice, test result, etc.]
```
