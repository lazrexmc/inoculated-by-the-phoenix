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
    ap.add_argument("--audio", help="optional audio file to mux (synced slice from --audio-start)")
    ap.add_argument("--audio-start", type=float, default=0.0, help="seconds into the audio to start")
    args = ap.parse_args()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-framerate", str(args.fps), "-start_number", str(args.start),
           "-i", os.path.join(args.frames_dir, args.pattern)]
    if args.audio:
        cmd += ["-ss", str(args.audio_start), "-i", args.audio]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"]
    if args.audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]   # video drives length; audio rides along
    cmd += ["-movflags", "+faststart", args.out]
    print("[encode]", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"[encode] -> {args.out}")


if __name__ == "__main__":
    main()
