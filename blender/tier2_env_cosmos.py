r"""
tier2_env_cosmos.py — ENV_Cosmos, the newborn universe (Act I, Chimes 2-3 @ 0:05-0:16).

After the first point of light (FX_FirstLight), the void inhales: "stars ignite in sequence — first
one, then thousands, then uncountable multitudes. Galaxies spiral outward." This builds a spiral
galaxy of emissive star-points (exponential disc + two arms + a central bulge) over a faint
background starfield, in the dark void. Parametric/scriptable scaffold; hero refinement is the owner's.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier2_env_cosmos.py -- --render out.png
"""
import bpy, bmesh, math, random, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import lookdev_tree

V = mathutils.Vector


def star_material():
    mat = bpy.data.materials.get("MAT_Star") or bpy.data.materials.new("MAT_Star")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Color"].default_value = (0.80, 0.90, 1.0, 1.0)
    emi.inputs["Strength"].default_value = 32.0
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    return mat


def build_galaxy(seed=7):
    random.seed(seed)
    pts = []
    for _ in range(1500):                              # the disc — exponential, two spiral arms
        u = random.random()
        r = -22.0 * math.log(1 - u * 0.985)
        arm = random.choice([0.0, math.pi])
        ang = 0.22 * r + arm + random.gauss(0, 0.34)
        x = r * math.cos(ang); y = r * math.sin(ang)
        z = random.gauss(0, 2.4 * math.exp(-r / 42.0))
        size = random.uniform(0.16, 0.48)
        if random.random() < 0.04:
            size *= random.uniform(1.8, 3.2)
        pts.append((x, y, z, size))
    for _ in range(240):                               # the central bulge
        rr = abs(random.gauss(0, 6.0))
        th = random.uniform(0, 2 * math.pi); ph = random.uniform(0, math.pi)
        pts.append((rr * math.sin(ph) * math.cos(th), rr * math.sin(ph) * math.sin(th),
                    rr * math.cos(ph) * 0.5, random.uniform(0.2, 0.46)))

    bm = bmesh.new()
    for (x, y, z, s) in pts:
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)
        bmesh.ops.translate(bm, verts=res["verts"], vec=(x, y, z))
    me = bpy.data.meshes.new("ENV_Cosmos"); bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(bootstrap.name("env", "Cosmos_Galaxy"), me)
    bootstrap.get_or_create_collection("ENV").objects.link(obj)
    obj.data.materials.append(star_material())
    return obj, len(pts)


def cosmos_world():
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    nt = world.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.004, 0.006, 0.013, 1.0); bg.inputs["Strength"].default_value = 1.0
    # faint background starfield via sharp noise
    tex = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 240.0
    nt.links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.92; cr.color_ramp.elements[0].color = (0, 0, 0, 1)
    cr.color_ramp.elements[1].position = 0.97; cr.color_ramp.elements[1].color = (0.6, 0.7, 1.0, 1)
    nt.links.new(noise.outputs["Fac"], cr.inputs["Fac"])
    add = nt.nodes.new("ShaderNodeAddShader")
    starbg = nt.nodes.new("ShaderNodeBackground"); starbg.inputs["Strength"].default_value = 2.0
    nt.links.new(cr.outputs["Color"], starbg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], add.inputs[0])
    nt.links.new(starbg.outputs["Background"], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    png = argv[argv.index("--render") + 1] if "--render" in argv else None

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj, n = build_galaxy()

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
    cosmos_world()
    cam = bootstrap.add_default_camera("CAM_Cosmos", location=(0.0, -120.0, 62.0), look_at=(0.0, 0.0, 0.0))
    cam.data.lens = 50
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 135.0
    cam.data.dof.aperture_fstop = 3.2

    print(f"[cosmos] galaxy {n} stars · device={dev}")
    if png:
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = png
        bpy.ops.render.render(write_still=True)
        print(f"[cosmos] rendered -> {png}")


if __name__ == "__main__":
    main()
