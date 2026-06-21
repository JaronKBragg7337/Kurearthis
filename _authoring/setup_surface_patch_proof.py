"""Set up Proof 2d — a Chaos body resting on a LOCAL surface-collision patch.

Finding 2c proved a planet cannot be one giant static collision mesh: the
Earth-sized ProofEarth mesh ejects a dynamic body via glitchy far-from-mesh-origin
contacts even with the floating origin holding the body's coordinates near (0,0,0).

This sets up the necessary next layer:
  - ProofEarth becomes VISUAL + query-only (line traces still hit it, but it no
    longer provides physics-simulation contacts) — the giant mesh stops being the
    collision surface.
  - A small LocalSurfacePatch (a few km across) is placed tangent to the sphere at
    the equator (+X), its top face at the surface radius, its up = radial up (+X).
    Because it is small, its collision geometry is precise near the world origin
    after rebasing — unlike the 6,371 km sphere.
  - The existing ARadialGravityTestBody is released ~1 km above the patch and the
    AFloatingOriginManager keeps the active region near origin.

When Simulate runs, the body should fall under radial gravity and REST on the patch
(rested=true, dist ~= surface radius, local_up ~= (1,0,0)). The patch follows the
floating origin automatically because UWorld::SetNewWorldOrigin shifts every actor.

Run via the harness:
  python _authoring/run_physics_harness.py 33 --setup _authoring/setup_surface_patch_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PATCH_LABEL = "LocalSurfacePatch"
BODY_LABEL = "ChaosGravityBody"
MANAGER_LABEL = "FloatingOriginManager"

SURFACE_R = 637_100_000.0           # nominal surface radius (cm) along +X (equator)
DROP_ALTITUDE = 100_000.0           # release ~1 km above the patch top

# Engine cube is 100 cm; scale (thick, wide, wide) gives a slab whose +X face is
# the top. Small extents keep the collision geometry precise near the origin.
PATCH_THICK_SCALE = 200.0           # 100 cm * 200  = 200 m thick
PATCH_EXTENT_SCALE = 5000.0         # 100 cm * 5000 = 5 km across
PATCH_HALF_THICK = 50.0 * PATCH_THICK_SCALE          # 10,000 cm = 100 m
PATCH_CENTER_X = SURFACE_R - PATCH_HALF_THICK        # top face exactly at SURFACE_R
BODY_SPAWN = unreal.Vector(SURFACE_R + DROP_ALTITUDE, 0.0, 0.0)

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("RadialGravityTestBody", "FloatingOriginManager"):
    if not hasattr(unreal, cls):
        raise RuntimeError(f"unreal.{cls} not found - C++ module did not load/compile")

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())

# Tag + downgrade the giant planet mesh to query-only so it stops ejecting bodies.
planet = next((a for a in actors if a.get_actor_label() == PLANET_LABEL), None)
if planet is None:
    raise RuntimeError("ProofEarth not found")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))
planet.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)

# Idempotent: clear prior test actors (patch, body, manager).
for a in actors:
    if a.get_actor_label() in (PATCH_LABEL, BODY_LABEL, MANAGER_LABEL):
        actor_sub.destroy_actor(a)

# --- Local surface-collision patch (small, precise, blocks physics) ---------
patch = actor_sub.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(PATCH_CENTER_X, 0.0, 0.0), unreal.Rotator()
)
patch.set_actor_label(PATCH_LABEL)
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
patch.static_mesh_component.set_static_mesh(cube)
patch.set_actor_scale3d(unreal.Vector(PATCH_THICK_SCALE, PATCH_EXTENT_SCALE, PATCH_EXTENT_SCALE))
patch.static_mesh_component.set_collision_profile_name("BlockAll")
patch.static_mesh_component.set_simulate_physics(False)

# --- Chaos test body, released ~1 km above the patch ------------------------
body = actor_sub.spawn_actor_from_class(unreal.RadialGravityTestBody, BODY_SPAWN, unreal.Rotator())
body.set_actor_label(BODY_LABEL)

# --- Floating-origin manager keeps the active region near (0,0,0) -----------
manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator()
)
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", body)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(
    f"KUREARTHIS_PATCH_SETUP patch={PATCH_LABEL} patch_top_x={SURFACE_R:.1f} "
    f"body_x={BODY_SPAWN.x:.1f} proofearth_collision=QUERY_ONLY actors={labels}"
)
