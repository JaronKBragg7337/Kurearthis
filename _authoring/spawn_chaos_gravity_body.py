"""Set up the floating-origin radial-gravity proof in PlanetaryProof.

- Tags ProofEarth with "Planet" so the gravity body reads the center dynamically.
- Spawns ARadialGravityTestBody ~1 km above the equator (+X).
- Spawns AFloatingOriginManager to keep the body near the world origin via world
  origin rebasing, so real Chaos physics runs in a precise frame.

When Simulate runs, the manager recenters the world on the body and the body
should fall in ~14 s and rest on the real surface.

Run from the editor console:
  py "<project>/_authoring/spawn_chaos_gravity_body.py"
"""

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
BODY_LABEL = "ChaosGravityBody"
MANAGER_LABEL = "FloatingOriginManager"
SPAWN = unreal.Vector(637_200_000.0, 0.0, 0.0)  # ~1 km above the equatorial surface

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

for cls in ("RadialGravityTestBody", "FloatingOriginManager"):
    if not hasattr(unreal, cls):
        raise RuntimeError(f"unreal.{cls} not found - C++ module did not load/compile")

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_sub.get_all_level_actors())

# Tag the planet so the gravity body finds its center.
planet = next((a for a in actors if a.get_actor_label() == PLANET_LABEL), None)
if planet is None:
    raise RuntimeError("ProofEarth not found")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))

# Idempotent: clear prior test actors.
for a in actors:
    if a.get_actor_label() in (BODY_LABEL, MANAGER_LABEL):
        actor_sub.destroy_actor(a)

body = actor_sub.spawn_actor_from_class(unreal.RadialGravityTestBody, SPAWN, unreal.Rotator())
body.set_actor_label(BODY_LABEL)

manager = actor_sub.spawn_actor_from_class(
    unreal.FloatingOriginManager, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator()
)
manager.set_actor_label(MANAGER_LABEL)
manager.set_editor_property("Focus", body)

level_sub.save_current_level()

labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print(f"KUREARTHIS_FLOATING_SETUP body={BODY_LABEL} manager={MANAGER_LABEL} planet_tagged=True actors={labels}")
