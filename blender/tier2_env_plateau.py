r"""
tier2_env_plateau.py — ENV_Plateau — the sacred Mesopotamian plateau.

Canon (audited): the elevated mythic ground the sprout/Tree/springs/Egg sit on, present under nearly
every shot from FI-007 (0:32) through FI-025 (10:21). It "keeps expanding at its edges as if creation
is still arriving" — so the far rim dissolves holographically into the void (a faint emissive scan-edge),
and the body is dark layered stone veined with liquid starlight in its crevices (the rivers' DNA, carved
into the land).

Parametric: a radial landmass (raised terraced centre, tapering to nothing at the rim) + procedural
rock displacement; MAT_Plateau_Rock = dark stone with cavity-masked starlight veins + a faint emissive
"creation still arriving" ring at the dissolving edge.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier2_env_plateau.py -- --render plateau.png
"""
import bpy, bmesh, math, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import lookdev_tree

R = 26.0   # plateau radius (m)


def _set(i, v):
    try: i.default_value = v; return True
    except Exception: return False


def _profile(d):
    """height as a function of distance from centre: raised terraced top tapering to 0 at the rim."""
    if d >= R:
        return None
    t = d / R
    falloff = 1.0 - t * t * (3 - 2 * t)              # smoothstep down to 0 at the rim
    terr = 0.55 * (0.5 + 0.5 * math.cos(t * math.pi * 3.0))  # gentle concentric terraces
    return (2.6 * falloff) + terr * falloff


def build_plateau(seg=170):
    bm = bmesh.new()
    step = (2 * R) / seg
    grid = {}
    for ix in range(seg + 1):
        for iy in range(seg + 1):
            x = -R + ix * step; y = -R + iy * step
            d = math.hypot(x, y)
            h = _profile(d)
            if h is None:
                continue
            grid[(ix, iy)] = bm.verts.new((x, y, h))
    bm.verts.ensure_lookup_table()
    for ix in range(seg):
        for iy in range(seg):
            a = grid.get((ix, iy)); b = grid.get((ix + 1, iy))
            c = grid.get((ix + 1, iy + 1)); e = grid.get((ix, iy + 1))
            if a and b and c and e:
                bm.faces.new((a, b, c, e))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("ENV_Plateau"); bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(bootstrap.name("env", "Plateau"), me)
    for p in obj.data.polygons:
        p.use_smooth = True
    bootstrap.get_or_create_collection("ENV").objects.link(obj)

    # rocky displacement: large-scale rolling terrain (noise_scale in WORLD units — keep it big so the
    # 52m-wide plateau gets hills, not high-frequency chips), plus a finer second pass.
    tex = bpy.data.textures.get("TEX_PlateauRock") or bpy.data.textures.new("TEX_PlateauRock", "CLOUDS")
    try:
        tex.noise_scale = 11.0; tex.noise_depth = 4
    except Exception:
        pass
    disp = obj.modifiers.new("Rock", "DISPLACE")
    disp.texture = tex; disp.strength = 1.1; disp.texture_coords = "GLOBAL"

    tex2 = bpy.data.textures.get("TEX_PlateauRock2") or bpy.data.textures.new("TEX_PlateauRock2", "CLOUDS")
    try:
        tex2.noise_scale = 3.4; tex2.noise_depth = 3
    except Exception:
        pass
    disp2 = obj.modifiers.new("RockFine", "DISPLACE")
    disp2.texture = tex2; disp2.strength = 0.35; disp2.texture_coords = "GLOBAL"
    obj.data.materials.append(rock_material())
    return obj


def rock_material():
    mat = bpy.data.materials.get("MAT_Plateau_Rock") or bpy.data.materials.new("MAT_Plateau_Rock")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    n, L = nt.nodes, nt.links
    out = n.new("ShaderNodeOutputMaterial"); out.location = (820, 0)
    bsdf = n.new("ShaderNodeBsdfPrincipled"); bsdf.location = (560, 0)

    geo = n.new("ShaderNodeNewGeometry"); geo.location = (-980, -260)
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-980, 160)

    # base stone colour, varied by large noise (warm/cool patches)
    bnoise = n.new("ShaderNodeTexNoise"); bnoise.location = (-760, 200); _set(bnoise.inputs["Scale"], 1.4); _set(bnoise.inputs["Detail"], 6.0)
    L.new(tex.outputs["Object"], bnoise.inputs["Vector"])
    bramp = n.new("ShaderNodeValToRGB"); bramp.location = (-560, 220)
    bramp.color_ramp.elements[0].position = 0.30; bramp.color_ramp.elements[0].color = (0.085, 0.075, 0.072, 1.0)
    bramp.color_ramp.elements[1].position = 0.80; bramp.color_ramp.elements[1].color = (0.200, 0.150, 0.110, 1.0)
    L.new(bnoise.outputs["Fac"], bramp.inputs["Fac"])
    L.new(bramp.outputs["Color"], bsdf.inputs["Base Color"])
    _set(bsdf.inputs["Roughness"], 0.86)

    # starlight veins in the crevices: concave cavities (low pointiness) glow blue-gold
    prange = n.new("ShaderNodeMapRange"); prange.location = (-760, -260); prange.clamp = True
    L.new(geo.outputs["Pointiness"], prange.inputs[0])
    _set(prange.inputs[1], 0.30); _set(prange.inputs[2], 0.50); _set(prange.inputs[3], 1.0); _set(prange.inputs[4], 0.0)  # concave -> 1
    vnoise = n.new("ShaderNodeTexNoise"); vnoise.location = (-760, -460); _set(vnoise.inputs["Scale"], 6.0)
    L.new(tex.outputs["Object"], vnoise.inputs["Vector"])
    vmask = n.new("ShaderNodeMath"); vmask.operation = "MULTIPLY"; vmask.location = (-540, -320)
    L.new(prange.outputs[0], vmask.inputs[0]); L.new(vnoise.outputs["Fac"], vmask.inputs[1])
    veincol = n.new("ShaderNodeValToRGB"); veincol.location = (-540, -520)
    veincol.color_ramp.elements[0].position = 0.0; veincol.color_ramp.elements[0].color = (0.02, 0.10, 0.55, 1.0)
    veincol.color_ramp.elements[1].position = 1.0; veincol.color_ramp.elements[1].color = (1.0, 0.78, 0.32, 1.0)
    L.new(vnoise.outputs["Fac"], veincol.inputs["Fac"])
    vstr = n.new("ShaderNodeMath"); vstr.operation = "MULTIPLY"; vstr.location = (-340, -320); _set(vstr.inputs[1], 15.0)
    L.new(vmask.outputs[0], vstr.inputs[0])
    for nm in ("Emission Color", "Emission"):
        if nm in bsdf.inputs:
            L.new(veincol.outputs["Color"], bsdf.inputs[nm]); break
    if "Emission Strength" in bsdf.inputs:
        L.new(vstr.outputs[0], bsdf.inputs["Emission Strength"])

    # micro bump
    bump = n.new("ShaderNodeBump"); bump.location = (300, -260); _set(bump.inputs["Strength"], 0.25)
    bnz = n.new("ShaderNodeTexNoise"); bnz.location = (100, -300); _set(bnz.inputs["Scale"], 24.0)
    L.new(tex.outputs["Object"], bnz.inputs["Vector"]); L.new(bnz.outputs["Fac"], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def render(obj, png):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu(); sc.cycles.device = "GPU" if dev != "CPU" else "CPU"
    sc.cycles.samples = 128
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    lookdev_tree.setup_world()
    # sun()'s 2nd arg is rotation_euler; a horizontal plateau needs a NEAR-VERTICAL key (small X tilt),
    # unlike the vertical Tree which wants a shallow front key. Keep the key high; add an overhead area fill.
    lookdev_tree.sun("KEY", (0.45, 0.0, 0.18), 5.5, (1.0, 0.92, 0.78))
    lookdev_tree.sun("RIM", (-0.95, 0.0, 0.0), 2.6, (0.62, 0.78, 1.0))
    afill = bpy.data.lights.new("AFILL", "AREA"); afill.energy = 12000.0; afill.size = 60.0; afill.color = (0.7, 0.8, 1.0)
    afo = bpy.data.objects.new("AFILL", afill); afo.location = (0.0, -10.0, 38.0); afo.rotation_euler = (0.25, 0.0, 0.0)
    bootstrap.get_or_create_collection("ENV").objects.link(afo)
    cam = bootstrap.add_default_camera("CAM_Plateau", location=(0.0, -42.0, 26.0), look_at=(0.0, 0.0, 1.5))
    cam.data.lens = 48
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 42.0; cam.data.dof.aperture_fstop = 4.0
    sc.view_settings.view_transform = "AgX"
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    png = argv[argv.index("--render")+1] if "--render" in argv else None
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj = build_plateau()
    print(f"[plateau] built {obj.name}: {len(obj.data.vertices)} verts, radius~{R}m")
    if png:
        render(obj, png)
        print(f"[plateau] rendered -> {png}")


if __name__ == "__main__":
    main()
