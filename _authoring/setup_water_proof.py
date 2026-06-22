"""T2d-3 proof: drive the pawn EAST across the Yamuna at Delhi; water reads flat.

Spawns the pawn west of the Yamuna (lat 28.66, lon 77.21) and drives it east (+lon) so it
crosses the river channel (~lon 77.24). Expect the height profile to show varying DEM land
then a FLAT segment at the water level (~208 m) over the river, then land — i.e. OSM water
flattening works in-engine. Pawn stays grounded throughout.

  python _authoring/run_physics_harness.py 30 --setup _authoring/setup_water_proof.py
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
LAT, LON = 28.66, 77.21          # just west of the Yamuna channel (~77.24)

lat_r = math.radians(LAT)
lon_r = math.radians(LON)
d = (math.cos(lat_r) * math.cos(lon_r), math.cos(lat_r) * math.sin(lon_r), math.sin(lat_r))
east = (-math.sin(lon_r), math.cos(lon_r), 0.0)   # tangent east at this lon

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())
by_label = {a.get_actor_label(): a for a in actors}
planet = by_label.get(PLANET_LABEL)
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))
planet.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

for a in actors:
    if a.get_actor_label() in (GRID_LABEL, PATCH_LABEL, "ProcTerrainTile", "SweptGravityBody",
                               "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL) \
       or a.get_actor_label().startswith("Tile_"):
        actor_sub.destroy_actor(a)

spawn = unreal.Vector(d[0] * (SURFACE_R + 50000.0), d[1] * (SURFACE_R + 50000.0), d[2] * (SURFACE_R + 50000.0))
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, spawn, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(east[0], east[1], east[2]))
pawn.set_editor_property("MoveSpeed", 15000.0)   # 150 m/s -> ~4.5 km east over 30 s

grid = actor_sub.spawn_actor_from_class(unreal.SurfaceTileManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
grid.set_actor_label(GRID_LABEL)
grid.set_editor_property("Focus", pawn)
grid.set_editor_property("PlanetActor", planet)

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

level_sub.save_current_level()
print(f"KUREARTHIS_WATER_SETUP pawn at Delhi ({LAT},{LON}) driving east across the Yamuna")
