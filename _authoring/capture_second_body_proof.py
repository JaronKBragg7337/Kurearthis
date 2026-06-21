"""Proof 4 captures — the first body still renders, and the second body coexists.

  p4_earth_surface : from the +X surface — ProofEarth + atmosphere still render fine.
  p4_earthrise     : from near ProofMoon looking back at Earth — the second body in the
                     foreground, Earth as a distant body (both coexist in one frame).

Prints `P4_CAPS <png> | <png>`; the agent reads the PNGs.

  python _authoring/ue_remote.py --file _authoring/capture_second_body_proof.py
"""

import time
from pathlib import Path

import unreal

R = 637_100_000.0          # ProofEarth surface radius (cm); center at world origin
MOON_D = 3.844e10          # ProofMoon distance along +Y
W, H = 1600, 900

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = ues.get_editor_world()
ml = unreal.MathLibrary


def look(cam, tgt):
    return ml.find_look_at_rotation(unreal.Vector(*cam), unreal.Vector(*tgt))


# (name, cam, target, far_plane)
shots = [
    ("p4_earth_surface", (R + 30000.0, 0.0, 0.0), (R + 30000.0, 1.0e8, 2.0e7), 5.0e9),
    ("p4_earthrise", (2.5e8, MOON_D + 9.0e8, 1.5e8), (0.0, 0.0, 0.0), 8.0e10),
]

out_dir = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
out_dir.mkdir(parents=True, exist_ok=True)
rt = unreal.RenderingLibrary.create_render_target2d(
    world, W, H, unreal.TextureRenderTargetFormat.RTF_RGBA8)

results = []
for name, cam, tgt, far in shots:
    cap = actor_sub.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*cam), look(cam, tgt))
    try:
        comp = cap.capture_component2d
        comp.set_editor_property("texture_target", rt)
        comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        comp.set_editor_property("max_view_distance_override", far)
        comp.capture_scene()
        fn = f"{name}_{time.strftime('%H%M%S')}.png"
        unreal.RenderingLibrary.export_render_target(world, rt, str(out_dir), fn)
        results.append(str((out_dir / fn).resolve()))
    finally:
        actor_sub.destroy_actor(cap)

print("P4_CAPS " + " | ".join(results))
