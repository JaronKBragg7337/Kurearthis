"""Set up Proof 2f — a RadialGravityPawn stands on the patch and walks tangentially.

CHARTER proof #2 (movement): the pawn must STAND on the surface with local up =
radial and MOVE along it. This places `ARadialGravityPawn` ~2 m above the patch at
the equator and drives it tangentially (+Y) head-lessly via DebugDriveWorldDir, so
the harness can verify the movement logic before Jaron tests controller feel.

Scene after setup: ProofEarth (NoCollision, "Planet"), LocalSurfacePatch,
RadialGravityPawn (DebugDrive +Y), FloatingOriginManager (Focus = pawn).

  python _authoring/run_physics_harness.py 14 --setup _authoring/setup_pawn_walk_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PATCH_LABEL = "LocalSurfacePatch"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"

SURFACE_R = 637_100_000.0
CAPSULE_HALF = 100.0
SPAWN_GAP = 200.0                    # start ~2 m above the patch so it settles fast
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

# Planet: tagged + NoCollision (sweeps are queries; the local patch is the surface).
planet = by_label.get(PLANET_LABEL)
if planet is None:
    raise RuntimeError("ProofEarth not found")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))
planet.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

# Ensure the local surface patch exists.
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

# Remove prior dynamic test actors.
for a in actors:
    if a.get_actor_label() in ("SweptGravityBody", "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL):
        actor_sub.destroy_actor(a)

# Spawn the pawn and drive it tangentially (+Y) for the head-less proof.
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, PAWN_SPAWN, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 1.0, 0.0))

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_PAWN_SETUP pawn={PAWN_LABEL} spawn_x={PAWN_SPAWN.x:.1f} drive=+Y actors={labels}")
