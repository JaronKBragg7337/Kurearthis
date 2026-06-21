# CHANGELOG_CAPABILITIES.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file is a dated log of capability changes — new tools discovered, limits found, integrations added or removed.
This is separate from BUILDLOG (which tracks what was BUILT).
This tracks what became POSSIBLE or IMPOSSIBLE.

---

## 2026-06-20 — Registry verified against the live machine (Claude)
- Changed by: Claude
- What is now confirmed POSSIBLE (verified live):
  - UE 5.8 C++ builds (VS Build Tools 2022 + .NET Framework 4.8.1 SDK installed via winget this session); module `Source/Kurearthis` compiles.
  - Driving the live editor via its Python console + GUI automation; running Simulate-In-Editor and reading results from `Saved/`.
  - Installing dependencies via winget (Jaron approves the UAC prompt the AI can't click).
  - Real tools verified: UE 5.8, Blender 5.1.2, git 2.54.0, node 24, python 3.12/3.14, VS Code, Docker CLI 29.5.3, winget 1.28.
- What is now confirmed IMPOSSIBLE / corrected (assumptions that were wrong):
  - **No Unreal Engine MCP** in the Claude environment (seed files assumed one). Use console + GUI.
  - **`gh` is NOT authenticated** (push/pull works via git Credential Manager; `gh api/pr/issue` would fail).
  - **Docker daemon not running** (CLI present only).
  - Stock Chaos physics fails at planetary absolute coordinates; a single Earth-sized static collision mesh ejects dynamic bodies even with floating origin (see KNOWN_LIMITS / PLANETARY_PROOF Proof 2).
- Source: live PowerShell inventory + this session's build/physics runs.

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
