"""Chunk T2a — one procedural displaced-mesh terrain tile; pawn grounds on the relief.

Places a single `AProcTerrainTile` (20 km, 400 m hills, deterministic Perlin fBm) tangent
to the sphere under spawn (+X), generates its mesh + collision, then drives the pawn +Y
across it. The pawn now ground-follows (snap up/down), so it should stay grounded the
whole way while its distance-from-center VARIES with the hills (it follows the terrain
height) — that is the T2a proof.

  python _authoring/run_physics_harness.py 30 --setup _authoring/setup_terrain_tile_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
TILE_LABEL = "ProcTerrainTile"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"
GRID_LABEL = "SurfaceTileGrid"
PATCH_LABEL = "LocalSurfacePatch"

SURFACE_R = 637_100_000.0
TILE_SIZE = 2_000_000.0     # 20 km
AMP = 40_000.0              # 400 m hills

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("ProcTerrainTile", "RadialGravityPawn", "FloatingOriginManager"):
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

# Clear prior ground/pawn/manager + any earlier proc tile.
for a in actors:
    if a.get_actor_label() in (GRID_LABEL, PATCH_LABEL, TILE_LABEL, "SweptGravityBody",
                               "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL) \
       or a.get_actor_label().startswith("Tile_"):
        actor_sub.destroy_actor(a)

# Terrain tile: tangent at +X, local Z = radial up.
tile_loc = unreal.Vector(SURFACE_R, 0.0, 0.0)
tile_rot = unreal.MathLibrary.make_rot_from_z(unreal.Vector(1.0, 0.0, 0.0))
tile = actor_sub.spawn_actor_from_class(unreal.ProcTerrainTile, tile_loc, tile_rot)
tile.set_actor_label(TILE_LABEL)
tile.set_editor_property("PlanetActor", planet)
tile.set_editor_property("SurfaceRadius", SURFACE_R)
tile.set_editor_property("TileSizeCm", TILE_SIZE)
tile.set_editor_property("HeightAmplitudeCm", AMP)
tile.set_editor_property("Resolution", 96)
tile.call_method("Generate")

# Pawn spawned 500 m up (above any 400 m hill) so it falls + grounds on the relief.
pawn_spawn = unreal.Vector(SURFACE_R + 50000.0, 0.0, 0.0)
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, pawn_spawn, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 1.0, 0.0))
pawn.set_editor_property("MoveSpeed", 25000.0)   # 250 m/s -> ~7.5 km over 30 s

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_TERRAIN_SETUP tile={TILE_SIZE/100000:.0f}km amp={AMP/100:.0f}m actors={labels}")
