"""T2d-2 proof: pawn grounds on REAL Delhi terrain (from the baked DEM).

Spawns the streamed terrain grid + pawn at Delhi's planet coordinates (lon=77.2090,
lat=28.6139; planet frame = geographic). The proc tiles' SampleHeight consults
Content/RealDEM/dem_active.bin where (lon,lat) is in the Delhi bbox, so the pawn walks
REAL Delhi elevations (~76-303 m, mostly ~200-250 m) rather than procedural 0-400 m hills.

  python _authoring/run_physics_harness.py 30 --setup _authoring/setup_realdem_proof.py
"""

import math

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"
GRID_LABEL = "SurfaceTileGrid"
PATCH_LABEL = "LocalSurfacePatch"

SURFACE_R = 637_100_000.0
DELHI_LAT, DELHI_LON = 28.6139, 77.2090

lat = math.radians(DELHI_LAT)
lon = math.radians(DELHI_LON)
d = (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("ProcTerrainTile", "SurfaceTileManager", "RadialGravityPawn", "FloatingOriginManager"):
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

for a in actors:
    if a.get_actor_label() in (GRID_LABEL, PATCH_LABEL, "ProcTerrainTile", "SweptGravityBody",
                               "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL) \
       or a.get_actor_label().startswith("Tile_"):
        actor_sub.destroy_actor(a)

# Pawn spawned ~500 m above Delhi (initial big snap lands it on the real terrain).
spawn = unreal.Vector(d[0] * (SURFACE_R + 50000.0), d[1] * (SURFACE_R + 50000.0), d[2] * (SURFACE_R + 50000.0))
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, spawn, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 1.0, 0.0))
pawn.set_editor_property("MoveSpeed", 25000.0)

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
print(f"KUREARTHIS_REALDEM_SETUP pawn at Delhi (lon={DELHI_LON}, lat={DELHI_LAT}) dir={d} actors={labels}")
