# SESSION_WARMUP.md
Last updated: 2026-06-20
Updated by: Claude

A capability being **down is not the same as it being unavailable.** Most things
(daemons, auth, the editor, MCP connections) just lapse between sessions and need
one command to bring back. Run the relevant check below before concluding
anything is impossible, and refresh it instead of working around it.

This is a PREFLIGHT, not session-startup reading — consult it when you're about
to use a capability, or when something that "should" work doesn't.

---

## Preflight checks + one-line refresh (verify only what you need)
| Capability | Check | If down, refresh |
|---|---|---|
| Unreal editor open | `Get-Process UnrealEditor` | `Start-Process "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "<root>\Kurearthis.uproject"` (wait ~1–3 min) |
| C++ module fresh after source edits | did `Source/Kurearthis/*` change? | close editor → `Build.bat KurearthisEditor Win64 Development -Project=...` → reopen |
| git push/pull | `git fetch` | credential manager handles it; if it prompts, Jaron signs in |
| `gh` (PRs/issues/api) | `gh auth status` | `gh auth login` (web device code → Jaron authorizes in browser) |
| Docker (only if a workflow needs it) | `docker info` | `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`; wait ~60–90 s |
| A dependency is missing | the tool errors "not found" | `winget install --id <Id> --silent ...` → Jaron approves UAC (see AUTHORIZATION.md) |
| An MCP/tool seems absent | use ToolSearch with a keyword | it may be deferred/connecting, not missing — load it before assuming |

## Principles
1. **Refresh before re-architecting.** A 1-line restart beats a workaround that
   adds permanent debt.
2. **Verify live, don't trust memory** — including this file. Re-run the check.
3. **If a refresh command fixes it, record nothing new; if the *fix* was
   non-obvious, add it here** so the next agent skips the discovery cost.
4. The AI cannot click UAC/browser prompts — when a refresh needs one, ask Jaron
   in plain text to approve, then continue.
