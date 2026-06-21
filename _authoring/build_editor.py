"""One-command local compile of the KurearthisEditor C++ target.

Wraps the proven `Build.bat KurearthisEditor Win64 Development` flow (see
AGENT_CAPABILITIES/TESTED_WORKFLOWS.md) so a true C++ compile is a single command
that a build session — or a future self-hosted CI runner — can call to catch a
broken module before it surfaces at the next editor open.

The editor must be CLOSED: while UnrealEditor runs it holds
UnrealEditor-Kurearthis.dll, so the link step fails. This script refuses by default
if the editor is running (exit 2) and tells you to close it; pass --allow-editor-open
to attempt anyway.

  python _authoring/build_editor.py                 # compile (editor must be closed)
  python _authoring/build_editor.py --allow-editor-open

Exit 0 = build success, 1 = build failed, 2 = refused (editor open / setup issue).
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPROJECT = ROOT / "Kurearthis.uproject"
UE_ROOT = Path(r"C:\Program Files\Epic Games\UE_5.8")
BUILD_BAT = UE_ROOT / "Engine" / "Build" / "BatchFiles" / "Build.bat"
TARGET = "KurearthisEditor"


def editor_running() -> bool:
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq UnrealEditor.exe", "/NH"],
            capture_output=True, text=True, timeout=20,
        ).stdout
        return "UnrealEditor.exe" in out
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-editor-open", action="store_true",
                    help="attempt the build even if the editor is running (link will likely fail)")
    args = ap.parse_args()

    if not BUILD_BAT.exists():
        print(f"REFUSED: Build.bat not found at {BUILD_BAT} (set the correct UE_5.8 path)")
        sys.exit(2)
    if not UPROJECT.exists():
        print(f"REFUSED: project not found at {UPROJECT}")
        sys.exit(2)
    if editor_running() and not args.allow_editor_open:
        print("REFUSED: UnrealEditor is running - it locks UnrealEditor-Kurearthis.dll, "
              "so the link step would fail.\nClose the editor and retry, or pass "
              "--allow-editor-open to attempt anyway.")
        sys.exit(2)

    cmd = [
        str(BUILD_BAT), TARGET, "Win64", "Development",
        f"-Project={UPROJECT}", "-WaitMutex", "-NoHotReload",
    ]
    print(f"[build] {' '.join(cmd)}")
    proc = subprocess.run(cmd, text=True)
    if proc.returncode == 0:
        print("BUILD_OK KurearthisEditor compiled")
        sys.exit(0)
    print(f"BUILD_FAILED rc={proc.returncode}")
    sys.exit(1)


if __name__ == "__main__":
    main()
