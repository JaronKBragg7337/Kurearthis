"""Proof 2, chunk 1: give ProofEarth usable surface collision and verify it.

- Sets the planet mesh body setup to Use Complex Collision As Simple so the
  triangle sphere becomes walkable/queryable collision (no pawn added here).
- Ensures the live ProofEarth component blocks queries.
- Verifies with a downward radial line trace from above the north pole and
  records the measured hit location and radius error.

Run from the Unreal editor Python console:
  py "<project>/_authoring/add_verify_surface_collision.py"
"""

import json
import math
from pathlib import Path

import unreal

PROJECT_ROOT = Path(unreal.Paths.project_dir())
OUT_PATH = PROJECT_ROOT / "Saved" / "CollisionProofAudit.json"

MESH_ASSET = "/Game/Planetary/SM_ProofPlanet_Base.SM_ProofPlanet_Base"
MAP_ASSET = "/Game/PlanetaryProof"
BODY_LABEL = "ProofEarth"

TARGET_RADIUS_CM = 637_100_000.0          # documented proof constant
KNOWN_COMPUTED_RADIUS_CM = 637_100_105.034  # measured in proof 1
TRACE_START_ALTITUDE_CM = 50_000_000.0     # 500 km above the pole

# --- 1. Make the planet mesh collision usable (complex-as-simple) -----------
mesh = unreal.EditorAssetLibrary.load_asset(MESH_ASSET)
if mesh is None:
    raise RuntimeError(f"Could not load mesh {MESH_ASSET}")

body_setup = mesh.get_editor_property("body_setup")
if body_setup is None:
    raise RuntimeError("Mesh has no body setup; cannot configure collision")

body_setup.set_editor_property(
    "collision_trace_flag",
    unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE,
)
trace_flag = str(body_setup.get_editor_property("collision_trace_flag"))
unreal.EditorAssetLibrary.save_asset(MESH_ASSET, only_if_is_dirty=False)

# --- 2. Ensure the live ProofEarth component blocks queries -----------------
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
body = next(
    (a for a in actor_sub.get_all_level_actors() if a.get_actor_label() == BODY_LABEL),
    None,
)
if body is None:
    raise RuntimeError(f"{BODY_LABEL} not found in live scene")

comp = body.static_mesh_component
comp.set_collision_profile_name("BlockAll")
comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)

# Persist the actor's collision so it survives a reopen.
level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level_sub.save_current_level():
    raise RuntimeError("PlanetaryProof level did not save after collision change")

# --- 3. Verify with a radial north-pole line trace --------------------------
editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor_sub.get_editor_world()

start = unreal.Vector(0.0, 0.0, TARGET_RADIUS_CM + TRACE_START_ALTITUDE_CM)
end = unreal.Vector(0.0, 0.0, 0.0)

res = unreal.SystemLibrary.line_trace_single(
    world,
    start,
    end,
    unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,  # Visibility channel
    False,                                    # simple trace -> proves walkable collision
    [],
    unreal.DrawDebugTrace.NONE,
    True,
)

hit = res[1] if isinstance(res, tuple) else res
hd = hit.to_dict()
blocking = bool(hd.get("blocking_hit", False))

audit = {
    "mesh_asset": MESH_ASSET,
    "collision_trace_flag": trace_flag,
    "component_collision_enabled": str(comp.get_collision_enabled()),
    "component_collision_profile": str(comp.get_collision_profile_name()),
    "trace_start_cm": [start.x, start.y, start.z],
    "trace_end_cm": [end.x, end.y, end.z],
    "trace_simple_blocking_hit": blocking,
}

if blocking:
    ip = hd["impact_point"]
    hit_loc = hd["location"]
    hit_actor = hd.get("hit_actor")
    dist_from_center = math.sqrt(ip.x * ip.x + ip.y * ip.y + ip.z * ip.z)
    audit.update(
        {
            "hit_actor": str(hit_actor.get_name()) if hit_actor else None,
            "impact_point_cm": [float(ip.x), float(ip.y), float(ip.z)],
            "impact_normal": [
                float(hd["impact_normal"].x),
                float(hd["impact_normal"].y),
                float(hd["impact_normal"].z),
            ],
            "hit_location_cm": [float(hit_loc.x), float(hit_loc.y), float(hit_loc.z)],
            "hit_distance_from_center_cm": dist_from_center,
            "error_vs_target_radius_cm": abs(dist_from_center - TARGET_RADIUS_CM),
            "error_vs_known_mesh_radius_cm": abs(dist_from_center - KNOWN_COMPUTED_RADIUS_CM),
            "precision_note": (
                "impact_point/location are float32; at ~6.37e8 cm the ULP is "
                "tens of cm, so sub-meter-to-few-meter scatter is expected"
            ),
        }
    )

OUT_PATH.write_text(json.dumps(audit, indent=2), encoding="utf-8")

print(
    "KUREARTHIS_COLLISION_PROOF "
    f"flag={trace_flag} blocking={blocking} "
    + (
        f"hit_z={audit.get('impact_point_cm', ['?','?','?'])[2]} "
        f"dist_from_center={audit.get('hit_distance_from_center_cm','?')} "
        f"err_vs_target={audit.get('error_vs_target_radius_cm','?')}"
        if blocking
        else "NO_HIT"
    )
)
