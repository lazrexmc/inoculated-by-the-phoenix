r"""
tier2_fx_holo_dissolve.py — FX_HolographicDissolve (NG_HoloDissolve), the materialize-into-being effect.

A reusable holographic dissolve (Asset Spec — futurist-holographic Mesopotamia; things resolve into
existence rather than just appearing). A single `Reveal` 0..1 input sweeps the asset into being from
the base up, with a bright scan-front edge glow, broken up by noise so it reads as energy condensing
into matter — not a wipe. Drivable from Python / the music conductor (creation lands on the chimes).

Scriptable per §5 (it's a parametric node effect, not a hand-painted hero look). Demoed here on the
Tree wearing MAT_LiquidStarlight, but NG_HoloDissolve drops onto any material (alpha + edge emission).

Run (one reveal stage per call):
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier2_fx_holo_dissolve.py -- --reveal 0.6 --render out.png
"""
import bpy, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree
import tier1_mat_liquid_starlight as starlight
import lookdev_tree

V = mathutils.Vector


def _set(inp, val):
    try:
        inp.default_value = val
        return True
    except Exception:
        return False


def build_group():
    ng = bpy.data.node_groups.get("NG_HoloDissolve")
    if ng:
        return ng
    ng = bpy.data.node_groups.new("NG_HoloDissolve", "ShaderNodeTree")
    itf = ng.interface
    r = itf.new_socket("Reveal", in_out="INPUT", socket_type="NodeSocketFloat")
    r.default_value = 0.5; r.min_value = 0.0; r.max_value = 1.1
    ew = itf.new_socket("Edge Width", in_out="INPUT", socket_type="NodeSocketFloat"); ew.default_value = 0.06
    ns = itf.new_socket("Noise Scale", in_out="INPUT", socket_type="NodeSocketFloat"); ns.default_value = 5.0
    itf.new_socket("Fac", in_out="OUTPUT", socket_type="NodeSocketFloat")     # 1 = solid, 0 = not yet formed
    itf.new_socket("Edge", in_out="OUTPUT", socket_type="NodeSocketFloat")    # scan-front glow mask

    n, L = ng.nodes, ng.links
    gi = n.new("NodeGroupInput"); gi.location = (-1000, 0)
    go = n.new("NodeGroupOutput"); go.location = (700, 0)
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1000, -300)
    sep = n.new("ShaderNodeSeparateXYZ"); sep.location = (-820, -240)
    noise = n.new("ShaderNodeTexNoise"); noise.location = (-820, -440)

    def m(op, a=None, b=None, loc=(0, 0)):
        nd = n.new("ShaderNodeMath"); nd.operation = op; nd.location = loc
        if a is not None: _set(nd.inputs[0], a)
        if b is not None: _set(nd.inputs[1], b)
        return nd

    mZ = m("MULTIPLY", b=0.70, loc=(-600, -200))
    mN = m("MULTIPLY", b=0.30, loc=(-600, -380))
    mask = m("ADD", loc=(-430, -280))
    fac = m("LESS_THAN", loc=(-250, -120))       # mask < Reveal -> solid
    diff = m("SUBTRACT", loc=(-250, -320))       # mask - Reveal
    tdiv = m("DIVIDE", loc=(-90, -320))          # /Edge Width
    tsq = m("MULTIPLY", loc=(70, -320))          # squared
    tneg = m("MULTIPLY", b=-1.0, loc=(230, -320))
    edge = m("EXPONENT", loc=(390, -320))        # e^-(t^2) -> bright at the front

    L.new(tex.outputs["Generated"], sep.inputs["Vector"])
    L.new(tex.outputs["Generated"], noise.inputs["Vector"])
    L.new(gi.outputs["Noise Scale"], noise.inputs["Scale"])
    L.new(sep.outputs["Z"], mZ.inputs[0])
    L.new(noise.outputs["Fac"], mN.inputs[0])
    L.new(mZ.outputs[0], mask.inputs[0]); L.new(mN.outputs[0], mask.inputs[1])
    L.new(mask.outputs[0], fac.inputs[0]); L.new(gi.outputs["Reveal"], fac.inputs[1])
    L.new(mask.outputs[0], diff.inputs[0]); L.new(gi.outputs["Reveal"], diff.inputs[1])
    L.new(diff.outputs[0], tdiv.inputs[0]); L.new(gi.outputs["Edge Width"], tdiv.inputs[1])
    L.new(tdiv.outputs[0], tsq.inputs[0]); L.new(tdiv.outputs[0], tsq.inputs[1])
    L.new(tsq.outputs[0], tneg.inputs[0])
    L.new(tneg.outputs[0], edge.inputs[0])
    L.new(fac.outputs[0], go.inputs["Fac"])
    L.new(edge.outputs[0], go.inputs["Edge"])
    return ng


def build_material(reveal):
    mat = bpy.data.materials.get("MAT_HoloDissolve_Tree") or bpy.data.materials.new("MAT_HoloDissolve_Tree")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (500, 0)
    sg = nt.nodes.new("ShaderNodeGroup"); sg.node_tree = starlight.build_group(); sg.location = (-200, 180)
    hg = nt.nodes.new("ShaderNodeGroup"); hg.node_tree = build_group(); hg.location = (-200, -260)
    _set(hg.inputs["Reveal"], reveal)

    emi = nt.nodes.new("ShaderNodeEmission"); emi.location = (60, -120)
    emi.inputs["Color"].default_value = (0.70, 0.95, 1.0, 1.0)
    es = nt.nodes.new("ShaderNodeMath"); es.operation = "MULTIPLY"; es.location = (-30, -260)
    _set(es.inputs[1], 9.0)
    nt.links.new(hg.outputs["Edge"], es.inputs[0])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])

    add = nt.nodes.new("ShaderNodeAddShader"); add.location = (260, 60)
    nt.links.new(sg.outputs["BSDF"], add.inputs[0])
    nt.links.new(emi.outputs["Emission"], add.inputs[1])

    transp = nt.nodes.new("ShaderNodeBsdfTransparent"); transp.location = (260, -120)
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.location = (380, 0)
    nt.links.new(hg.outputs["Fac"], mix.inputs[0])
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(add.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return mat


def render(obj, png):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu()
    scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = 64
    try:
        scene.cycles.use_denoising = True
    except Exception:
        pass
    scene.render.resolution_x, scene.render.resolution_y = 1100, 760
    lookdev_tree.setup_world()
    coords = [obj.matrix_world @ V(c) for c in obj.bound_box]
    cx = sum(c.x for c in coords) / 8; cy = sum(c.y for c in coords) / 8
    zmin = min(c.z for c in coords); zmax = max(c.z for c in coords)
    cz = zmin + (zmax - zmin) * 0.5
    span = max((max(c[i] for c in coords) - min(c[i] for c in coords)) for i in range(3))
    dist = span * 2.0
    cam = bootstrap.add_default_camera("CAM_Holo",
                                       location=(cx + dist * 0.45, cy - dist, cz + span * 0.08),
                                       look_at=(cx, cy, cz))
    cam.data.lens = 50
    lookdev_tree.sun("RIM", (-1.15, 0.0, -2.5), 2.6, (0.8, 0.9, 1.0))
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    reveal = float(argv[argv.index("--reveal") + 1]) if "--reveal" in argv else 0.6
    stage = argv[argv.index("--stage") + 1] if "--stage" in argv else "mature"
    png = argv[argv.index("--render") + 1] if "--render" in argv else None

    tree.clear_scene(); bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = tree.build_tree(stage)
    for mdl in list(obj.data.materials):
        pass
    obj.data.materials.clear(); obj.data.materials.append(build_material(reveal))
    print(f"[holo] {obj.name}: NG_HoloDissolve Reveal={reveal:.2f}")
    if png:
        render(obj, png)
        print(f"[holo] rendered -> {png}")


if __name__ == "__main__":
    main()
