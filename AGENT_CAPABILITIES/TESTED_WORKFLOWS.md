# TESTED_WORKFLOWS.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file records workflows that have been tested end to end and confirmed working.
Do not mark a workflow as proven unless Jaron or a verifiable output confirmed it.

---

## Blender → Unreal FBX pipeline
- **Status:** Proven (prior project)
- **Flow:** `blender --background --python _authoring/make_*.py` → exports FBX → `StaticMeshTools.import_file` in Unreal via MCP
- **Model in:** METERS (Unreal auto-converts to cm on import)
- **Export format:** FBX only — not glb
- **Verified by:** Prior project sessions — multiple assets imported successfully
- **Gotchas:** Blender Python API version must match installed Blender version

---

## Claude Code + GitHub CLI commit/push loop
- **Status:** Proven
- **Flow:** Claude Code makes file changes → `git add` → `git commit -m "..." --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"` → `git push`
- **Verified by:** Live repo — commits appearing at https://github.com/JaronKBragg7337/Kurearthis
- **Gotchas:** Always commit before risky changes to create rollback point

---

## Unreal MCP live scene verification
- **Status:** Proven (current project)
- **Flow:** Enumerate actors via MCP → compare with BUILDLOG current state → proceed or flag STATE DIVERGENCE
- **Verified by:** Caught ghost actors in prior project that caused undiagnosable bugs
- **Gotchas:** Must have Unreal editor open; MCP server must be running

---

## Claude + Codex cross-agent handoff
- **Status:** Proven in prior project (Kurearthis predecessor)
- **Flow:** One agent builds chunk → logs to BUILDLOG → commits → pushes → other agent reads BUILDLOG "Next" on startup
- **Verified by:** Jaron confirmed loop ran end to end
- **Gotchas:** Agents must ONLY share state through committed files — no assumed context from prior chats
