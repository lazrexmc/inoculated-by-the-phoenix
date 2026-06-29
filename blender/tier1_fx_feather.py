r"""
tier1_fx_feather.py — FX_Feather + MAT_Feather_StateRange (Asset Spec §6/§9, Tier-1).

The film's core motif. The One Being is feathered; feathers drift, grey with corruption,
ignite with the Phoenix, and the very last speck of the cycle is a single ember-feather.

Two pieces, both parametric (scriptable per §5 — the hero fire graph is hand-authored later):

  FX_Feather            a clean stylized feather mesh — central rachis ridge + smooth vane
                        membrane (bmesh + Subsurf). One silhouette that reads as a feather and
                        carries the state material. Hero barb detailing comes later.

  MAT_Feather_StateRange  ONE material with a single exposed `State` float (0..1) that morphs the
                          feather across its whole life on a ColorRamp:
                              0.00  ash grey      (dormant / wounded)
                              0.45  starlight cyan (alive, luminous — the One Being)
                              0.75  gold
                              1.00  hot ember      (ignited / the final speck)
                          Emission rises with State (ash barely glows; ember burns). `State` is
                          drivable from Python so a feather can age/ignite on cue.

Run (renders the feather at a chosen state; --state picks the life-stage):
  "E:\Software\blender.exe" --background --factory-startup --python blender/tier1_fx_feather.py -- --state 0.45 --render alive.png
  states to try: 0.0 (ash) · 0.45 (starlight) · 1.0 (ember)
"""
import bpy, bmesh, mathutils, math, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree

V = mathutils.Vector

PARAMS = dict(length=0.34, width=0.080, bend=0.075, ridge=0.014, samples=48, sweep=0.12,
              lead=0.78)   # lead = leading (left) vane width vs trailing — feather asymmetry


def _profile(t):
    """Feather half-width as a fraction of max: 0 at base, broad at the shoulder, fine point at tip."""
    rise = math.sin(math.pi * min(t * 1.25, 1.0)) ** 0.70   # shoulder sits earlier
    return max(rise * (1.0 - 0.30 * t), 0.0)                 # longer taper to a slimmer tip


def build_feather(p=PARAMS):
    bm = bmesh.new()
    N = p["samples"]
    rachis, left, right = [], [], []
    for i in range(N):
        t = i / (N - 1)
        z = t * p["length"]
        x_bend = p["bend"] * (t ** 1.5)                 # scythe curve toward the tip
        w = p["width"] * _profile(t)
        wl, wr = w * p["lead"], w                        # leading vane narrower than trailing
        zr = z - p["sweep"] * w                          # edge lags toward the base -> swept barbs
        ridge = p["ridge"] * _profile(t)                 # raised central shaft
        rachis.append(bm.verts.new((x_bend, ridge, z)))
        left.append(bm.verts.new((x_bend - wl, 0.0, zr)))
        right.append(bm.verts.new((x_bend + wr, 0.0, zr)))
    for i in range(N - 1):
        bm.faces.new((rachis[i], left[i], left[i + 1], rachis[i + 1]))
        bm.faces.new((rachis[i], rachis[i + 1], right[i + 1], right[i]))
    bm.normal_update()
    mesh = bpy.data.meshes.new("FX_Feather")
    bm.to_mesh(mesh); bm.free()

    obj = bpy.data.objects.new(bootstrap.name("fx", "Feather"), mesh)
    bootstrap.get_or_create_collection("FX").objects.link(obj)
    sub = obj.modifiers.new("Subsurf", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
    return obj


def _set(node_input, value):
    try:
        node_input.default_value = value
        return True
    except Exception:
        return False


def build_state_group():
    ng = bpy.data.node_groups.get("NG_FeatherState")
    if ng:
        return ng
    ng = bpy.data.node_groups.new("NG_FeatherState", "ShaderNodeTree")
    itf = ng.interface

    s = itf.new_socket("State", in_out="INPUT", socket_type="NodeSocketFloat")
    s.default_value = 0.45; s.min_value = 0.0; s.max_value = 1.0
    es = itf.new_socket("Emission Strength", in_out="INPUT", socket_type="NodeSocketFloat")
    es.default_value = 2.0
    itf.new_socket("BSDF", in_out="OUTPUT", socket_type="NodeSocketShader")

    n, L = ng.nodes, ng.links
    gi = n.new("NodeGroupInput"); gi.location = (-900, 0)
    go = n.new("NodeGroupOutput"); go.location = (600, 0)
    cr = n.new("ShaderNodeValToRGB"); cr.location = (-660, 120)
    bsdf = n.new("ShaderNodeBsdfPrincipled"); bsdf.location = (300, 0)

    # life-stage ramp: ash -> starlight -> gold -> ember
    ramp = cr.color_ramp
    ramp.elements[0].position = 0.0; ramp.elements[0].color = (0.180, 0.185, 0.205, 1.0)
    ramp.elements[1].position = 1.0; ramp.elements[1].color = (1.000, 0.300, 0.070, 1.0)
    e1 = ramp.elements.new(0.45); e1.color = (0.200, 0.850, 1.000, 1.0)
    e2 = ramp.elements.new(0.75); e2.color = (1.000, 0.750, 0.250, 1.0)

    def math_node(op, x=None, y=None, loc=(0, 0)):
        m = n.new("ShaderNodeMath"); m.operation = op; m.location = loc
        if x is not None: _set(m.inputs[0], x)
        if y is not None: _set(m.inputs[1], y)
        return m

    # emission = Emission Strength * (0.18 + 1.7 * State^1.5)   (ash barely glows, ember burns)
    m_pow = math_node("POWER", y=1.5, loc=(-360, -220))
    m_mul = math_node("MULTIPLY", y=1.7, loc=(-180, -220))
    m_add = math_node("ADD", y=0.18, loc=(0, -220))
    m_es = math_node("MULTIPLY", loc=(180, -220))

    L.new(gi.outputs["State"], cr.inputs["Fac"])
    L.new(gi.outputs["State"], m_pow.inputs[0])
    L.new(m_pow.outputs[0], m_mul.inputs[0])
    L.new(m_mul.outputs[0], m_add.inputs[0])
    L.new(m_add.outputs[0], m_es.inputs[0]); L.new(gi.outputs["Emission Strength"], m_es.inputs[1])

    L.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    for nm in ("Emission Color", "Emission"):
        if nm in bsdf.inputs:
            L.new(cr.outputs["Color"], bsdf.inputs[nm]); break
    if "Emission Strength" in bsdf.inputs:
        L.new(m_es.outputs[0], bsdf.inputs["Emission Strength"])
    _set(bsdf.inputs["Roughness"], 0.42)
    L.new(bsdf.outputs["BSDF"], go.inputs["BSDF"])
    return ng


def build_material():
    mat = bpy.data.materials.get("MAT_Feather_StateRange") or bpy.data.materials.new("MAT_Feather_StateRange")
    mat.use_nodes = True
    mat.use_backface_culling = False
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (300, 0)
    grp = nt.nodes.new("ShaderNodeGroup"); grp.node_tree = build_state_group(); grp.location = (0, 0)
    nt.links.new(grp.outputs["BSDF"], out.inputs["Surface"])
    return mat, grp


def apply_state(obj, state):
    mat, grp = build_material()
    obj.data.materials.clear(); obj.data.materials.append(mat)
    _set(grp.inputs["State"], state)
    return mat


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []

    def opt(flag, default=None):
        return argv[argv.index(flag)+1] if flag in argv else default

    state = float(opt("--state", "0.45"))
    png = opt("--render")

    tree.clear_scene()
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj = build_feather()
    apply_state(obj, state)
    print(f"[feather] built {obj.name} ({len(obj.data.vertices)} verts), MAT_Feather_StateRange State={state:.2f}")
    if png:
        tree.render(obj, {"trunk_r": 0.004}, png)
        print(f"[feather] rendered -> {png}")


if __name__ == "__main__":
    main()
