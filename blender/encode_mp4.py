r"""
encode_mp4.py — encode a Blender PNG sequence to MP4.

This Blender build was compiled without an FFmpeg codec, so animations render to a PNG sequence and
are encoded here with the ffmpeg binary bundled by `imageio-ffmpeg`. Run with the audio venv:

  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" blender/encode_mp4.py <frames_dir> --out out.mp4 --fps 24
"""
import os, subprocess, argparse
import imageio_ffmpeg


def main():
    ap = argparse.ArgumentParser(description="PNG sequence -> MP4 (H.264)")
    ap.add_argument("frames_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--pattern", default="f_%04d.png")
    ap.add_argument("--start", type=int, default=0)
    args = ap.parse_args()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-framerate", str(args.fps), "-start_number", str(args.start),
           "-i", os.path.join(args.frames_dir, args.pattern),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", args.out]
    print("[encode]", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"[encode] -> {args.out}")


if __name__ == "__main__":
    main()
