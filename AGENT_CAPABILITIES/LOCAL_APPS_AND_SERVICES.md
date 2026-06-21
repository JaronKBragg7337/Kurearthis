# LOCAL_APPS_AND_SERVICES.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file tracks local apps and services that exist on this machine and could be useful to the workflow,
including ones not yet integrated. Check here before assuming a capability is impossible.

---

## Apps with confirmed workflow use
| App | How it's used | Notes |
|---|---|---|
| Unreal Engine 5 | Game editor, live scene, MCP target | Must be open for MCP |
| Blender | Headless geometry authoring, FBX export | CLI only in workflow |
| GitHub Desktop / gh CLI | Version control | Use CLI, not GUI |

## Apps installed but not yet fully used in workflow
| App | Potential use | Status |
|---|---|---|
| Docker | Containerized local services, build tools, local API servers | Installed, unverified |
| Visual Studio | Required by UE5 C++ — may already be used silently | Likely installed |
| Python (system) | Scripting, automation, tooling | Likely present via Blender embed |
| Browser | Could be used for local web dashboards, MCP servers with web UI | Available |

## MCP servers — known or discoverable
| MCP server | Status | Notes |
|---|---|---|
| Unreal Engine MCP | Active | New as of ~June 2026 |
| Claude Code filesystem MCP | Built-in | Always available in Claude Code sessions |
| GitHub MCP | Active via gh | Confirmed working |
| Blender MCP | Unknown | Check if a Blender MCP now exists — was not available in prior project |
| Docker MCP | Unknown | May now exist — check if workflow would benefit |
| Browser automation MCP | Unknown | Could help with web-based tasks |

## Rule
Before concluding a task is impossible, check:
1. Is there an app already installed that could help?
2. Is there an MCP server now available for that app?
3. Is there a CLI tool already present that could be scripted?
If yes to any of these, document it here and use it.
