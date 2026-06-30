r"""
tier2_env_water.py — ENV_Water, the first river of liquid starlight (Asset Spec, Tier-2).

The creation slice's "first river reveal": a meandering channel of MAT_LiquidStarlight winding off
into the dark — rivers are an explicit use of the one liquid-starlight master shader. The geometry is
parametric/scriptable (a meandering ribbon + procedural surface ripples via a Displace modifier); the
hero look is the (owner-hand-authored) starlight shader on top.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier2_env_water.py -- --render out.png
"""
import bpy, bmesh, math, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_mat_liquid_starlight as starlight
import lookdev_tree

V = mathutils.Vector
PARAMS = dict(length=120.0, width=7.0, amp=9.0, freq=1.6, segments=160, ripple=0.18)


def build_river(p=PARAMS):
    bm = bmesh.new()
    n = p["segments"]
    left, right = [], []
    for i in range(n):
        t = i / (n - 1)
        y = -t * p["length"]
        xc = p["amp"] * math.sin(t * p["freq"] * 2 * math.pi) * (0.4 + 0.6 * t)   # widens its wander downstream
        hw = p["width"] * 0.5 * (0.75 + 0.25 * math.sin(t * 3.0))
        left.append(bm.verts.new((xc - hw, y, 0.0)))
        right.append(bm.verts.new((xc + hw, y, 0.0)))
    for i in range(n - 1):
        bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
    bm.normal_update()
    mesh = bpy.data.meshes.new("ENV_Water"); bm.to_mesh(mesh); bm.free()

    obj = bpy.data.objects.new(bootstrap.name("env", "Water_River"), mesh)
    bootstrap.get_or_create_collection("ENV").objects.link(obj)
    sub = obj.modifiers.new("Subsurf", "SUBSURF"); sub.levels = 1; sub.render_levels = 2

    tex = bpy.data.textures.get("TEX_RiverRipple") or bpy.data.textures.new("TEX_RiverRipple", "STUCCI")
    try:
        tex.noise_scale = 1.2
    except Exception:
        pass
    disp = obj.modifiers.new("Ripple", "DISPLACE")
    disp.texture = tex; disp.strength = p["ripple"]; disp.texture_coords = "GLOBAL"
    obj.data.materials.append(starlight.build_material())
    return obj, p


def render(obj, png):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu()
    scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = 96
    try:
        scene.cycles.use_denoising = True
    except Exception:
        pass
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    lookdev_tree.setup_world()
    lookdev_tree.ground()
    cam = bootstrap.add_default_camera("CAM_River", location=(11.0, 14.0, 5.5), look_at=(0.0, -55.0, 0.0))
    cam.data.lens = 42
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 38.0
    cam.data.dof.aperture_fstop = 2.8
    lookdev_tree.sun("RIM", (-1.2, 0.0, -2.2), 2.2, (0.8, 0.9, 1.0))
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    png = argv[argv.index("--render") + 1] if "--render" in argv else None
    lookdev_tree.tree.clear_scene() if hasattr(lookdev_tree, "tree") else None
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = build_river()
    print(f"[water] built {obj.name}: {len(obj.data.vertices)} verts, length~{p['length']}m")
    if png:
        render(obj, png)
        print(f"[water] rendered -> {png}")


if __name__ == "__main__":
    main()
