r"""
tier1_mat_liquid_starlight.py — MAT_LiquidStarlight / NG_LiquidStarlight — the HERO DNA look.

The film's single most-reused shader (rivers, springs, oceans, the Egg's interior, the Tree's pulse,
the Phoenix's fire base). Authored to Lance's art direction (he directs by prompt; Claude produces the
finished look — NOT a hand-author-it-later scaffold):

  "deep dark blue, almost black but still certainly blue ... a 'galaxy' skin with bright star speckles,
   pure white with the smallest thin gold outline and shine (not just a white dot that sparkles) ...
   it should move like a thick resin but swift, as it is part of the cosmos and nothing can stop it."

Graph: a deep near-black-blue nebula base (Base Color + faint emission); a Voronoi star-field whose
cell-centres are pure-white emissive cores ringed by a thin gold rim; the whole field domain-warped by
a time-driven noise so the cosmos flows like thick, swift resin. Glassy/translucent (low roughness +
transmission + IOR ~1.45).

Exposed inputs (Python/conductor-drivable): Starlight Density (fades with corruption), Emission Strength
(breathing), Time (flow phase — drive from frame), Flow Speed, Star Scale.

Run (renders the mature Tree wearing the look; use lookdev_tree.py for the beauty render):
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier1_mat_liquid_starlight.py -- --stage mature --render out.png
"""
import bpy, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree


def _set(node_input, value):
    try:
        node_input.default_value = value
        return True
    except Exception:
        return False


def build_group():
    ng = bpy.data.node_groups.get("NG_LiquidStarlight")
    if ng:
        ng.nodes.clear()
        for it in list(ng.interface.items_tree):
            ng.interface.remove(it)
    else:
        ng = bpy.data.node_groups.new("NG_LiquidStarlight", "ShaderNodeTree")
    itf = ng.interface

    def add_in(nm, default, mn=None, mx=None):
        s = itf.new_socket(nm, in_out="INPUT", socket_type="NodeSocketFloat")
        s.default_value = default
        if mn is not None: s.min_value = mn
        if mx is not None: s.max_value = mx
        return s

    add_in("Starlight Density", 1.0, 0.0, 1.0)   # fades with corruption / returns with the Phoenix
    add_in("Emission Strength", 1.5)             # breathing (conductor-driven)
    add_in("Time", 0.0)                          # flow phase (drive from frame)
    add_in("Flow Speed", 0.15)
    add_in("Star Scale", 9.0)
    itf.new_socket("BSDF", in_out="OUTPUT", socket_type="NodeSocketShader")

    n, L = ng.nodes, ng.links
    gi = n.new("NodeGroupInput"); gi.location = (-1500, 0)
    go = n.new("NodeGroupOutput"); go.location = (2300, 0)
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1500, -420)

    def fm(op, loc, a=None, b=None):
        nd = n.new("ShaderNodeMath"); nd.operation = op; nd.location = loc
        if a is not None: _set(nd.inputs[0], a)
        if b is not None: _set(nd.inputs[1], b)
        return nd

    def vmth(op, loc):
        nd = n.new("ShaderNodeVectorMath"); nd.operation = op; nd.location = loc; return nd

    def rgb(col, loc):
        nd = n.new("ShaderNodeRGB"); nd.location = loc; nd.outputs[0].default_value = (*col, 1.0); return nd

    def mixrgba(loc):                            # in[0]=Factor, in[6]=A(color), in[7]=B(color), out[2]=Result
        nd = n.new("ShaderNodeMix"); nd.data_type = "RGBA"; nd.location = loc; return nd

    # --- flow: a time-driven drift that warps the cosmos (thick but swift) ---
    tphase = fm("MULTIPLY", (-1250, -250)); L.new(gi.outputs["Time"], tphase.inputs[0]); L.new(gi.outputs["Flow Speed"], tphase.inputs[1])
    dX = fm("MULTIPLY", (-1080, -200), b=0.30); L.new(tphase.outputs[0], dX.inputs[0])
    dY = fm("MULTIPLY", (-1080, -300), b=0.15); L.new(tphase.outputs[0], dY.inputs[0])
    drift = n.new("ShaderNodeCombineXYZ"); drift.location = (-920, -260)
    L.new(dX.outputs[0], drift.inputs[0]); L.new(dY.outputs[0], drift.inputs[1]); L.new(tphase.outputs[0], drift.inputs[2])
    warpIn = vmth("ADD", (-920, -40)); L.new(tex.outputs["Object"], warpIn.inputs[0]); L.new(drift.outputs[0], warpIn.inputs[1])
    warpN = n.new("ShaderNodeTexNoise"); warpN.location = (-740, -40); _set(warpN.inputs["Scale"], 1.4)
    _set(warpN.inputs["Detail"], 4.0)
    L.new(warpIn.outputs[0], warpN.inputs["Vector"])
    half = n.new("ShaderNodeCombineXYZ"); half.location = (-740, -230)
    for i in range(3): _set(half.inputs[i], 0.5)
    sub = vmth("SUBTRACT", (-560, -120)); L.new(warpN.outputs["Color"], sub.inputs[0]); L.new(half.outputs[0], sub.inputs[1])
    scl = vmth("SCALE", (-400, -120)); L.new(sub.outputs[0], scl.inputs[0]); _set(scl.inputs["Scale"], 0.7)
    Pw = vmth("ADD", (-220, 40)); L.new(tex.outputs["Object"], Pw.inputs[0]); L.new(scl.outputs[0], Pw.inputs[1])

    # --- the star field ---
    vor = n.new("ShaderNodeTexVoronoi"); vor.location = (-40, 140); vor.voronoi_dimensions = "3D"; vor.feature = "F1"
    L.new(Pw.outputs[0], vor.inputs["Vector"]); L.new(gi.outputs["Star Scale"], vor.inputs["Scale"])
    d = vor.outputs["Distance"]
    rnd = n.new("ShaderNodeSeparateXYZ"); rnd.location = (150, -60); L.new(vor.outputs["Color"], rnd.inputs[0])
    gate = fm("GREATER_THAN", (320, -80), b=0.62); L.new(rnd.outputs["X"], gate.inputs[0])  # star sparsity

    core = n.new("ShaderNodeMapRange"); core.location = (320, 220); core.clamp = True
    L.new(d, core.inputs[0]); _set(core.inputs[1], 0.0); _set(core.inputs[2], 0.12); _set(core.inputs[3], 1.0); _set(core.inputs[4], 0.0)
    halo = n.new("ShaderNodeMapRange"); halo.location = (320, 380); halo.clamp = True   # soft bloom skirt
    L.new(d, halo.inputs[0]); _set(halo.inputs[1], 0.0); _set(halo.inputs[2], 0.34); _set(halo.inputs[3], 0.30); _set(halo.inputs[4], 0.0)
    coreM = fm("MULTIPLY", (500, 200)); L.new(core.outputs[0], coreM.inputs[0]); L.new(gate.outputs[0], coreM.inputs[1])
    haloM = fm("MULTIPLY", (500, 360)); L.new(halo.outputs[0], haloM.inputs[0]); L.new(gate.outputs[0], haloM.inputs[1])

    dsub = fm("SUBTRACT", (320, 60), b=0.155); L.new(d, dsub.inputs[0])    # thin gold ring just OUTSIDE the white core
    tdiv = fm("DIVIDE", (460, 60), b=0.022); L.new(dsub.outputs[0], tdiv.inputs[0])
    t2 = fm("MULTIPLY", (580, 60)); L.new(tdiv.outputs[0], t2.inputs[0]); L.new(tdiv.outputs[0], t2.inputs[1])
    tneg = fm("MULTIPLY", (700, 60), b=-1.0); L.new(t2.outputs[0], tneg.inputs[0])
    ring = fm("EXPONENT", (820, 60)); L.new(tneg.outputs[0], ring.inputs[0])
    rimM = fm("MULTIPLY", (960, 60)); L.new(ring.outputs[0], rimM.inputs[0]); L.new(gate.outputs[0], rimM.inputs[1])

    # --- nebula base: deep dark blue, almost black but certainly blue ---
    nebN = n.new("ShaderNodeTexNoise"); nebN.location = (-220, -300); _set(nebN.inputs["Scale"], 0.8)
    L.new(Pw.outputs[0], nebN.inputs["Vector"])
    nebR = n.new("ShaderNodeValToRGB"); nebR.location = (-30, -320)
    nebR.color_ramp.elements[0].position = 0.25; nebR.color_ramp.elements[0].color = (0.0020, 0.0045, 0.022, 1.0)
    nebR.color_ramp.elements[1].position = 0.85; nebR.color_ramp.elements[1].color = (0.0090, 0.030, 0.110, 1.0)
    L.new(nebN.outputs["Fac"], nebR.inputs["Fac"])

    white = rgb((1.0, 1.0, 1.0), (520, 380))
    gold = rgb((1.0, 0.78, 0.32), (700, 380))
    mixC = mixrgba((700, 280)); L.new(coreM.outputs[0], mixC.inputs[0]); L.new(nebR.outputs["Color"], mixC.inputs[6]); L.new(white.outputs[0], mixC.inputs[7])
    mixG = mixrgba((880, 320)); L.new(rimM.outputs[0], mixG.inputs[0]); L.new(mixC.outputs[2], mixG.inputs[6]); L.new(gold.outputs[0], mixG.inputs[7])

    # --- emission strength: stars blaze, base glows faintly · * Density * Emission Strength ---
    rndS = n.new("ShaderNodeMapRange"); rndS.location = (320, -240); rndS.clamp = True
    L.new(rnd.outputs["X"], rndS.inputs[0]); _set(rndS.inputs[1], 0.0); _set(rndS.inputs[2], 1.0); _set(rndS.inputs[3], 0.5); _set(rndS.inputs[4], 1.0)
    rimW = fm("MULTIPLY", (1100, 60), b=1.15); L.new(rimM.outputs[0], rimW.inputs[0])
    glow = fm("ADD", (1080, 280)); L.new(coreM.outputs[0], glow.inputs[0]); L.new(haloM.outputs[0], glow.inputs[1])
    slum = fm("ADD", (1240, 200)); L.new(glow.outputs[0], slum.inputs[0]); L.new(rimW.outputs[0], slum.inputs[1])
    slum2 = fm("MULTIPLY", (1380, 200)); L.new(slum.outputs[0], slum2.inputs[0]); L.new(rndS.outputs[0], slum2.inputs[1])
    emStars = fm("MULTIPLY", (1520, 200), b=13.0); L.new(slum2.outputs[0], emStars.inputs[0])
    emBase = fm("ADD", (1560, 200), b=0.10); L.new(emStars.outputs[0], emBase.inputs[0])
    emDens = fm("MULTIPLY", (1700, 200)); L.new(emBase.outputs[0], emDens.inputs[0]); L.new(gi.outputs["Starlight Density"], emDens.inputs[1])
    emFin = fm("MULTIPLY", (1840, 200)); L.new(emDens.outputs[0], emFin.inputs[0]); L.new(gi.outputs["Emission Strength"], emFin.inputs[1])

    bsdf = n.new("ShaderNodeBsdfPrincipled"); bsdf.location = (2020, 0)
    L.new(nebR.outputs["Color"], bsdf.inputs["Base Color"])
    for nm in ("Emission Color", "Emission"):
        if nm in bsdf.inputs:
            L.new(mixG.outputs[2], bsdf.inputs[nm]); break
    if "Emission Strength" in bsdf.inputs:
        L.new(emFin.outputs[0], bsdf.inputs["Emission Strength"])
    _set(bsdf.inputs["Roughness"], 0.14)   # thick resin: glossy, not a perfect mirror (softens studio specular)
    for nm in ("Transmission Weight", "Transmission"):
        if nm in bsdf.inputs and _set(bsdf.inputs[nm], 0.32):
            break
    if "IOR" in bsdf.inputs:
        _set(bsdf.inputs["IOR"], 1.45)
    L.new(bsdf.outputs["BSDF"], go.inputs["BSDF"])
    return ng


def build_material():
    mat = bpy.data.materials.get("MAT_LiquidStarlight") or bpy.data.materials.new("MAT_LiquidStarlight")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (300, 0)
    grp = nt.nodes.new("ShaderNodeGroup"); grp.node_tree = build_group(); grp.location = (0, 0)
    nt.links.new(grp.outputs["BSDF"], out.inputs["Surface"])
    return mat


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    stage = argv[argv.index("--stage")+1] if "--stage" in argv else "mature"
    png = argv[argv.index("--render")+1] if "--render" in argv else None
    tree.clear_scene()
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = tree.build_tree(stage)
    mat = build_material()
    obj.data.materials.clear(); obj.data.materials.append(mat)
    print(f"[starlight] applied HERO MAT_LiquidStarlight (NG_LiquidStarlight) to {obj.name}")
    if png:
        tree.render(obj, p, png)
        print(f"[starlight] rendered -> {png}")


if __name__ == "__main__":
    main()
