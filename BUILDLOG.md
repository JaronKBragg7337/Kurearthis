# BUILDLOG — current state only

Older history lives in `BUILDLOG_ARCHIVE.md`. Do not load that file at session start unless debugging a regression or tracing a decision.

---

## Current state
- **Project:** Kurearthis
- **Unreal status:** Unreal Engine 5.8 project created; `Foundation` is the verified control map; planetary proof work has not started
- **GitHub:** https://github.com/JaronKBragg7337/Kurearthis
- **Git status:** Clean — planetary-first direction committed
- **Last verified good state:** `Content/Foundation.umap` open and saved with 8 actors; live audit matched the log before the direction change
- **Current builder:** Codex
- **Active blockers:** None

## Known issues
- Planet scale and coordinate/reference-frame strategy are not yet proven.
- `Foundation` is intentionally flat and must remain a control map, not become the game-world architecture.

## Next up
1. Create a dedicated `PlanetaryProof` map with one spherical body at a deliberate, documented radius; do not add gravity or a player in the same chunk.
2. Verify the body's geometry, scale, origin, actor count, and map save with evidence.
3. Only after that proof is committed, add radial gravity and local player up direction as the next chunk.

## Recent entries

### 2026-06-20 — Builder: Codex
- Did: Corrected the project law from flat economy-first to a staged planetary architecture proof; preserved `Foundation` as a known-good control map
- Verified: Reconnected to Unreal before editing and audited the live `Foundation` scene: exactly 8 expected actors with no live/log divergence; reviewed the charter, workflow, and next-up sequence for consistency
- Files changed: `CHARTER.md`, `WORKFLOW.md`, `BUILDLOG.md`
- Notes: Planetary-first is an architecture-validation order, not permission to build a giant solar system at once. Economy, plots, placement, procedural galaxies, and orbital simulation remain deferred until the four planetary proofs pass.
- Next: Create `PlanetaryProof` with one spherical body at a deliberate, documented radius and verify that single-body scale proof

### 2026-06-20 — Builder: Codex
- Did: Created the Unreal Engine 5.8 project scaffold and saved a small Basic level as `Content/Foundation.umap`; set it as the editor and game startup map
- Verified: Unreal Python actor audit reported exactly 8 actors: Floor, PlayerStart, DirectionalLight, SkyLight, SkyAtmosphere, ExponentialHeightFog, VolumetricCloud, and SM_SkySphere; level save confirmed on disk
- Files changed: `Kurearthis.uproject`, `.gitignore`, `Config/DefaultEngine.ini`, `Config/DefaultGame.ini`, `Config/DefaultInput.ini`, `Content/Foundation.umap`, `ASSETS_MANIFEST.md`, `BUILDLOG.md`
- Notes: Initial bare project opened Unreal's unsaved 138-actor Open World template; it was audited, not saved, and replaced with the small Basic level. Local checkout was missing at session start and was restored from the public GitHub remote. No live/log divergence was found before work began.
- Next: Add one grounded controllable player to `Foundation` and verify movement in Play-in-Editor

### 2026-06-20 — Builder: Perplexity (kit setup)
- Did: Created GitHub repo Kurearthis, pushed full project kit
- Verified: Files pushed and visible on GitHub
- Files changed: All kit files
- Notes: Kit structured from lessons learned in prior SpaceYouLand project — lean logs, mandatory live-scene verification, SESSION INCOMPLETE protocol, log rotation to prevent token drain
- Next: Jaron creates the Unreal project and starts first Claude/Codex session
