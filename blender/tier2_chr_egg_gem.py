r"""
tier2_chr_egg_gem.py — CHR_Egg as a REAL 3D gem asset (the "pop" that 2D post-processing couldn't fake).

The Egg is the film's central recurring hero prop, so it should be a real 3D object with a real material:
a sealed egg whose shell is a mosaic of small faceted GEM-SCALES (Voronoi cells), each a translucent
gemstone tinted across a warm GOLD / RUBY-RED / IVORY palette (owner spec, ancient Egyptian/Mesopotamian),
lit FROM WITHIN by an emissive core so the light glows out through the translucent scales. Total control
over colour + glow + sparkle, renders clean every time, consistent from any angle, animatable. Cycles/OptiX.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/tier2_chr_egg_gem.py -- --render OUT.png
Tunables: --glow (inner-core strength) --emit (per-scale self-glow) --scale (gem-scale count) --seed
"""
import bpy, bmesh, sys, os, math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap, lookdev_tree


def _clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def _set(bsdf, names, value):
    """Set a Principled input by trying a list of version-dependent names."""
    for n in names:
        if n in bsdf.inputs:
            try:
                bsdf.inputs[n].default_value = value; return True
            except Exception:
                pass
    return False


def build_egg(name="CHR_Egg", rz=1.28):
    """A sealed egg silhouette: uv-sphere, elongated and tapered to a softly pointed top."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=72, radius=1.0)
    ob = bpy.context.active_object; ob.name = name
    me = ob.data
    zmax = max(v.co.z for v in me.vertices)
    for v in me.vertices:
        t = max(0.0, v.co.z / zmax)            # 0 at equator-down, 1 at top
        taper = 1.0 - 0.34 * (t ** 2)          # pinch the top into an egg point
        v.co.x *= taper; v.co.y *= taper
        v.co.z *= rz
    for p in me.polygons:
        p.use_smooth = True
    return ob


def gem_material(seed=0, emit=0.45, gem_scale=26.0):
    mat = bpy.data.materials.new("MAT_Egg_Gem"); mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")

    coord = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.voronoi_dimensions = "3D"; vor.feature = "F1"
    vor.inputs["Scale"].default_value = gem_scale
    if "Randomness" in vor.inputs:
        vor.inputs["Randomness"].default_value = 1.0
    nt.links.new(coord.outputs["Object"], vor.inputs["Vector"])

    # per-cell random colour -> warm ramp (ruby -> gold -> ivory) = per-scale warm variety
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(vor.outputs["Color"], sep.inputs["Color"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0.42, 0.02, 0.02, 1)      # deep ruby
    e[1].position = 1.0; e[1].color = (0.95, 0.88, 0.74, 1)      # ivory (not pure white)
    for pos, col in ((0.30, (0.66, 0.07, 0.04, 1)), (0.52, (0.85, 0.50, 0.11, 1)),
                     (0.74, (0.92, 0.73, 0.33, 1))):             # crimson, rich gold, pale gold
        el = ramp.color_ramp.elements.new(pos); el.color = col
    nt.links.new(sep.outputs[0], ramp.inputs["Fac"])            # R of the random cell colour = ramp index

    # faceted relief from the cell-edge distance...
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    nt.links.new(vor.outputs["Distance"], bump.inputs["Height"])
    # ...plus a per-cell FLAT-FACET normal so each gem-scale catches light at its own angle (gem, not confetti)
    cell_ctr = nt.nodes.new("ShaderNodeVectorMath"); cell_ctr.operation = "SUBTRACT"
    cell_ctr.inputs[1].default_value = (0.5, 0.5, 0.5)
    nt.links.new(vor.outputs["Color"], cell_ctr.inputs[0])
    cell_scale = nt.nodes.new("ShaderNodeVectorMath"); cell_scale.operation = "SCALE"
    if "Scale" in cell_scale.inputs:
        cell_scale.inputs["Scale"].default_value = 0.7
    nt.links.new(cell_ctr.outputs["Vector"], cell_scale.inputs[0])
    facet_add = nt.nodes.new("ShaderNodeVectorMath"); facet_add.operation = "ADD"
    nt.links.new(bump.outputs["Normal"], facet_add.inputs[0])
    nt.links.new(cell_scale.outputs["Vector"], facet_add.inputs[1])
    facet_norm = nt.nodes.new("ShaderNodeVectorMath"); facet_norm.operation = "NORMALIZE"
    nt.links.new(facet_add.outputs["Vector"], facet_norm.inputs[0])

    # gem BSDF: coloured, translucent, glossy, faintly self-emissive (so every scale glows)
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    _set(bsdf, ("Roughness",), 0.06)
    _set(bsdf, ("IOR",), 1.55)
    _set(bsdf, ("Transmission Weight", "Transmission"), 0.92)   # colored GLASS gem -> refraction = pop
    _set(bsdf, ("Coat Weight", "Clearcoat"), 0.35)
    _set(bsdf, ("Emission Strength",), emit)
    if not _set(bsdf, ("Emission Color",), None):  # link colour into emission
        pass
    if "Emission Color" in bsdf.inputs:
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission"])
    if "Normal" in bsdf.inputs:
        nt.links.new(facet_norm.outputs["Vector"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def inner_core(parent_z_scale=1.28, glow=7.0):
    """An emissive sphere INSIDE the egg — its light glows out through the translucent gem-scales."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.62, location=(0, 0, 0))
    core = bpy.context.active_object; core.name = "FX_Egg_InnerLight"
    core.scale.z = parent_z_scale
    for p in core.data.polygons:
        p.use_smooth = True
    m = bpy.data.materials.new("MAT_Egg_Core"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Color"].default_value = (1.0, 0.78, 0.42, 1.0)   # warm gold core
    emi.inputs["Strength"].default_value = glow
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emi.outputs["Emission"], o.inputs["Surface"])
    core.data.materials.append(m)
    return core


def setup_bloom():
    """Blender 5.x compositor bloom (fog glow) for the gem 'pop'. Group-output node-graph API."""
    scene = bpy.context.scene
    try: scene.render.use_compositing = True
    except Exception: pass
    ng = None
    if hasattr(scene, "compositing_node_group"):
        ng = scene.compositing_node_group or bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
        scene.compositing_node_group = ng
    else:
        scene.use_nodes = True; ng = scene.node_tree
    for n in list(ng.nodes):
        ng.nodes.remove(n)
    iface = getattr(ng, "interface", None)
    if iface is not None and not any(getattr(s, "in_out", None) == "OUTPUT" for s in iface.items_tree):
        iface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = ng.nodes.new("CompositorNodeRLayers")
    fog = ng.nodes.new("CompositorNodeGlare")
    def _s(node, name, val):
        s = node.inputs.get(name)
        if s is not None:
            try: s.default_value = val
            except Exception: pass
    for k, v in (("Type", "Fog Glow"), ("Quality", "High"), ("Threshold", 0.5), ("Size", 0.7), ("Strength", 0.55)):
        _s(fog, k, v)
    try:
        gout = ng.nodes.new("NodeGroupOutput")
    except Exception:
        gout = ng.nodes.new("CompositorNodeComposite")
    ng.links.new(rl.outputs["Image"], fog.inputs["Image"])
    ng.links.new(fog.outputs["Image"], gout.inputs[0])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    def arg(flag, d, cast=float):
        return cast(argv[argv.index(flag) + 1]) if flag in argv else d
    png = argv[argv.index("--render") + 1] if "--render" in argv else \
        "F:/Inoculated by the Phoenix/_scratch/egg_gem_blender.png"
    glow = arg("--glow", 7.0); emit = arg("--emit", 0.45); gem_scale = arg("--scale", 26.0)
    seed = arg("--seed", 0, int)

    _clear(); bootstrap.set_units(); bootstrap.ensure_collections()
    egg = build_egg()
    egg.data.materials.append(gem_material(seed=seed, emit=emit, gem_scale=gem_scale))
    inner_core(glow=glow)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu(); scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = 160
    try: scene.cycles.use_denoising = True
    except Exception: pass
    scene.render.resolution_x = scene.render.resolution_y = 1080
    scene.view_settings.view_transform = "AgX"

    # dark warm world for reflections (keeps the gem glow popping against black)
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.012, 0.006, 0.004, 1.0); bg.inputs[1].default_value = 0.25

    # key + rim (the inner core does the rest)
    lookdev_tree.sun("KEY", (1.02, 0.0, 0.5), 1.4, (1.0, 0.86, 0.62))
    lookdev_tree.sun("RIM", (-1.15, 0.0, -2.4), 1.1, (1.0, 0.78, 0.5))

    cam = bootstrap.add_default_camera("CAM_Egg", location=(0.0, -5.6, 0.35), look_at=(0.0, 0.0, 0.0))
    cam.data.lens = 85
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 5.6
    cam.data.dof.aperture_fstop = 3.5

    setup_bloom()
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = png
    print(f"[egg-gem] device={dev} glow={glow} emit={emit} scale={gem_scale} -> {png}")
    bpy.ops.render.render(write_still=True)
    print(f"[egg-gem] rendered -> {png}")


if __name__ == "__main__":
    main()
