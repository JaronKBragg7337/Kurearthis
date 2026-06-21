# CURRENT_STACK.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file records the known operational stack — what is wired up, configured, and actively used.
Update whenever a tool is added, removed, or changes status.

---

## AI agents
| Agent | Role | Access method | Status |
|---|---|---|---|
| Claude Code | Primary builder — files, code, git, MCP tools | Local CLI pointed at project folder | Active |
| Codex (OpenAI) | Secondary builder — code and handoff work | OpenAI Codex interface | Active |
| Perplexity AI | Research, planning, external knowledge, repo management | Web interface | Active |

## Core MCP connections
| MCP | What it connects | Status | Notes |
|---|---|---|---|
| Unreal Engine MCP | Live Unreal editor — actor enumeration, import, compile | Active | Must have Unreal editor open and MCP server running |
| GitHub MCP (via gh) | Repo create, push, commit | Active | Confirmed working |
| Blender (headless) | Not MCP — CLI scripting via `blender --background --python` | Active | FBX export pipeline proven |

## Version control
- Platform: GitHub
- Repo: https://github.com/JaronKBragg7337/Kurearthis
- Branch: main
- Visibility: Public
- Rule: Never commit secrets or personal data

## Key folder structure
```
Kurearthis/
├── CHARTER.md              ← Vision and laws (read every session)
├── WORKFLOW.md             ← Operating rules (read every session)
├── BUILDLOG.md             ← Current state and next steps (read every session)
├── AUTHORIZATION.md        ← Standing permissions
├── ASSETS_MANIFEST.md      ← Every asset origin logged here
├── AGENT_CAPABILITIES/     ← This folder — read when blocked or uncertain
├── _authoring/             ← Blender scripts and authoring tools
├── Content/                ← Unreal content
├── Source/                 ← Unreal C++ source
└── Config/                 ← Unreal config files
```
