"""Capture the T2a terrain relief with the atmosphere temporarily hidden (clear view)."""

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


# Hide atmosphere + moon so the bare relief reads.
hidden = []
for a in actor_sub.get_all_level_actors():
    if a.get_actor_label() in ("SurfaceAtmosphere", "ProofMoon"):
        a.set_actor_hidden_in_game(True)
        try:
            a.set_is_temporarily_hidden_in_editor(True)
        except Exception:
            pass
        hidden.append(a)

cam = (R + 350000.0, -250000.0, 250000.0)   # ~3.5 km up, oblique over the tile
tgt = (R, 100000.0, 0.0)
fwd = unreal.Vector(tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2])
rot = ml.make_rot_from_xz(fwd, norm(cam))

out_dir = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
rt = unreal.RenderingLibrary.create_render_target2d(world, W, H, unreal.TextureRenderTargetFormat.RTF_RGBA8)
cap = actor_sub.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*cam), rot)
try:
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("max_view_distance_override", 5.0e9)
    comp.capture_scene()
    fn = f"terrain_clear_{time.strftime('%H%M%S')}.png"
    unreal.RenderingLibrary.export_render_target(world, rt, str(out_dir), fn)
    out = str((out_dir / fn).resolve())
finally:
    actor_sub.destroy_actor(cap)
    for a in hidden:
        a.set_actor_hidden_in_game(False)
        try:
            a.set_is_temporarily_hidden_in_editor(False)
        except Exception:
            pass

print(f"TERRAIN_CLEAR {out}")
