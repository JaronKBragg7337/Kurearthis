"""Build the reproducible in-house base sphere for the planetary scale proof."""

from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "_authoring" / "SM_ProofPlanet_Base.fbx"
BASE_RADIUS_METERS = 1_000.0


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0

bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=5,
    radius=BASE_RADIUS_METERS,
    location=(0.0, 0.0, 0.0),
)
planet = bpy.context.active_object
planet.name = "SM_ProofPlanet_Base"
planet.data.name = "SM_ProofPlanet_Base_Mesh"

for polygon in planet.data.polygons:
    polygon.use_smooth = True

bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
planet.select_set(True)

bpy.ops.export_scene.fbx(
    filepath=str(OUTPUT_PATH),
    use_selection=True,
    object_types={"MESH"},
    axis_forward="-Y",
    axis_up="Z",
    apply_unit_scale=True,
    bake_space_transform=False,
    use_mesh_modifiers=True,
    add_leaf_bones=False,
)

print(
    f"KUREARTHIS_PLANET_FBX path={OUTPUT_PATH} "
    f"base_radius_m={BASE_RADIUS_METERS:.1f}"
)
