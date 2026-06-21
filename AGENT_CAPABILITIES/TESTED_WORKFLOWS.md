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
- **Gotchas:** remote exec is off; editor must be open; use `hit.to_dict()` for HitResults.

## Live scene verification
- **Status:** PROVEN 2026-06-20
- **Flow:** run `_authoring/live_scene_audit.py` → compare actor list/transforms with BUILDLOG → proceed or flag STATE DIVERGENCE.
- **Verified by:** matched `PlanetaryProof` (ProofEarth @origin) to the log; re-verified clean after each Simulate.

## C++ module build + reload
- **Status:** PROVEN 2026-06-20
- **Flow:** edit `Source/Kurearthis/*` → close editor → `Build.bat KurearthisEditor Win64 Development -Project=...` → reopen editor → new `unreal.<Class>` is available to Python.
- **Verified by:** built `RadialGravityTestBody` and `FloatingOriginManager`, spawned them from Python.
- **Gotchas:** needs .NET 4.8.1 SDK; Target.cs `BuildSettingsVersion.V7`; don't leave an uncompilable module in `.uproject` (bricks the editor with "Missing target file").

## Run real physics via Simulate-In-Editor + read result
- **Status:** PROVEN 2026-06-20
- **Flow:** spawn physics actor + save level → play-mode menu → **Simulate** (GUI click) → wait → read `Saved/RadialGravityProof.*` → **Stop** (red button, Win32 click) → re-audit scene.
- **Verified by:** the Chaos gravity runs (Proof 2b/2c).
- **Gotchas:** `get_editor_world()` returns `<none>` while Simulate is active — stop first, then audit.

## Install a dependency via winget
- **Status:** PROVEN 2026-06-20 (.NET Framework 4.8.1 SDK)
- **Flow:** `winget install --id <Id> --silent --accept-package-agreements --accept-source-agreements` → tell Jaron a UAC prompt may appear → Jaron approves → verify registry/files.

## Commit / push loop
- **Status:** PROVEN — commits live at the repo
- **Flow:** edit → `git add` → `git commit` (Co-Authored-By trailer) → `git fetch` + `git rebase origin/main` → `git push`. Plain git (gh not authed).
- **Gotchas:** revert auto-generated `Config/DefaultEngine.ini` (AndroidFileServer block) before committing.

## Blender → Unreal FBX pipeline
- **Status:** Proven in prior project — NOT re-verified this session (Blender is now 5.1.2; check API)
- **Flow:** `blender --background --python _authoring/make_*.py` → FBX (meters) → import via Unreal Python `AssetImportTask`.

## Claude + Codex cross-agent handoff
- **Status:** Proven — share state ONLY through committed files; read BUILDLOG "Next" on startup.
