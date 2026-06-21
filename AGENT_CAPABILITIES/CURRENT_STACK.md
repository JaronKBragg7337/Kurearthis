# CURRENT_STACK.md
Last updated: 2026-06-20
Updated by: Claude (verified)

This file records the known operational stack — what is wired up, configured, and actively used.
Update whenever a tool is added, removed, or changes status.

---

## AI agents
| Agent | Role | Access method | Status |
|---|---|---|---|
| Claude Code | Primary builder — files, code, git, system automation | Local CLI pointed at project folder | Active |
| Codex (OpenAI) | Secondary builder — code and handoff work | OpenAI Codex interface | Active (env may differ; verify) |
| Perplexity AI | Research, planning, repo/folder management | Web interface | Active |

## How Unreal is actually driven (CORRECTED 2026-06-20)
There is **no Unreal Engine MCP** in the Claude environment. The live editor is
controlled by:
| Mechanism | What it does | Status |
|---|---|---|
| Editor **Python console** (`py "abs/path.py"`) | Run authoring/audit/test scripts in the live editor; results written to `Saved/` and `Saved/Logs/Kurearthis.log` | Active, proven |
| **GUI automation** (Win32 + Windows-MCP) | Focus window, click console/buttons, start/stop Simulate, dismiss dialogs | Active, proven |
| **UnrealBuildTool** (`Build.bat`) | Compile the C++ module (editor closed) | Active, proven |
| Unreal Python remote execution (network) | DISABLED in this project — not used | Off |

## System automation MCPs available to Claude Code
| MCP | Use | Notes |
|---|---|---|
| Windows-MCP | Snapshot/screenshot, Clipboard, Shortcut, App focus, PowerShell | Heavily used; `Click/Type` `loc` is buggy — use Win32 |
| Desktop Commander | Files, processes, search, long-running procs | Available |
| computer-use / Claude-in-Chrome | Desktop/browser control | Available if needed |
(Many cloud connectors are also listed but are irrelevant to game dev.)

## Tooling
- Blender 5.1.2 (headless CLI authoring) — NOT on PATH, full path required
- Git 2.54.0 — push/pull work via Windows Credential Manager (HTTPS)
- `gh` 2.93.0 — installed but **NOT authenticated**; use plain `git` for push/pull.
  `gh`-specific commands (PRs/issues) need `gh auth login` or GH_TOKEN first.
- C++ build: VS Build Tools 2022 (MSVC 14.44) + .NET Framework 4.8.1 SDK

## Version control
- Platform: GitHub · Repo: https://github.com/JaronKBragg7337/Kurearthis · Branch: main · Public
- Rule: never commit secrets/personal data. Remote pushes happen via `git push` (credential manager).

## Key folder structure (verified)
```
Kurearthis/
├── CHARTER.md              ← Vision and laws (read every session)
├── AUTHORIZATION.md        ← Standing build/install permissions
├── WORKFLOW.md             ← Operating rules
├── BUILDLOG.md             ← Current state and next steps
├── PLANETARY_PROOF.md      ← Recorded proofs (scale, gravity, physics findings)
├── ASSETS_MANIFEST.md      ← Every asset origin logged here
├── AGENT_CAPABILITIES/     ← This folder — read when blocked or uncertain
├── _authoring/             ← Authoring/test scripts (Blender + Unreal Python) + ignored FBX
├── Content/                ← Unreal content (PlanetaryProof.umap, Foundation.umap, Planetary/)
├── Source/Kurearthis/      ← Unreal C++ module (RadialGravityTestBody, FloatingOriginManager)
├── Config/                 ← Unreal config
├── Binaries/ Intermediate/ Saved/ DerivedDataCache/  ← all gitignored
```
