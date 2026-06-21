# SYSTEM_INVENTORY.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file records what is ACTUALLY on the machine — not assumed, not guessed.
Update this file whenever you discover, install, or confirm anything on the system.
Do not trust this file blindly — verify live before relying on entries older than one week.

---

## Machine
- OS: Windows (user: lilli)
- Primary project path: C:\Users\lilli\Documents\Unreal Projects\Kurearthis

## Confirmed installed applications
| App | Version / Notes | Last verified |
|---|---|---|
| Unreal Engine | UE5 (project exists and runs) | 2026-06-20 |
| Blender | Installed, used in prior project for headless FBX export | 2026-06-20 |
| Epic Games Launcher | Present (used to launch UE) | 2026-06-20 |
| Docker | Installed — potential for containerized services | Unverified |
| Git | Present (repo is live and pushing) | 2026-06-20 |
| GitHub CLI (gh) | Used to create repos — confirmed working | 2026-06-20 |

## Confirmed CLIs / tools
| Tool | Notes | Last verified |
|---|---|---|
| `blender --background` | Headless Blender scripting proven in prior project | 2026-06-20 |
| `gh` | GitHub CLI — used for repo management | 2026-06-20 |
| `git` | Standard git operations | 2026-06-20 |

## Unverified / suspected installed
- Docker Desktop — installed but not yet used in this project
- Python — likely present (Blender embeds it; check system Python separately)
- Node.js — unknown
- VS Code — unknown
- Visual Studio — likely (UE5 C++ projects need it)

## Instructions for first session after this file is created
Run the following checks and update this file with results:
1. `blender --version` — confirm Blender version
2. `gh --version` — confirm GitHub CLI version
3. `docker --version` — confirm Docker presence
4. `python --version` or `python3 --version` — confirm Python
5. Confirm Unreal MCP server is installed and on what port
6. List any MCP servers currently configured in Claude Code settings
