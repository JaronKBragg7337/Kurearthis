"""Scripted physics harness — run a Simulate-In-Editor physics test with NO GUI.

Drives the live editor over remote execution (ue_remote.py):
  1. set up the scene (spawn the gravity body + floating-origin manager, save)
  2. start Simulate via LevelEditorSubsystem.editor_play_simulate()
  3. let physics run for a fixed wall-clock duration (the C++ writes results)
  4. stop via editor_request_end_play()
  5. read and summarize Saved/RadialGravityProof.json

Usage (system Python, editor must be open with remote exec enabled):
  python _authoring/run_physics_harness.py [seconds]
  python _authoring/run_physics_harness.py 33 --setup _authoring/setup_surface_patch_proof.py

This replaces hand-driving the Simulate/Stop buttons.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UE_REMOTE = ROOT / "_authoring" / "ue_remote.py"
DEFAULT_SETUP = ROOT / "_authoring" / "spawn_chaos_gravity_body.py"
RESULT = ROOT / "Saved" / "RadialGravityProof.json"

START = "import unreal; unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()"
STOP = "import unreal; unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()"
IS_PLAYING = "import unreal; print(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())"


def remote(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(UE_REMOTE), *args],
        capture_output=True, text=True, timeout=120,
    )


def step(label, cp):
    out = (cp.stdout or "").strip()
    err = (cp.stderr or "").strip()
    print(f"[{label}] rc={cp.returncode} {out}{(' | ERR ' + err) if err else ''}")
    if cp.returncode != 0:
        raise SystemExit(f"harness aborted at: {label}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seconds", nargs="?", type=float, default=25.0,
                    help="wall-clock seconds to let the simulation run")
    ap.add_argument("--setup", default=str(DEFAULT_SETUP),
                    help="path to the editor-Python setup script to run before Simulate")
    args = ap.parse_args()
    sim_seconds = args.seconds
    setup_path = Path(args.setup).resolve()
    if not setup_path.exists():
        raise SystemExit(f"setup script not found: {setup_path}")

    # Make sure the editor socket is reachable before we touch state.
    probe = remote("--stmt", "print('PING')")
    if probe.returncode != 0 or "PING" not in (probe.stdout or ""):
        raise SystemExit("editor not reachable over remote execution — is it open and restarted?")

    if RESULT.exists():
        RESULT.unlink()

    print(f"[setup] {setup_path.name}")
    step("setup", remote("--file", str(setup_path)))
    step("start-simulate", remote("--stmt", START))

    print(f"[run] simulating ~{sim_seconds:.0f}s ...")
    time.sleep(sim_seconds)

    step("stop", remote("--stmt", STOP))
    time.sleep(1.5)

    if not RESULT.exists():
        raise SystemExit("no result written — the C++ body may not have ticked")
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    print("\n=== RESULT ===")
    print(json.dumps(data, indent=2))
    rested = data.get("rested")
    dist = data.get("distance_from_center_cm")
    up = data.get("local_up")
    print(f"\nSUMMARY rested={rested} dist_from_center={dist} local_up={up}")


if __name__ == "__main__":
    main()
