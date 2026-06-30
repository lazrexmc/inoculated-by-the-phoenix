"""build_scene.py — build a test scene + Level Sequence + Movie Render Queue, all saved to /Game.

Validates the headless render loop before we invest in the egg: an engine sphere with an emissive
material, a point light, a CineCamera, a 1-frame Level Sequence (camera cut), and a MoviePipelineQueue
job that outputs a PNG. Run as a commandlet (no -nullrhi — the material needs to compile):

  UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=".../build_scene.py" -unattended -nopause -stdout

Then render the saved queue from the command line (see ue5/README.md). Per-stage [IBTP-UE] logging so
the engine log shows exactly where anything fails.
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
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def stage(name, fn):
    try:
        r = fn(); log("OK  " + name); return r
    except Exception as e:
        err("FAIL " + name + ": " + repr(e)); raise


def main():
    log("===== build_scene start =====")

    # 0) clean slate — delete prior /Game/EggTest assets so create_asset doesn't return null
    try:
        if eal.does_directory_exist(CONTENT):
            eal.delete_directory(CONTENT); log("cleaned " + CONTENT)
    except Exception as e:
        err("clean dir: " + repr(e))

    # 1) fresh level
    stage("new_level", lambda: les.new_level(MAP))

    # 2) emissive material (warm) — base color + emissive
    def mk_mat():
        mat = at.create_asset("M_Gem", CONTENT, unreal.Material, unreal.MaterialFactoryNew())
        MEL = unreal.MaterialEditingLibrary
        col = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
        col.set_editor_property("constant", unreal.LinearColor(1.0, 0.45, 0.12, 1.0))
        emi = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 180)
        emi.set_editor_property("r", 4.0)
        mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, 90)
        MEL.connect_material_expressions(col, "", mul, "A")
        MEL.connect_material_expressions(emi, "", mul, "B")
        MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
        MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.recompile_material(mat)
        eal.save_asset(mat.get_path_name())
        return mat
    # mat = stage("material", mk_mat)   # SKIP for the render-loop test; the gem material is built with the egg

    # 3) sphere actor (default material — just validating the render path)
    def mk_sphere():
        mesh = unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
        a = eas.spawn_actor_from_object(mesh, unreal.Vector(0, 0, 0))
        a.set_actor_label("Egg_Test")
        return a
    sphere = stage("sphere", mk_sphere)

    # 4) lights — directional + sky for fill, a point light for sparkle
    def mk_lights():
        dl = eas.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 300),
                                        unreal.Rotator(-45, 30, 0))
        dl.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(6.0)
        eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 200))
        pl = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(160, -160, 160))
        plc = pl.get_component_by_class(unreal.PointLightComponent)
        plc.set_intensity(150000.0); plc.set_attenuation_radius(2000.0)
        return dl
    stage("lights", mk_lights)

    # 5) cine camera aimed at the origin
    def mk_cam():
        cam = eas.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(-360, 0, 30))
        rot = unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(), unreal.Vector(0, 0, 0))
        cam.set_actor_rotation(rot, False)
        return cam
    cam = stage("camera", mk_cam)

    # 6) level sequence with a camera-cut bound to the cine camera
    def mk_seq():
        seq = at.create_asset("Seq_EggTest", CONTENT, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
        MSE = unreal.MovieSceneSequenceExtensions
        try: MSE.set_display_rate(seq, unreal.FrameRate(24, 1))
        except Exception as e: err("display_rate: " + repr(e))
        try:
            MSE.set_playback_start(seq, 0); MSE.set_playback_end(seq, 2)
        except Exception as e: err("playback: " + repr(e))
        binding = MSE.add_possessable(seq, cam)
        cut = MSE.add_track(seq, unreal.MovieSceneCameraCutTrack)
        sec = cut.add_section()
        try: sec.set_range(0, 2)
        except Exception as e: err("set_range: " + repr(e))
        # camera-cut binding id (the API varies across UE versions — try the known ways)
        guid = None
        for getter in (lambda: unreal.MovieSceneBindingExtensions.get_id(binding),
                       lambda: binding.get_id(),
                       lambda: binding.binding_id):
            try:
                guid = getter()
                if guid is not None:
                    break
            except Exception:
                pass
        bid = None
        try:
            bid = unreal.MovieSceneObjectBindingID(guid=guid)
        except Exception:
            try:
                bid = unreal.MovieSceneObjectBindingID()
                bid.set_editor_property("guid", guid)
            except Exception as e:
                err("binding_id ctor: " + repr(e))
        if bid is not None:
            try:
                sec.set_camera_binding_id(bid); log("camera binding set guid=%s" % str(guid))
            except Exception as e:
                err("set_camera_binding_id: " + repr(e))
        eal.save_asset(seq.get_path_name())
        return seq
    stage("sequence", mk_seq)

    # 7) (the render queue is built in-memory by render.py, not saved here)

    # 8) save level
    stage("save_level", lambda: les.save_current_level())
    log("===== build_scene DONE-BUILD =====")


# Editor ops (new_level/spawn) need a real editor world -> run with -ExecutePythonScript (NOT the
# -run=pythonscript commandlet, which has no world and access-violates). Quit the editor when done.
try:
    main()
except Exception as e:
    err("build_scene aborted: " + repr(e))
finally:
    try:
        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass

