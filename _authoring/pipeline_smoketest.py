"""End-to-end Blender -> FBX -> Unreal import smoke-test (head-less).

Verifies the asset pipeline round-trips with the current Blender 5.1.2 + UE 5.8:
  1. Blender authors a 2 m cube and exports FBX (in meters).
  2. Unreal imports it to a temp content path, checks bounds (200 cm), deletes it.

  python _authoring/pipeline_smoketest.py

Prints PIPELINE_OK / PIPELINE_FAIL. The temp FBX (_authoring/_smoketest_cube.fbx)
is gitignored and removed at the end.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UE_REMOTE = ROOT / "_authoring" / "ue_remote.py"
MAKE = ROOT / "_authoring" / "pipeline_smoketest_make.py"
IMPORT = ROOT / "_authoring" / "pipeline_smoketest_import.py"
FBX = ROOT / "_authoring" / "_smoketest_cube.fbx"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")


def main():
    if not BLENDER.exists():
        print(f"PIPELINE_FAIL Blender not found at {BLENDER}")
        sys.exit(1)

    if FBX.exists():
        FBX.unlink()

    # 1) Blender authoring -> FBX
    bl = subprocess.run(
        [str(BLENDER), "--background", "--python", str(MAKE)],
        capture_output=True, text=True, timeout=180,
    )
    if not FBX.exists():
        print("PIPELINE_FAIL Blender did not produce the FBX")
        print((bl.stdout or "")[-1500:])
        print((bl.stderr or "")[-500:])
        sys.exit(1)
    size_kb = FBX.stat().st_size / 1024.0
    print(f"[blender] FBX written: {FBX.name} ({size_kb:.1f} KB)")

    # 2) Unreal import + verify + cleanup
    ue = subprocess.run(
        [sys.executable, str(UE_REMOTE), "--file", str(IMPORT)],
        capture_output=True, text=True, timeout=120,
    )
    out = (ue.stdout or "") + (ue.stderr or "")
    marker = next((ln for ln in out.splitlines() if ln.startswith("SMOKE_IMPORT_")), None)
    print(f"[unreal] {marker or out.strip()[-300:]}")

    # tidy the temp FBX regardless of outcome
    if FBX.exists():
        FBX.unlink()

    if marker and marker.startswith("SMOKE_IMPORT_OK"):
        print("PIPELINE_OK Blender 5.1.2 -> FBX -> UE 5.8 import round-trips at correct scale")
        sys.exit(0)
    print("PIPELINE_FAIL see [unreal] line above")
    sys.exit(1)


if __name__ == "__main__":
    main()
