"""probe.py — prove the headless UE5 Python loop executes user scripts (writes a sentinel file to disk).

unreal.log output is easy to miss in the giant engine log, so this writes an unambiguous proof file.
Run via:  UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="...probe.py" -nullrhi -unattended
"""
import unreal
import os

proof = r"F:\Inoculated by the Phoenix\_scratch\ue_proof.txt"
try:
    with open(proof, "w") as f:
        f.write("UE-PYTHON-RAN\n")
        f.write("engine: " + unreal.SystemLibrary.get_engine_version() + "\n")
        f.write("project: " + unreal.Paths.project_dir() + "\n")
        for cls in ("MoviePipelineQueue", "MoviePipelineExecutorBase", "StaticMesh", "Material",
                    "MaterialEditingLibrary", "EditorAssetLibrary", "AssetToolsHelpers",
                    "EditorActorSubsystem", "CineCameraActor"):
            f.write("has %s: %s\n" % (cls, hasattr(unreal, cls)))
    unreal.log("[IBTP-UE] probe wrote " + proof)
except Exception as e:
    unreal.log_error("[IBTP-UE] probe FAILED: " + str(e))
