"""Enumerate the LIVE editor scene (in-memory) and write a fresh audit.

Run from the Unreal editor Python console:  py "<project>/_authoring/live_scene_audit.py"
This reads the world currently loaded in the running editor, NOT a saved .umap.
"""

import json
from pathlib import Path

import unreal

PROJECT_ROOT = Path(unreal.Paths.project_dir())
OUT_PATH = PROJECT_ROOT / "Saved" / "LiveSceneAudit.json"

editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor_subsystem.get_editor_world()
world_name = world.get_name() if world else "<none>"

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())

audit = {
    "live_world": world_name,
    "actor_count": len(actors),
    "actors": [
        {
            "label": a.get_actor_label(),
            "class": a.get_class().get_name(),
            "location_cm": [
                float(a.get_actor_location().x),
                float(a.get_actor_location().y),
                float(a.get_actor_location().z),
            ],
            "scale": [
                float(a.get_actor_scale3d().x),
                float(a.get_actor_scale3d().y),
                float(a.get_actor_scale3d().z),
            ],
        }
        for a in actors
    ],
}

OUT_PATH.write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(
    f"KUREARTHIS_LIVE_AUDIT world={world_name} actors={len(audit['actors'])} "
    f"labels={[a['label'] for a in audit['actors']]}"
)
