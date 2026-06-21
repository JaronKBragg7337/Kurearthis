# MCP_OPTIONS.md
Last updated: 2026-06-20
Updated by: Claude

Assessment of optional MCP servers for this project, and how to enable one when wanted.

> KEY POINT: a new MCP server only loads when the **Claude Code app restarts** — it
> cannot be installed and verified inside the same session. So "enable an MCP" =
> install + configure now, then restart Claude Code and verify next session.

---

## Unreal Engine MCP — investigated 2026-06-20
Several community MCP servers exist that let an AI drive UE through structured tool
calls (spawn actors, edit Blueprints, headless build/test, etc.):
| Project | Notes |
|---|---|
| `remiphilippe/mcp-unreal` | Go binary, "full control… headless builds & tests, Blueprint editing"; targets **UE 5.7**; mentions Claude Code |
| `ChiR24/Unreal_mcp` | Plugin hosts an HTTP MCP server directly — no Node bridge |
| `GenOrca/unreal-mcp`, `chongdashu/unreal-mcp`, `avdo403/UnrealMCP`, `Natfii/UnrealClaude` | Various; mostly UE **5.5–5.7**, aimed at Claude Desktop / Cursor |

**Recommendation: not adopting one right now.** Reasons:
1. **Redundant with remote execution (#1)** — `_authoring/ue_remote.py` already runs
   arbitrary editor Python over a localhost socket, with no extra dependency.
2. Each needs a **companion UE plugin compiled into the project**, and they target
   5.5–5.7, not our **5.8** — version/build risk and a new dependency to maintain.
3. Can't be verified this session (needs a Claude Code restart).

Revisit if a server cleanly supports 5.8 and offers something remote-exec can't
(e.g. a curated, safer tool surface). Until then, build structured helpers in
Python on top of remote exec instead (see the test harness work).

### To enable one later (general steps)
1. Clone/install the server; install its `.uplugin` into the project and let UE compile it (editor closed → build → reopen).
2. Add it to Claude Code MCP config (project `.mcp.json` or user settings), e.g.:
   ```json
   { "mcpServers": { "unreal": { "command": "<server-binary-or-npx>", "args": ["..."] } } }
   ```
3. Restart Claude Code; verify the `mcp__unreal__*` tools appear and respond.
4. Record the result + version in CONNECTED_TOOLS.md and CHANGELOG_CAPABILITIES.md.

## Blender MCP — investigated 2026-06-20
`ahujasid/blender-mcp` (popular) drives Blender live via an addon + socket — great
for **interactive** modeling by an AI. Our pipeline is **headless CLI** FBX export,
which already works, so a Blender MCP is optional. Consider it only if we want the
AI to model interactively rather than via committed scripts.

## Bottom line
The capability these MCPs provide (programmatic engine control) is already covered
by remote execution. Treat MCPs as a *nicer interface* to revisit, not a gap.
