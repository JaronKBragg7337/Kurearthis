# CONNECTED_TOOLS.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file records tools that have been actively connected and tested in this project.
For each tool: what it can do, what it cannot do, requirements, risks, and the best way to use it.

---

## Unreal Engine MCP
- **Status:** Active
- **Last verified:** 2026-06-20
- **What it can do:**
  - Enumerate scene actors (used to verify live state vs log)
  - Import static mesh FBX files via `StaticMeshTools.import_file`
  - Compile Blueprints
  - Interact with the editor programmatically
- **What it cannot do / known issues:**
  - Unreliable during or immediately after destructive operations (delete all, large asset swaps)
  - Requires Unreal editor to be OPEN and MCP server running — does not work headless
  - A crashed session can leave ghost actors; always verify live scene before trusting logs
- **Requirements:** Unreal editor open, MCP server process running on configured port
- **Risks:** Ghost actors, stale state, crash during large imports
- **Best pattern:** Enumerate actors first → compare with log → then proceed with work

---

## Blender (headless CLI)
- **Status:** Active — proven in prior project
- **Last verified:** 2026-06-20
- **What it can do:**
  - Run Python scripts headlessly: `blender --background --python _authoring/make_*.py`
  - Generate and export FBX geometry without opening the GUI
  - Model in meters (Unreal imports at cm scale)
- **What it cannot do:** GUI-dependent operations, rendering final frames headlessly without config
- **Requirements:** Blender installed, script in `_authoring/` folder
- **Risks:** Blender version mismatches can break Python API calls — always test after Blender updates
- **Best pattern:** Write script → test locally → export FBX → import via Unreal MCP

---

## GitHub CLI (gh)
- **Status:** Active
- **Last verified:** 2026-06-20
- **What it can do:** Create repos, push commits, manage PRs and issues
- **Requirements:** `gh` authenticated on the machine
- **Best pattern:** Use for all repo operations — Jaron does not use GitHub UI manually

---

## Docker
- **Status:** Installed — NOT yet integrated into this project
- **Last verified:** Unverified
- **Potential uses:** Run local services, isolated build environments, local API servers
- **Next step:** Verify `docker --version`, identify if any workflow would benefit from containerization
