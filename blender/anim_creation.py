r"""
anim_creation.py — the 30-second style test in MOTION (creation slice, music-driven).

Animates the creation tableau: the first Tree materialising into being (FX_HolographicDissolve sweeps
Reveal 0->1 across the opening), beside the starlight river — with the Four Instruments driving the
light in real time from the conductor track:
    Tree glow  <- the guitar/"other" envelope (Adam -> the Being & the energy of objects)
    River glow <- the bass envelope            (Justin -> light & mood)
Rendered as a bounded ~6 s slice to MP4 (Cycles/OptiX). Still scaffolds + first-pass shaders; this is
the systems-in-motion test, not the final look.

Run (background — it's a Cycles sequence):
  "E:\Software\blender.exe" -b --factory-startup --python blender/anim_creation.py -- --seconds 6 --out <dir>
"""
import bpy, sys, os, json, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree
import tier2_env_water as water
import tier2_fx_holo_dissolve as holo
import lookdev_tree

V = mathutils.Vector
CONDUCTOR = r"F:\Inoculated by the Phoenix\audio\analysis\Fear Inoculum_conductor_24fps.json"


def find_group_node(mat, group_name):
    for nd in mat.node_tree.nodes:
        if nd.type == "GROUP" and nd.node_tree and nd.node_tree.name == group_name:
            return nd
    return None


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def opt(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    seconds = float(opt(argv, "--seconds", "6"))
    outdir = opt(argv, "--out", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_scratch"))
    os.makedirs(outdir, exist_ok=True)

    with open(CONDUCTOR) as f:
        c = json.load(f)
    fps = c["fps"]
    guitar = c["stems"].get("other") or c["bands"]["mid"]   # ft 'other' (residual) = the Being's guitar/synth
    bass = c["stems"].get("bass") or c["bands"]["bass"]

    tree.clear_scene(); bootstrap.set_units(); bootstrap.ensure_collections()
    lookdev_tree.ground()
    river, _ = water.build_river()
    obj, p = tree.build_tree("mid")
    obj.location = (10.5, -24.0, 0.0)
    tmat = holo.build_material(0.0)
    obj.data.materials.clear(); obj.data.materials.append(tmat)

    hg = find_group_node(tmat, "NG_HoloDissolve")          # Reveal
    sg_tree = find_group_node(tmat, "NG_LiquidStarlight")  # Tree glow
    sg_river = find_group_node(river.data.materials[0], "NG_LiquidStarlight")  # River glow

    f0, f1 = 0, int(seconds * fps)
    r0, r1 = int(0.5 * fps), int((seconds - 0.3) * fps)    # tree starts forming after a beat of river
    for fr in range(f0, f1 + 1):
        rev = smoothstep((fr - r0) / max(r1 - r0, 1)) * 1.05
        hg.inputs["Reveal"].default_value = rev
        hg.inputs["Reveal"].keyframe_insert("default_value", frame=fr)

        g = guitar[fr] if fr < len(guitar) else 0.0
        sg_tree.inputs["Emission Strength"].default_value = 1.0 + 3.2 * g
        sg_tree.inputs["Emission Strength"].keyframe_insert("default_value", frame=fr)

        b = bass[fr] if fr < len(bass) else 0.0
        sg_river.inputs["Emission Strength"].default_value = 1.5 + 2.6 * b
        sg_river.inputs["Emission Strength"].keyframe_insert("default_value", frame=fr)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    dev = lookdev_tree.enable_gpu()
    scene.cycles.device = "GPU" if dev != "CPU" else "CPU"
    scene.cycles.samples = 48
    try:
        scene.cycles.use_denoising = True
    except Exception:
        pass
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.fps = int(fps); scene.frame_start = f0; scene.frame_end = f1
    lookdev_tree.setup_world()

    cam = bootstrap.add_default_camera("CAM_StyleTest", location=(34.0, 8.0, 11.0), look_at=(9.0, -26.0, 6.0))
    cam.data.lens = 44
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (V(cam.location) - V((10.5, -24.0, 6.0))).length
    cam.data.dof.aperture_fstop = 2.6
    lookdev_tree.sun("RIM", (-1.2, 0.2, -2.0), 2.4, (0.8, 0.9, 1.0))
    lookdev_tree.sun("KEY", (1.0, 0.0, 0.7), 1.1, (0.55, 0.7, 1.0))

    mode = opt(argv, "--mode", "video")
    print(f"[anim] frames {f0}-{f1} @ {fps}fps · device={dev} · Tree<-guitar, River<-bass, Reveal 0->1 · mode={mode}")
    if mode in ("stills", "both"):
        for fr in (r0, int((r0 + r1) / 2), f1):
            scene.frame_set(fr)
            scene.render.image_settings.file_format = "PNG"
            scene.render.filepath = os.path.join(outdir, f"creation_f{fr:03d}.png")
            bpy.ops.render.render(write_still=True)
            print(f"[anim] still {fr} (reveal={smoothstep((fr-r0)/max(r1-r0,1))*1.05:.2f}) -> creation_f{fr:03d}.png")
    if mode in ("video", "both"):
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"; scene.render.ffmpeg.codec = "H264"
        try:
            scene.render.ffmpeg.constant_rate_factor = "HIGH"
        except Exception:
            pass
        mp4 = os.path.join(outdir, "creation_test.mp4")
        scene.render.filepath = mp4
        bpy.ops.render.render(animation=True)
        print(f"[anim] rendered -> {mp4}")


if __name__ == "__main__":
    main()
