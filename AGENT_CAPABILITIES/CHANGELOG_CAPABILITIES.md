# CHANGELOG_CAPABILITIES.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file is a dated log of capability changes — new tools discovered, limits found, integrations added or removed.
This is separate from BUILDLOG (which tracks what was BUILT).
This tracks what became POSSIBLE or IMPOSSIBLE.

---

## 2026-06-21 — Capability #5: headless visual capture (Claude)
- Changed by: Claude
- Now POSSIBLE: capture a PNG of the live editor scene with NO GUI — `python _authoring/capture_view.py` (wraps `_authoring/capture_scene.py`). It renders the active viewport camera off-screen via `SceneCapture2D` → render target → PNG, so it works even when the editor window is minimized (an on-screen `HighResShot` does not). The agent reads the PNG to actually see the scene — visual evidence on every chunk instead of relying on Jaron's eyes for geometry checks.
- Verified: captured `PlanetaryProof`; the Earth-scale `ProofEarth` sphere renders against black space.
- Gotchas found: render target must be `RTF_RGBA8` (a float format exports OpenEXR under a .png name); proof maps are unlit so the script adds + removes temporary lights for the shot.
- Source: live runs 2026-06-21.

## 2026-06-21 — Capability #6: physics-settings introspection (Claude)
- Changed by: Claude
- Now POSSIBLE: dump the project's Chaos/physics settings head-less — `python _authoring/ue_remote.py --file _authoring/dump_physics_settings.py` (writes `Saved/PhysicsSettings.json`). Surfaced `max_physics_delta_time=1/30`, `max_substep_delta_time=1/60`, `max_substeps=6`, `default_terminal_velocity=4000`, `default_gravity_z=-980` for reasoning about the Proof 2d physics.
- Finding: these rule out terminal-velocity capping and a low-fps slow-motion artifact for the 2d ~100× `AddForce` deficit (Simulate ran real-time), so that anomaly stays open with data attached. The custom integrator sidesteps it.
- Limit found: `EditorPerformanceSettings` and the `b_substepping*` bools are not exposed to Python in 5.8 — read those from config ini, not the CDO.
- Source: live run 2026-06-21.

## 2026-06-21 — Capability #7: CI hardening for the C++ module (Claude)
- Changed by: Claude
- Now POSSIBLE: catch broken C++ at push time. (1) `_authoring/check_cpp_static.py` — engine-free structural checks (GENERATED_BODY present, `*.generated.h` is the last include, each `.cpp` includes its own header, brace balance, core Build.cs deps); added as a CI step so it runs free on the GitHub-hosted runner. (2) `_authoring/build_editor.py` — one-command real compile of `KurearthisEditor` wrapping the proven Build.bat flow, with a safety pre-check that refuses (exit 2) while the editor is open (it locks the module DLL).
- Why not a full CI compile: GitHub-hosted runners have no engine (UE ~150 GB) and locally the editor locks `UnrealEditor-Kurearthis.dll`, so an automatic compile-on-push is impractical/disruptive. Static check + one-command local compile is the honest hardening; a self-hosted runner calling `build_editor.py` (push-to-main only, for the public-repo security caveat) remains the future option.
- Verified: static check passes on the known-good module and its brace logic is unit-tested; `build_editor.py` correctly refused while the editor was open.
- Source: live runs 2026-06-21.

## 2026-06-21 — Capability #8: Blender→FBX→UE pipeline re-verified (Claude)
- Changed by: Claude
- Now CONFIRMED working with current tools: `python _authoring/pipeline_smoketest.py` round-trips Blender 5.1.2 → FBX (meters) → UE 5.8 import. A 2 m cube imported at box-extent (100,100,100) cm = 200 cm; temp asset auto-deleted, FBX gitignored.
- Gotcha: UE names the imported StaticMesh after the FBX file stem, not the mesh object name.
- Source: live run 2026-06-21.

## 2026-06-21 — Asset-production toolkit installed (Claude)
- Changed by: Claude (Jaron requested; approved UAC where prompted)
- Now POSSIBLE — the agent can produce real assets from scripts, not just placeholders:
  - **Art/textures:** ImageMagick 7.1.2 (`magick`) + Inkscape 1.4.4 — generate/convert textures, icons, SVG→PNG.
  - **Diagrams/docs:** Graphviz 15.1.0 (`dot`) + Pandoc 3.10 — diagrams from text, docs → PDF/DOCX. Verified by rendering `_authoring/diagrams/status.png`.
  - **Audio:** SoX 14.4.2 (+ ffmpeg) — generate/process sound from scripts.
  - **.NET + C++ tooling:** .NET SDK 8.0.422, CMake 4.3.3, Ninja 1.13.2 — build/run MCP servers and standalone tools.
  - Earlier batch: uv, jq, ripgrep, ffmpeg, 7-Zip.
- Source: live installs + version checks 2026-06-21. Inkscape/Graphviz need full paths (see SYSTEM_INVENTORY).

## 2026-06-21 — Capability upgrades #3 + #4 (Claude)
- Changed by: Claude (Jaron approved the gh `workflow` scope in the browser)
- #3 CI: `.github/workflows/ci.yml` runs on every push (GitHub-hosted) — compiles authoring Python, validates `Kurearthis.uproject`, checks C++ files present, no build artifacts tracked, docs present. Verified: first run = success in 7s. Required adding the `workflow` scope to gh's token. Full C++ compile still needs the engine (local or a self-hosted runner — documented).
- #4 Scripted physics harness: `python _authoring/run_physics_harness.py [seconds]` runs a Simulate-In-Editor physics test with NO GUI (start/stop via `LevelEditorSubsystem.editor_play_simulate()`/`editor_request_end_play()` over remote exec) and prints the result JSON. Verified end-to-end; editor returns clean.
- Source: live runs 2026-06-21.

## 2026-06-20 — Capability upgrade #1: Unreal Python remote execution (Claude)
- Changed by: Claude
- Now POSSIBLE: run editor Python from the command line over a localhost socket (`python _authoring/ue_remote.py --file/--stmt/--eval`). Enabled via `bRemoteExecution=True` in `Config/DefaultEngine.ini`; uses the engine's `remote_execution.py`. Verified: ran `live_scene_audit.py` remotely (Foundation, 8 actors) with no GUI.
- Replaces the fragile clipboard-paste-into-console + Win32-click workflow (kept as fallback). Requires the editor open and restarted after enabling.
- Source: live test 2026-06-20.

## 2026-06-20 — Fixed gh + Docker; scoped agent-specific facts (Claude)
- Changed by: Claude (Jaron approved the gh browser authorization)
- Now POSSIBLE: `gh` is authenticated (JaronKBragg7337) → PRs/issues/`gh api` work; Docker daemon is running (29.5.3). Both were "not finished setup," not real blockers.
- Clarified SCOPE across the capability files: machine-level facts (installed software, versions, gh/docker/git state, engine physics behavior) apply to any agent on this PC including Codex; items tagged **[CLAUDE-ENV]** (which MCP servers were loaded, the Windows-MCP `loc` bug, "no Unreal MCP") are Claude-session-specific — Codex must verify its own loaded tools and not treat these as universal.
- Source: live verification (`gh api user`, `docker info`).

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
