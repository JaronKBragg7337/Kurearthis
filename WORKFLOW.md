# WORKFLOW — how Claude, Codex, and Jaron operate

Read `CHARTER.md` first.

## Session start order
1. Read `CHARTER.md`
2. Read `AUTHORIZATION.md` (standing build/install permissions)
3. Read `WORKFLOW.md`
4. Read `BUILDLOG.md`
5. Connect to Unreal
6. Verify live scene vs log (see below)

## Live scene verification (mandatory before new work)
Before trusting the log, enumerate key scene actors and compare against what BUILDLOG.md says should exist.

If live state and log match — continue.

If they do not match, write:
```
STATE DIVERGENCE — [what you found] vs [what log says]
```
Then stop new feature work and resolve the mismatch first.

This step exists because a crashed session can leave ghost actors in Unreal with no log entry. Those ghosts cause bugs that no future session can diagnose from the log alone.

## Capability check rule (read when blocked, uncertain, or failing)
Do NOT assume a tool is unavailable just because it is not immediately obvious.

When blocked, uncertain, or repeating a failing workflow:
1. Inspect the local environment first — check what is already installed, connected, authenticated, or reachable on this machine before assuming anything.
2. Consult `AGENT_CAPABILITIES/` for known tools, working patterns, and documented limits.
3. If still blocked, search for newly available tools, MCPs, connectors, prompts, or workflows that could help.

Prefer verified local capability over memory or assumption.
If a new capability is discovered, record it in `AGENT_CAPABILITIES/`.
If a new limitation is discovered, record that too.

## Active architecture proof order
Until the planetary foundation milestone in `CHARTER.md` is complete, work in this order:
1. Create one spherical body at a deliberate, documented scale.
2. Prove radial gravity and the player's local up direction on that body.
3. Prove the visible surface-to-atmosphere-to-dark-space transition.
4. Add a second distant body and prove both coexist in the same world model.

Treat each numbered proof as one or more small, independently verified chunks. Do not skip ahead, and do not start economy, plot ownership, object placement, procedural galaxy, or orbital simulation work during these proofs.

`Foundation` remains a control map only. Planetary proof work should live in a dedicated map so the known-good control scene stays available for comparison.

## Build loop
1. Do ONE coherent, small chunk only.
2. Save the Unreal project.
3. Verify with evidence: trace, capture, compile result, or Jaron playtest.
4. Append a short BUILDLOG entry (see format below).
5. Commit and push with honest builder attribution.
6. Stop at a clean handoff point.

## BUILDLOG entry format
```
### YYYY-MM-DD — Builder: [Claude | Codex]
- Did: [what was built]
- Verified: [how it was confirmed]
- Files changed: [key paths]
- Notes: [gotchas, decisions, warnings]
- Next: [exact next step]
```

## Incomplete session rule
If approaching a usage limit before finishing, write this BEFORE stopping:
```
SESSION INCOMPLETE — stopped during [task]; next action is [exact step]
```
Commit and push that entry before the session ends.

## Log rotation rule
BUILDLOG.md holds only:
- Current state block
- Known issues
- Last 10 entries max
- Next up list

Anything older moves to `BUILDLOG_ARCHIVE.md`. This keeps session startup cheap and prevents the log from becoming a token drain.

## Commit rules
- Commit after each coherent chunk.
- Commit BEFORE risky destructive changes too (creates a rollback point).
- Commit attribution trailers:
  - Claude: `Co-Authored-By: Claude <noreply@anthropic.com>`
  - Codex: `Co-Authored-By: Codex <noreply@openai.com>`
- Never commit secrets, personal data, or anything private.
- Repo is PUBLIC. The name must not hint at the game's space arc.

## Cross-agent rule
Claude and Codex share state ONLY through committed files. Do not assume context from prior chats. Do not treat uncommitted work as real.

## Jaron's test loop
Jaron tests what the AI cannot reliably know:
- movement feel
- visual read
- whether surface, atmosphere, and space read as one continuous world
- interaction feel
- whether it actually works in play

Ask Jaron to test anything that requires human eyes or a controller.

## Asset tracking
Whenever an asset is added or changed, update `ASSETS_MANIFEST.md`:
- asset path
- IN-HOUSE or OPEN-SOURCE
- source URL + license if open-source
- builder
- date

## Pipeline (proven in prior project — reuse it)
- Model geometry in Blender headless (`blender --background --python _authoring/make_*.py`)
- Export FBX (not glb), model in METERS
- Import via `StaticMeshTools.import_file`
- Game logic via Blueprint; data-driven where possible
