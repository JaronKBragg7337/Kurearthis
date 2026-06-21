"""Off-screen screenshot of the live editor scene from the active viewport camera.

Runs INSIDE the editor (via ue_remote --file). Renders through a SceneCapture2D into
a render target and exports a PNG, so it works even when the editor window is
minimized/occluded (an on-screen HighResShot does NOT render in that case). It is
synchronous — no deferred-frame waiting — and prints `CAPTURE_OK <abs_path>`.

  python _authoring/ue_remote.py --file _authoring/capture_scene.py
  (or use the wrapper: python _authoring/capture_view.py)
"""

import time
from pathlib import Path

import unreal

W, H = 1600, 900

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = ues.get_editor_world()

# Match the active perspective viewport's camera so the shot is what a user would see.
key = les.get_active_viewport_config_key()
loc, rot = les.get_level_viewport_camera_info(key)

# RTF_RGBA8 (LDR) so export_render_target writes a real PNG. A float format makes
# it export OpenEXR data under a .png name instead.
render_target = unreal.RenderingLibrary.create_render_target2d(
    world, W, H, unreal.TextureRenderTargetFormat.RTF_RGBA8
)

# The planetary proof maps are deliberately bare (no lights), so a faithful capture
# would be pure black. If the scene has no DirectionalLight, add a temporary "sun"
# (and a SkyLight for ambient fill) just for this shot, then remove them — the saved
# scene is never touched.
temp_lights = []
has_dir_light = any(
    isinstance(a, unreal.DirectionalLight) for a in actor_sub.get_all_level_actors()
)
if not has_dir_light:
    sun = actor_sub.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0, 0, 0), unreal.Rotator(-25.0, 15.0, 0.0)
    )
    sun.light_component.set_intensity(6.0)
    temp_lights.append(sun)
    sky = actor_sub.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0, 0, 0), unreal.Rotator()
    )
    sky.light_component.set_intensity(1.0)
    temp_lights.append(sky)

cap = actor_sub.spawn_actor_from_class(unreal.SceneCapture2D, loc, rot)
try:
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", render_target)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    # Wide far plane so the Earth-scale body is not clipped from the far camera.
    comp.set_editor_property("max_view_distance_override", 5.0e9)
    comp.capture_scene()

    out_dir = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"view_{time.strftime('%Y%m%d_%H%M%S')}"
    unreal.RenderingLibrary.export_render_target(world, render_target, str(out_dir), f"{name}.png")
    out_path = out_dir / f"{name}.png"
finally:
    actor_sub.destroy_actor(cap)
    for light in temp_lights:
        actor_sub.destroy_actor(light)

print(f"CAPTURE_OK {out_path}")
