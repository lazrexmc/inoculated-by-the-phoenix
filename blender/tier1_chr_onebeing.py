r"""
tier1_chr_onebeing.py — RIG_OneBeing + CHR_OneBeing proxy (Asset Spec §6 / §8 / §9, Tier-1).

The protagonist. Canon (Asset Spec): ONE being, three readable stages — Eaglet -> mature Eagle
-> Phoenix — sharing topology and ONE skeleton, so each transformation reads as "the same body
remembering itself," not a new creature.

Per §5/§6 the mature Eagle MESH is HAND-SCULPTED by the owner (it is the hero canonical mesh,
like the hero shaders). This script therefore builds only the parts that are properly scripted:

  RIG_OneBeing            one bird armature: spine/neck/head, a tail, two wings (humerus ->
                          radius -> hand -> a long PRIMARY chain sized for the Phoenix's extended
                          span — eaglet/Eagle just constrain/scale the subset), two legs with
                          talons. Symmetric .L/.R. This is what §8 calls for.

  CHR_OneBeing_Proxy      a clearly-labelled BLOCKY PLACEHOLDER (body + head + wing planes + tail)
                          sized to the rig, bound to it so the skeleton is testable now. The owner
                          replaces it with the hand-sculpt; the rig + bindings carry straight over.

  STAGES                  proportion targets for the three shape-key stages (eaglet/eagle/phoenix)
                          the owner will sculpt against — documented here so the derivation is
                          driven by canon, not guessed later.

Run (builds, binds, poses wings up to prove the rig deforms, renders):
  "E:\Software\blender.exe" --background --factory-startup --python blender/tier1_chr_onebeing.py -- --pose fly --render onebeing.png
  poses: rest | fly   (fly raises the wings + bows the head)
"""
import bpy, bmesh, mathutils, math, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree

V = mathutils.Vector

# proportion targets the owner sculpts against (relative to the mature Eagle = 1.0). Canon §6.
STAGES = {
    "eaglet":  dict(scale=0.32, wing_len=0.45, head=1.7, eye=1.3, note="downy, oversized head/feet, stub wings"),
    "eagle":   dict(scale=1.00, wing_len=1.00, head=1.0, eye=1.0, note="canonical hand-sculpt"),
    "phoenix": dict(scale=1.15, wing_len=1.45, head=1.0, eye=1.6, note="extended wing geo + fire layers, twin-sun eyes"),
}

# --- the skeleton ----------------------------------------------------------------------
# centerline bones: (name, head, tail, parent, connect)
SPINE = [
    ("Pelvis", (0, 0.30, 1.00), (0, 0.10, 1.02), None, False),
    ("Spine",  (0, 0.10, 1.02), (0, -0.10, 1.04), "Pelvis", True),
    ("Chest",  (0, -0.10, 1.04), (0, -0.28, 1.06), "Spine", True),
    ("Neck",   (0, -0.28, 1.06), (0, -0.42, 1.14), "Chest", True),
    ("Head",   (0, -0.42, 1.14), (0, -0.56, 1.15), "Neck", True),
    ("Tail",   (0, 0.30, 1.00), (0, 0.64, 0.97), "Pelvis", False),
]
# side chains (built per side, x mirrored): (name, head, tail, parent, connect)
WING = [
    ("Wing_Humerus", (0.07, -0.12, 1.06), (0.40, -0.06, 1.10), "Chest", False),
    ("Wing_Radius",  (0.40, -0.06, 1.10), (0.78, -0.02, 1.08), "Wing_Humerus", True),
    ("Wing_Hand",    (0.78, -0.02, 1.08), (1.02, 0.02, 1.05), "Wing_Radius", True),
    ("Wing_Primary", (1.02, 0.02, 1.05), (1.40, 0.06, 1.00), "Wing_Hand", True),   # Phoenix-length
]
LEG = [
    ("Leg_Thigh", (0.10, 0.20, 0.96), (0.14, 0.22, 0.78), "Pelvis", False),
    ("Leg_Shin",  (0.14, 0.22, 0.78), (0.16, 0.12, 0.60), "Leg_Thigh", True),
    ("Leg_Foot",  (0.16, 0.12, 0.60), (0.17, -0.04, 0.57), "Leg_Shin", True),
    ("Leg_Talon", (0.17, -0.04, 0.57), (0.18, -0.12, 0.55), "Leg_Foot", True),
]


def _mirror(v):
    return (-v[0], v[1], v[2])


def build_rig():
    arm = bpy.data.armatures.new("RIG_OneBeing")
    obj = bpy.data.objects.new("RIG_OneBeing", arm)
    bootstrap.get_or_create_collection("CHR").objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones

    def add(nm, head, tail, parent, connect):
        b = eb.new(nm); b.head = head; b.tail = tail
        if parent:
            b.parent = eb[parent]
        b.use_connect = connect
        return b

    for nm, h, t, par, con in SPINE:
        add(nm, h, t, par, con)
    for s, suf in ((1, ".R"), (-1, ".L")):
        for nm, h, t, par, con in WING + LEG:
            hh = h if s == 1 else _mirror(h)
            tt = t if s == 1 else _mirror(t)
            parent = par + suf if par not in [b[0] for b in SPINE] else par
            add(nm + suf, hh, tt, parent, con)

    bpy.ops.object.mode_set(mode="OBJECT")
    # envelope volumes (fallback deform if auto-weights are unavailable headless)
    for b in arm.bones:
        b.envelope_distance = 0.14
        b.head_radius = b.tail_radius = 0.06
    return obj


# --- the placeholder proxy mesh --------------------------------------------------------
def _sphere(bm, radius, center, scale=(1, 1, 1)):
    try:
        res = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=radius)
    except TypeError:
        res = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, diameter=radius)
    c = V(center)
    for v in res["verts"]:
        v.co = V((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2])) + c
    return res["verts"]


def build_proxy():
    bm = bmesh.new()
    _sphere(bm, 1.0, (0, 0.00, 1.03), scale=(0.18, 0.42, 0.20))   # body
    _sphere(bm, 0.10, (0, -0.49, 1.14))                            # head

    def quad(a, b, c, d):
        bm.faces.new([bm.verts.new(p) for p in (a, b, c, d)])

    for s in (1, -1):
        quad((0.07 * s, -0.16, 1.06), (1.40 * s, 0.00, 1.01),
             (1.28 * s, 0.12, 1.00), (0.10 * s, 0.30, 1.02))       # wing plane
    quad((0.12, 0.30, 1.00), (0.16, 0.66, 0.97),
         (-0.16, 0.66, 0.97), (-0.12, 0.30, 1.00))                 # tail fan
    bm.normal_update()

    mesh = bpy.data.meshes.new("CHR_OneBeing_Proxy")
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(bootstrap.name("char", "OneBeing_Proxy"), mesh)
    bootstrap.get_or_create_collection("CHR").objects.link(obj)
    obj.data.materials.append(_proxy_material())
    return obj


def _proxy_material():
    mat = bpy.data.materials.get("MAT_PLACEHOLDER_OneBeing") or bpy.data.materials.new("MAT_PLACEHOLDER_OneBeing")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Color"].default_value = (0.42, 0.60, 0.85, 1.0)   # placeholder eagle-blue
    emi.inputs["Strength"].default_value = 1.4
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    return mat


def bind(proxy, rig):
    """Auto-weights if the op is available headless, else an envelope Armature modifier."""
    try:
        bpy.ops.object.select_all(action="DESELECT")
        proxy.select_set(True); rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        return "auto-weights"
    except Exception as e:
        print(f"[onebeing] auto-weights unavailable ({e}); using envelope modifier")
        m = proxy.modifiers.get("Armature") or proxy.modifiers.new("Armature", "ARMATURE")
        m.object = rig; m.use_bone_envelopes = True; m.use_vertex_groups = False
        proxy.parent = rig
        return "envelopes"


def pose(rig, kind):
    if kind == "rest":
        return
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    for suf, sign in ((".R", 1), (".L", -1)):
        pb = rig.pose.bones.get("Wing_Humerus" + suf)
        if pb:
            pb.rotation_mode = "XYZ"
            pb.rotation_euler.y = math.radians(38 * sign)   # raise the wings
        pr = rig.pose.bones.get("Wing_Primary" + suf)
        if pr:
            pr.rotation_mode = "XYZ"
            pr.rotation_euler.y = math.radians(20 * sign)   # curl the primaries up
    nb = rig.pose.bones.get("Neck")
    if nb:
        nb.rotation_mode = "XYZ"; nb.rotation_euler.x = math.radians(18)   # slight bow
    bpy.ops.object.mode_set(mode="OBJECT")


def render_bird(proxy, png):
    """A reverent 3/4 high angle so the posed proxy reads as a bird (not head-on like the Tree)."""
    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng; break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = 1200, 800
    try:
        scene.eevee.taa_render_samples = 48
    except Exception:
        pass
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.008, 0.011, 0.020, 1.0); bg.inputs[1].default_value = 1.0
    coords = [proxy.matrix_world @ V(c) for c in proxy.bound_box]
    cx = sum(c.x for c in coords)/8; cy = sum(c.y for c in coords)/8; cz = sum(c.z for c in coords)/8
    span = max((max(c[i] for c in coords) - min(c[i] for c in coords)) for i in range(3))
    dist = max(span*1.5, 1.0)
    bootstrap.add_default_camera("CAM_OneBeing",
                                 location=(cx + dist*0.62, cy - dist*0.85, cz + dist*0.50),
                                 look_at=(cx, cy, cz))
    light = bpy.data.lights.new("KEY", "AREA"); light.energy = max(span*span*60, 400); light.size = max(span, 1.0)
    lo = bpy.data.objects.new("KEY", light); lo.location = (cx + dist, cy - dist, cz + dist*1.2)
    bootstrap.get_or_create_collection("CHR").objects.link(lo)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []

    def opt(flag, default=None):
        return argv[argv.index(flag)+1] if flag in argv else default

    kind = opt("--pose", "fly")
    png = opt("--render")

    tree.clear_scene()
    bootstrap.set_units(); bootstrap.ensure_collections()
    rig = build_rig()
    proxy = build_proxy()
    how = bind(proxy, rig)
    pose(rig, kind)

    nb = len(rig.data.bones)
    print(f"[onebeing] RIG_OneBeing: {nb} bones; proxy {len(proxy.data.vertices)} verts; bound via {how}; pose={kind}")
    print("[onebeing] bone hierarchy:")
    for b in rig.data.bones:
        depth = 0; p = b.parent
        while p:
            depth += 1; p = p.parent
        print("   " + "  " * depth + b.name)
    print("[onebeing] sculpt stages (proportion targets vs mature Eagle=1.0):")
    for k, s in STAGES.items():
        print(f"   {k:8s} scale={s['scale']:.2f} wing={s['wing_len']:.2f} head={s['head']:.1f}  ({s['note']})")

    if png:
        render_bird(proxy, png)
        print(f"[onebeing] rendered -> {png}")


if __name__ == "__main__":
    main()
