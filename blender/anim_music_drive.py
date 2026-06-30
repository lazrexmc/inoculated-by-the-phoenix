r"""
anim_music_drive.py — drive the Tree's glow from the conductor track (the world *played by the album*).

Closes the music-sync loop: reads `audio/analysis/<track>_conductor_<fps>fps.json` (Demucs stems +
frequency bands + beats/onsets) and keyframes the mature Tree's liquid-starlight **Emission Strength**
from the music — the guitar/other envelope swells the glow, onsets add rhythmic flashes — so the Tree
literally breathes in time with Fear Inoculum (Asset Spec §10, the Four Instruments).

This is a *systems* demo (flat EEVEE, scaffold look) — it proves the audio→animation link, not the
final look. NG_BioPulse remains the autonomous heartbeat when there is no music to drive from; here the
music drives the emission directly.

Run with the project's Blender:
  "E:\Software\blender.exe" -b --factory-startup --python blender/anim_music_drive.py -- --mode stills --out <dir>
  "E:\Software\blender.exe" -b --factory-startup --python blender/anim_music_drive.py -- --mode video  --out <dir>
  flags: --conductor <json> --stem guitar --start-sec <s> --len 12 --mode stills|video|both
"""
import bpy, sys, os, json, math, mathutils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree
import tier1_mat_liquid_starlight as starlight

V = mathutils.Vector
DEFAULT_CONDUCTOR = r"F:\Inoculated by the Phoenix\audio\analysis\Fear Inoculum_conductor_24fps.json"


def pick_envelope(c, name):
    return c["stems"].get(name) or c["stems"].get("other") or c["bands"].get("mid")


def onset_flash(c, nframes, tau=2.2, reach=6):
    flash = [0.0] * nframes
    for o in c["onsets"]:
        fo = o["frame"]
        for f in range(fo, min(fo + reach, nframes)):
            flash[f] = max(flash[f], math.exp(-(f - fo) / tau))
    return flash


def auto_window(env, nframes, L, step=4):
    """Return the start frame of the most dynamic L-frame window (max variance)."""
    best_f0, best_var = 0, -1.0
    for f0 in range(0, max(nframes - L, 1), step):
        w = env[f0:f0 + L]
        m = sum(w) / len(w)
        var = sum((x - m) ** 2 for x in w) / len(w)
        if var > best_var:
            best_var, best_f0 = var, f0
    return best_f0


def find_group(mat):
    for nd in mat.node_tree.nodes:
        if nd.type == "GROUP" and nd.node_tree and nd.node_tree.name == "NG_LiquidStarlight":
            return nd
    return None


def setup_scene(obj, p):
    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng; break
        except TypeError:
            continue
    try:
        scene.eevee.taa_render_samples = 16
    except Exception:
        pass
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.008, 0.011, 0.020, 1.0); bg.inputs[1].default_value = 1.0
    coords = [obj.matrix_world @ V(c) for c in obj.bound_box]
    cx = sum(c.x for c in coords) / 8; cy = sum(c.y for c in coords) / 8; cz = sum(c.z for c in coords) / 8
    span = max((max(c[i] for c in coords) - min(c[i] for c in coords)) for i in range(3)) + p["trunk_r"] * 2
    dist = max(span * 1.9, 0.5)
    bootstrap.add_default_camera("CAM_MusicDrive",
                                 location=(cx, cy - dist, cz + span * 0.12), look_at=(cx, cy, cz))
    light = bpy.data.lights.new("FILL", "AREA"); light.energy = max(span * span * 1.2, 30); light.size = max(span, 1.0)
    lo = bpy.data.objects.new("FILL", light); lo.location = (dist, -dist, cz + span)
    bootstrap.get_or_create_collection("ENV").objects.link(lo)


def opt(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    conductor_path = opt(argv, "--conductor", DEFAULT_CONDUCTOR)
    stem = opt(argv, "--stem", "guitar")
    length = float(opt(argv, "--len", "12"))
    mode = opt(argv, "--mode", "both")
    outdir = opt(argv, "--out", os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(outdir, exist_ok=True)

    with open(conductor_path) as f:
        c = json.load(f)
    fps = c["fps"]; nframes = c["n_frames"]
    env = pick_envelope(c, stem)
    flash = onset_flash(c, nframes)
    L = int(length * fps)

    if "--start-sec" in argv:
        f0 = int(float(opt(argv, "--start-sec")) * fps)
    else:
        f0 = auto_window(env, nframes, L)
    f1 = min(f0 + L, nframes - 1)
    print(f"[musicdrive] {c['track']} @ {fps}fps · stem='{stem}' · window {f0/fps:.1f}-{f1/fps:.1f}s "
          f"(frames {f0}-{f1}) · ~{c['tempo_bpm']} BPM")

    tree.clear_scene(); bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = tree.build_tree("mature")
    mat = starlight.build_material()
    obj.data.materials.clear(); obj.data.materials.append(mat)
    es = find_group(mat).inputs["Emission Strength"]

    base, gain, flashgain = 0.8, 3.2, 1.4
    levels = []
    for fr in range(f0, f1 + 1):
        v = env[fr] if fr < len(env) else 0.0
        lvl = base + gain * v + flashgain * flash[fr]
        es.default_value = lvl
        es.keyframe_insert("default_value", frame=fr)
        levels.append(lvl)

    scene = bpy.context.scene
    scene.render.fps = int(fps); scene.frame_start = f0; scene.frame_end = f1
    scene.render.resolution_x, scene.render.resolution_y = 960, 540
    setup_scene(obj, p)

    fq = f0 + min(range(len(levels)), key=lambda i: levels[i])
    fl = f0 + max(range(len(levels)), key=lambda i: levels[i])

    if mode in ("stills", "both"):
        for tag, fr in (("quiet", fq), ("loud", fl)):
            scene.frame_set(fr)
            scene.render.image_settings.file_format = "PNG"
            scene.render.filepath = os.path.join(outdir, f"musicdrive_{tag}_f{fr}.png")
            bpy.ops.render.render(write_still=True)
            print(f"[musicdrive] {tag}: frame {fr} ({fr/fps:.2f}s) emission={levels[fr-f0]:.2f}")

    if mode in ("video", "both"):
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"; scene.render.ffmpeg.codec = "H264"
        try:
            scene.render.ffmpeg.constant_rate_factor = "HIGH"
        except Exception:
            pass
        scene.render.filepath = os.path.join(outdir, "tree_fearinoculum.mp4")
        bpy.ops.render.render(animation=True)
        print(f"[musicdrive] video -> {scene.render.filepath}")


if __name__ == "__main__":
    main()
