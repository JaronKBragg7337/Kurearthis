"""Capture the real Delhi terrain (from the baked DEM) in the editor.

Spawns a 3x3 block of proc tiles at Delhi's planet cells (DEM active there), generates
them, captures an oblique view (atmosphere hidden), then destroys the temp tiles.
Delhi is a flat plain, so expect gentle real relief, not dramatic hills.
"""

import math
import time
from pathlib import Path

import unreal

R = 637_100_000.0
TILE = 500000.0
DANG = TILE / R
W, H = 1600, 900

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = ues.get_editor_world()
ml = unreal.MathLibrary

by_label = {a.get_actor_label(): a for a in actor_sub.get_all_level_actors()}
planet = by_label.get("ProofEarth")
if planet and "Planet" not in [str(t) for t in planet.tags]:
    planet.tags.append(unreal.Name("Planet"))

lat = math.radians(28.6139)
lon = math.radians(77.2090)
i0 = int(math.floor(lon / DANG))
j0 = int(math.floor(lat / DANG))


def cell_dir(i, j):
    th = (i + 0.5) * DANG
    ph = (j + 0.5) * DANG
    cp = math.cos(ph)
    return unreal.Vector(cp * math.cos(th), cp * math.sin(th), math.sin(ph))


temp = []
for i in range(i0 - 1, i0 + 2):
    for j in range(j0 - 1, j0 + 2):
        d = cell_dir(i, j)
        loc = unreal.Vector(d.x * R, d.y * R, d.z * R)
        rot = unreal.MathLibrary.make_rot_from_z(d)
        t = actor_sub.spawn_actor_from_class(unreal.ProcTerrainTile, loc, rot)
        t.set_actor_label(f"CapTile_{i}_{j}")
        t.set_editor_property("PlanetActor", planet)
        t.set_editor_property("SurfaceRadius", R)
        t.set_editor_property("TileSizeCm", TILE)
        t.set_editor_property("Resolution", 48)
        t.set_editor_property("bUseLonLatCell", True)
        t.set_editor_property("CellLon0", i * DANG)
        t.set_editor_property("CellLat0", j * DANG)
        t.set_editor_property("CellAngularSize", DANG)
        t.call_method("Generate")
        temp.append(t)

hidden = []
for a in actor_sub.get_all_level_actors():
    if a.get_actor_label() in ("SurfaceAtmosphere", "ProofMoon"):
        a.set_actor_hidden_in_game(True)
        try:
            a.set_is_temporarily_hidden_in_editor(True)
        except Exception:
            pass
        hidden.append(a)

dC = cell_dir(i0, j0)
up = (dC.x, dC.y, dC.z)
# East/north tangent basis for an oblique camera.
ex, ey, ez = -dC.y, dC.x, 0.0
en = math.sqrt(ex * ex + ey * ey)
east = (ex / en, ey / en, 0.0)
north = (up[1] * east[2] - up[2] * east[1], up[2] * east[0] - up[0] * east[2], up[0] * east[1] - up[1] * east[0])

cam = (dC.x * (R + 250000.0) - east[0] * 220000.0 - north[0] * 220000.0,
       dC.y * (R + 250000.0) - east[1] * 220000.0 - north[1] * 220000.0,
       dC.z * (R + 250000.0) - east[2] * 220000.0 - north[2] * 220000.0)
tgt = (dC.x * R, dC.y * R, dC.z * R)
fwd = unreal.Vector(tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2])
rot = ml.make_rot_from_xz(fwd, unreal.Vector(up[0], up[1], up[2]))

out_dir = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
rt = unreal.RenderingLibrary.create_render_target2d(world, W, H, unreal.TextureRenderTargetFormat.RTF_RGBA8)
cap = actor_sub.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*cam), rot)
try:
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("max_view_distance_override", 5.0e9)
    comp.capture_scene()
    fn = f"realdem_delhi_{time.strftime('%H%M%S')}.png"
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

print(f"REALDEM_CAP {out}")
