"""Blender side of the pipeline smoke-test: author a small known-size mesh -> FBX.

A 2 m cube (distinct from any real asset) exported in METERS, so the UE import side
can confirm the round-trip preserves scale (2 m -> 200 cm in Unreal). Mirrors the
real authoring pattern in make_planetary_proof_body.py.

  blender --background --python _authoring/pipeline_smoketest_make.py
"""

from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parents[1] / "_authoring" / "_smoketest_cube.fbx"
SIZE_M = 2.0

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0

bpy.ops.mesh.primitive_cube_add(size=SIZE_M, location=(0.0, 0.0, 0.0))
cube = bpy.context.active_object
cube.name = "SM_SmokeTestCube"
cube.data.name = "SM_SmokeTestCube_Mesh"

bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
cube.select_set(True)

bpy.ops.export_scene.fbx(
    filepath=str(OUT),
    use_selection=True,
    object_types={"MESH"},
    axis_forward="-Y",
    axis_up="Z",
    apply_unit_scale=True,
    bake_space_transform=False,
    use_mesh_modifiers=True,
    add_leaf_bones=False,
)

print(f"KUREARTHIS_SMOKE_FBX path={OUT} size_m={SIZE_M}")
