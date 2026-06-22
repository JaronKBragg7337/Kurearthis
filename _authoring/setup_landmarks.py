"""Chunk T1 — surface landmarks (visual reference points for roaming).

Places a handful of distinct, radial-up-oriented pillar landmarks on the surface near
spawn (+X), at known tangential offsets, so the player can tell they are moving (Jaron
could roam indefinitely with no reference). Each pillar is the engine Cylinder, scaled
tall, oriented so its long axis = the LOCAL radial up at its surface point, base at the
surface radius. Landmarks are VISUAL-ONLY (NoCollision) so they cannot interfere with the
pawn's swept grounding, and are NOT "Planet"-tagged. Added to the playable scene + saved.

Self-verifies head-less: prints each landmark's distance-from-center and (actor up · local
radial) — placement is correct when dist ≈ R + height/2 and up·radial ≈ 1.

  python _authoring/ue_remote.py --file _authoring/setup_landmarks.py
"""

import math

import unreal

MAP_ASSET = "/Game/PlanetaryProof"
CYL_MESH = "/Engine/BasicShapes/Cylinder.Cylinder"
R = 637_100_000.0  # surface radius (cm); planet center at world origin

# (name, tangent dir (perpendicular to +X), arc distance cm, height m, width m)
LANDMARKS = [
    ("PlusY",  (0.0, 1.0, 0.0),   80_000.0,  400.0, 50.0),
    ("MinusY", (0.0, -1.0, 0.0),  120_000.0, 300.0, 40.0),
    ("PlusZ",  (0.0, 0.0, 1.0),   100_000.0, 500.0, 60.0),
    ("MinusZ", (0.0, 0.0, -1.0),  150_000.0, 350.0, 45.0),
    ("Far",    (0.0, 0.707, 0.707), 250_000.0, 600.0, 70.0),
]

level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mesh = unreal.EditorAssetLibrary.load_asset(CYL_MESH)

# Idempotent: drop any prior landmarks.
for a in list(actor_sub.get_all_level_actors()):
    if a.get_actor_label().startswith("Landmark_"):
        actor_sub.destroy_actor(a)

results = []
for name, t, arc_cm, h_m, w_m in LANDMARKS:
    tn = math.sqrt(t[0] * t[0] + t[1] * t[1] + t[2] * t[2])
    t = (t[0] / tn, t[1] / tn, t[2] / tn)
    theta = arc_cm / R
    c, s = math.cos(theta), math.sin(theta)
    d = (c, s * t[1], s * t[2])               # outward unit direction to the surface point
    h_cm = h_m * 100.0
    half = h_cm / 2.0
    center = unreal.Vector(d[0] * (R + half), d[1] * (R + half), d[2] * (R + half))
    rot = unreal.MathLibrary.make_rot_from_z(unreal.Vector(d[0], d[1], d[2]))

    lm = actor_sub.spawn_actor_from_class(unreal.StaticMeshActor, center, rot)
    lm.set_actor_label(f"Landmark_{name}")
    lm.static_mesh_component.set_static_mesh(mesh)
    # Engine cylinder is 100 cm (=1 m) per axis, so actor scale = size in metres.
    lm.set_actor_scale3d(unreal.Vector(w_m, w_m, h_m))
    lm.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    loc = lm.get_actor_location()
    dist = math.sqrt(loc.x * loc.x + loc.y * loc.y + loc.z * loc.z)
    up = lm.get_actor_up_vector()
    updot = up.x * d[0] + up.y * d[1] + up.z * d[2]
    results.append((name, dist, R + half, updot))

level_sub.save_current_level()

print("KUREARTHIS_LANDMARKS")
for name, dist, expect, updot in results:
    print(f"  {name}: dist={dist:.1f} expect={expect:.1f} (diff={dist-expect:.2f}) up_dot_radial={updot:.6f}")
labels = [a.get_actor_label() for a in actor_sub.get_all_level_actors()]
print("actors=", labels)
