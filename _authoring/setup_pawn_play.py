"""Leave PlanetaryProof in a PLAYABLE state so Jaron can walk the pawn (proof #2 feel).

Configures and SAVES the scene: RadialGravityPawn on the patch (DebugDrive OFF so
input drives it; AutoPossessPlayer=Player0 in the class possesses it on Play), the
local patch, the visual-only planet, a DirectionalLight + SkyLight so the surface is
visible (the proof map is otherwise unlit), and the floating-origin manager.

After this runs, open `Content/PlanetaryProof` in the editor and press Play (or
Alt+P). Controls: W/A/S/D move, mouse looks. Esc/Shift+F1 to release the mouse.

  python _authoring/ue_remote.py --file _authoring/setup_pawn_play.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PATCH_LABEL = "LocalSurfacePatch"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"
SUN_LABEL = "SurfaceSun"
SKY_LABEL = "SurfaceSky"

SURFACE_R = 637_100_000.0
CAPSULE_HALF = 100.0
SPAWN_GAP = 200.0
PAWN_SPAWN = unreal.Vector(SURFACE_R + CAPSULE_HALF + SPAWN_GAP, 0.0, 0.0)

PATCH_THICK_SCALE = 200.0
PATCH_EXTENT_SCALE = 5000.0
PATCH_HALF_THICK = 50.0 * PATCH_THICK_SCALE
PATCH_CENTER_X = SURFACE_R - PATCH_HALF_THICK

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

if not hasattr(unreal, "RadialGravityPawn"):
    raise RuntimeError("unreal.RadialGravityPawn not found - C++ module did not compile/reload")

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())
by_label = {a.get_actor_label(): a for a in actors}

planet = by_label.get(PLANET_LABEL)
if planet is None:
    raise RuntimeError("ProofEarth not found")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))
planet.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

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

# Clear prior dynamic test actors so only the playable pawn remains.
for a in actors:
    if a.get_actor_label() in ("SweptGravityBody", "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL):
        actor_sub.destroy_actor(a)

pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, PAWN_SPAWN, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 0.0, 0.0))  # input-driven

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

# Lighting so the surface is visible (sun from the +X sky; black space beyond).
if SUN_LABEL not in by_label:
    sun = actor_sub.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(-30.0, 180.0, 0.0))
    sun.set_actor_label(SUN_LABEL)
    sun.light_component.set_intensity(10.0)
if SKY_LABEL not in by_label:
    sky = actor_sub.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
    sky.set_actor_label(SKY_LABEL)
    sky.light_component.set_intensity(0.6)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_PAWN_PLAY pawn={PAWN_LABEL} input-driven, lit; press Play. actors={labels}")
