r"""
tier1_chr_egg.py — CHR_Egg + MAT_EggShell_Iridescent — the sealed protagonist of Act I.

Canon (audited FI-012 .. FI-025):
  - The Egg CONDENSES from psychedelic energy above the Tree at ~1:02 and is held in the Creator's
    cradle. Its iridescent shell "never settles on a color" — neon blues, purples, golds, greens
    folding into themselves.
  - The Egg stays SEALED through ALL of Act I. It can radiate/intensify (FX_InoculationGlow) but the
    shell MUST NEVER crack. Glow is fully independent of any fracture state. The only hatch is Pneuma.
  - It pulses in rhythm with the Tree (NG_BioPulse), and during the inoculation its purity flares
    outward (Glow up) to passively repel the shadow — no hatchling, no strike, no motion.

So this asset is: an egg-form mesh + a hero iridescent shell whose colour-bands fold with a Phase
input (animatable), with a Glow input (drive from NG_BioPulse / raise for the inoculation flare).
The shell is glassy with a clear coat; emission carries the iridescence so it reads in the dark void.

Exposed material inputs (Value nodes, Python/conductor-drivable):
  Phase  — folds the iridescent bands (drive from frame for the "never settles" shimmer)
  Glow   — emission strength multiplier (breathing pulse; spikes for the FI-023 inoculation climax)

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier1_chr_egg.py -- --phase 0.6 --glow 2.5 --render egg.png
"""
import bpy, bmesh, sys, os, math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import lookdev_tree


def _set(i, v):
    try:
        i.default_value = v; return True
    except Exception:
        return False


def build_egg(radius=1.0, height=1.34, name="CHR_Egg"):
    """A clean egg silhouette: a sphere tapered narrower toward the top, stretched in Z."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=48, radius=radius)
    for v in bm.verts:
        t = max(0.0, min(1.0, (v.co.z / radius) * 0.5 + 0.5))   # 0 bottom .. 1 top
        taper = 1.0 - 0.34 * (t ** 1.6)                          # narrow the upper half (egg point)
        v.co.x *= taper; v.co.y *= taper
        v.co.z *= height
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(name, me)
    for p in obj.data.polygons:
        p.use_smooth = True
    bootstrap.get_or_create_collection("CHR").objects.link(obj)
    obj.data.materials.append(build_shell_material())
    return obj


def build_shell_material():
    mat = bpy.data.materials.get("MAT_EggShell_Iridescent") or bpy.data.materials.new("MAT_EggShell_Iridescent")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    n, L = nt.nodes, nt.links
    out = n.new("ShaderNodeOutputMaterial"); out.location = (900, 0)
    bsdf = n.new("ShaderNodeBsdfPrincipled"); bsdf.location = (640, 0)

    phase = n.new("ShaderNodeValue"); phase.label = "Phase"; phase.location = (-1100, -340); phase.outputs[0].default_value = 0.0
    glow = n.new("ShaderNodeValue"); glow.label = "Glow"; glow.location = (-1100, -440); glow.outputs[0].default_value = 2.4

    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1100, 120)

    # swirling fold: object-space noise drifted by Phase so the bands never settle
    drift = n.new("ShaderNodeCombineXYZ"); drift.location = (-920, -160)
    L.new(phase.outputs[0], drift.inputs[0])
    pm = n.new("ShaderNodeMath"); pm.operation = "MULTIPLY"; pm.location = (-1080, -160); _set(pm.inputs[1], 0.5); L.new(phase.outputs[0], pm.inputs[0])
    L.new(pm.outputs[0], drift.inputs[2])
    warp = n.new("ShaderNodeVectorMath"); warp.operation = "ADD"; warp.location = (-740, 40)
    L.new(tex.outputs["Object"], warp.inputs[0]); L.new(drift.outputs[0], warp.inputs[1])
    noise = n.new("ShaderNodeTexNoise"); noise.location = (-560, 40); _set(noise.inputs["Scale"], 2.6); _set(noise.inputs["Detail"], 6.0)
    L.new(warp.outputs[0], noise.inputs["Vector"])

    # Fresnel facing — iridescence peaks at grazing angles
    lw = n.new("ShaderNodeLayerWeight"); lw.location = (-560, -160); _set(lw.inputs["Blend"], 0.45)

    fac = n.new("ShaderNodeMath"); fac.operation = "MULTIPLY_ADD"; fac.location = (-360, 0)
    L.new(noise.outputs["Fac"], fac.inputs[0]); _set(fac.inputs[1], 0.65); L.new(lw.outputs["Facing"], fac.inputs[2])
    facw = n.new("ShaderNodeMath"); facw.operation = "WRAP"; facw.location = (-200, 0); _set(facw.inputs[1], 0.0); _set(facw.inputs[2], 1.0)
    L.new(fac.outputs[0], facw.inputs[0])

    iri = n.new("ShaderNodeValToRGB"); iri.location = (0, 140)
    cr = iri.color_ramp; cr.color_mode = "RGB"; cr.interpolation = "EASE"
    cr.elements[0].position = 0.0;  cr.elements[0].color = (0.04, 0.16, 0.85, 1.0)   # blue
    cr.elements[1].position = 1.0;  cr.elements[1].color = (0.06, 0.22, 0.80, 1.0)   # back to blue (cyclic)
    for pos, col in [(0.22, (0.45, 0.06, 0.78, 1.0)),   # violet
                     (0.45, (0.95, 0.78, 0.22, 1.0)),   # gold
                     (0.68, (0.10, 0.82, 0.45, 1.0))]:   # green
        e = cr.elements.new(pos); e.color = col
    L.new(facw.outputs[0], iri.inputs["Fac"])

    # emission strength: a faint base + a bright rim (facing) so the dark glassy form reads, times Glow
    rim = n.new("ShaderNodeMath"); rim.operation = "MULTIPLY_ADD"; rim.location = (0, -200)
    L.new(lw.outputs["Facing"], rim.inputs[0]); _set(rim.inputs[1], 1.5); _set(rim.inputs[2], 0.14)
    ems = n.new("ShaderNodeMath"); ems.operation = "MULTIPLY"; ems.location = (220, -200)
    L.new(rim.outputs[0], ems.inputs[0]); L.new(glow.outputs[0], ems.inputs[1])

    # dark glassy base; iridescence rides the emission so it glows in the void
    _set(bsdf.inputs["Base Color"], (0.010, 0.013, 0.035, 1.0))
    _set(bsdf.inputs["Roughness"], 0.11)
    for nm in ("Transmission Weight", "Transmission"):
        if nm in bsdf.inputs and _set(bsdf.inputs[nm], 0.18): break
    if "IOR" in bsdf.inputs: _set(bsdf.inputs["IOR"], 1.46)
    for nm in ("Coat Weight", "Coat"):
        if nm in bsdf.inputs and _set(bsdf.inputs[nm], 1.0): break
    if "Coat Roughness" in bsdf.inputs: _set(bsdf.inputs["Coat Roughness"], 0.04)
    for nm in ("Emission Color", "Emission"):
        if nm in bsdf.inputs:
            L.new(iri.outputs["Color"], bsdf.inputs[nm]); break
    if "Emission Strength" in bsdf.inputs:
        L.new(ems.outputs[0], bsdf.inputs["Emission Strength"])

    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def render(obj, png, glow=2.4):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu(); sc.cycles.device = "GPU" if dev != "CPU" else "CPU"
    sc.cycles.samples = 180
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    lookdev_tree.setup_world()
    # a soft cradle of light: cool key, warm under-fill (the Creator's glow from below)
    lookdev_tree.sun("KEY", (-1.0, -0.7, -1.6), 1.1, (0.82, 0.88, 1.0))
    lookdev_tree.sun("UNDER", (0.6, 0.8, 1.2), 0.55, (1.0, 0.8, 0.5))
    cam = bootstrap.add_default_camera("CAM_Egg", location=(0.0, -9.5, 0.4), look_at=(0.0, 0.0, 0.05))
    cam.data.lens = 70
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 9.5; cam.data.dof.aperture_fstop = 3.2
    sc.view_settings.view_transform = "AgX"
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = png
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    phase = float(argv[argv.index("--phase")+1]) if "--phase" in argv else 0.6
    glow = float(argv[argv.index("--glow")+1]) if "--glow" in argv else 2.4
    png = argv[argv.index("--render")+1] if "--render" in argv else None
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj = build_egg()
    # set exposed values
    nt = obj.data.materials[0].node_tree
    for nd in nt.nodes:
        if nd.type == "VALUE" and nd.label == "Phase": nd.outputs[0].default_value = phase
        if nd.type == "VALUE" and nd.label == "Glow":  nd.outputs[0].default_value = glow
    print(f"[egg] built CHR_Egg + MAT_EggShell_Iridescent · phase={phase} glow={glow} · SEALED (Act I canon)")
    if png:
        render(obj, png, glow)
        print(f"[egg] rendered -> {png}")


if __name__ == "__main__":
    main()
