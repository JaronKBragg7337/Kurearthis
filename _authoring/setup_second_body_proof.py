"""Proof 4 (harness setup) — a second body coexisting at distance.

Adds `ProofMoon` (the in-house planet mesh scaled to a 1,737 km moon) at the real Moon
distance (384,400 km = 3.844e10 cm) along +Y from `ProofEarth`. The moon is visual-only
(NoCollision) and is NOT "Planet"-tagged, so the pawn/tiles keep using ProofEarth as the
gravity center. Then it sets the pawn to the head-less roam drive (+Y, 500 m/s) over the
streamed tile grid, so the harness verifies the pawn STILL stands/roams with a second
body present (i.e. the second body does not break the first body's frame/gravity).

  python _authoring/run_physics_harness.py 40 --setup _authoring/setup_second_body_proof.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
MOON_LABEL = "ProofMoon"
PATCH_LABEL = "LocalSurfacePatch"
GRID_LABEL = "SurfaceTileGrid"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"

MOON_MESH = "/Game/Planetary/SM_ProofPlanet_Base"
MOON_RADIUS_KM = 1737.0                 # mesh base radius is 1 km, so scale = radius in km
MOON_DISTANCE_CM = 3.844e10             # 384,400 km — real Moon distance

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

# Replace prior patch / grid / tiles / dynamic test actors / pawn / manager / moon.
for a in actors:
    if a.get_actor_label() in (PATCH_LABEL, GRID_LABEL, "SweptGravityBody",
                               "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL, MOON_LABEL) \
       or a.get_actor_label().startswith("Tile_"):
        actor_sub.destroy_actor(a)

# Second body: a moon at distance. Visual-only, NOT "Planet"-tagged.
moon = actor_sub.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(0.0, MOON_DISTANCE_CM, 0.0), unreal.Rotator())
moon.set_actor_label(MOON_LABEL)
moon_mesh = unreal.EditorAssetLibrary.load_asset(MOON_MESH)
moon.static_mesh_component.set_static_mesh(moon_mesh)
moon.set_actor_scale3d(unreal.Vector(MOON_RADIUS_KM, MOON_RADIUS_KM, MOON_RADIUS_KM))
moon.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

# Pawn driven +Y fast over the streamed grid (same as the 2i roam proof).
pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, PAWN_SPAWN, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 1.0, 0.0))
pawn.set_editor_property("MoveSpeed", 50000.0)

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
print(f"KUREARTHIS_SECONDBODY_SETUP moon@{MOON_DISTANCE_CM:.3e}cm r={MOON_RADIUS_KM}km actors={labels}")
