# BUILDLOG — current state only

Older history lives in `BUILDLOG_ARCHIVE.md`. Do not load that file at session start unless debugging a regression or tracing a decision.

---

## Current state
- **Project:** Kurearthis
- **Unreal status:** Planetary proof 1 complete and `ProofEarth` now has verified usable surface collision; `PlanetaryProof` holds one rounded-Earth-mean-radius body at world origin; `Foundation` remains the control map
- **GitHub:** https://github.com/JaronKBragg7337/Kurearthis
- **Git status:** Clean — surface collision proof committed
- **Last verified good state:** Live editor audit of `PlanetaryProof` = exactly 1 actor `ProofEarth` at origin, scale 6371; a simple radial north-pole line trace blocks on it with impact normal `(0,0,1)` at radius `~637,100,672 cm`
- **Current builder:** Claude
- **Active blockers:** None

## Known issues
- Local reference frame, radial gravity, and player behavior are not yet proven; `ProofEarth` is now a collidable static mesh but nothing stands on it yet.
- Collision/trace impact results are float32: at ~6.37e8 cm the ULP is tens of cm, so trace hit points carry sub-meter-to-few-meter scatter (impact `637,100,672` vs proof-1 bounds `637,100,105`). Acceptable for representation/collision; keep in mind for gravity and movement math.
- `Foundation` is intentionally flat and must remain a control map, not become the game-world architecture.

## Next up
1. Add a minimal radial-gravity test pawn as a separate chunk: spawn a physics body above the north pole and prove it falls toward planet center and rests on the surface.
2. Then prove a correct local up direction for a controlled pawn (surface stand + orientation), still in `PlanetaryProof`.
3. Defer atmosphere/space transition (proof 3) and the second body (proof 4) until gravity + local up are proven.

## Recent entries

### 2026-06-20 — Builder: Claude
- Did: Connected to the live Unreal editor, audited the in-memory `PlanetaryProof` scene (matched the log: 1 actor `ProofEarth` at origin, scale 6371 — no divergence), then gave `ProofEarth` usable surface collision by setting the planet mesh body setup to Use Complex Collision As Simple and confirming the actor component blocks queries (`BlockAll`, `QueryAndPhysics`)
- Verified: A simple (non-complex) downward radial line trace from 500 km above the north pole returns `blocking_hit=True` on the ProofEarth StaticMeshActor with impact normal `(0,0,1)` and impact point z `637,100,672 cm`; recorded full result in `Saved/CollisionProofAudit.json`. Because a simple trace blocks, the surface is walkable collision, not just a render mesh
- Files changed: `Content/Planetary/SM_ProofPlanet_Base.uasset`, `Content/PlanetaryProof.umap`, `_authoring/add_verify_surface_collision.py`, `_authoring/live_scene_audit.py`, `BUILDLOG.md`
- Notes: No pawn was added (kept to one chunk). Collision queries return float32 positions; at planetary scale that is tens-of-cm precision, so the ~567 cm gap vs the proof-1 bounds radius is expected float scatter, recorded not hidden. Editor Python was driven through the live editor console (remote execution is disabled); the throwaway HitResult probe was deleted
- Next: Add a minimal radial-gravity test pawn that falls toward planet center and rests on the surface, as a separate verified chunk

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
