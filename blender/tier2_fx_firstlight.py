r"""
tier2_fx_firstlight.py — FX_FirstLight, the genesis (Act I, Chime 1 @ 0:00 — the true first image).

Absolute darkness, then a single point of light in the void — the dot, the breath, the awakening —
expanding outward in concentric ripples, "a crack forming through the fabric of nothingness," each
ripple a new law of physics writing itself into being. This is literally frame 1 of the film.

Parametric/scriptable: a bright emissive core (the point) + a ripple shader (concentric expanding
rings of liquid starlight on a void plane, driven by an animatable Phase). The hero refinement is the
owner's; this is the on-canon scaffold of the opening.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier2_fx_firstlight.py -- --phase 7 --render out.png
"""
import bpy, bmesh, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import lookdev_tree

V = mathutils.Vector


def _set(i, v):
    try:
        i.default_value = v
        return True
    except Exception:
        return False


def ripple_material(phase):
    mat = bpy.data.materials.get("MAT_FirstLight") or bpy.data.materials.new("MAT_FirstLight")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    n, L = nt.nodes, nt.links
    out = n.new("ShaderNodeOutputMaterial"); out.location = (700, 0)
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1000, 0)
    sep = n.new("ShaderNodeSeparateXYZ"); sep.location = (-820, 0)
    L.new(tex.outputs["Object"], sep.inputs["Vector"])
    ph = n.new("ShaderNodeValue"); ph.label = "Phase"; ph.location = (-1000, -260); ph.outputs[0].default_value = phase

    def m(op, a=None, b=None, loc=(0, 0)):
        nd = n.new("ShaderNodeMath"); nd.operation = op; nd.location = loc
        if a is not None: _set(nd.inputs[0], a)
        if b is not None: _set(nd.inputs[1], b)
        return nd

    x2 = m("MULTIPLY", loc=(-640, 80)); L.new(sep.outputs["X"], x2.inputs[0]); L.new(sep.outputs["X"], x2.inputs[1])
    z2 = m("MULTIPLY", loc=(-640, -80)); L.new(sep.outputs["Z"], z2.inputs[0]); L.new(sep.outputs["Z"], z2.inputs[1])
    s = m("ADD", loc=(-480, 0)); L.new(x2.outputs[0], s.inputs[0]); L.new(z2.outputs[0], s.inputs[1])
    dist = m("SQRT", loc=(-320, 0)); L.new(s.outputs[0], dist.inputs[0])

    df = m("MULTIPLY", b=0.42, loc=(-160, 120)); L.new(dist.outputs[0], df.inputs[0])      # dist*freq
    phsub = m("SUBTRACT", loc=(0, 120)); L.new(df.outputs[0], phsub.inputs[0]); L.new(ph.outputs[0], phsub.inputs[1])
    ring = m("SINE", loc=(160, 120)); L.new(phsub.outputs[0], ring.inputs[0])
    r01 = m("MULTIPLY_ADD", a=None, loc=(320, 120)); _set(r01.inputs[1], 0.5); _set(r01.inputs[2], 0.5)
    L.new(ring.outputs[0], r01.inputs[0])
    sharp = m("POWER", b=3.5, loc=(480, 120)); L.new(r01.outputs[0], sharp.inputs[0])

    fneg = m("MULTIPLY", b=-0.03, loc=(160, -120)); L.new(dist.outputs[0], fneg.inputs[0])   # -dist*k
    fall = m("EXPONENT", loc=(320, -120)); L.new(fneg.outputs[0], fall.inputs[0])             # e^(-dist*k)
    fac = m("MULTIPLY", loc=(540, 0)); L.new(sharp.outputs[0], fac.inputs[0]); L.new(fall.outputs[0], fac.inputs[1])
    strength = m("MULTIPLY", b=16.0, loc=(540, -160)); L.new(fac.outputs[0], strength.inputs[0])

    # color: cyan-white core -> deep blue outer, by distance
    cr = n.new("ShaderNodeValToRGB"); cr.location = (300, -340)
    dn = m("MULTIPLY", b=0.012, loc=(140, -340)); L.new(dist.outputs[0], dn.inputs[0])
    L.new(dn.outputs[0], cr.inputs["Fac"])
    ramp = cr.color_ramp
    ramp.elements[0].position = 0.0; ramp.elements[0].color = (0.85, 0.97, 1.0, 1.0)
    ramp.elements[1].position = 1.0; ramp.elements[1].color = (0.02, 0.05, 0.25, 1.0)
    e = ramp.elements.new(0.4); e.color = (0.15, 0.6, 1.0, 1.0)

    emi = n.new("ShaderNodeEmission"); emi.location = (540, 320)
    L.new(cr.outputs["Color"], emi.inputs["Color"])
    L.new(strength.outputs[0], emi.inputs["Strength"])
    L.new(emi.outputs["Emission"], out.inputs["Surface"])
    return mat


def build_genesis(phase):
    # the void plane (XZ, facing the camera) carrying the ripples
    bm = bmesh.new()
    s = 90.0
    for co in ((-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)):
        bm.verts.new(co)
    bm.faces.new(bm.verts)
    me = bpy.data.meshes.new("FX_FirstLight_Field"); bm.to_mesh(me); bm.free()
    field = bpy.data.objects.new("FX_FirstLight_Field", me)
    bootstrap.get_or_create_collection("FX").objects.link(field)
    field.data.materials.append(ripple_material(phase))

    # the point of light — the dot
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.1)
    me = bpy.data.meshes.new("FX_FirstLight_Point"); bm.to_mesh(me); bm.free()
    point = bpy.data.objects.new("FX_FirstLight_Point", me)
    bootstrap.get_or_create_collection("FX").objects.link(point)
    pm = bpy.data.materials.new("MAT_FirstLight_Point"); pm.use_nodes = True
    pnt = pm.node_tree; pnt.nodes.clear()
    o = pnt.nodes.new("ShaderNodeOutputMaterial"); em = pnt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.9, 0.97, 1.0, 1.0); em.inputs["Strength"].default_value = 60.0
    pnt.links.new(em.outputs["Emission"], o.inputs["Surface"])
    point.data.materials.append(pm)
    return field, point


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    phase = float(argv[argv.index("--phase") + 1]) if "--phase" in argv else 7.0
    png = argv[argv.index("--render") + 1] if "--render" in argv else None

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units(); bootstrap.ensure_collections()
    build_genesis(phase)

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
    cam = bootstrap.add_default_camera("CAM_Genesis", location=(0.0, -150.0, 4.0), look_at=(0.0, 0.0, 0.0))
    cam.data.lens = 40
    print(f"[firstlight] genesis @ phase {phase:.1f} · device={dev}")
    if png:
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = png
        bpy.ops.render.render(write_still=True)
        print(f"[firstlight] rendered -> {png}")


if __name__ == "__main__":
    main()
