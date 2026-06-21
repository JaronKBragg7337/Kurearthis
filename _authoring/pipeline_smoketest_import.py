"""Unreal side of the pipeline smoke-test: import the FBX, verify scale, clean up.

Imports _authoring/_smoketest_cube.fbx via AssetImportTask into a TEMP content path,
reads the imported StaticMesh bounds (a 2 m cube should be 200 cm in Unreal), then
deletes the temp asset so Content is not polluted. Prints SMOKE_IMPORT_OK / _FAIL.

  python _authoring/ue_remote.py --file _authoring/pipeline_smoketest_import.py
"""

from pathlib import Path

import unreal

FBX = Path(unreal.Paths.project_dir()) / "_authoring" / "_smoketest_cube.fbx"
DEST = "/Game/_PipelineSmokeTest"
# UE names the imported StaticMesh after the FBX file stem, not the mesh object name.
ASSET = f"{DEST}/{FBX.stem}"
EXPECTED_HALF_CM = 100.0   # 2 m cube -> 200 cm -> 100 cm half-extent
TOL = 2.0

if not FBX.exists():
    print(f"SMOKE_IMPORT_FAIL fbx not found: {FBX}")
else:
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(FBX))
    task.set_editor_property("destination_path", DEST)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)

    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    task.set_editor_property("options", options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    sm = unreal.EditorAssetLibrary.load_asset(ASSET)
    if sm is None:
        print(f"SMOKE_IMPORT_FAIL asset did not import at {ASSET}")
    else:
        bounds = sm.get_bounds()  # BoxSphereBounds
        ext = bounds.box_extent
        ok = (
            abs(ext.x - EXPECTED_HALF_CM) < TOL
            and abs(ext.y - EXPECTED_HALF_CM) < TOL
            and abs(ext.z - EXPECTED_HALF_CM) < TOL
        )
        # Clean up the temp asset so Content stays clean (import used save=False).
        unreal.EditorAssetLibrary.delete_directory(DEST)
        verdict = "SMOKE_IMPORT_OK" if ok else "SMOKE_IMPORT_FAIL"
        print(f"{verdict} box_extent_cm=({ext.x:.2f},{ext.y:.2f},{ext.z:.2f}) "
              f"expected_half={EXPECTED_HALF_CM} cleaned={not unreal.EditorAssetLibrary.does_asset_exist(ASSET)}")
