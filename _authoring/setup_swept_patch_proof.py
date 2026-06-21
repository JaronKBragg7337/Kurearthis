"""Set up Proof 2e — a CUSTOM swept integrator resting on the local patch.

Proof 2d showed Chaos `AddForce` cannot make a body fall and rest on the local
patch (won't fall at scale; ~100x too slow at origin). This sets up the proven
path instead: `ASweptGravityBody` integrates radial gravity directly (double
precision) and moves by sweeping against `LocalSurfacePatch`, so it should fall
~950 m and REST on the patch with local up = radial.

Scene after setup: ProofEarth (QueryOnly, "Planet"), GravityRestMarker (collision
neutralised — it is a 1 km visual marker around the release point), LocalSurfacePatch,
SweptGravityBody, FloatingOriginManager (Focus = swept body). The Chaos test body is
removed so only the swept body writes RadialGravityProof.json.

  python _authoring/run_physics_harness.py 33 --setup _authoring/setup_swept_patch_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
MARKER_LABEL = "GravityRestMarker"
PATCH_LABEL = "LocalSurfacePatch"
BODY_LABEL = "SweptGravityBody"
MANAGER_LABEL = "FloatingOriginManager"

SURFACE_R = 637_100_000.0
DROP_ALTITUDE = 100_000.0                       # release ~1 km above the patch top
BODY_SPAWN = unreal.Vector(SURFACE_R + DROP_ALTITUDE, 0.0, 0.0)

# LocalSurfacePatch geometry (matches setup_surface_patch_proof.py) — ensured present.
PATCH_THICK_SCALE = 200.0
PATCH_EXTENT_SCALE = 5000.0
PATCH_HALF_THICK = 50.0 * PATCH_THICK_SCALE
PATCH_CENTER_X = SURFACE_R - PATCH_HALF_THICK

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

if not hasattr(unreal, "SweptGravityBody"):
    raise RuntimeError("unreal.SweptGravityBody not found - C++ module did not compile/reload")

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())
by_label = {a.get_actor_label(): a for a in actors}

# Planet: tagged, but collision OFF. Sweeps are QUERIES, so QueryOnly would still
# make the giant 6,371 km mesh (imprecise at planetary scale, finding 2c) block the
# swept body even 1 km above its surface. The LOCAL patch is the collision surface;
# the giant mesh is visual only here.
planet = by_label.get(PLANET_LABEL)
if planet is None:
    raise RuntimeError("ProofEarth not found")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))
planet.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

# The 1 km GravityRestMarker (a proof-2a visual artifact) sits AROUND the release
# point, so the body spawns inside it and start-penetrates it. set_collision_enabled
# (NO_COLLISION) does NOT survive PIE duplication reliably, so just remove the marker
# from the test scene — proof 2a is fully recorded in PLANETARY_PROOF.md.
marker = by_label.get(MARKER_LABEL)
if marker is not None:
    actor_sub.destroy_actor(marker)

# Ensure the local surface patch exists (re-create if a fresh load lacks it).
patch = by_label.get(PATCH_LABEL)
if patch is None:
    patch = actor_sub.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(PATCH_CENTER_X, 0.0, 0.0), unreal.Rotator())
    patch.set_actor_label(PATCH_LABEL)
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
    patch.static_mesh_component.set_static_mesh(cube)
    patch.set_actor_scale3d(unreal.Vector(PATCH_THICK_SCALE, PATCH_EXTENT_SCALE, PATCH_EXTENT_SCALE))
    patch.static_mesh_component.set_collision_profile_name("BlockAll")
    patch.static_mesh_component.set_simulate_physics(False)

# Remove prior dynamic test actors (Chaos body, prior swept body, prior manager).
for a in actors:
    if a.get_actor_label() in ("ChaosGravityBody", BODY_LABEL, MANAGER_LABEL):
        actor_sub.destroy_actor(a)

# Swept integrator body, released ~1 km above the patch.
body = actor_sub.spawn_actor_from_class(unreal.SweptGravityBody, BODY_SPAWN, unreal.Rotator())
body.set_actor_label(BODY_LABEL)

# Floating-origin manager keeps the active region near (0,0,0).
manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", body)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_SWEPT_SETUP body={BODY_LABEL} body_x={BODY_SPAWN.x:.1f} "
      f"marker_collision=NONE actors={labels}")
