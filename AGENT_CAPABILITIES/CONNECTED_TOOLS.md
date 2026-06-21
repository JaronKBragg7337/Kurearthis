# CONNECTED_TOOLS.md
Last updated: 2026-06-21
Updated by: Codex (verified)

This file records tools that have been actively connected and tested in this project.
For each tool: what it can do, what it cannot do, requirements, risks, and the best way to use it.

---

## Unreal editor control — Python REMOTE EXECUTION (primary, 2026-06-20)
- **Status:** Active, proven 2026-06-20. `bRemoteExecution=True` in DefaultEngine.ini.
- **How:** run editor Python from the command line over a localhost socket — NO GUI:
  - `python _authoring/ue_remote.py --stmt "import unreal; ..."`
  - `python _authoring/ue_remote.py --file _authoring/<script>.py`
  - `python _authoring/ue_remote.py --eval "<expr>"`
  Output (prints/errors) comes back to stdout/stderr; scripts also write to `Saved/`.
- **Requires:** editor open AND restarted since remote exec was enabled. Localhost only (TTL 0).
- **This replaces** the old clipboard-paste-into-console + Win32-click method (kept below as fallback only if the socket is unavailable).

## Fallback: console paste + GUI automation — [CLAUDE-ENV]
- Use ONLY if remote execution is unavailable. How the Claude session drove the editor before remote exec: clipboard `py "abs/path"` → Win32 click console → Ctrl+V → Enter; Win32 clicks for Simulate/Stop/dialogs.
- **Status:** Active fallback, proven 2026-06-20
- **What it can do:**
  - Enumerate live scene actors (verify state vs log) and read transforms
  - Import static meshes (`AssetImportTask`), create/save levels, spawn/configure actors
  - Set collision (`body_setup.collision_trace_flag`), run line traces, set viewport camera
  - Start/stop **Simulate-In-Editor** to run real Chaos physics; read results from `Saved/`
- **What it cannot do / gotchas:**
  - This fallback is slower and UI-dependent; prefer remote execution whenever its socket is available
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

## OCR / PDF / metadata inspection — machine-level
- **Status:** Active, proven 2026-06-21 from Codex.
- **Tools:** Tesseract + 163 language models, Poppler (`pdfinfo`, `pdftotext`,
  `pdftoppm`, etc.), qpdf, Ghostscript, and ExifTool.
- **Verify:** `python _authoring/document_stack_smoketest.py` performs an exact
  image OCR → PDF → validation/render → OCR round trip and metadata check.
- **Gotcha:** after first install in an already-running agent app, refresh
  `TESSDATA_PREFIX` from the user environment or restart the app. The smoke test
  automatically falls back to Scoop's language-data path.
