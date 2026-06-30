"""make_queue.py — build + save a MoviePipelineQueue asset that the command-line -game render consumes.

The Map + Sequence already exist (build_scene.py). This adds a queue with one job (map+seq+config -> PNG).
Run with -ExecutePythonScript (editor mode, so asset creation works); it quits when done.
"""
import unreal

def log(s): unreal.log("[IBTP-UE] " + s)
def err(s): unreal.log_error("[IBTP-UE] " + s)

CONTENT = "/Game/EggTest"
MAP = CONTENT + "/Map_EggTest"
SEQ = CONTENT + "/Seq_EggTest"
QUEUE = CONTENT + "/Q_EggTest"
OUT = r"F:\Inoculated by the Phoenix\_scratch\ue"

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary

try:
    if eal.does_asset_exist(QUEUE):
        eal.delete_asset(QUEUE)
    queue = None
    for factory in (None,):
        try:
            queue = at.create_asset("Q_EggTest", CONTENT, unreal.MoviePipelineQueue, factory)
        except Exception as e:
            err("create_asset(queue) factory=%s: %s" % (factory, repr(e)))
        if queue is not None:
            break
    if queue is None:
        raise RuntimeError("MoviePipelineQueue asset could not be created")
    log("queue created: " + str(queue))

    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.set_editor_property("map", unreal.SoftObjectPath(MAP + "." + MAP.split("/")[-1]))
    job.set_editor_property("sequence", unreal.SoftObjectPath(SEQ + "." + SEQ.split("/")[-1]))
    job.set_editor_property("job_name", "EggTest")

    cfg = job.get_configuration()
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    outs = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    outs.set_editor_property("output_directory", unreal.DirectoryPath(OUT))
    outs.set_editor_property("output_resolution", unreal.IntPoint(1080, 1080))
    outs.set_editor_property("file_name_format", "egg_ue.{frame_number}")
    try:
        aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        aa.set_editor_property("override_anti_aliasing", True)
        aa.set_editor_property("spatial_sample_count", 8)
    except Exception as e:
        err("AA: " + repr(e))

    eal.save_asset(queue.get_path_name())
    log("QUEUE-SAVED jobs=%d" % len(queue.get_jobs()))
except Exception as e:
    err("make_queue aborted: " + repr(e))
finally:
    try:
        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass
