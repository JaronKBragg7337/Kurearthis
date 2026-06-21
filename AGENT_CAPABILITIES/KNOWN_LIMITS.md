# KNOWN_LIMITS.md
Last updated: 2026-06-20
Updated by: Claude (added verified findings)

This file records things that were assumed possible but proved false, flaky, unreliable, or blocked.
If you hit a hard limit, document it here so the next session does not repeat the same dead end.

---

## Chaos physics fails at planetary absolute coordinates (VERIFIED 2026-06-20)
- **What happened:** a real Chaos rigid body under radial gravity at ~6.37e8 cm from world origin would not fall correctly — ~5× too slow, drifted outward, slid without resting.
- **Rule:** do gravity/movement math in double precision; do not trust raw Chaos far from origin. The double-precision integrator (`_authoring/prove_radial_gravity.py`) is correct. See `PLANETARY_PROOF.md` Proof 2b.

## A planet cannot be one giant static collision mesh (VERIFIED 2026-06-20)
- **What happened:** even with floating origin holding the body at the origin, the Chaos body was ejected (~985 cm/s position drift vs ~10 cm/s physics velocity, ~1 km/frame jumps) by glitchy contacts with the Earth-sized single static collision mesh.
- **Rule:** the surface under the player must be LOCAL collision near origin (a terrain chunk that follows the floating origin), plus a custom radial-gravity controller. See Proof 2c.

## [CLAUDE-ENV] No Unreal MCP loaded for Claude (CORRECTED 2026-06-20)
- **What happened:** seed files assumed an "Unreal Engine MCP" was active. None was loaded in the Claude session.
- **Rule (Claude):** drive the editor via its Python console + GUI automation. **Codex:** session-specific — check your own loaded tools; don't infer yours from Claude's.

## gh CLI authentication does not reliably persist (VERIFIED 2026-06-21)
- Claude authenticated `gh` on 2026-06-20, but Codex's live
  `gh auth status` on 2026-06-21 reported no logged-in hosts.
- **Rule:** verify before API/PR use. Plain git push/pull remains functional via
  Windows Credential Manager; run `gh auth login` with Jaron's browser approval
  only when a `gh` workflow is needed.

## [CLAUDE-ENV] Windows-MCP Click/Type `loc` is buggy (VERIFIED 2026-06-20)
- **What happened:** passing `loc=[x,y]` fails pydantic validation (serialized to a string) in Claude's Windows-MCP bridge.
- **Rule (Claude):** click/move with Win32 (`SetCursorPos`+`mouse_event`). `Clipboard`, `Shortcut`, `Snapshot`, `App` work fine. Codex may not use this bridge.

## Editor must be closed to build a new/changed C++ module (VERIFIED 2026-06-20)
- **What happened:** a new module can't hot-load; leaving an uncompilable module in `.uproject` bricks the editor ("Missing target file"/"Target Upgrade Required").
- **Rule:** close editor → build → reopen. UE C++ build also requires the .NET Framework 4.8.1 SDK.

## Ghost actors after crashes
- **Rule:** always enumerate live actors vs log before new work (WORKFLOW.md).

## Over-context boxing design
- **Rule:** hold the vision in CHARTER.md; build the next small real thing.

## glb not reliable for Unreal import
- **Rule:** export FBX from Blender, not glb.

## Session usage limits
- **Rule:** if approaching a limit, write `SESSION INCOMPLETE — stopped during [task]; next action is [exact step]` to BUILDLOG and push BEFORE the session ends.
