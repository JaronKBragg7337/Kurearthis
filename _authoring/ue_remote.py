"""Run Python in the LIVE Unreal editor over its remote-execution socket.

This replaces the fragile "paste into the editor console + click" workflow.
Requires `bRemoteExecution=True` in Config/DefaultEngine.ini (added 2026-06-20)
and an editor restart so the setting takes effect. Localhost only (TTL 0).

Usage (run with system Python, NOT inside the editor):
  python _authoring/ue_remote.py --stmt "import unreal; print(unreal.SystemLibrary.get_project_directory())"
  python _authoring/ue_remote.py --file _authoring/live_scene_audit.py
  python _authoring/ue_remote.py "print(1+1)"          # bare arg = statement

Exit code 0 on success, 1 on failure / no editor found.
"""

import argparse
import sys
import time
from pathlib import Path

# Make the engine's remote_execution helper importable.
ENGINE_PY = Path(
    r"C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"
)
if not (ENGINE_PY / "remote_execution.py").exists():
    print(f"remote_execution.py not found at {ENGINE_PY}", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, str(ENGINE_PY))

import remote_execution as re  # noqa: E402


def run(command: str, exec_mode: str, discover_timeout: float = 10.0):
    rexec = re.RemoteExecution()
    rexec.start()
    try:
        deadline = time.time() + discover_timeout
        node = None
        while time.time() < deadline:
            nodes = rexec.remote_nodes
            if nodes:
                node = nodes[0]
                break
            time.sleep(0.3)
        if not node:
            print(
                "No Unreal editor responded on the remote-execution socket.\n"
                "Is the editor open AND restarted since bRemoteExecution was enabled?",
                file=sys.stderr,
            )
            return 1

        rexec.open_command_connection(node["node_id"])
        result = rexec.run_command(command, unattended=True, exec_mode=exec_mode)
        for line in result.get("output", []) or []:
            stream = sys.stderr if line.get("type") == "Error" else sys.stdout
            print(line.get("output", ""), file=stream)
        if result.get("result") not in (None, "None"):
            print(result["result"])
        return 0 if result.get("success") else 1
    finally:
        if rexec.has_command_connection():
            rexec.close_command_connection()
        rexec.stop()


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--file", help="path to a .py file to execute in the editor")
    g.add_argument("--stmt", help="a single statement to execute")
    g.add_argument("--eval", dest="evaluate", help="a single expression to evaluate and return")
    ap.add_argument("rest", nargs="*", help="bare statement (if no flag given)")
    args = ap.parse_args()

    if args.file:
        # MODE_EXEC_FILE wants a file PATH (+ optional args), not literal content.
        command = str(Path(args.file).resolve()).replace("\\", "/")
        mode = re.MODE_EXEC_FILE
    elif args.evaluate:
        command, mode = args.evaluate, re.MODE_EVAL_STATEMENT
    elif args.stmt:
        command, mode = args.stmt, re.MODE_EXEC_STATEMENT
    elif args.rest:
        command, mode = " ".join(args.rest), re.MODE_EXEC_STATEMENT
    else:
        ap.error("provide --file, --stmt, --eval, or a bare statement")

    sys.exit(run(command, mode))


if __name__ == "__main__":
    main()
