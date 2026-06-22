"""Set up Proof 2i — seamless roaming over a STREAMED grid of FIXED tiles.

`ASurfaceTileManager` keeps a 3x3 block of fixed tiles in world space centered on the
pawn's cell; as the pawn crosses tile boundaries it spawns tiles ahead and destroys
tiles behind. Unlike the single follower patch (2h), each tile stays put — so the
ground never moves under the player (good feel) AND never runs out.

Drives the pawn +Y at 500 m/s. Over ~40 s that is ~20 km = 4 tiles (5 km each), so the
pawn crosses several tile boundaries and the grid must stream. Verify:
  - Saved/RadialGravityProof.json: grounded=true, height_above_surface ~ 0, up_dot ~ 1,
    tangential_traveled ~ MoveSpeed * time  (pawn stayed grounded across boundaries)
  - Saved/TileGrid.json: active_tiles == 9, total_spawned > 9, total_destroyed > 0,
    current_cell advanced  (tiles streamed in ahead / out behind)

  python _authoring/run_physics_harness.py 40 --setup _authoring/setup_tile_grid_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PATCH_LABEL = "LocalSurfacePatch"
GRID_LABEL = "SurfaceTileGrid"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"

SURFACE_R = 637_100_000.0
CAPSULE_HALF = 100.0
PAWN_SPAWN = unreal.Vector(SURFACE_R + CAPSULE_HALF + 200.0, 0.0, 0.0)

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("SurfacePatch", "SurfaceTileManager", "RadialGravityPawn", "FloatingOriginManager"):
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

# Replace any prior patch / grid / dynamic test actors / pawn / manager.
for a in actors:
    if a.get_actor_label() in (PATCH_LABEL, GRID_LABEL, "ProcTerrainTile", "SweptGravityBody",
                               "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL) \
       or a.get_actor_label().startswith("Tile_"):
        actor_sub.destroy_actor(a)

# Pawn, driven +Y fast so it crosses several 5 km tiles.
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, PAWN_SPAWN, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 1.0, 0.0))
pawn.set_editor_property("MoveSpeed", 50000.0)

# Streamed tile grid (3x3 of 5 km fixed tiles), centered on the pawn.
grid = actor_sub.spawn_actor_from_class(unreal.SurfaceTileManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
grid.set_actor_label(GRID_LABEL)
grid.set_editor_property("Focus", pawn)
grid.set_editor_property("PlanetActor", planet)

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_TILEGRID_SETUP grid(3x3 fixed) + pawn(+Y, 500 m/s) actors={labels}")
