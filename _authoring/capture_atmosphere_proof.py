"""Capture the surface→atmosphere→space transition at several altitudes (head-less).

Renders off-screen SceneCapture2D shots from increasing altitude so the atmosphere is
seen thinning into black:
  - atmo_surface: ~300 m above the +X surface, looking along the horizon
  - atmo_low:     low orbit, planet limb + surface with the atmosphere band
  - atmo_space:   out in space, whole planet with a thin atmosphere ring against black

Prints `ATMO_CAPS <png> | <png> | ...`; the agent reads the PNGs as visual evidence.

  python _authoring/ue_remote.py --file _authoring/capture_atmosphere_proof.py
"""

import time
from pathlib import Path

import unreal

R = 637_100_000.0  # ProofEarth surface radius (cm); planet center at world origin
W, H = 1600, 900

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = ues.get_editor_world()
ml = unreal.MathLibrary


def look(cam, tgt):
    return ml.find_look_at_rotation(unreal.Vector(*cam), unreal.Vector(*tgt))


shots = [
    ("atmo_surface", (R + 30000.0, 0.0, 0.0), (R + 30000.0, 1.0e8, 2.0e7)),
    ("atmo_low",     (R * 1.05, 0.0, R * 0.30), (0.0, 0.0, 0.0)),
    ("atmo_space",   (R * 0.40, 0.0, R * 1.70), (0.0, 0.0, 0.0)),
]

out_dir = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
out_dir.mkdir(parents=True, exist_ok=True)
rt = unreal.RenderingLibrary.create_render_target2d(
    world, W, H, unreal.TextureRenderTargetFormat.RTF_RGBA8)

results = []
for name, cam, tgt in shots:
    cap = actor_sub.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*cam), look(cam, tgt))
    try:
        comp = cap.capture_component2d
        comp.set_editor_property("texture_target", rt)
        comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        comp.set_editor_property("max_view_distance_override", 5.0e9)
        comp.capture_scene()
        fn = f"{name}_{time.strftime('%H%M%S')}.png"
        unreal.RenderingLibrary.export_render_target(world, rt, str(out_dir), fn)
        results.append(str((out_dir / fn).resolve()))
    finally:
        actor_sub.destroy_actor(cap)

print("ATMO_CAPS " + " | ".join(results))
