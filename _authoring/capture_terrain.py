"""Capture the T2a procedural terrain tile relief (head-less)."""

import time
from pathlib import Path

import unreal

R = 637_100_000.0
W, H = 1600, 900

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = ues.get_editor_world()
ml = unreal.MathLibrary


def norm(v):
    n = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
    return unreal.Vector(v[0] / n, v[1] / n, v[2] / n)


def shot_rot(cam, tgt):
    fwd = unreal.Vector(tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2])
    return ml.make_rot_from_xz(fwd, norm(cam))


shots = [
    ("terrain_a", (R + 120000.0, -400000.0, 150000.0), (R - 4.0e5, 5.0e5, 0.0)),
    ("terrain_b", (R + 200000.0, 300000.0, 300000.0), (R - 5.0e5, -2.0e5, -2.0e5)),
]

out_dir = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
out_dir.mkdir(parents=True, exist_ok=True)
rt = unreal.RenderingLibrary.create_render_target2d(world, W, H, unreal.TextureRenderTargetFormat.RTF_RGBA8)

results = []
for name, cam, tgt in shots:
    cap = actor_sub.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*cam), shot_rot(cam, tgt))
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

print("TERRAIN_CAPS " + " | ".join(results))
