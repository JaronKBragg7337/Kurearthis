"""Spawn the C++ Chaos radial-gravity test body in PlanetaryProof, ready for PIE.

Places ARadialGravityTestBody ~1 km above the equator (+X). When PIE/Simulate
runs, the C++ disables flat -Z gravity, simulates physics, applies radial
acceleration toward the planet center each tick, and writes the rest state to
Saved/RadialGravityProof.json.

Run from the editor console:
  py "<project>/_authoring/spawn_chaos_gravity_body.py"
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
BODY_LABEL = "ChaosGravityBody"
SPAWN = unreal.Vector(637_200_000.0, 0.0, 0.0)  # ~1 km above the equatorial surface

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

if not hasattr(unreal, "RadialGravityTestBody"):
    raise RuntimeError("unreal.RadialGravityTestBody not found - C++ module did not load")

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# Idempotent: remove any prior Chaos body before spawning a fresh one.
for a in list(actor_sub.get_all_level_actors()):
    if a.get_actor_label() == BODY_LABEL:
        actor_sub.destroy_actor(a)

body = actor_sub.spawn_actor_from_class(
    unreal.RadialGravityTestBody, SPAWN, unreal.Rotator(0.0, 0.0, 0.0)
)
body.set_actor_label(BODY_LABEL)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_CHAOS_SPAWN label={BODY_LABEL} at={SPAWN} actors={labels}")
