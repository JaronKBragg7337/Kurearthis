"""Directly test AProcTerrainTile.SampleHeight at known water vs land points (T2d-3)."""
import math

import unreal

R = 637_100_000.0
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
planet = next(a for a in actor_sub.get_all_level_actors() if a.get_actor_label() == "ProofEarth")
if "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))

tile = actor_sub.spawn_actor_from_class(unreal.ProcTerrainTile, unreal.Vector(R, 0.0, 0.0), unreal.Rotator())
tile.set_editor_property("PlanetActor", planet)
tile.set_editor_property("SurfaceRadius", R)


def wp(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    d = (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
    return unreal.Vector(d[0] * R, d[1] * R, d[2] * R)


print("SAMPLEHEIGHT_TEST (water_level should be ~20800 cm = 208 m):")
for name, lat, lon in [("water_yamuna", 28.66, 77.24), ("land_west", 28.66, 77.21),
                       ("land_far", 28.55, 77.10), ("outside_bbox_pacific", 0.0, 0.0)]:
    h = tile.sample_height(wp(lat, lon))
    print(f"  {name} ({lat},{lon}): {h:.1f} cm = {h/100:.1f} m")

actor_sub.destroy_actor(tile)
