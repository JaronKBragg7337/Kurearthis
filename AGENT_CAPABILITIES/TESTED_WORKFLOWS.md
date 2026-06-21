# TESTED_WORKFLOWS.md
Last updated: 2026-06-20
Updated by: Claude (verified)

This file records workflows that have been tested end to end and confirmed working.
Do not mark a workflow as proven unless Jaron or a verifiable output confirmed it.

---

## Drive the live Unreal editor via the Python console
- **Status:** PROVEN 2026-06-20 (current project)
- **Flow:** clipboard `py "C:/abs/path/script.py"` → click console field (Win32) → Ctrl+V → Enter. Script writes JSON to `Saved/` and prints `LogPython:` lines to `Saved/Logs/Kurearthis.log`; agent reads those.
- **Verified by:** live scene audits, collision setup, line traces, actor spawns this session.
- **Gotchas:** this clipboard method is now the FALLBACK — remote exec is ON (see the harness/capture entries; prefer `ue_remote.py`). Editor must be open; use `hit.to_dict()` for HitResults.

## Live scene verification
- **Status:** PROVEN 2026-06-20
- **Flow:** run `_authoring/live_scene_audit.py` → compare actor list/transforms with BUILDLOG → proceed or flag STATE DIVERGENCE.
- **Verified by:** matched `PlanetaryProof` (ProofEarth @origin) to the log; re-verified clean after each Simulate.

## C++ module build + reload
- **Status:** PROVEN 2026-06-20
- **Flow:** edit `Source/Kurearthis/*` → close editor → `Build.bat KurearthisEditor Win64 Development -Project=...` → reopen editor → new `unreal.<Class>` is available to Python.
- **Verified by:** built `RadialGravityTestBody` and `FloatingOriginManager`, spawned them from Python.
- **Gotchas:** needs .NET 4.8.1 SDK; Target.cs `BuildSettingsVersion.V7`; don't leave an uncompilable module in `.uproject` (bricks the editor with "Missing target file").

## Scripted physics harness (NO GUI) — primary
- **Status:** PROVEN 2026-06-20
- **Flow:** `python _authoring/run_physics_harness.py [seconds]` — it sets up the
  scene, starts Simulate via `LevelEditorSubsystem.editor_play_simulate()`, waits,
  stops via `editor_request_end_play()`, and prints `Saved/RadialGravityProof.json`.
  All over remote execution; no Simulate/Stop button clicks.
- **Verified by:** ran the gravity test scripted; editor returned to a clean 4-actor
  scene (`is_in_play_in_editor()=False`).
- **Gotchas:** `get_editor_world()` returns `<none>` while Simulate is active — stop first, then audit. Run physics math in doubles (see KNOWN_LIMITS).
- **Old GUI method** (play-mode menu → Simulate, Win32-click Stop) is the fallback only if remote exec is unavailable.

## Headless visual capture (off-screen render) — NEW
- **Status:** PROVEN 2026-06-21
- **Flow:** `python _authoring/capture_view.py` → prints `CAPTURE_OK <abs_path>` of a PNG; the agent reads that PNG to see the live scene. Internally `_authoring/capture_scene.py` renders the active viewport camera through a `SceneCapture2D` → `TextureRenderTarget2D` (RTF_RGBA8) → `export_render_target` PNG.
- **Verified by:** captured `PlanetaryProof` — the Earth-scale `ProofEarth` sphere renders correctly against black space (`Saved/Screenshots/view_*.png`).
- **Gotchas:** (1) On-screen `HighResShot` does NOT render when the editor window is minimized/occluded — use this off-screen path instead. (2) Use `TextureRenderTargetFormat.RTF_RGBA8`, else `export_render_target` writes OpenEXR bytes under a `.png` name. (3) The proof maps have no lights, so the script spawns a temporary DirectionalLight + SkyLight just for the shot and removes them (the saved scene is untouched). (4) Output lands in `Saved/Screenshots/` (gitignored).

## Install a dependency via winget
- **Status:** PROVEN 2026-06-20 (.NET Framework 4.8.1 SDK)
- **Flow:** `winget install --id <Id> --silent --accept-package-agreements --accept-source-agreements` → tell Jaron a UAC prompt may appear → Jaron approves → verify registry/files.

## Commit / push loop
- **Status:** PROVEN — commits live at the repo
- **Flow:** edit → `git add` → `git commit` (Co-Authored-By trailer) → `git fetch` + `git rebase origin/main` → `git push`. Push/pull use plain git; `gh` is authed too (PRs/issues/api available).
- **Gotchas:** revert auto-generated `Config/DefaultEngine.ini` (AndroidFileServer block) before committing.

## Blender → Unreal FBX pipeline
- **Status:** Proven in prior project — NOT re-verified this session (Blender is now 5.1.2; check API)
- **Flow:** `blender --background --python _authoring/make_*.py` → FBX (meters) → import via Unreal Python `AssetImportTask`.

## Claude + Codex cross-agent handoff
- **Status:** Proven — share state ONLY through committed files; read BUILDLOG "Next" on startup.
