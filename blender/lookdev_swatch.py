r"""
lookdev_swatch.py — hero material swatch render (the classic look-dev ball).

Renders a chosen NG_ material on a smooth sphere that FILLS the frame, lit to reveal
both the surface (glassy dark-blue glass) and its self-emission (the star-field). This is
how a hero shader is presented — not draped on thin geometry against a void.

Run (liquid starlight):
  "E:\Software\blender.exe" -b --factory-startup --python blender/lookdev_swatch.py -- --mat starlight --out swatch.png
"""
import bpy, sys, os, math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap


def enable_gpu():
    prefs = bpy.context.preferences.addons["cycles"].preferences
    chosen = None
    for backend in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            if any(d.type == backend for d in prefs.devices):
                chosen = backend; break
        except Exception:
            continue
    bpy.context.scene.cycles.device = "GPU" if chosen else "CPU"
    if chosen:
        for d in prefs.devices:
            d.use = (d.type in (chosen, "CPU"))
    return chosen or "CPU"


def world(strength=0.05):
    w = bpy.data.worlds.new("W_Swatch"); bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.006, 0.012, 0.035, 1.0)   # faint cold blue ambient
    bg.inputs[1].default_value = strength


def light(name, loc, energy, size=6.0, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = color
    o = bpy.data.objects.new(name, d); o.location = loc
    bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = (math.radians(0), 0, 0)
    c = o.constraints.new("TRACK_TO"); c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    return o


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    mat_key = argv[argv.index("--mat")+1] if "--mat" in argv else "starlight"
    out = argv[argv.index("--out")+1] if "--out" in argv else "swatch.png"
    samples = int(argv[argv.index("--samples")+1]) if "--samples" in argv else 160

    # fresh scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bootstrap.set_units()

    # the ball
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1.0)
    ball = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    sub = ball.modifiers.new("subsurf", "SUBSURF"); sub.levels = 2; sub.render_levels = 2

    if mat_key == "starlight":
        import tier1_mat_liquid_starlight as ls
        mat = ls.build_material()
    else:
        raise SystemExit(f"unknown --mat {mat_key}")
    ball.data.materials.clear(); ball.data.materials.append(mat)

    # camera — fill the frame
    cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (0, -3.4, 0.35); cam.rotation_euler = (math.radians(84), 0, 0)
    cam_d.lens = 85
    bpy.context.scene.camera = cam
    tc = cam.constraints.new("TRACK_TO"); tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    tgt = bpy.data.objects.new("Tgt", None); tgt.location = (0, 0, 0)
    bpy.context.scene.collection.objects.link(tgt); tc.target = tgt

    # lighting: large soft cool key grazing from above-left (broad, low specular), warm edge rim
    light("Key", (-4.0, -2.2, 3.6), 180, size=10.0, color=(0.80, 0.86, 1.0)).constraints[0].target = tgt
    light("Rim", (3.2, 1.4, -1.0), 150, size=3.0, color=(1.0, 0.82, 0.5)).constraints[0].target = tgt
    world(0.06)

    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    dev = enable_gpu()
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1080; sc.render.resolution_y = 1080
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"   # filmic-style tonemap; preserves the bright cores
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f"[swatch] mat={mat_key} device={dev} samples={samples} -> {out}")


if __name__ == "__main__":
    main()
