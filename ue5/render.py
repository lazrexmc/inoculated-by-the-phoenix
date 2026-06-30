"""render.py — render the saved EggTest map+sequence to a PNG via Movie Render Queue (editor PIE executor).

Run with -ExecutePythonScript (editor mode keeps ticking after the script, so the async MRQ render can
run to completion; the on-finished callback quits the editor and writes a sentinel). NOT the commandlet.
"""
import unreal
import os

DONE = r"F:\Inoculated by the Phoenix\_scratch\ue_render_done.txt"
MAP = "/Game/EggTest/Map_EggTest"
SEQ = "/Game/EggTest/Seq_EggTest"
OUT = r"F:\Inoculated by the Phoenix\_scratch\ue"

def log(s): unreal.log("[IBTP-UE] " + s)

try:
    os.remove(DONE)
except Exception:
    pass

sub = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
q = sub.get_queue()
for j in list(q.get_jobs()):
    q.delete_job(j)

job = q.allocate_new_job(unreal.MoviePipelineExecutorJob)
map_sop = MAP + "." + MAP.split("/")[-1]      # /Game/EggTest/Map_EggTest.Map_EggTest
seq_sop = SEQ + "." + SEQ.split("/")[-1]      # /Game/EggTest/Seq_EggTest.Seq_EggTest
job.set_editor_property("map", unreal.SoftObjectPath(map_sop))
job.set_editor_property("sequence", unreal.SoftObjectPath(seq_sop))
job.set_editor_property("job_name", "EggTest")
log("job map=%s seq=%s jobs=%d" % (map_sop, seq_sop, len(q.get_jobs())))

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
    log("AA setting skipped: " + repr(e))

def on_done(executor, success):
    try:
        with open(DONE, "w") as f:
            f.write("RENDER-DONE success=%s\n" % success)
    except Exception:
        pass
    log("render finished success=%s" % success)
    unreal.SystemLibrary.quit_editor()

# headless render must spawn its own -game process (PIE executor needs a viewport we don't have)
try:
    executor = unreal.MoviePipelineNewProcessExecutor()
except Exception:
    executor = unreal.MoviePipelinePIEExecutor()
executor.on_executor_finished_delegate.add_callable(on_done)
sub.render_queue_with_executor_instance(executor)
log("render dispatched via %s, ticking until finished..." % type(executor).__name__)
