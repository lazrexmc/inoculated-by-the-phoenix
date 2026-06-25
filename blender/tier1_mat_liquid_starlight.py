r"""
tier1_mat_liquid_starlight.py — MAT_LiquidStarlight, FIRST-PASS scaffold (Asset Spec §6/§7, Tier-1).

The film's single most-reused look (rivers, springs, oceans, the Egg's interior, the Tree's pulse,
the Phoenix's fire base). Per Asset Spec §5 the HERO graph is hand-authored — this is a *working
starting point* so we can see the bioluminescence immediately and you refine from a real base.

It builds `NG_LiquidStarlight` (a shader node group) with the drivable inputs EXPOSED exactly as
§5 wants (Starlight Density, Flow Speed, Noise Scale, Emission Strength) so Python can later drive
"the starlight fades with corruption / returns with the Phoenix" and the tempo-synced flow. The
internal graph: Generated coords -> flowing Noise -> a starlight Color Ramp (deep blue -> teal ->
cyan -> gold) for the iridescent veins, plus a Fresnel rim, into a Principled BSDF emission +
light transmission (glowing translucent liquid).

Run (renders the mature Tree wearing the look):
  "E:\Software\blender.exe" --background --factory-startup --python blender/tier1_mat_liquid_starlight.py -- --stage mature --render out.png
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
        return ng
    ng = bpy.data.node_groups.new("NG_LiquidStarlight", "ShaderNodeTree")
    itf = ng.interface

    def add_in(nm, stype, default=None, mn=None, mx=None):
        s = itf.new_socket(nm, in_out="INPUT", socket_type=stype)
        if default is not None:
            s.default_value = default
        if mn is not None:
            s.min_value = mn
        if mx is not None:
            s.max_value = mx
        return s

    add_in("Starlight Density", "NodeSocketFloat", 1.0, 0.0, 1.0)  # fades with corruption, returns w/ Phoenix
    add_in("Flow Speed", "NodeSocketFloat", 0.10)
    add_in("Noise Scale", "NodeSocketFloat", 3.0)
    add_in("Emission Strength", "NodeSocketFloat", 3.0)
    itf.new_socket("BSDF", in_out="OUTPUT", socket_type="NodeSocketShader")

    n, L = ng.nodes, ng.links
    gi = n.new("NodeGroupInput"); gi.location = (-1000, 0)
    go = n.new("NodeGroupOutput"); go.location = (600, 0)
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1000, -320)
    noise = n.new("ShaderNodeTexNoise"); noise.location = (-720, -240)
    cr = n.new("ShaderNodeValToRGB"); cr.location = (-480, -260)
    fres = n.new("ShaderNodeFresnel"); fres.location = (-720, 220); _set(fres.inputs["IOR"], 1.30)
    bsdf = n.new("ShaderNodeBsdfPrincipled"); bsdf.location = (300, 0)

    # starlight palette ramp: deep blue -> teal -> cyan -> gold
    ramp = cr.color_ramp
    ramp.elements[0].position = 0.0; ramp.elements[0].color = (0.010, 0.030, 0.250, 1.0)
    ramp.elements[1].position = 1.0; ramp.elements[1].color = (1.000, 0.750, 0.300, 1.0)
    e2 = ramp.elements.new(0.40); e2.color = (0.040, 0.500, 0.850, 1.0)
    e3 = ramp.elements.new(0.72); e3.color = (0.200, 0.920, 1.000, 1.0)

    # emission strength = (0.3 + 0.7*noise + 0.5*rim) * Density * Emission Strength
    def math(op, x=None, y=None, loc=(0, 0)):
        m = n.new("ShaderNodeMath"); m.operation = op; m.location = loc
        if x is not None: _set(m.inputs[0], x)
        if y is not None: _set(m.inputs[1], y)
        return m

    mA = math("MULTIPLY", y=0.70, loc=(-480, 320))   # noise*0.7
    mB = math("MULTIPLY", y=0.50, loc=(-480, 180))    # rim*0.5
    mC = math("ADD", y=0.30, loc=(-300, 320))         # +0.3
    mD = math("ADD", loc=(-120, 280))                 # +rim term
    mE = math("MULTIPLY", loc=(60, 240))              # *Density
    mF = math("MULTIPLY", loc=(240, 220))             # *Emission Strength

    L.new(tex.outputs["Generated"], noise.inputs["Vector"])
    L.new(gi.outputs["Noise Scale"], noise.inputs["Scale"])
    L.new(noise.outputs["Fac"], cr.inputs["Fac"])
    L.new(noise.outputs["Fac"], mA.inputs[0])
    L.new(fres.outputs["Fac"], mB.inputs[0])
    L.new(mA.outputs[0], mC.inputs[0])
    L.new(mC.outputs[0], mD.inputs[0]); L.new(mB.outputs[0], mD.inputs[1])
    L.new(mD.outputs[0], mE.inputs[0]); L.new(gi.outputs["Starlight Density"], mE.inputs[1])
    L.new(mE.outputs[0], mF.inputs[0]); L.new(gi.outputs["Emission Strength"], mF.inputs[1])

    L.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    for nm in ("Emission Color", "Emission"):
        if nm in bsdf.inputs:
            L.new(cr.outputs["Color"], bsdf.inputs[nm]); break
    if "Emission Strength" in bsdf.inputs:
        L.new(mF.outputs[0], bsdf.inputs["Emission Strength"])
    _set(bsdf.inputs["Roughness"], 0.12)
    for nm in ("Transmission Weight", "Transmission"):
        if nm in bsdf.inputs and _set(bsdf.inputs[nm], 0.25):
            break
    if "IOR" in bsdf.inputs:
        _set(bsdf.inputs["IOR"], 1.33)
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
    print(f"[starlight] applied MAT_LiquidStarlight (NG_LiquidStarlight) to {obj.name}")
    if png:
        tree.render(obj, p, png)
        print(f"[starlight] rendered -> {png}")


if __name__ == "__main__":
    main()
