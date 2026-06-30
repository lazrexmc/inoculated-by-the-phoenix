r"""
residual_other.py — build "other" as a RESIDUAL: master - (vocals + drums + bass).

Succumbing to the separation ceiling (owner's call): the models reliably identify vocals, drums,
and bass; everything else (guitar, synths, Danny's mandala pad, ...) is a junk drawer the model
separates badly. So instead of trusting the model's rough "other", we trust only its v/d/b, subtract
them from the master, and DEFINE:

    other_residual = master - vocals - drums - bass

The residual is exactly as clean as the v/d/b we subtract (use the cleanest model available — e.g.
htdemucs_ft). It's a controllable signal we can then refine (band-limit, HPSS, denoise) — see --help
and audio/README.md for the "make other cleaner" options.

Run with the audio venv (Python 3.12):
  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" audio\residual_other.py "Fear Inoculum" --model htdemucs_ft
"""
import os, sys, argparse
import numpy as np
import soundfile as sf
import librosa

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = r"F:\Inoculated by the Phoenix\FearInoculum_Resolve\Audio"
STEMS_DIR = os.path.join(HERE, "stems")
SR = 44100


def resolve_master(track):
    if os.path.isfile(track):
        return track
    for ext in (".mp3", ".wav", ".flac", ".m4a"):
        p = os.path.join(AUDIO_DIR, track + ext)
        if os.path.isfile(p):
            return p
    raise SystemExit(f"[residual] master not found: {track!r}")


def load_stereo(path, sr=SR):
    """-> float32 array shape (n, 2) at sr."""
    y, _ = librosa.load(path, sr=sr, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y])
    return y.T.astype(np.float32)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def main():
    ap = argparse.ArgumentParser(description="other = master - (vocals+drums+bass)")
    ap.add_argument("track")
    ap.add_argument("--model", default="htdemucs_ft", help="stem model dir under stems/ (htdemucs | htdemucs_6s | htdemucs_ft)")
    ap.add_argument("--subtract", default="vocals,drums,bass", help="comma list of stems to remove")
    ap.add_argument("--out", help="output wav (default audio/stems/<model>/<track>/other_residual.wav)")
    args = ap.parse_args()

    master_path = resolve_master(args.track)
    name = os.path.splitext(os.path.basename(master_path))[0]
    sdir = os.path.join(STEMS_DIR, args.model, name)
    if not os.path.isdir(sdir):
        raise SystemExit(f"[residual] stems not found: {sdir} — run separate_stems.py --model {args.model} first")

    master = load_stereo(master_path)
    subtract = [s.strip() for s in args.subtract.split(",") if s.strip()]
    stems = {}
    for s in subtract:
        p = os.path.join(sdir, s + ".wav")
        if not os.path.isfile(p):
            raise SystemExit(f"[residual] missing stem: {p}")
        stems[s] = load_stereo(p)

    n = min([master.shape[0]] + [v.shape[0] for v in stems.values()])
    residual = master[:n].copy()
    for s, v in stems.items():
        residual -= v[:n]

    out = args.out or os.path.join(sdir, "other_residual.wav")
    sf.write(out, residual, SR)

    print(f"[residual] {name}  model={args.model}  removed={subtract}")
    print(f"[residual] RMS  master={rms(master[:n]):.4f}  residual={rms(residual):.4f}  "
          f"({100*rms(residual)/ (rms(master[:n]) or 1):.0f}% of master energy remains)")
    direct = os.path.join(sdir, "other.wav")
    if os.path.isfile(direct):
        d = load_stereo(direct)[:n]
        print(f"[residual] vs model's direct other.wav RMS={rms(d):.4f} "
              f"(diff RMS={rms(residual - d):.5f} — near 0 means the model's stems already sum to the mix)")
    print(f"[residual] -> {out}")


if __name__ == "__main__":
    main()
