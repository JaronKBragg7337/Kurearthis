# KNOWN_LIMITS.md
Last updated: 2026-06-20
Updated by: Perplexity AI (initial seed)

This file records things that were assumed possible but proved false, flaky, unreliable, or blocked.
If you hit a hard limit, document it here so the next session does not repeat the same dead end.

---

## Ghost actors after crashes
- **What happened:** A crashed build session left an invisible object in the Unreal scene. Later sessions trusted the log instead of verifying the live scene and could not diagnose the resulting bugs.
- **Rule added:** Always enumerate live actors and compare with log before starting new work (see WORKFLOW.md).

---

## Over-context boxing design
- **What happened:** Putting too much design context into the session startup locked the AI into re-litigating scope instead of building. The prior project restarted partly because of this.
- **Rule added:** Hold the full vision in CHARTER.md. Build only the next small real thing. Do not dump design plans into session context.

---

## Unreal MCP instability during destructive operations
- **What happened:** MCP connections became unreliable during or immediately after large deletes or asset swaps.
- **Rule:** Commit before risky destructive changes. Reconnect MCP after major operations.

---

## glb format not reliable for Unreal import
- **What happened:** glb exports from Blender did not import cleanly into UE5 via MCP.
- **Rule:** Always export FBX from Blender, not glb.

---

## Session usage limits
- **What happens:** Claude or Codex can hit usage limits mid-session.
- **Rule:** If approaching a limit, write `SESSION INCOMPLETE — stopped during [task]; next action is [exact step]` to BUILDLOG and push BEFORE the session ends.
