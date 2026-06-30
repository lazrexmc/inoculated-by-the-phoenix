r"""
lookdev_tree.py — a look-dev pass on ENV_Tree + MAT_LiquidStarlight (scaffold -> film-frame).

NOT a new asset — the SAME mature Tree and the SAME first-pass starlight material as the scaffolds,
but rendered properly: Cycles GI (GPU/OptiX on the RTX 3080), a 3-point-ish moody key/rim, a ground
plane to catch the glow, an atmospheric world volume so the emission haloes (physically-based bloom,
no compositor), depth of field, and higher subdivision. The point is to show what look-dev does to a
scaffold — the hero shader is still owner-hand-authored (Asset Spec §5); this just dresses the stand-in.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/lookdev_tree.py -- --render <out.png>
"""
import bpy, bmesh, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree
import tier1_mat_liquid_starlight as starlight

V = mathutils.Vector


def enable_gpu():
    ca = bpy.context.preferences.addons.get("cycles")
    if not ca:
        return "CPU"
    cp = ca.preferences
    for ctype in ("OPTIX", "CUDA"):
        try:
            cp.compute_device_type = ctype
        except TypeError:
            continue
        try:
            cp.get_devices()
        except Exception:
            pass
        on = False
        for d in cp.devices:
            if d.type == ctype:
                d.use = True; on = True
            elif d.type == "CPU":
                d.use = False
        if on:
            return ctype
    return "CPU"


def ground():
    bm = bmesh.new()
    s = 500.0
    for co in ((-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)):
        bm.verts.new(co)
    bm.faces.new(bm.verts)
    me = bpy.data.meshes.new("ENV_Ground"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("ENV_Ground", me)
    bootstrap.get_or_create_collection("ENV").objects.link(ob)
    mat = bpy.data.materials.new("MAT_Ground"); mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.012, 0.018, 0.030, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.36
    ob.data.materials.append(mat)
    return ob


def setup_world():
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    out = nt.nodes.get("World Output"); bg = nt.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.004, 0.007, 0.016, 1.0); bg.inputs[1].default_value = 0.25
    vol = nt.nodes.new("ShaderNodeVolumeScatter")
    vol.inputs["Density"].default_value = 0.004
    vol.inputs["Color"].default_value = (0.35, 0.55, 1.0, 1.0)
    for nm in ("Anisotropy",):
        if nm in vol.inputs:
            vol.inputs[nm].default_value = 0.45
    if out and "Volume" in out.inputs:
        nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])


def sun(name, rot, energy, color, angle=0.08):
    d = bpy.data.lights.new(name, "SUN"); d.energy = energy; d.color = color
    try:
        d.angle = angle
    except Exception:
        pass
    o = bpy.data.objects.new(name, d); o.rotation_euler = rot
    bootstrap.get_or_create_collection("ENV").objects.link(o)
    return o


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    png = argv[argv.index("--render") + 1] if "--render" in argv else None

    tree.clear_scene(); bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = tree.build_tree("mature")
    mat = starlight.build_material()
    obj.data.materials.clear(); obj.data.materials.append(mat)
    for m in obj.modifiers:
        if m.type == "SUBSURF":
            m.render_levels = 3
    ground()

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = enable_gpu()
    scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = 96
    for attr, val in (("use_denoising", True),):
        try:
            setattr(scene.cycles, attr, val)
        except Exception:
            pass
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.film_transparent = False
    setup_world()

    # frame the tree (tall, ~42 m): a reverent 3/4 angle, looking at mid-height
    coords = [obj.matrix_world @ V(c) for c in obj.bound_box]
    cx = sum(c.x for c in coords) / 8; cy = sum(c.y for c in coords) / 8
    zmin = min(c.z for c in coords); zmax = max(c.z for c in coords)
    cz = zmin + (zmax - zmin) * 0.52
    span = max((max(c[i] for c in coords) - min(c[i] for c in coords)) for i in range(3))
    dist = span * 2.05
    cam = bootstrap.add_default_camera("CAM_LookDev",
                                       location=(cx + dist * 0.5, cy - dist, cz + span * 0.10),
                                       look_at=(cx, cy, cz))
    cam.data.lens = 50
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (V(cam.location) - V((cx, cy, cz))).length
    cam.data.dof.aperture_fstop = 2.2

    # moody key/rim — emission + GI do the rest
    sun("KEY", (1.05, 0.0, 0.6), 1.6, (0.55, 0.7, 1.0))    # cool key, front-left high
    sun("RIM", (-1.15, 0.0, -2.5), 3.2, (0.8, 0.9, 1.0))   # back rim to separate the branches
    fill = bpy.data.lights.new("FILL", "AREA"); fill.energy = span * span * 2.0; fill.size = span
    fo = bpy.data.objects.new("FILL", fill); fo.location = (cx - dist, cy - dist, cz)
    bootstrap.get_or_create_collection("ENV").objects.link(fo)

    print(f"[lookdev] Cycles device={dev}; tree span~{span:.0f}m; samples={scene.cycles.samples}")
    if png:
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = png
        bpy.ops.render.render(write_still=True)
        print(f"[lookdev] rendered -> {png}")


if __name__ == "__main__":
    main()
