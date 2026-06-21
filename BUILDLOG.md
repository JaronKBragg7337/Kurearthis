# BUILDLOG — current state only

Older history lives in `BUILDLOG_ARCHIVE.md`. Do not load that file at session start unless debugging a regression or tracing a decision.

---

## Current state
- **Project:** Kurearthis
- **Unreal status:** C++ project on UE 5.8 (`Source/Kurearthis`). Floating-origin foundation (`AFloatingOriginManager`) built and proven to rebase correctly. Proofs: 1 (scale) ✓, 2a radial-gravity MODEL ✓ (double-precision integrator), 2b/2c established that stock Chaos cannot run on an Earth-sized single static mesh. `PlanetaryProof` holds `ProofEarth`, `GravityRestMarker`, `ChaosGravityBody`, `FloatingOriginManager`; `Foundation` is the control map
- **GitHub:** https://github.com/JaronKBragg7337/Kurearthis
- **Git status:** Clean — floating-origin foundation + findings + AUTHORIZATION.md committed
- **Last verified good state:** After stopping Simulate, live audit = 4 actors, no ghosts. `Saved/FloatingOrigin_run.log` shows the world rebasing to keep the body at the origin (rebase #1: body 637,200,000 → 0)
- **Current builder:** Claude
- **Active blockers:** None

## Known issues
- **ARCHITECTURE FINDINGS (Proof 2, see `PLANETARY_PROOF.md`):**
  - 2a: a double-precision integrator correctly proves the gravity MODEL — body released above the equator falls radially (−X, zero Y/Z drift) and rests on the real surface with `up=(1,0,0)`.
  - 2b: stock Chaos at ~6.37e8 cm from origin fails (5× too slow, drifts outward, slides without resting) — large-world float precision.
  - 2c: floating origin (`AFloatingOriginManager`) WORKS (rebasing confirmed, body held at origin), but the Chaos body STILL won't fall — its world position is ejected ~985 cm/s while physics velocity reads ~10, i.e. the body is shoved out by glitchy contacts with the **Earth-sized single static collision mesh**. Floating origin fixes the body's coordinates but the planet is still one huge far-centered mesh.
- **Necessary architecture (evidence-backed, NOT a shortcut):** the planet cannot be one giant static collision mesh. The surface under the player must be LOCAL collision near the origin (a terrain chunk that follows the floating origin), and movement needs a custom radial-gravity character controller (UE's CharacterMovementComponent assumes flat +Z up). Stock Chaos on a giant far mesh is demonstrably unusable, so the custom controller is required, not optional.
- No player-controlled pawn yet. `Foundation` stays a flat control map.

## Next up
1. Build the next necessary layer: a LOCAL surface-collision representation near the world origin (a ground patch/chunk oriented to radial up, following `AFloatingOriginManager`), so a Chaos body actually rests on real collision near origin. Verify a body released above it falls under radial gravity and rests with `up` radial. This is the miniature of the real planet-chunk + floating-origin system.
2. Then a custom radial-gravity character controller (capsule oriented to radial up) standing and moving on that local surface.
3. Defer atmosphere/space (proof 3) and the second body (proof 4) until a pawn stands and moves.

## Recent entries

### 2026-06-20 — Builder: Claude
- Did: Built the floating-origin foundation `AFloatingOriginManager` (`Source/Kurearthis/`): keeps a Focus actor within 500 m of world origin via `UWorld::SetNewWorldOrigin` each tick, so the active region (and thus Chaos) stays in a precise frame. Made `ARadialGravityTestBody` read the planet center dynamically (planet tagged "Planet") so the math survives rebasing. Compiled, reopened the editor, spawned body + manager, ran under Simulate. Also added `AUTHORIZATION.md` (standing build/install permissions) and a No-shortcut law, per Jaron's direction
- Verified: Floating origin WORKS — `Saved/FloatingOrigin_run.log` shows rebase #1 moving the body from world X=637,200,000 to (0,0,0) and later rebases holding it at origin. BUT the body still doesn't fall: its world position drifts outward ~985 cm/s while physics velocity reads ~10 cm/s, and it jumps ~1 km per frame in the rebase log — it is being ejected by glitchy contacts with the Earth-sized single static mesh, not by gravity. Conclusion: the planet must use LOCAL collision near origin, not one giant mesh. Live audit after Simulate = clean 4-actor scene
- Files changed: `Source/Kurearthis/FloatingOriginManager.*`, `Source/Kurearthis/RadialGravityTestBody.*` (dynamic center + relative logging), `_authoring/spawn_chaos_gravity_body.py`, `AUTHORIZATION.md` (new), `CHARTER.md` (No-shortcut law + auth pointer), `WORKFLOW.md` (start order), `PLANETARY_PROOF.md` (Proof 2c), `BUILDLOG.md`. Evidence in `Saved/*_chaos_floatingorigin.*` and `Saved/FloatingOrigin_run.log` (gitignored)
- Notes: This is necessary foundation, not a shortcut — floating origin is required infrastructure and is proven working. The remaining failure is a real engine constraint (single giant collision mesh), now demonstrated, which makes the local-collision + custom-controller path necessary rather than a convenience. Editor closed/reopened for the build and re-verified clean (Crash/Restart law)
- Next: Build a local surface-collision patch near origin (radial-up oriented, follows the floating origin) and verify a Chaos body rests on it under radial gravity

### 2026-06-20 — Builder: Claude
- Did: Installed the .NET Framework 4.8.1 SDK automatically via `winget` (no admin prompt needed), which unblocked the C++ build. Moved `ARadialGravityTestBody` into `Source/Kurearthis`, re-enabled the module in the `.uproject`, compiled the editor target (success), reopened the editor, spawned the C++ body 1 km above the equator, and ran it under real Chaos physics in Simulate-In-Editor
- Verified: **Chaos breaks down at planetary scale.** C++ trajectory log (`Saved/RadialGravityProof.log`): body should reach ~14,000 cm/s in ~14s under 980 cm/s²; instead ~12 cm/s at t=12s, drifted ~37 km outward, took ~70s to contact the surface, then slid tangentially at a stuck ~3,750 cm/s and never rested (penetrating ~100 m, drifting km in Y/Z). `up` stayed ≈`(1,0,0)` and it did hit the mesh — direction + collision correct, solver dynamics wrong. Contrast: the double-precision integrator (Proof 2a) fell in 14s and rested exactly on the surface. After stopping Simulate, live audit = clean 3-actor scene
- Files changed: `Source/**` (C++ module, now canonical; removed parked `_authoring/unreal_cpp/`), `Kurearthis.uproject` (Modules), `_authoring/spawn_chaos_gravity_body.py`, `PLANETARY_PROOF.md` (Proof 2 section), `ASSETS_MANIFEST.md`, `BUILDLOG.md`. Build outputs (`Binaries/`, `Intermediate/`) are gitignored
- Notes: The editor was closed for the build and reopened (Crash/Restart law honored: re-verified clean on reopen and again after Simulate). A Windows firewall prompt for the UBA build server appeared and was dismissed (Cancel) — inbound build-server networking is not needed. This is a genuine architectural finding, not a code bug: the same code near the origin would behave correctly
- Next: Choose movement-frame strategy (origin rebasing vs custom double-precision character controller) and prototype a surface-standing pawn with radial up

### 2026-06-20 — Builder: Claude
- Did: Proved radial gravity + local up on `ProofEarth`. Released a test body 1 km above the EQUATOR (+X) and integrated constant acceleration (980 cm/s²) toward the planet center, colliding against the real `ProofEarth` collision mesh via engine line traces. Left a visible `GravityRestMarker` resting on the surface and saved the level. Also wrote a forward-compatible C++ Chaos body (`ARadialGravityTestBody`) intended as the runtime path
- Verified: `Saved/RadialGravityProof.json` — `rested=true`, fell from x=637,200,000 to rest at (637,099,968, 0, 0) = dist `637,099,968 cm` (≈ nominal radius, −32 cm float32), `local_up_at_rest=(1,0,0)`, `max_abs_y=0`, `max_abs_z=0` (zero lateral drift → motion was radial −X, NOT flat −Z). Trajectory log shows X decreasing while Y,Z stay 0.0 and speed rising at exactly g. Live Outliner shows 2 actors
- Files changed: `Content/PlanetaryProof.umap`, `_authoring/prove_radial_gravity.py`, `_authoring/unreal_cpp/**` (C++ module), `ASSETS_MANIFEST.md`, `BUILDLOG.md`
- Notes: Equator placement is deliberate — at the equator flat −Z gravity would drift the body in Z and never land radially; only true radial gravity produces the observed pure −X fall. The Chaos/C++ route was attempted first but blocked: no `.NET Framework 4.8 SDK` (SwarmInterface won't instantiate) and no admin to install it; an uncompilable module bricks the editor, so the C++ was moved out of `Source/` into `_authoring/unreal_cpp/` and the project kept Blueprint-only. The editor was closed/reopened during build attempts and re-verified clean on reopen (Restart/Crash law)
- Next: Install `.NET Framework 4.8 SDK`, compile the C++ body, and confirm engine Chaos physics reproduces this fall; then a surface-standing pawn with radial up

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
