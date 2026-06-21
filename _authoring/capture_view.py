"""Convenience wrapper: capture the live editor scene to a PNG, head-less.

Runs `capture_scene.py` inside the editor over remote execution (off-screen
SceneCapture2D → render target → PNG, so it works even when the window is
minimized), then prints the absolute path of the written PNG. The agent reads
that PNG to actually see the scene — visual evidence with no GUI clicking.

  python _authoring/capture_view.py

Prints `CAPTURE_OK <abs_path>` on success; exits non-zero otherwise.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UE_REMOTE = ROOT / "_authoring" / "ue_remote.py"
CAPTURE_SCENE = ROOT / "_authoring" / "capture_scene.py"


def main():
    cp = subprocess.run(
        [sys.executable, str(UE_REMOTE), "--file", str(CAPTURE_SCENE)],
        capture_output=True, text=True, timeout=90,
    )
    out = (cp.stdout or "") + (cp.stderr or "")
    marker = next((ln for ln in out.splitlines() if ln.startswith("CAPTURE_OK")), None)
    if cp.returncode != 0 or not marker:
        print(f"CAPTURE_FAIL editor capture failed:\n{out.strip()}")
        sys.exit(1)

    # capture_scene.py prints a path relative to the engine CWD; resolve it.
    raw = marker.split(None, 1)[1].strip()
    path = Path(raw)
    if not path.is_absolute():
        path = (ROOT / "Saved" / "Screenshots" / path.name)
    if not path.exists():
        # Fall back to the newest PNG under Saved/Screenshots.
        shots = sorted((ROOT / "Saved" / "Screenshots").glob("*.png"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        if not shots:
            print(f"CAPTURE_FAIL no PNG found; editor said: {raw}")
            sys.exit(1)
        path = shots[0]

    print(f"CAPTURE_OK {path.resolve()}")


if __name__ == "__main__":
    main()
