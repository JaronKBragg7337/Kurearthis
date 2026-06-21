# WATCHLIST.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file tracks new tools, MCPs, model updates, TOS changes, and experiments to revisit.
Anything that could change what's possible belongs here.
Perplexity AI or Jaron updates this; Claude and Codex act on it.

---

## Recently confirmed new capabilities
| Capability | Status | Notes | Date confirmed |
|---|---|---|---|
| Unreal Engine MCP | Now available | Was not available in prior project — enables live editor control from Claude Code | 2026-06-20 |
| Claude Code MCP Tool Search | Released | Claude can now load tools on demand instead of all at once — reduces token usage | 2026-01 |

---

## To verify / investigate
| Item | Why it matters | Priority |
|---|---|---|
| Blender MCP | If a Blender MCP now exists, the headless CLI pipeline could be replaced or augmented with direct MCP control | High |
| Docker MCP | Docker is installed — check if an MCP exists for containerized workflows | Medium |
| Codex tool access | What local tools and MCPs does Codex have access to in its current environment? | High |
| TOS for Claude Code re: local file access | Confirm no new restrictions on local filesystem operations | Medium |
| Anthropic MCP roadmap updates | MCP is evolving fast — check for new connectors, auth changes, skill/tool patterns | Ongoing |
| OpenAI Codex capability updates | Codex capabilities change — verify current tool access and limits | Ongoing |

---

## Rule
When Perplexity or Jaron finds something new and relevant, add it here.
When Claude or Codex starts a session, this file is NOT read by default — it is consulted from `AGENT_CAPABILITIES/` only when needed.
But any agent doing research or hitting a limit SHOULD check WATCHLIST.md before concluding something is impossible.
