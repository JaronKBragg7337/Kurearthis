"""Dump the project's Chaos/physics settings, head-less, to explain physics behaviour.

Reads UPhysicsSettings (and the body's physics-relevant properties) so a build
session can reason about the Proof 2d finding (a Chaos `AddForce(bAccelChange)`
body fell ~100x too slowly even near the origin) without guessing. Writes
Saved/PhysicsSettings.json and prints the key values.

  python _authoring/ue_remote.py --file _authoring/dump_physics_settings.py
"""

import json
from pathlib import Path

import unreal

ps = unreal.PhysicsSettings.get_default_object()

# Curated UPhysicsSettings properties; guard each so one missing name never aborts.
WANTED = [
    "default_gravity_z",
    "default_terminal_velocity",
    "default_fluid_friction",
    "b_substepping",
    "b_substepping_async",
    "max_substep_delta_time",
    "max_substeps",
    "max_physics_delta_time",
    "b_enable_enhanced_determinism",
    "b_simulate_skeletal_mesh_on_dedicated_server",
    "min_delta_velocity_for_hit_units",
    "solver_type",
]

settings = {}
for name in WANTED:
    try:
        settings[name] = repr(ps.get_editor_property(name))
    except Exception as exc:  # property not present in this engine build
        settings[name] = f"<n/a: {exc}>"

# The Chaos sub-settings struct, if exposed.
try:
    chaos = ps.get_editor_property("chaos_settings")
    settings["chaos_settings"] = repr(chaos)
except Exception as exc:
    settings["chaos_settings"] = f"<n/a: {exc}>"

# The test body's physics-relevant defaults (mass override, damping, CCD).
body_info = {}
try:
    cdo = unreal.RadialGravityTestBody.get_default_object()
    mesh = cdo.get_editor_property("mesh")
    for name in ("linear_damping", "angular_damping", "b_use_ccd",
                 "body_mass", "mass_in_kg"):
        try:
            body_info[name] = repr(mesh.get_editor_property(name))
        except Exception as exc:
            body_info[name] = f"<n/a: {exc}>"
except Exception as exc:
    body_info["error"] = repr(exc)

out = {"physics_settings": settings, "test_body_mesh": body_info}

OUT_PATH = Path(unreal.Paths.project_saved_dir()) / "PhysicsSettings.json"
OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")

print("KUREARTHIS_PHYSICS_SETTINGS")
print(f"  substepping={settings.get('b_substepping')} async={settings.get('b_substepping_async')}")
print(f"  max_substep_delta_time={settings.get('max_substep_delta_time')} max_substeps={settings.get('max_substeps')}")
print(f"  max_physics_delta_time={settings.get('max_physics_delta_time')}")
print(f"  default_gravity_z={settings.get('default_gravity_z')} terminal_velocity={settings.get('default_terminal_velocity')}")
print(f"  wrote {OUT_PATH}")
