# BUILDLOG — current state only

Older history lives in `BUILDLOG_ARCHIVE.md`. Do not load that file at session start unless debugging a regression or tracing a decision.

---

## Current state
- **Project:** Kurearthis
- **Unreal status:** Planetary proof 1 complete; `PlanetaryProof` contains one rounded-Earth-mean-radius spherical body at world origin; `Foundation` remains the control map
- **GitHub:** https://github.com/JaronKBragg7337/Kurearthis
- **Git status:** Clean — single-body scale proof committed
- **Last verified good state:** `PlanetaryProof` saved and reopened with exactly one actor, `ProofEarth`; computed radius `637,100,105.034 cm`
- **Current builder:** Codex
- **Active blockers:** None

## Known issues
- Surface collision, local reference frame, radial gravity, and player behavior are not yet proven; `ProofEarth` is currently a visual static mesh only.
- `Foundation` is intentionally flat and must remain a control map, not become the game-world architecture.

## Next up
1. Add usable surface collision to `ProofEarth` without adding a pawn.
2. Verify a radial line trace from above the north pole hits at the documented radius and record the measured hit location.
3. Only after collision is proven, add a minimal radial-gravity test pawn as a separate chunk.

## Recent entries

### 2026-06-20 — Builder: Codex
- Did: Authored and imported one reproducible in-house sphere, created `PlanetaryProof`, and placed the sole `ProofEarth` actor at world origin with a documented rounded-Earth-mean target radius of 6,371,000 m
- Verified: Unreal audit reported 1 actor (`ProofEarth`, `StaticMeshActor`) at `(0,0,0)` with uniform scale `6371`; imported bounds compute to `637,100,105.034 cm`, 1.050 m from target; map save/reopen passed and `Foundation` was unchanged
- Files changed: `Content/PlanetaryProof.umap`, `Content/Planetary/SM_ProofPlanet_Base.uasset`, `PLANETARY_PROOF.md`, `_authoring/make_planetary_proof_body.py`, `_authoring/setup_planetary_proof.py`, `ASSETS_MANIFEST.md`, `BUILDLOG.md`
- Notes: This proves representation and scale only. No surface collision, gravity, player, atmosphere, orbit, or second body was added. The generated FBX remains ignored; its reproducible Blender authoring script is committed.
- Next: Add and verify `ProofEarth` surface collision with a radial north-pole line trace; do not add a pawn in the same chunk

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
