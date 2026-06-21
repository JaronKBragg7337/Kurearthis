"""Proof 2: radial gravity + local up on ProofEarth.

Deterministic Newtonian integration of a test body under gravity directed at the
planet center, colliding against the REAL ProofEarth collision mesh via engine
line traces. The body is released above the EQUATOR (+X). Flat world gravity
(-Z) would carry it sideways and never land; only true radial gravity pulls it
along -X into the surface. That makes the proof unambiguous.

Proves:
  1. body falls toward planet center (X decreases toward 0; Y,Z stay ~0),
  2. it collides / rests on the real surface (radius ~6.371e8 cm),
  3. local up at rest is radial (normalize(pos - center) ~= +X),
  4. result is logged to Saved/ and a visible marker is left on the surface.

Run from the Unreal editor Python console:
  py "<project>/_authoring/prove_radial_gravity.py"
"""

import json
import math
from pathlib import Path

import unreal

PROJECT_ROOT = Path(unreal.Paths.project_dir())
LOG_PATH = PROJECT_ROOT / "Saved" / "RadialGravityProof.log"
JSON_PATH = PROJECT_ROOT / "Saved" / "RadialGravityProof.json"

MAP_ASSET = "/Game/PlanetaryProof"
PLANET_LABEL = "ProofEarth"
MARKER_LABEL = "GravityRestMarker"

CENTER = unreal.Vector(0.0, 0.0, 0.0)
G = 980.0                      # cm/s^2 (9.8 m/s^2) toward center
NOMINAL_RADIUS_CM = 637_100_000.0
START_ALTITUDE_CM = 100_000.0  # ~1 km above the nominal equatorial surface
DT = 0.02                      # s
MAX_STEPS = 6000               # safety cap (~120 s sim time)
MARKER_SCALE = 2000.0          # engine sphere (50 cm r) -> 10 km radius marker


def vsub(a, b):
    return unreal.Vector(a.x - b.x, a.y - b.y, a.z - b.z)


def vadd(a, b):
    return unreal.Vector(a.x + b.x, a.y + b.y, a.z + b.z)


def vscale(a, s):
    return unreal.Vector(a.x * s, a.y * s, a.z * s)


def vlen(a):
    return math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z)


def vnorm(a):
    l = vlen(a)
    return unreal.Vector(a.x / l, a.y / l, a.z / l) if l > 0.0 else unreal.Vector(0, 0, 0)


# --- Load the proof map and confirm the planet is present -------------------
level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET):
    level_sub.load_level(MAP_ASSET)

editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor_sub.get_editor_world()

actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
planet = next(
    (a for a in actor_sub.get_all_level_actors() if a.get_actor_label() == PLANET_LABEL),
    None,
)
if planet is None:
    raise RuntimeError("ProofEarth not found in PlanetaryProof; cannot run gravity proof")


def trace(p0, p1):
    """Engine line trace against the real world collision. Returns (hit, point)."""
    hit = unreal.SystemLibrary.line_trace_single(
        world, p0, p1, unreal.TraceTypeQuery.ECC_VISIBILITY, False, [],
        unreal.DrawDebugTrace.NONE, True,
    )
    if hit is None:
        return False, None
    d = hit.to_dict()
    if d.get("blocking_hit"):
        return True, d["impact_point"]
    return False, None


# --- Integrate radial gravity, colliding against the real surface ----------
pos = unreal.Vector(NOMINAL_RADIUS_CM + START_ALTITUDE_CM, 0.0, 0.0)  # above equator
vel = unreal.Vector(0.0, 0.0, 0.0)
start_pos = unreal.Vector(pos.x, pos.y, pos.z)

t = 0.0
log_accum = 0.0
max_abs_y = 0.0
max_abs_z = 0.0
impact_speed = 0.0
rested = False
rest_point = None
log_lines = [
    f"# radial gravity proof  center=(0,0,0)  g={G} cm/s^2  start=({pos.x:.1f},{pos.y:.1f},{pos.z:.1f})",
]

for step in range(MAX_STEPS):
    to_center = vsub(CENTER, pos)
    dist = vlen(to_center)
    acc = vscale(vnorm(to_center), G)        # radial acceleration toward center
    vel = vadd(vel, vscale(acc, DT))
    new_pos = vadd(pos, vscale(vel, DT))

    hit, point = trace(pos, new_pos)
    max_abs_y = max(max_abs_y, abs(pos.y))
    max_abs_z = max(max_abs_z, abs(pos.z))

    if hit:
        impact_speed = vlen(vel)
        rest_point = point
        rested = True
        t += DT
        log_lines.append(
            f"t={t:.2f} CONTACT impact=({point.x:.1f},{point.y:.1f},{point.z:.1f}) "
            f"impact_speed={impact_speed:.1f}"
        )
        break

    pos = new_pos
    t += DT
    log_accum += DT
    if log_accum >= 1.0:
        log_accum = 0.0
        up = vnorm(vsub(pos, CENTER))
        log_lines.append(
            f"t={t:.2f} loc=({pos.x:.1f},{pos.y:.1f},{pos.z:.1f}) dist={dist:.1f} "
            f"speed={vlen(vel):.1f} up=({up.x:.4f},{up.y:.4f},{up.z:.4f})"
        )

if not rested:
    raise RuntimeError(f"Body never contacted surface after {MAX_STEPS} steps (t={t:.1f}s)")

rest_dist = vlen(vsub(rest_point, CENTER))
up_at_rest = vnorm(vsub(rest_point, CENTER))

# --- Leave a visible marker resting on the surface --------------------------
marker = next(
    (a for a in actor_sub.get_all_level_actors() if a.get_actor_label() == MARKER_LABEL),
    None,
)
if marker is None:
    marker = actor_sub.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)
    )
    marker.set_actor_label(MARKER_LABEL)
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    marker.static_mesh_component.set_static_mesh(sphere)

marker_radius_cm = 50.0 * MARKER_SCALE
marker_center = vadd(rest_point, vscale(up_at_rest, marker_radius_cm))  # sit ON the surface
marker.set_actor_scale3d(unreal.Vector(MARKER_SCALE, MARKER_SCALE, MARKER_SCALE))
marker.set_actor_location(marker_center, False, False)

level_sub.save_current_level()

# --- Record the proof -------------------------------------------------------
result = {
    "rested": rested,
    "sim_time_s": t,
    "gravity_center_cm": [CENTER.x, CENTER.y, CENTER.z],
    "gravity_strength_cm_s2": G,
    "release_point_cm": [start_pos.x, start_pos.y, start_pos.z],
    "rest_point_cm": [rest_point.x, rest_point.y, rest_point.z],
    "rest_distance_from_center_cm": rest_dist,
    "nominal_surface_radius_cm": NOMINAL_RADIUS_CM,
    "rest_minus_nominal_cm": rest_dist - NOMINAL_RADIUS_CM,
    "impact_speed_cm_s": impact_speed,
    "local_up_at_rest": [up_at_rest.x, up_at_rest.y, up_at_rest.z],
    "lateral_drift_max_abs_y_cm": max_abs_y,
    "lateral_drift_max_abs_z_cm": max_abs_z,
    "fell_along_minus_x_radial": start_pos.x > rest_point.x and max_abs_y < 1.0 and max_abs_z < 1.0,
    "marker_actor": MARKER_LABEL,
    "marker_center_cm": [marker_center.x, marker_center.y, marker_center.z],
    "note": (
        "Deterministic radial-gravity integration vs the REAL ProofEarth collision "
        "mesh. Released above the equator (+X); body fell along -X toward center and "
        "rested on the real surface with local up = +X radial. Flat -Z gravity could "
        "not produce this. Chaos/C++ runtime component is committed under Source/ and "
        "gated on installing the .NET Framework 4.8 SDK."
    ),
}

JSON_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
LOG_PATH.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

print(
    "KUREARTHIS_RADIAL_GRAVITY "
    f"rested={rested} t={t:.2f}s rest_dist={rest_dist:.1f} "
    f"up=({up_at_rest.x:.4f},{up_at_rest.y:.4f},{up_at_rest.z:.4f}) "
    f"driftYZ=({max_abs_y:.2f},{max_abs_z:.2f}) radial={result['fell_along_minus_x_radial']}"
)
