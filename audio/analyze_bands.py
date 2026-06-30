r"""
analyze_bands.py — artifact-free frequency-band energy envelopes (off the full master).

Source separation can't pull a specific synth/pad/guitar out of a dense mix like Fear Inoculum, and
its "other" bucket is a junk drawer. Filtering doesn't have that problem: splitting the master into
musical frequency bands gives clean, per-frame energy envelopes with **zero separation artifacts** —
often a better animation driver than a bleedy stem.

Each band → a feel the Blender/UE side can drive with:

    sub  20–60Hz · bass 60–250 · low_mid 250–500 · mid 500–2k · high_mid 2k–4k · presence 4k–6k · brilliance 6k–20k

Run with the audio venv (Python 3.12):
  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" audio\analyze_bands.py "Fear Inoculum" --fps 24
"""
import os, json, argparse
import numpy as np
import librosa

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = r"F:\Inoculated by the Phoenix\FearInoculum_Resolve\Audio"

# (name, low Hz, high Hz) — musical bands, not arbitrary splits
BANDS = [
    ("sub",        20,    60),
    ("bass",       60,    250),
    ("low_mid",    250,   500),
    ("mid",        500,   2000),
    ("high_mid",   2000,  4000),
    ("presence",   4000,  6000),
    ("brilliance", 6000,  20000),
]


def band_envelopes(y, sr, fps, n_fft=2048, hop=512):
    """Return {band: np.array(0..1 per film frame)}, n_frames, duration."""
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop)) ** 2          # power spectrogram
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    stft_t = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
    dur = len(y) / sr
    nframes = int(dur * fps) + 1
    frame_t = np.arange(nframes) / fps

    out = {}
    for name, lo, hi in BANDS:
        mask = (freqs >= lo) & (freqs < hi)
        e = np.sqrt(S[mask].sum(axis=0)) if mask.any() else np.zeros(S.shape[1])
        env = np.interp(frame_t, stft_t, e)
        peak = float(env.max()) or 1.0
        out[name] = (env / peak).round(5)
    return out, nframes, dur


def resolve(track):
    if os.path.isfile(track):
        return track
    for ext in (".mp3", ".wav", ".flac", ".m4a"):
        p = os.path.join(AUDIO_DIR, track + ext)
        if os.path.isfile(p):
            return p
    raise SystemExit(f"[bands] track not found: {track!r}")


def main():
    ap = argparse.ArgumentParser(description="frequency-band energy envelopes")
    ap.add_argument("track")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--out")
    args = ap.parse_args()

    src = resolve(args.track)
    y, sr = librosa.load(src, mono=True)
    bands, nframes, dur = band_envelopes(y, sr, args.fps)
    data = {"file": os.path.basename(src), "sr": sr, "fps": args.fps,
            "duration": round(dur, 3), "n_frames": nframes,
            "bands": {k: v.tolist() for k, v in bands.items()}}
    out = args.out or os.path.join(HERE, "analysis",
                                   os.path.splitext(os.path.basename(src))[0] + f"_bands_{args.fps}fps.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=1)
    print(f"[bands] {data['file']}: {len(BANDS)} bands x {nframes} frames @ {args.fps}fps -> {out}")


if __name__ == "__main__":
    main()
