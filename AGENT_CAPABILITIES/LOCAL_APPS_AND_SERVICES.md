# LOCAL_APPS_AND_SERVICES.md
Last updated: 2026-06-20
Updated by: Claude (verified)

This file tracks local apps and services that exist on this machine and could be useful to the workflow,
including ones not yet integrated. Check here before assuming a capability is impossible.

---

## Apps with confirmed workflow use (verified 2026-06-20)
| App | How it's used | Notes |
|---|---|---|
| Unreal Engine 5.8 | Game editor / live scene; driven via Python console + GUI automation | Must be open for editor scripting; closed for C++ builds |
| VS Build Tools 2022 + .NET 4.8.1 SDK | Compile the UE C++ module | Proven this session |
| Git | Version control (HTTPS via Credential Manager) | Use plain `git` (gh not authed) |
| winget | Install dependencies | Jaron approves UAC |
| Blender 5.1.2 | Headless geometry authoring, FBX export | CLI only; full path needed |

## Installed but not in active workflow
| App | Potential use | Status (verified 2026-06-20) |
|---|---|---|
| Docker 29.5.3 | Containerized local services/build envs | Installed; **daemon NOT running** |
| VS Code | Editing, extensions, integrated tooling | Installed (`code` on PATH) |
| Node.js v24 / npm 11 | JS tooling, MCP servers, scripts | Installed |
| Python 3.12 / 3.14 | Scripting/automation outside Blender | Installed |
| GitHub CLI `gh` 2.93.0 | PRs/issues/api | Installed but **NOT authenticated** |

## MCP servers — what's REALLY available to Claude Code (2026-06-20)
| MCP | Status | Notes |
|---|---|---|
| Windows-MCP | Available, used | Desktop screenshot/snapshot, clipboard, shortcuts, PowerShell, app focus |
| Desktop Commander | Available | Files, processes, search, long-running procs |
| computer-use / Claude-in-Chrome / Claude_Preview | Available | Desktop & browser control if needed |
| **Unreal Engine MCP** | **NOT present in Claude env** | Seed files assumed one exists — it does not here. Editor is driven via console + GUI. Re-check if one is added later. |
| **Blender MCP** | Not present | Use the headless CLI |
| **Docker MCP** | Not relevant | Daemon isn't even running |
| Cloud connectors (Supabase, Vercel, Cloudflare, Gmail, Calendar, etc.) | Available but off-topic | Not used for game dev |

## Rule
Before concluding a task is impossible:
1. Is there an installed app/CLI that does it? (Check SYSTEM_INVENTORY.)
2. Is there an MCP/tool actually loaded? (Use ToolSearch — don't assume from these notes.)
3. Can a dependency be installed via winget? (Allowed; Jaron approves UAC.)
Record anything newly discovered here and in CHANGELOG_CAPABILITIES.md.
