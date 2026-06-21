# CONNECTED_TOOLS.md
Last updated: 2026-06-20
Updated by: Claude (verified)

This file records tools that have been actively connected and tested in this project.
For each tool: what it can do, what it cannot do, requirements, risks, and the best way to use it.

---

## Unreal editor control — Python console + GUI automation (NOT an MCP)
- **Scope:** [CLAUDE-ENV] — this is how the *Claude* session drives the editor (no
  Unreal MCP was loaded). Codex should use whatever editor tooling its own session
  has; verify before assuming.
- **Status:** Active, proven 2026-06-20
- **What it can do:**
  - Enumerate live scene actors (verify state vs log) and read transforms
  - Import static meshes (`AssetImportTask`), create/save levels, spawn/configure actors
  - Set collision (`body_setup.collision_trace_flag`), run line traces, set viewport camera
  - Start/stop **Simulate-In-Editor** to run real Chaos physics; read results from `Saved/`
- **What it cannot do / gotchas:**
  - No network Python remote execution (disabled) — must paste into the console bar
  - Editor must be OPEN; a new/changed C++ module needs the editor CLOSED to build, then reopened
  - `FHitResult` fields aren't direct attrs / `get_editor_property("blocking_hit")` fails — use `hit.to_dict()`
  - `unreal.SystemLibrary.line_trace_single` returns `None` on no-hit (not an empty struct)
  - `StaticMeshComponent` has no `recreate_physics_state()` in Python
- **Best pattern:** write a `.py` to `_authoring/`, run via console, have it dump JSON to `Saved/`, read it back. Always audit live actors first (catches ghost actors).

## C++ build (UnrealBuildTool)
- **Status:** Active, proven 2026-06-20 (requires .NET Framework 4.8.1 SDK — installed)
- **Build:** `& "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" KurearthisEditor Win64 Development -Project="<root>\Kurearthis.uproject" -WaitMutex -FromMsBuild`
- **Gotchas:** editor must be closed; Target.cs must use `BuildSettingsVersion.V7`; a UBA firewall prompt may appear (Cancel it). Module: `Source/Kurearthis`.

## Blender (headless CLI)
- **Status:** Installed (Blender **5.1.2**), pipeline proven in prior project — NOT re-verified this session
- **Run:** `& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python _authoring/make_*.py`
- **Gotchas:** Blender **5.1** is a major version — the prior project's scripts may need Python-API checks against 5.x. Export **FBX** (not glb), model in METERS.

## Git (push/pull)
- **Status:** Active — `git push`/`pull` work via Windows Credential Manager (HTTPS)
- **Best pattern:** plain `git add/commit/push`. Attribution trailers per WORKFLOW. Rebase onto `origin/main` before pushing (other agents push too).

## GitHub CLI (gh)
- **Status:** Installed (2.93.0) and **authenticated** as `JaronKBragg7337` (keyring, verified `gh api user` 2026-06-20). [MACHINE]
- **What it can do:** create/manage PRs, issues, `gh api`, releases. Repo push/pull still goes through plain `git` (credential manager).
- **Note:** auth is stored on the machine, so it applies to any agent on this PC (verify with `gh auth status`).

## winget (dependency installs)
- **Status:** Active — used to install the .NET Framework 4.8.1 SDK this session
- **Pattern:** `winget install --id <Id> --silent --accept-package-agreements --accept-source-agreements`. May trigger a UAC prompt — **Jaron approves it** (the AI can't click it). See `AUTHORIZATION.md`.

## Docker
- **Status:** CLI 29.5.3; **daemon running** (Docker Desktop started 2026-06-20; `docker info` OK). [MACHINE]
- **Note:** if `docker info` ever fails again, the Desktop app just needs to be (re)started: `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"` and wait ~60–90 s. Not yet part of any game-dev workflow.
