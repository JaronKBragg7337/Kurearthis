"""CONTROL for Proof 2d — same Chaos body + local patch, but ALL near the origin.

Proof 2d (setup_surface_patch_proof.py) showed the Chaos body will not fall onto
a clean local patch when the gravity center is the real planet center 6,371 km
away — it drifts outward with near-zero reported velocity.

This control removes scale as a variable: gravity center at the origin, a tiny
surface radius (200 m), the patch a few hundred metres out, and the body released
~300 m above it. No floating-origin manager (nothing is far from origin). If the
Chaos body FALLS and RESTS here, the patch + Chaos force-integration mechanics are
sound and the 2d failure is purely the planetary coordinate scale. If it also fails
here, there is a setup bug to fix before drawing any conclusion.

This script does NOT save the level — the control actors are in-memory only, so the
on-disk PlanetaryProof keeps the real 2d setup. Reload the level afterwards.

Run via the harness:
  python _authoring/run_physics_harness.py 33 --setup _authoring/setup_nearorigin_control.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PATCH_LABEL = "ControlPatch"
BODY_LABEL = "ControlBody"

R = 20_000.0                 # tiny "surface radius" (200 m) along +X
DROP = 30_000.0              # release 300 m above the patch top
PATCH_THICK_SCALE = 20.0     # 100 cm * 20  = 20 m thick
PATCH_EXTENT_SCALE = 200.0   # 100 cm * 200 = 200 m across (wide enough for the body)
PATCH_HALF_THICK = 50.0 * PATCH_THICK_SCALE      # 1,000 cm = 10 m
PATCH_CENTER_X = R - PATCH_HALF_THICK            # top face at R
BODY_SPAWN = unreal.Vector(R + DROP, 0.0, 0.0)

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())

# Remove any prior 2d test actors AND any prior control actors. Also strip the
# "Planet" tag from ProofEarth so the body uses FallbackCenter (the origin) and is
# not pulled toward the giant sphere's center handling.
for a in actors:
    if a.get_actor_label() in (
        "LocalSurfacePatch", "ChaosGravityBody", "FloatingOriginManager",
        PATCH_LABEL, BODY_LABEL,
    ):
        actor_sub.destroy_actor(a)
    if a.get_actor_label() == "ProofEarth":
        a.tags = unreal.Array(unreal.Name)  # clear tags for the control

# --- Local patch near origin -------------------------------------------------
patch = actor_sub.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(PATCH_CENTER_X, 0.0, 0.0), unreal.Rotator()
)
patch.set_actor_label(PATCH_LABEL)
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
patch.static_mesh_component.set_static_mesh(cube)
patch.set_actor_scale3d(unreal.Vector(PATCH_THICK_SCALE, PATCH_EXTENT_SCALE, PATCH_EXTENT_SCALE))
patch.static_mesh_component.set_collision_profile_name("BlockAll")
patch.static_mesh_component.set_simulate_physics(False)

# --- Chaos body near origin, gravity center = origin -------------------------
body = actor_sub.spawn_actor_from_class(unreal.RadialGravityTestBody, BODY_SPAWN, unreal.Rotator())
body.set_actor_label(BODY_LABEL)
body.set_editor_property("PlanetActor", None)
body.set_editor_property("FallbackCenter", unreal.Vector(0.0, 0.0, 0.0))
body.set_editor_property("SurfaceRadius", R)

# Intentionally NOT saving the level — control actors stay in-memory only.
labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(
    f"KUREARTHIS_CONTROL_SETUP patch_top_x={R:.1f} body_x={BODY_SPAWN.x:.1f} "
    f"gravity_center=origin saved=False actors={labels}"
)
