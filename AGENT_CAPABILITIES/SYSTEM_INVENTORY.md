# SYSTEM_INVENTORY.md
Last updated: 2026-06-20
Updated by: Claude (verified live on the machine)

This file records what is ACTUALLY on the machine — not assumed, not guessed.
Update this file whenever you discover, install, or confirm anything on the system.
Do not trust this file blindly — verify live before relying on entries older than one week.

> SCOPE: Installed software, versions, paths, and the gh/docker/git state below
> are **machine-level** — they apply to any agent on this PC, Codex included.
> What differs per agent is which **MCP tools/servers are loaded in a given
> session** (see the MCP notes in LOCAL_APPS_AND_SERVICES.md / CONNECTED_TOOLS.md
> marked [CLAUDE-ENV]); Codex must check its own loaded tools, not assume Claude's.

---

## Machine
- OS: Windows 11 Home (10.0.26200), user: `lilli`
- Shell available to agents: PowerShell 7+ (pwsh) and Git Bash (POSIX sh)
- **Primary project path: `C:\Users\lilli\OneDrive\Desktop\Kurearthis`**
  (NOTE: the project lives under OneDrive Desktop, which syncs to OneDrive — and
  some file ops also surface in Google Drive. Not `Documents\Unreal Projects`.)
- CPU: 24 physical / 32 logical cores; ~38 GB RAM

## Confirmed installed (verified 2026-06-20)
| Thing | Version / path | Verified |
|---|---|---|
| Unreal Engine | **5.8** — `C:\Program Files\Epic Games\UE_5.8` | 2026-06-20 OK |
| Visual Studio **Build Tools** 2022 | MSVC 14.44 toolchain (not full VS IDE) | 2026-06-20 OK |
| .NET Framework **4.8.1 SDK** | `C:\Program Files (x86)\Windows Kits\NETFXSDK\4.8.1` (installed this session via winget; required by UE C++ build) | 2026-06-20 OK |
| Blender | **5.1.2** — `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe` (NOT on PATH) | 2026-06-20 OK |
| Git | 2.54.0 — HTTPS remote via Windows **Credential Manager** (`credential.helper=manager`) | 2026-06-20 OK |
| GitHub CLI `gh` | 2.93.0 — **authenticated** as `JaronKBragg7337` (keyring); `gh api user` works. PRs/issues/api available. | 2026-06-20 OK |
| Node.js / npm | node v24.16.0 / npm 11.13.0 | 2026-06-20 OK |
| Python | system `python` = 3.12.10; `py` launcher default 3.14 (`...\pythoncore-3.14-64`) | 2026-06-20 OK |
| VS Code | `%LOCALAPPDATA%\Programs\Microsoft VS Code` (`code` on PATH) | 2026-06-20 OK |
| Docker | CLI 29.5.3 — **daemon running** (Docker Desktop started this session; `docker info` OK) | 2026-06-20 OK |
| winget | 1.28.240 — works; can install deps (Jaron approves UAC prompts) | 2026-06-20 OK |
| Dev CLIs | uv 0.11.17, jq 1.8.2, ripgrep 15.1.0, ffmpeg 8.1.1, 7-Zip | 2026-06-21 OK |
| Art/textures | ImageMagick 7.1.2 (`magick`), Inkscape 1.4.4 (`C:\Program Files\Inkscape\bin\inkscape.exe`) | 2026-06-21 OK |
| Diagrams/docs | Graphviz 15.1.0 (`C:\Program Files\Graphviz\bin\dot.exe`), Pandoc 3.10 | 2026-06-21 OK |
| Audio | SoX 14.4.2 (`sox`), ffmpeg | 2026-06-21 OK |
| .NET + C++ tooling | .NET SDK 8.0.422 (`dotnet`), CMake 4.3.3, Ninja 1.13.2 | 2026-06-21 OK |
| Note | Inkscape & Graphviz aren't on PATH — use full paths above, or refresh PATH from registry in-session | 2026-06-21 |

## NOT present / corrected assumptions
- **No standalone .NET (Core) SDK** on PATH — `dotnet --list-sdks` empty. UE uses a
  bundled dotnet for UnrealBuildTool, so this is fine; don't assume `dotnet build`.
- **[CLAUDE-ENV] No Unreal Engine MCP loaded in this Claude session.** The live
  editor is driven by its built-in Python console + GUI automation (see
  CONNECTED_TOOLS / TESTED_WORKFLOWS). Earlier seed files assumed an Unreal MCP —
  none was present for Claude here. This is session/agent-specific: Codex should
  check its own loaded tools rather than assume the same.

## How the editor is actually controlled (verified)
- Project Python remote execution is DISABLED. Drive the editor's bottom **Console
  Command** bar: set the clipboard to `py "C:/abs/path/script.py"`, click the
  console field, paste (Ctrl+V), Enter. The script writes results to `Saved/` and
  prints to `Saved/Logs/Kurearthis.log` (`LogPython:`), which agents then read.
- Window focus / button clicks (Simulate, Stop, dialogs) are done with Win32
  (`SetForegroundWindow`/`SetCursorPos`/`mouse_event`) and the Windows-MCP tools.
  The Windows-MCP `Click`/`Type` `loc` param is buggy on this bridge (serializes
  the list to a string) — use Win32 clicks instead.

## Re-verify checklist for the next session
1. `git --version`, `gh auth status` (still unauth?), `node --version`, `python --version`
2. Blender path still `Blender 5.1`? `& "<path>" --version`
3. `docker info` — daemon running yet?
4. UE engine path still `UE_5.8`?
5. Any Unreal/Blender MCP now actually present? (Check tool list / WATCHLIST.)
