r"""
tier1_env_tree.py — ENV_Tree growth-stage system (Asset Spec §6.2 · Build-Order Tier-1).

ONE parametric asset at stages — Sprout -> Mid -> Mature -> Wounded -> Regrown — driven by a
single parameter set (trunk girth, branch count, canopy spread, luminance), per the spec. Built
as a bmesh skeleton + Skin + Subsurf modifiers (organic tapering tubes). It carries a clearly
labelled PLACEHOLDER emission so it renders; the real bioluminescent liquid-starlight shader is
hand-authored later (Asset Spec §5) and the pulse will come from NG_BioPulse.

Run:
  "E:\Software\blender.exe" --background --factory-startup --python blender/tier1_env_tree.py -- --stage sprout --render out.png
  stages: sprout | mid | mature | wounded | regrown   (omit --render to just build)
"""
import bpy, bmesh, mathutils, math, random, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap

V = mathutils.Vector

# stage -> growth params (the "single driver" the spec asks for)
STAGES = {
    "sprout":  dict(height=0.35, trunk_r=0.018, levels=0, splits=0, angle=18, spread=0.0, lenf=0.70, radf=0.60, segs=3, wobble=0.10, lum=2.0, color=(0.30,0.95,0.80), wounded=False),
    "mid":     dict(height=12.0, trunk_r=0.35,  levels=2, splits=3, angle=35, spread=1.0, lenf=0.66, radf=0.62, segs=4, wobble=0.18, lum=2.5, color=(0.35,0.85,0.95), wounded=False),
    "mature":  dict(height=42.0, trunk_r=1.15,  levels=4, splits=3, angle=38, spread=1.0, lenf=0.70, radf=0.66, segs=4, wobble=0.20, lum=3.0, color=(0.45,0.85,1.00), wounded=False),
    "wounded": dict(height=40.0, trunk_r=1.10,  levels=4, splits=3, angle=44, spread=1.3, lenf=0.66, radf=0.60, segs=4, wobble=0.40, lum=0.6, color=(0.55,0.55,0.60), wounded=True),
    "regrown": dict(height=48.0, trunk_r=1.30,  levels=5, splits=3, angle=36, spread=1.0, lenf=0.71, radf=0.67, segs=4, wobble=0.18, lum=4.0, color=(0.55,0.90,1.00), wounded=False),
}


def _wobble(d, amt):
    return (d + V((random.uniform(-amt, amt), random.uniform(-amt, amt), random.uniform(-amt*0.3, amt*0.3)))).normalized()


def _child_dir(parent, k, n, angle_deg, spread):
    ang = math.radians(angle_deg)
    azimuth = (k / max(n, 1)) * 2*math.pi + random.uniform(-0.35, 0.35)
    up = V((0, 0, 1))
    side = parent.cross(up)
    if side.length < 1e-4:
        side = V((1, 0, 0))
    side.normalize()
    fwd = parent.cross(side).normalized()
    tilt = (math.cos(azimuth)*side + math.sin(azimuth)*fwd) * math.sin(ang) * spread
    return (parent*math.cos(ang) + tilt + V((0, 0, 0.25))).normalized()


def build_skeleton(p):
    bm = bmesh.new()
    verts, radii = [], []

    def add(co, r):
        verts.append(bm.verts.new(co)); radii.append(max(r, 0.006)); return len(verts)-1

    n = p["levels"] + 1
    series = (1 - p["lenf"]**n) / (1 - p["lenf"]) if p["lenf"] != 1 else n
    seg_h = p["height"] / series

    def grow(parent_idx, co, d, length, radius, depth):
        co = co.copy(); cur = parent_idx
        for s in range(p["segs"]):
            d = _wobble((d + V((0, 0, 0.15))).normalized(), p["wobble"])
            co = co + d * (length / p["segs"])
            r = radius * (1 - (s+1)/p["segs"] * 0.45)
            idx = add(co, r); bm.edges.new((verts[cur], verts[idx])); cur = idx
        if depth < p["levels"]:
            for k in range(p["splits"]):
                grow(cur, co, _child_dir(d, k, p["splits"], p["angle"], p["spread"]),
                     length*p["lenf"], radius*p["radf"], depth+1)

    root = add(V((0, 0, 0)), p["trunk_r"])
    grow(root, V((0, 0, 0)), V((0, 0, 1)), seg_h, p["trunk_r"], 0)
    mesh = bpy.data.meshes.new("ENV_Tree")
    bm.to_mesh(mesh); bm.free()
    return mesh, radii


def placeholder_material(color, lum):
    mat = bpy.data.materials.get("MAT_PLACEHOLDER_TreeGlow") or bpy.data.materials.new("MAT_PLACEHOLDER_TreeGlow")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Color"].default_value = (*color, 1.0)
    emi.inputs["Strength"].default_value = lum
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    return mat


def build_tree(stage):
    p = STAGES[stage]
    random.seed(7)
    mesh, radii = build_skeleton(p)
    obj = bpy.data.objects.new(bootstrap.name("env", f"Tree_{stage.capitalize()}"), mesh)
    bootstrap.get_or_create_collection("ENV").objects.link(obj)
    obj.modifiers.new("Skin", "SKIN")
    sv = obj.data.skin_vertices[0].data
    for i, r in enumerate(radii):
        sv[i].radius = (r, r)
    sv[0].use_root = True
    sub = obj.modifiers.new("Subsurf", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
    obj.data.materials.append(placeholder_material(p["color"], p["lum"]))
    return obj, p


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def render(obj, p, png):
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
        bg.inputs[0].default_value = (0.008, 0.011, 0.020, 1.0)
        bg.inputs[1].default_value = 1.0
    # frame the asset from its actual bounds
    coords = [obj.matrix_world @ V(c) for c in obj.bound_box]
    cx = sum(c.x for c in coords)/8; cy = sum(c.y for c in coords)/8; cz = sum(c.z for c in coords)/8
    span = max((max(c[i] for c in coords) - min(c[i] for c in coords)) for i in range(3)) + p["trunk_r"]*2
    dist = max(span*1.9, 0.5)
    bootstrap.add_default_camera("CAM_TreeShot",
                                 location=(cx, cy - dist, cz + span*0.12),
                                 look_at=(cx, cy, cz))
    light = bpy.data.lights.new("FILL", "AREA"); light.energy = max(span*span*1.5, 40); light.size = max(span, 1.0)
    lo = bpy.data.objects.new("FILL", light); lo.location = (dist, -dist, cz + span)
    bootstrap.get_or_create_collection("ENV").objects.link(lo)
    # NOTE: bloom/glow is hand-authored look-dev (Asset Spec §5), added with the real
    # liquid-starlight shader later. The preview renders raw emission.
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    stage = argv[argv.index("--stage")+1] if "--stage" in argv else "sprout"
    png = argv[argv.index("--render")+1] if "--render" in argv else None
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; expected {list(STAGES)}")
    clear_scene()
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = build_tree(stage)
    print(f"[tree] built {obj.name}: base_verts={len(obj.data.vertices)}  target_height~{p['height']}m")
    if png:
        render(obj, p, png)
        print(f"[tree] rendered -> {png}")


if __name__ == "__main__":
    main()
