"""Capture a block of streamed-style proc terrain tiles to check border seamlessness.

Spawns a 3x3 block of AProcTerrainTile at adjacent lon/lat cells (same scheme as
ASurfaceTileManager), generates them, captures an oblique view with the atmosphere
hidden, then DESTROYS the temp tiles (scene not saved). If the relief flows continuously
across tile borders with no cracks/cliffs, T2b borders are seamless.

  python _authoring/ue_remote.py --file _authoring/capture_terrain_grid.py
"""

import time
from pathlib import Path

import unreal

R = 637_100_000.0
TILE = 500000.0
DANG = TILE / R
AMP = 40000.0
W, H = 1600, 900

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = ues.get_editor_world()
ml = unreal.MathLibrary

by_label = {a.get_actor_label(): a for a in actor_sub.get_all_level_actors()}
planet = by_label.get("ProofEarth")
if planet and "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))


def cell_dir(i, j):
    theta = (i + 0.5) * DANG
    phi = (j + 0.5) * DANG
    cp = unreal.MathLibrary.cos(phi)
    return unreal.Vector(cp * unreal.MathLibrary.cos(theta), cp * unreal.MathLibrary.sin(theta), unreal.MathLibrary.sin(phi))


temp = []
for i in range(-1, 2):
    for j in range(-1, 2):
        d = cell_dir(i, j)
        loc = unreal.Vector(d.x * R, d.y * R, d.z * R)
        rot = unreal.MathLibrary.make_rot_from_z(d)
        t = actor_sub.spawn_actor_from_class(unreal.ProcTerrainTile, loc, rot)
        t.set_actor_label(f"CapTile_{i}_{j}")
        t.set_editor_property("PlanetActor", planet)
        t.set_editor_property("SurfaceRadius", R)
        t.set_editor_property("TileSizeCm", TILE)
        t.set_editor_property("Resolution", 32)
        t.set_editor_property("HeightAmplitudeCm", AMP)
        t.set_editor_property("bUseLonLatCell", True)
        t.set_editor_property("CellLon0", i * DANG)
        t.set_editor_property("CellLat0", j * DANG)
        t.set_editor_property("CellAngularSize", DANG)
        t.call_method("Generate")
        temp.append(t)

# Hide atmosphere/moon for a clear view.
hidden = []
for a in actor_sub.get_all_level_actors():
    if a.get_actor_label() in ("SurfaceAtmosphere", "ProofMoon"):
        a.set_actor_hidden_in_game(True)
        try:
            a.set_is_temporarily_hidden_in_editor(True)
        except Exception:
            pass
        hidden.append(a)


def norm(v):
    n = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
    return unreal.Vector(v[0] / n, v[1] / n, v[2] / n)


cam = (R + 300000.0, -350000.0, 250000.0)
tgt = (R, 0.0, 0.0)
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
    fn = f"terrain_grid_{time.strftime('%H%M%S')}.png"
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
    for t in temp:
        actor_sub.destroy_actor(t)

print(f"TERRAIN_GRID_CAP {out}")
