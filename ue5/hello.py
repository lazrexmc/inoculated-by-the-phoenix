"""hello.py — first headless UE5 Python smoke test (run via UnrealEditor-Cmd -run=pythonscript).

Verifies the Claude-driven headless loop works: the project opens, the `unreal` module is live, and the
Python + Movie Render Queue plugins are enabled. Logs markers we grep for. No rendering (safe under -nullrhi).
"""
import unreal

unreal.log("[IBTP-UE] ===== hello =====")
unreal.log("[IBTP-UE] engine: " + unreal.SystemLibrary.get_engine_version())
unreal.log("[IBTP-UE] project dir: " + unreal.Paths.project_dir())
unreal.log("[IBTP-UE] content dir: " + unreal.Paths.project_content_dir())
for cls in ("MoviePipelineQueue", "MoviePipelineMasterConfig", "StaticMesh", "Material"):
    unreal.log("[IBTP-UE] has unreal.%s: %s" % (cls, hasattr(unreal, cls)))
unreal.log("[IBTP-UE] DONE-HELLO")
