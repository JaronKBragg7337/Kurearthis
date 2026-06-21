"""Set up Proof 2h — the pawn roams far past the old patch edge on a FOLLOWER patch.

`ASurfacePatch` re-centers under the pawn each tick, so the pawn should stay grounded
no matter how far it walks. Drives the pawn +Y at high speed for ~20 s (~10 km, 4x the
old 2.5 km patch half-width). If it stays grounded the whole way (height_above_surface
~ 0) the follower works.

  python _authoring/run_physics_harness.py 20 --setup _authoring/setup_pawn_roam_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PATCH_LABEL = "LocalSurfacePatch"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"

SURFACE_R = 637_100_000.0
CAPSULE_HALF = 100.0
PAWN_SPAWN = unreal.Vector(SURFACE_R + CAPSULE_HALF + 200.0, 0.0, 0.0)

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("SurfacePatch", "RadialGravityPawn", "FloatingOriginManager"):
    if not hasattr(unreal, cls):
        raise RuntimeError(f"unreal.{cls} not found - C++ module did not compile/reload")

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())
by_label = {a.get_actor_label(): a for a in actors}

planet = by_label.get(PLANET_LABEL)
if planet is None:
    raise RuntimeError("ProofEarth not found")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))
planet.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

# Replace any prior patch (static StaticMeshActor or follower) + dynamic test actors.
for a in actors:
    if a.get_actor_label() in (PATCH_LABEL, "SweptGravityBody", "ChaosGravityBody",
                               PAWN_LABEL, MANAGER_LABEL):
        actor_sub.destroy_actor(a)

# Follower patch.
patch = actor_sub.spawn_actor_from_class(unreal.SurfacePatch, unreal.Vector(SURFACE_R, 0.0, 0.0), unreal.Rotator())
patch.set_actor_label(PATCH_LABEL)
patch.set_actor_scale3d(unreal.Vector(200.0, 5000.0, 5000.0))

# Pawn, driven +Y fast so it covers ~10 km in 20 s.
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, PAWN_SPAWN, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 1.0, 0.0))
pawn.set_editor_property("MoveSpeed", 50000.0)

patch.set_editor_property("Focus", pawn)

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_ROAM_SETUP follower patch + pawn(+Y, 500 m/s) actors={labels}")
