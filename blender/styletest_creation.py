r"""
styletest_creation.py — the 30-second style test, first composite frame (Asset Spec §9 step 3).

The integration the whole build order points at: pull the Tier-1/2 pieces into ONE creation tableau
and ask the gate question — *does the look hold together in a frame?* Here: the starlight river
(ENV_Water) winding through the dark, leading the eye to the first Tree (ENV_Tree) materializing into
being (FX_HolographicDissolve), all in liquid starlight, look-dev lit. Still a composite of scaffolds +
first-pass shaders — the owner's hero shader + final staging go on top — but it proves the elements
compose. Animation (music-driven reveal on the chimes) is the next step after the still reads right.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/styletest_creation.py -- --reveal 0.66 --render out.png
"""
import bpy, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree
import tier2_env_water as water
import tier2_fx_holo_dissolve as holo
import lookdev_tree

V = mathutils.Vector


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    reveal = float(argv[argv.index("--reveal") + 1]) if "--reveal" in argv else 0.66
    stage = argv[argv.index("--stage") + 1] if "--stage" in argv else "mid"
    png = argv[argv.index("--render") + 1] if "--render" in argv else None

    tree.clear_scene(); bootstrap.set_units(); bootstrap.ensure_collections()

    # the world the slice lives in
    lookdev_tree.ground()
    river, _ = water.build_river()

    # the first Tree, off the river's near bend, mid-materialization
    obj, p = tree.build_tree(stage)
    obj.location = (10.5, -24.0, 0.0)
    obj.data.materials.clear(); obj.data.materials.append(holo.build_material(reveal))

    # render — a reverent hero 3/4 with the river leading into the tree
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu()
    scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = 110
    try:
        scene.cycles.use_denoising = True
    except Exception:
        pass
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    lookdev_tree.setup_world()

    cam = bootstrap.add_default_camera("CAM_StyleTest", location=(34.0, 8.0, 11.0),
                                       look_at=(9.0, -26.0, 6.0))
    cam.data.lens = 44
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (V(cam.location) - V((10.5, -24.0, 6.0))).length
    cam.data.dof.aperture_fstop = 2.6
    lookdev_tree.sun("RIM", (-1.2, 0.2, -2.0), 2.4, (0.8, 0.9, 1.0))
    lookdev_tree.sun("KEY", (1.0, 0.0, 0.7), 1.1, (0.55, 0.7, 1.0))

    print(f"[styletest] river={len(river.data.vertices)}v · tree={stage}@reveal {reveal:.2f} · device={dev}")
    if png:
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = png
        bpy.ops.render.render(write_still=True)
        print(f"[styletest] rendered -> {png}")


if __name__ == "__main__":
    main()
