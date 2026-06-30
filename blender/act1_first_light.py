r"""
act1_first_light.py — Act I, FI-001 "First Light" (the literal first instant of the film).

Owner canon (2026-06-30, locked in ProjectDocs/Reference/ART_DIRECTION.md):
  pure ABSOLUTE BLACK -> a single spec of light is brought *through* the black by the opening chime ->
  the light is the exact ANTIQUE BRASS-GOLD of the *Fear Inoculum* lettering (the One Being's light).
  NO blue, NO dotted mesh, NO concentric ripple field. Just black -> one gold spark, blooming on the chime.

This is the one beat better built here than in gen-AI: a single point on true black is almost no "content,"
so SDXL invents structure (mesh/flower/ring). Blender gives an exact, animatable gold spec with a clean
bloom keyed to the downbeat. Gold = the same hue that returns as the Phoenix's fire (the gold through-line).

Still:
  "E:\Software\blender.exe" -b --factory-startup --python blender/act1_first_light.py -- --render OUT.png
Ignition sequence (strength 0 -> peak over the chime, then hold/breathe):
  "E:\Software\blender.exe" -b --factory-startup --python blender/act1_first_light.py -- --frames 96 --out DIR
"""
import bpy, sys, os, math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap, lookdev_tree

# Locked gold = #C9A24B (the lettering), converted sRGB -> scene-linear.
GOLD_LINEAR = (0.585, 0.360, 0.070)


def _clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def black_world():
    """Pure black world — no stars, no volume, no ambient. The void is truly empty."""
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        bg.inputs[1].default_value = 0.0


def build_spec(radius=0.08, strength=22.0):
    """One tiny gold emissive sphere at the origin — the first photon."""
    mesh = bpy.data.meshes.new("FX_FirstLight")
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=radius, location=(0, 0, 0))
    point = bpy.context.active_object
    point.name = "FX_FirstLight"
    for p in point.data.polygons:
        p.use_smooth = True

    mat = bpy.data.materials.new("MAT_FirstLight"); mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Color"].default_value = (*GOLD_LINEAR, 1.0)
    emi.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    point.data.materials.append(mat)
    return point, emi


def setup_compositor():
    """Physically-clean bloom (fog glow) + a faint 6-point chime starburst (streaks).

    Blender 5.x replaced the per-scene compositor (scene.node_tree + a Composite node) with a reusable
    *compositing node group* whose result is a Group Output. Handle both, falling back for <5.x.
    """
    scene = bpy.context.scene
    try: scene.render.use_compositing = True
    except Exception: pass

    ng = None
    if hasattr(scene, "compositing_node_group"):           # Blender 5.x
        ng = scene.compositing_node_group
        if ng is None:
            ng = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
            scene.compositing_node_group = ng
    else:                                                   # Blender <=4.x
        scene.use_nodes = True
        ng = scene.node_tree

    for n in list(ng.nodes):
        ng.nodes.remove(n)
    iface = getattr(ng, "interface", None)
    if iface is not None and not any(getattr(s, "in_out", None) == "OUTPUT" for s in iface.items_tree):
        iface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    def _sock(node, name, value):
        s = node.inputs.get(name)
        if s is not None:
            try: s.default_value = value
            except Exception: pass

    rl = ng.nodes.new("CompositorNodeRLayers")
    # Blender 5.x: glare params are INPUT SOCKETS; the type is a MENU socket taking the display name.
    fog = ng.nodes.new("CompositorNodeGlare")
    for k, v in (("Type", "Fog Glow"), ("Quality", "High"), ("Threshold", 0.12),
                 ("Size", 0.8), ("Strength", 1.0)):
        _sock(fog, k, v)
    star = ng.nodes.new("CompositorNodeGlare")
    for k, v in (("Type", "Streaks"), ("Quality", "High"), ("Threshold", 0.35),
                 ("Streaks", 6), ("Fade", 0.92), ("Strength", 0.6)):
        _sock(star, k, v)
    try:
        gout = ng.nodes.new("NodeGroupOutput")             # 5.x scene compositor result
    except Exception:
        gout = ng.nodes.new("CompositorNodeComposite")     # <=4.x
    ng.links.new(rl.outputs["Image"], fog.inputs["Image"])
    ng.links.new(fog.outputs["Image"], star.inputs["Image"])
    ng.links.new(star.outputs["Image"], gout.inputs[0])


def setup_render(res=(1920, 1080), samples=64):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu()
    scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = samples
    try: scene.cycles.use_denoising = True
    except Exception: pass
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    bootstrap.add_default_camera("CAM_FirstLight", location=(0.0, -18.0, 0.0),
                                 look_at=(0.0, 0.0, 0.0)).data.lens = 50
    return dev


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    png = argv[argv.index("--render") + 1] if "--render" in argv else None
    frames = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 0
    out_dir = argv[argv.index("--out") + 1] if "--out" in argv else None
    peak = float(argv[argv.index("--strength") + 1]) if "--strength" in argv else 22.0

    _clear()
    bootstrap.set_units(); bootstrap.ensure_collections()
    black_world()
    point, emi = build_spec(strength=peak)
    setup_compositor()
    dev = setup_render()
    scene = bpy.context.scene

    if frames > 0:
        out_dir = out_dir or "F:/Inoculated by the Phoenix/_scratch/first_light_seq"
        os.makedirs(out_dir, exist_ok=True)
        scene.frame_start = 1; scene.frame_end = frames
        try: scene.render.fps = 24
        except Exception: pass
        # the spec is BORN by the chime: dark -> fast ignite (frames 1..10) -> gentle breathing hold
        for f in range(1, frames + 1):
            t = (f - 1) / 10.0
            ignite = 0.0 if f <= 1 else min(1.0, t)
            breathe = 1.0 + 0.06 * math.sin((f / frames) * math.pi * 3.0)
            emi.inputs["Strength"].default_value = peak * ignite * breathe
            emi.inputs["Strength"].keyframe_insert("default_value", frame=f)
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = os.path.join(out_dir, "frame_")
        print(f"[first-light] {frames}f @24 device={dev} gold={GOLD_LINEAR} -> {out_dir}")
        bpy.ops.render.render(animation=True)
        print(f"[first-light] done -> {out_dir}")
    else:
        png = png or "F:/Inoculated by the Phoenix/_scratch/ref_first_light_blender.png"
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = png
        print(f"[first-light] still device={dev} gold={GOLD_LINEAR} -> {png}")
        bpy.ops.render.render(write_still=True)
        print(f"[first-light] rendered -> {png}")


if __name__ == "__main__":
    main()
