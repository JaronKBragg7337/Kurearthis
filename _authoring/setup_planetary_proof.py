"""Import the proof sphere, create PlanetaryProof, and record a machine audit."""

import json
from pathlib import Path

import unreal


PROJECT_ROOT = Path(unreal.Paths.project_dir())
FBX_PATH = PROJECT_ROOT / "_authoring" / "SM_ProofPlanet_Base.fbx"
AUDIT_PATH = PROJECT_ROOT / "Saved" / "PlanetaryProofAudit.json"

DESTINATION_PATH = "/Game/Planetary"
MESH_ASSET_PATH = f"{DESTINATION_PATH}/SM_ProofPlanet_Base.SM_ProofPlanet_Base"
MAP_ASSET_PATH = "/Game/PlanetaryProof"
BODY_LABEL = "ProofEarth"

BASE_RADIUS_METERS = 1_000.0
BODY_SCALE = 6_371.0
TARGET_RADIUS_METERS = 6_371_000.0
TARGET_RADIUS_CENTIMETERS = 637_100_000.0


if not FBX_PATH.exists():
    raise RuntimeError(f"Missing authored FBX: {FBX_PATH}")

task = unreal.AssetImportTask()
task.filename = str(FBX_PATH)
task.destination_path = DESTINATION_PATH
task.destination_name = "SM_ProofPlanet_Base"
task.automated = True
task.replace_existing = True
task.save = True

options = unreal.FbxImportUI()
options.import_mesh = True
options.import_as_skeletal = False
options.import_materials = False
options.import_textures = False
options.static_mesh_import_data.convert_scene = True
options.static_mesh_import_data.convert_scene_unit = True
task.options = options

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = unreal.EditorAssetLibrary.load_asset(MESH_ASSET_PATH)
if not mesh:
    raise RuntimeError(
        f"Static mesh import failed. Imported paths: {list(task.imported_object_paths)}"
    )

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_ASSET_PATH):
    if not level_subsystem.load_level(MAP_ASSET_PATH):
        raise RuntimeError(f"Could not load existing map {MAP_ASSET_PATH}")
else:
    if not level_subsystem.new_level(MAP_ASSET_PATH):
        raise RuntimeError(f"Could not create map {MAP_ASSET_PATH}")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
unexpected = [actor.get_actor_label() for actor in actors if actor.get_actor_label() != BODY_LABEL]
if unexpected:
    raise RuntimeError(f"PlanetaryProof contains unexpected actors: {unexpected}")

body = next((actor for actor in actors if actor.get_actor_label() == BODY_LABEL), None)
if body is None:
    body = actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    body.set_actor_label(BODY_LABEL)

body.set_actor_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
body.set_actor_rotation(unreal.Rotator(0.0, 0.0, 0.0), False)
body.set_actor_scale3d(unreal.Vector(BODY_SCALE, BODY_SCALE, BODY_SCALE))
component = body.static_mesh_component
component.set_static_mesh(mesh)

if not level_subsystem.save_current_level():
    raise RuntimeError("PlanetaryProof map did not save")
unreal.EditorAssetLibrary.save_asset(MESH_ASSET_PATH, only_if_is_dirty=False)

actors = list(actor_subsystem.get_all_level_actors())
bounds = mesh.get_bounds()
base_radius_cm = float(bounds.sphere_radius)
computed_radius_cm = base_radius_cm * BODY_SCALE
radius_error_cm = abs(computed_radius_cm - TARGET_RADIUS_CENTIMETERS)

audit = {
    "map_asset": MAP_ASSET_PATH,
    "mesh_asset": MESH_ASSET_PATH,
    "actor_count": len(actors),
    "actors": [
        {
            "label": actor.get_actor_label(),
            "class": actor.get_class().get_name(),
            "location_cm": [
                float(actor.get_actor_location().x),
                float(actor.get_actor_location().y),
                float(actor.get_actor_location().z),
            ],
            "scale": [
                float(actor.get_actor_scale3d().x),
                float(actor.get_actor_scale3d().y),
                float(actor.get_actor_scale3d().z),
            ],
        }
        for actor in actors
    ],
    "authored_base_radius_m": BASE_RADIUS_METERS,
    "imported_base_radius_cm": base_radius_cm,
    "actor_uniform_scale": BODY_SCALE,
    "target_radius_m": TARGET_RADIUS_METERS,
    "target_radius_cm": TARGET_RADIUS_CENTIMETERS,
    "computed_radius_cm": computed_radius_cm,
    "absolute_radius_error_cm": radius_error_cm,
}

AUDIT_PATH.write_text(json.dumps(audit, indent=2), encoding="utf-8")

editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
editor_subsystem.set_level_viewport_camera_info(
    unreal.Vector(-1_274_200_000.0, 0.0, 0.0),
    unreal.Rotator(0.0, 0.0, 0.0),
)

print(
    "KUREARTHIS_PLANETARY_PROOF "
    f"actors={len(actors)} target_radius_cm={TARGET_RADIUS_CENTIMETERS:.1f} "
    f"computed_radius_cm={computed_radius_cm:.1f} error_cm={radius_error_cm:.3f}"
)
