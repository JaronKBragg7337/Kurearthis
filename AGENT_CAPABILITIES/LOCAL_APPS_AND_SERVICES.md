# LOCAL_APPS_AND_SERVICES.md
Last updated: 2026-06-21
Updated by: Codex (verified)

This file tracks local apps and services that exist on this machine and could be useful to the workflow,
including ones not yet integrated. Check here before assuming a capability is impossible.

---

## Apps with confirmed workflow use (verified 2026-06-20)
| App | How it's used | Notes |
|---|---|---|
| Unreal Engine 5.8 | Game editor / live scene; driven via Python console + GUI automation | Must be open for editor scripting; closed for C++ builds |
| VS Build Tools 2022 + .NET 4.8.1 SDK | Compile the UE C++ module | Proven this session |
| Git | Version control (HTTPS via Credential Manager) | Plain `git` push/pull works; independent of `gh` auth |
| winget | Install dependencies | Jaron approves UAC |
| Blender 5.1.2 | Headless geometry authoring, FBX export | CLI only; full path needed |
| Tesseract + Poppler + qpdf + Ghostscript + ExifTool | OCR, PDF extraction/render/validation, metadata inspection | Proven by `_authoring/document_stack_smoketest.py` |

## Installed but not in active workflow
| App | Potential use | Status (verified 2026-06-20) |
|---|---|---|
| Docker 29.5.3 | Containerized local services/build envs | Installed; **daemon running** (started this session) |
| VS Code | Editing, extensions, integrated tooling | Installed (`code` on PATH) |
| Node.js v24 / npm 11 | JS tooling, MCP servers, scripts | Installed |
| Python 3.12 / 3.14 | Scripting/automation outside Blender | Installed |
| GitHub CLI `gh` 2.93.0 | PRs/issues/api | Installed, currently **not authenticated**; run `gh auth login` when needed |
| Scoop | Per-user CLI/app installation without UAC for available packages | Active; main/extras/versions/java buckets |
| Go, Rust, Java 21, Git LFS | Cross-project builds and large-file support | Installed and on PATH |

## MCP servers — loaded in THIS Claude session (2026-06-20) — [CLAUDE-ENV]
> This table is agent/session-specific: it lists what the *Claude* session had
> loaded. Codex has its own tool set — it must check its own, not assume this.
| MCP | Status | Notes |
|---|---|---|
| Windows-MCP | Available, used | Desktop screenshot/snapshot, clipboard, shortcuts, PowerShell, app focus |
| Desktop Commander | Available | Files, processes, search, long-running procs |
| computer-use / Claude-in-Chrome / Claude_Preview | Available | Desktop & browser control if needed |
| **Unreal Engine MCP** | **Not loaded for Claude** | Seed files assumed one exists — it was not loaded in this Claude session. Editor driven via console + GUI. Codex: check your own tools. |
| **Blender MCP** | Not present | Use the headless CLI |
| **Docker MCP** | Not relevant | Daemon isn't even running |
| Cloud connectors (Supabase, Vercel, Cloudflare, Gmail, Calendar, etc.) | Available but off-topic | Not used for game dev |

## Rule
Before concluding a task is impossible:
1. Is there an installed app/CLI that does it? (Check SYSTEM_INVENTORY.)
2. Is there an MCP/tool actually loaded? (Use ToolSearch — don't assume from these notes.)
3. Can a dependency be installed via winget? (Allowed; Jaron approves UAC.)
Record anything newly discovered here and in CHANGELOG_CAPABILITIES.md.
