r"""
act1_genesis_anim.py — Act I, FI-001: the First Light, animated (the literal first seconds of the film).

Black void -> a point of white-gold light ignites on the chime -> concentric ripples expand outward,
each "a new law of physics writing itself into being." Renders a PNG sequence; encode with the opening
of the album via encode_mp4.py so the ignition lands on Chime 1.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/act1_genesis_anim.py -- --frames 72 --out DIR
"""
import bpy, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap, lookdev_tree
import tier2_fx_firstlight as fl


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    frames = int(argv[argv.index("--frames")+1]) if "--frames" in argv else 72
    out = argv[argv.index("--out")+1] if "--out" in argv else "F:/Inoculated by the Phoenix/_scratch/genesis_seq"
    os.makedirs(out, exist_ok=True)

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units(); bootstrap.ensure_collections()
    field, point = fl.build_genesis(phase=0.0)

    # locate the animatable nodes
    phase_node = next((nd for nd in field.data.materials[0].node_tree.nodes
                       if nd.type == "VALUE" and nd.label == "Phase"), None)
    emi = next((nd for nd in point.data.materials[0].node_tree.nodes if nd.type == "EMISSION"), None)

    sc = bpy.context.scene
    sc.frame_start = 1; sc.frame_end = frames
    try: sc.render.fps = 24
    except Exception: pass

    for f in range(1, frames + 1):
        t = (f - 1) / (frames - 1)                      # 0..1
        # ripples sweep outward: Phase climbs steadily
        if phase_node:
            phase_node.outputs[0].default_value = t * 17.0
            phase_node.outputs[0].keyframe_insert("default_value", frame=f)
        # the point ignites fast (frames 1-6), then holds and breathes
        if emi:
            ignite = min(1.0, (f - 1) / 5.0)
            emi.inputs["Strength"].default_value = 60.0 * ignite
            emi.inputs["Strength"].keyframe_insert("default_value", frame=f)

    # render setup (Cycles/OptiX, the genesis void)
    sc.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu(); sc.cycles.device = "GPU" if dev != "CPU" else "CPU"
    sc.cycles.samples = 48
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    lookdev_tree.setup_world()
    bootstrap.add_default_camera("CAM_Genesis", location=(0.0, -150.0, 4.0), look_at=(0.0, 0.0, 0.0)).data.lens = 40
    sc.view_settings.view_transform = "AgX"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.join(out, "frame_")
    print(f"[genesis-anim] {frames} frames @24fps device={dev} -> {out}")
    bpy.ops.render.render(animation=True)
    print(f"[genesis-anim] done -> {out}")


if __name__ == "__main__":
    main()
