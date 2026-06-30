r"""
act1_scene.py — Act I "creation plateau" assembler + the back-half FX (shadow / inoculation glow).

Composes the existing hero assets (ENV_Plateau, ENV_Tree growth stages, CHR_Egg, MAT_LiquidStarlight)
with three Act-I FX built here as first-pass functions — twin springs, the Creator's cradle, the
formless Shadow Deceiver, and the Egg's Inoculation Glow — and renders a hero still per named FI beat.

Canon-bound (audited FI-001..025):
  - the sprout and the Tree are ONE asset at growth stages (ENV_Tree)
  - all springs share MAT_LiquidStarlight (the liquid-starlight DNA)
  - the Egg is SEALED every frame of Act I (glow only, never a crack)
  - the Deceiver is a SENSE/fog — never a form, never a character
  - the inoculation is PASSIVE — the Egg's light repels the shadow; no motion, no hatch
  - Act I ends on a FALSE peace (shadow repelled, not destroyed)

Beats: FI006_sprout · FI012_egg · FI017_shadow · FI023_climax · FI025_peace
Run (one render):
  "E:\Software\blender.exe" -b --factory-startup --python blender/act1_scene.py -- --beat FI012_egg --render out.png
Run (all beats to a folder):
  "E:\Software\blender.exe" -b --factory-startup --python blender/act1_scene.py -- --all DIR
"""
import bpy, bmesh, math, sys, os, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap, lookdev_tree
import tier2_env_plateau as plat
import tier1_env_tree as tree
import tier1_chr_egg as egg
import tier1_mat_liquid_starlight as starlight

V = mathutils.Vector
PLAT_TOP = 3.2   # approx plateau centre height (see tier2_env_plateau._profile)


def _set(i, v):
    try: i.default_value = v; return True
    except Exception: return False


def _emissive(name, color, strength):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1.0); e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"]); return m


# ---------------------------------------------------------------- springs (FX, share starlight DNA)
def build_spring(center, r=2.2, name="ENV_Spring"):
    bm = bmesh.new()
    res = bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=r)
    bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.22), verts=res["verts"])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    for p in ob.data.polygons: p.use_smooth = True
    ob.location = center
    bootstrap.get_or_create_collection("ENV").objects.link(ob)
    ob.data.materials.append(starlight.build_material())   # the same liquid-starlight master shader
    return ob


def build_twin_springs(center, sep=6.0, r=1.5):
    a = build_spring((center[0] - sep*0.5, center[1] + 1.0, center[2]), r=r, name="ENV_Spring_L")
    b = build_spring((center[0] + sep*0.5, center[1] - 1.0, center[2]), r=r, name="ENV_Spring_R")
    return a, b


# ---------------------------------------------------------------- Creator's cradle (Holding Device)
def build_creator_cradle(center, ring_r=1.7):
    """Primordial light given a cradle form: a thin luminous ring cupping the Egg from below + a warm
    under-glow (the Creator's light). Placeholder design — the Holding Device gets its own pass later."""
    ob = None
    try:
        bpy.ops.mesh.primitive_torus_add(major_radius=ring_r, minor_radius=0.14,
                                         location=(center[0], center[1], center[2] - ring_r*0.95),
                                         major_segments=72, minor_segments=12)
        ob = bpy.context.active_object; ob.name = "CHR_Creator_Cradle"
        ob.scale = (1.0, 1.0, 0.6)
        for p in ob.data.polygons: p.use_smooth = True
        ob.data.materials.append(_emissive("MAT_Cradle", (1.0, 0.82, 0.5), 3.0))
    except Exception:
        pass
    li = bpy.data.lights.new("CradleGlow", "POINT"); li.energy = 500.0; li.color = (1.0, 0.8, 0.55); li.shadow_soft_size = 1.6
    lo = bpy.data.objects.new("CradleGlow", li); lo.location = (center[0], center[1], center[2] - ring_r*1.1)
    bootstrap.get_or_create_collection("CHR").objects.link(lo)
    return ob


# ---------------------------------------------------------------- the Egg (sealed) + its glow
def place_egg(center, glow=1.7, phase=0.6):
    obj = egg.build_egg()
    obj.location = center
    nt = obj.data.materials[0].node_tree
    for nd in nt.nodes:
        if nd.type == "VALUE" and nd.label == "Phase": nd.outputs[0].default_value = phase
        if nd.type == "VALUE" and nd.label == "Glow":  nd.outputs[0].default_value = glow
    return obj


def build_inoculation_glow(center, flare=0.0):
    """FX_InoculationGlow — the Egg's outward light that PASSIVELY repels the shadow. Independent of the
    shell (no crack). A point light + a faint additive halo; `flare` 0..1 drives the FI-023 climax."""
    li = bpy.data.lights.new("InoculationGlow", "POINT")
    li.energy = 120.0 + flare * 6000.0
    li.color = (0.85, 0.93, 1.0); li.shadow_soft_size = 2.5
    lo = bpy.data.objects.new("InoculationGlow", li); lo.location = center
    bootstrap.get_or_create_collection("FX").objects.link(lo)
    if flare > 0.05:
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=2.4 + flare*2.0)
        me = bpy.data.meshes.new("FX_InoculationGlow_Halo"); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new("FX_InoculationGlow_Halo", me)
        for p in ob.data.polygons: p.use_smooth = True
        ob.location = center
        bootstrap.get_or_create_collection("FX").objects.link(ob)
        ob.data.materials.append(_emissive("MAT_InocHalo", (0.9, 0.95, 1.0), 2.5 + flare*8.0))
    return lo


# ---------------------------------------------------------------- the Shadow Deceiver (formless fog)
def build_shadow_deceiver(center, reach=0.5, density=6.0, span=70.0):
    """FX_Shadow_Deceiver — a formless dark volume that rings the plateau and presses inward. NEVER a
    form. `reach` 0..1 = how far toward the protected centre it presses (1 = lunge at the Tree)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new("FX_Shadow_Deceiver"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("FX_Shadow_Deceiver", me)
    # a LOW ground-bank that creeps around the plateau — NOT a tall box enveloping the camera/Egg
    ob.location = (center[0], center[1], center[2] + 2.0)
    ob.scale = (span, span, 7.0)
    bootstrap.get_or_create_collection("FX").objects.link(ob)

    m = bpy.data.materials.get("MAT_Shadow_Deceiver") or bpy.data.materials.new("MAT_Shadow_Deceiver")
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    n, L = nt.nodes, nt.links
    out = n.new("ShaderNodeOutputMaterial"); out.location = (700, 0)
    vol = n.new("ShaderNodeVolumePrincipled"); vol.location = (440, 0)
    _set(vol.inputs["Color"], (0.035, 0.040, 0.055, 1.0))   # faint cool scatter so it reads as mist, not a void
    # density = noise * radial-ring mask (low at centre = the protected zone; high at edge)
    tc = n.new("ShaderNodeTexCoord"); tc.location = (-900, 0)
    gen = n.new("ShaderNodeVectorMath"); gen.operation = "SUBTRACT"; gen.location = (-720, 0)
    L.new(tc.outputs["Generated"], gen.inputs[0]); _set(gen.inputs[1], (0.5, 0.5, 0.5))
    ln = n.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; ln.location = (-540, -40); L.new(gen.outputs[0], ln.inputs[0])
    ring = n.new("ShaderNodeMapRange"); ring.location = (-360, -40); ring.clamp = True
    inner = 0.5 * (1.0 - reach)   # the clear centre shrinks as reach -> 1
    _set(ring.inputs[1], inner * 0.55); _set(ring.inputs[2], 0.5); _set(ring.inputs[3], 0.0); _set(ring.inputs[4], 1.0)
    L.new(ln.outputs["Value"], ring.inputs[0])
    noise = n.new("ShaderNodeTexNoise"); noise.location = (-360, 200); _set(noise.inputs["Scale"], 2.6); _set(noise.inputs["Detail"], 8.0)
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    dmul = n.new("ShaderNodeMath"); dmul.operation = "MULTIPLY"; dmul.location = (-140, 80)
    L.new(ring.outputs[0], dmul.inputs[0]); L.new(noise.outputs["Fac"], dmul.inputs[1])
    dens = n.new("ShaderNodeMath"); dens.operation = "MULTIPLY"; dens.location = (60, 80); _set(dens.inputs[1], density)
    L.new(dmul.outputs[0], dens.inputs[0])
    L.new(dens.outputs[0], vol.inputs["Density"])
    L.new(vol.outputs[0], out.inputs["Volume"])
    ob.data.materials.append(m)
    return ob


# ---------------------------------------------------------------- assembly per beat
def _tree_at(stage, z=PLAT_TOP):
    obj, p = tree.build_tree(stage)
    obj.location = (0.0, 0.0, z - 0.15)
    return obj, p


def assemble(beat):
    bootstrap.set_units(); bootstrap.ensure_collections()
    plat.build_plateau()
    c = (0.0, 0.0, PLAT_TOP)

    if beat == "FI006_sprout":
        sp, _ = _tree_at("sprout"); sp.scale = (3.2, 3.2, 3.2)   # scale the fragile sprout up for screen presence
        build_twin_springs(c, sep=4.4, r=1.25)
        cam = bootstrap.add_default_camera("CAM", location=(2.8, -5.4, 4.3), look_at=(0.0, 0.0, 3.6)); cam.data.lens = 50
        return cam, dict(key=2.6, fill=5000, mood="genesis")

    tree_obj, tp = _tree_at("mid")
    egg_z = PLAT_TOP + tp["height"] + 3.2
    ec = (0.0, 0.0, egg_z)
    build_twin_springs(c, sep=6.5, r=1.6)

    if beat == "FI012_egg":
        place_egg(ec, glow=1.5); build_creator_cradle(ec); build_inoculation_glow(ec, flare=0.05)
        cam = bootstrap.add_default_camera("CAM", location=(17.0, -37.0, 12.0), look_at=(0.0, 0.0, 10.5)); cam.data.lens = 44
        return cam, dict(key=2.2, fill=4200, mood="reveal")

    if beat == "FI017_shadow":
        place_egg(ec, glow=1.6); build_creator_cradle(ec); build_inoculation_glow(ec, flare=0.0)
        build_shadow_deceiver(c, reach=0.35, density=0.22)
        cam = bootstrap.add_default_camera("CAM", location=(19.0, -42.0, 12.0), look_at=(0.0, 0.0, 7.5)); cam.data.lens = 42
        return cam, dict(key=1.4, fill=2200, mood="threat")

    if beat == "FI023_climax":
        place_egg(ec, glow=3.4); build_creator_cradle(ec); build_inoculation_glow(ec, flare=0.9)
        build_shadow_deceiver(c, reach=0.55, density=0.32)
        cam = bootstrap.add_default_camera("CAM", location=(19.0, -42.0, 12.0), look_at=(0.0, 0.0, 7.5)); cam.data.lens = 42
        return cam, dict(key=1.2, fill=1800, mood="climax")

    if beat == "FI025_peace":
        place_egg(ec, glow=1.05); build_creator_cradle(ec); build_inoculation_glow(ec, flare=0.1)
        cam = bootstrap.add_default_camera("CAM", location=(28.0, -64.0, 25.0), look_at=(0.0, 0.0, egg_z*0.5)); cam.data.lens = 42
        return cam, dict(key=2.4, fill=4600, mood="false_peace")

    raise SystemExit(f"unknown beat {beat}")


def render(beat, png):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    cam, cfg = assemble(beat)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu(); sc.cycles.device = "GPU" if dev != "CPU" else "CPU"
    sc.cycles.samples = 140
    try: sc.cycles.use_denoising = True
    except Exception: pass
    try: sc.cycles.volume_max_steps = 256
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    lookdev_tree.setup_world()
    lookdev_tree.sun("KEY", (0.5, 0.0, 0.2), cfg["key"], (1.0, 0.93, 0.8))
    lookdev_tree.sun("RIM", (-0.95, 0.0, 0.0), cfg["key"]*0.6, (0.62, 0.78, 1.0))
    afill = bpy.data.lights.new("AFILL", "AREA"); afill.energy = cfg["fill"]; afill.size = 70.0; afill.color = (0.7, 0.8, 1.0)
    afo = bpy.data.objects.new("AFILL", afill); afo.location = (0.0, -16.0, 44.0); afo.rotation_euler = (0.3, 0.0, 0.0)
    bootstrap.get_or_create_collection("ENV").objects.link(afo)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (V(cam.location)).length
    cam.data.dof.aperture_fstop = 3.5
    sc.view_settings.view_transform = "AgX"
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = png
    bpy.ops.render.render(write_still=True)
    print(f"[act1] {beat} ({cfg['mood']}) device={dev} -> {png}")


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if "--all" in argv:
        d = argv[argv.index("--all")+1]
        for beat in ("FI006_sprout", "FI012_egg", "FI017_shadow", "FI023_climax", "FI025_peace"):
            render(beat, os.path.join(d, f"act1_{beat}.png"))
    else:
        beat = argv[argv.index("--beat")+1] if "--beat" in argv else "FI012_egg"
        png = argv[argv.index("--render")+1] if "--render" in argv else "act1_scene.png"
        render(beat, png)


if __name__ == "__main__":
    main()
