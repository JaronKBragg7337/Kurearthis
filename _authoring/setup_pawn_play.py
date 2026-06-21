"""Leave PlanetaryProof in a PLAYABLE state so Jaron can walk the pawn (proof #2 feel).

Configures and SAVES the scene: RadialGravityPawn (DebugDrive OFF so input drives it;
AutoPossessPlayer=Player0 in the class possesses it on Play), a STREAMED grid of fixed
surface tiles (ASurfaceTileManager — seamless infinite roaming, 2i), the visual-only
planet, a DirectionalLight + SkyLight so the surface is visible (the proof map is
otherwise unlit), and the floating-origin manager.

After this runs, open `Content/PlanetaryProof` in the editor and press Play (or
Alt+P). Controls: W/A/S/D move, mouse looks. Esc/Shift+F1 to release the mouse.

  python _authoring/ue_remote.py --file _authoring/setup_pawn_play.py
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
PATCH_LABEL = "LocalSurfacePatch"
GRID_LABEL = "SurfaceTileGrid"
PAWN_LABEL = "RadialGravityPawn"
MANAGER_LABEL = "FloatingOriginManager"
SUN_LABEL = "SurfaceSun"
SKY_LABEL = "SurfaceSky"

SURFACE_R = 637_100_000.0
CAPSULE_HALF = 100.0
SPAWN_GAP = 200.0
PAWN_SPAWN = unreal.Vector(SURFACE_R + CAPSULE_HALF + SPAWN_GAP, 0.0, 0.0)

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("RadialGravityPawn", "SurfaceTileManager"):
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

# Replace any prior patch (static/follower), streamed tiles, grid + dynamic test actors.
for a in actors:
    if a.get_actor_label() in (PATCH_LABEL, GRID_LABEL, "SweptGravityBody",
                               "ChaosGravityBody", PAWN_LABEL, MANAGER_LABEL) \
       or a.get_actor_label().startswith("Tile_"):
        actor_sub.destroy_actor(a)

pawn = actor_sub.spawn_actor_from_class(unreal.RadialGravityPawn, PAWN_SPAWN, unreal.Rotator())
pawn.set_actor_label(PAWN_LABEL)
pawn.tags.append(unreal.Name("Focus"))
pawn.set_editor_property("DebugDriveWorldDir", unreal.Vector(0.0, 0.0, 0.0))  # input-driven

# Seamless infinite roaming: a STREAMED 3x3 grid of FIXED 5 km tiles centered on the
# pawn. Each tile stays put in the world (good feel — the ground doesn't glue to the
# player like the single follower tile did, 2h), while tiles load ahead / unload behind
# as the pawn crosses boundaries, so the ground never runs out. Proven head-less in 2i
# (grounded across 4 crossings, 21 spawned / 12 unloaded, 9 active).
grid = actor_sub.spawn_actor_from_class(
    unreal.SurfaceTileManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
grid.set_actor_label(GRID_LABEL)
grid.set_editor_property("Focus", pawn)
grid.set_editor_property("PlanetActor", planet)

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", pawn)

# Lighting so the surface is visible (sun from the +X sky; black space beyond).
sun = by_label.get(SUN_LABEL)
if sun is None:
    sun = actor_sub.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(-30.0, 180.0, 0.0))
    sun.set_actor_label(SUN_LABEL)
sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)  # dynamic; no lighting build
sun.light_component.set_intensity(10.0)

sky = by_label.get(SKY_LABEL)
if sky is None:
    sky = actor_sub.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
    sky.set_actor_label(SKY_LABEL)
sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky.light_component.set_intensity(0.6)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_PAWN_PLAY pawn={PAWN_LABEL} input-driven, lit; press Play. actors={labels}")
