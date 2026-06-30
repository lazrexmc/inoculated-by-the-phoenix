r"""
build_act1_animatic.py — assemble the FULL Act I ("Fear Inoculum") as an animatic.

Completes Act I as a watchable, full-length sequence: the entire 10:21 song cut from the rendered hero
beats in canon order (FI-001..025), each held for its treatment timecode span with a slow Ken-Burns push,
muxed with the whole track, landing on the false-peace that bridges into Act II (Pneuma). This is the
edit-level "complete Act I" — frame-by-frame hero animation of all 10.5 min is a later render-heavy pass.

  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" blender/build_act1_animatic.py
"""
import os, subprocess, imageio_ffmpeg

S = r"F:\Inoculated by the Phoenix\_scratch"
AUDIO = r"F:\Inoculated by the Phoenix\FearInoculum_Resolve\Audio\Fear Inoculum.mp3"
OUT = os.path.join(S, "act1_full.mp4")
FPS, W, H = 24, 1280, 720

# (still, duration s, label) — durations sum to 621s = 10:21 (the full song)
TIMELINE = [
    ("act1_01_firstlight.png",   8,  "FI-001 First Light"),
    ("act1_02_cosmos.png",      13,  "FI-002/3 Cosmos"),
    ("act1_05_river.png",       13,  "FI-005 Starlight river"),
    ("act1_FI006_sprout.png",   16,  "FI-006 Sprout + springs"),
    ("act1_07_plateau.png",     12,  "FI-007/10 Sacred plateau"),
    ("act1_FI012_egg.png",     116,  "FI-012/16 Egg + Maynder enters"),
    ("act1_FI017_shadow.png",  122,  "FI-017/18 First shadow"),
    ("act1_FI012_egg.png",     154,  "FI-019/22 Egg answers (inoculation)"),
    ("act1_FI023_climax.png",   37,  "FI-023 Inoculation flare"),
    ("act1_FI025_peace.png",   130,  "FI-024/25 False peace -> Pneuma"),
]


def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    assert abs(sum(d for _, d, _ in TIMELINE) - 621) < 2, "timeline must total ~621s"
    os.makedirs(os.path.join(S, "_clips"), exist_ok=True)
    listpath = os.path.join(S, "_clips", "list.txt")
    lines = []
    for i, (fn, dur, label) in enumerate(TIMELINE):
        src = os.path.join(S, fn)
        clip = os.path.join(S, "_clips", f"seg_{i:02d}.mp4")
        nfr = int(dur * FPS)
        # SINGLE image input -> zoompan d=nfr generates exactly nfr frames (a slow Ken-Burns push).
        # (Do NOT use -loop/-t here: a looped stream * d=nfr explodes the frame count.)
        vf = (f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
              f"zoompan=z='min(zoom+0.0006,1.16)':d={nfr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"s={W}x{H}:fps={FPS},setsar=1")
        cmd = [ff, "-y", "-i", src, "-vf", vf, "-frames:v", str(nfr),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-crf", "20", clip]
        print(f"[animatic] seg {i:02d} {dur:>4}s  {label}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        lines.append(f"file '{clip.replace(chr(92), '/')}'")
    with open(listpath, "w") as f:
        f.write("\n".join(lines) + "\n")

    # concat the segments + mux the whole track, cap at 10:21
    cmd = [ff, "-y", "-f", "concat", "-safe", "0", "-i", listpath, "-i", AUDIO,
           "-map", "0:v", "-map", "1:a", "-t", "621",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT]
    print("[animatic] concat + audio ->", OUT)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sz = os.path.getsize(OUT) // 1024
    print(f"[animatic] DONE -> {OUT} ({sz} KB, ~10:21)")


if __name__ == "__main__":
    main()
