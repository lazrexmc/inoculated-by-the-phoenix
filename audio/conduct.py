r"""
conduct.py — the consolidated per-frame "conductor track" + a visual analysis dashboard.

Fuses everything the music-sync side needs into ONE artifact per track, keyed by film frame, plus a
PNG dashboard you can actually inspect (does the drum envelope spike on the hits? do beats line up?).

Honest division of labor (separation has a hard ceiling on a dense mix — see audio/README.md):
  - per-stem energy  (Demucs 6-stem if present, else 4-stem)  -> broad, bleed-tolerant family intensity
  - frequency-band energy (off the master, artifact-free)     -> clean continuous drivers
  - beats / onsets / tempo (librosa)                          -> NG_BioPulse Rate + FX/cut frames
  - the owner's ear-annotations (in the Treatment)            -> the AUTHORITATIVE event track (not here)

Run with the audio venv (Python 3.12):
  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" audio\conduct.py "Fear Inoculum" --fps 24
"""
import os, json, glob, argparse
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze_bands import band_envelopes, BANDS, resolve

HERE = os.path.dirname(os.path.abspath(__file__))
STEMS_DIR = os.path.join(HERE, "stems")

STEM_COLORS = {"drums": "#ff5566", "bass": "#ffb000", "guitar": "#55ff99",
               "vocals": "#66ccff", "piano": "#c98bff", "other": "#9aa0a6"}


def find_stems(track):
    """Prefer htdemucs_ft (cleanest v/d/b); use the residual 'other' if we built one."""
    name = os.path.splitext(os.path.basename(resolve(track)))[0]
    for model in ("htdemucs_ft", "htdemucs_6s", "htdemucs"):
        d = os.path.join(STEMS_DIR, model, name)
        if os.path.isdir(d):
            wavs = sorted(glob.glob(os.path.join(d, "*.wav")))
            resid = os.path.join(d, "other_residual.wav")
            if os.path.isfile(resid):  # prefer residual master-(v+d+b) over the model's rough 'other'
                wavs = [w for w in wavs if os.path.basename(w) not in ("other.wav", "other_residual.wav")]
                wavs.append(resid)
            return wavs, model
    return [], None


def to_frames(t, sr, nframes, fps, values):
    """Resample a per-stft envelope onto film frames, normalized 0..1."""
    env = np.interp(np.arange(nframes) / fps, t, values)
    return (env / (float(env.max()) or 1.0)).round(5)


def segments_from_envelope(env, fps, thr=0.08, min_dur=0.4, merge_gap=0.5):
    """Contiguous active regions of an envelope (e.g. vocals -> 'Maynard is singing' spans)."""
    on = [v > thr for v in env]
    runs, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            runs.append([i, j - 1]); i = j
        else:
            i += 1
    merged = []
    for s in runs:
        if merged and (s[0] - merged[-1][1]) / fps <= merge_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [s for s in merged if (s[1] - s[0]) / fps >= min_dur]


def build(track, fps):
    master = resolve(track)
    y, sr = librosa.load(master, mono=True)
    dur = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    tempo = float(np.atleast_1d(tempo)[0])
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=True)
    bands, nframes, _ = band_envelopes(y, sr, fps)

    stems, (paths, model) = {}, find_stems(track)
    for p in paths:
        base = os.path.splitext(os.path.basename(p))[0]
        label = "other" if base.startswith("other_residual") else base   # residual stands in for 'other'
        ys, srs = librosa.load(p, mono=True)
        rms = librosa.feature.rms(y=ys)[0]
        rt = librosa.frames_to_time(np.arange(len(rms)), sr=srs)
        stems[label] = to_frames(rt, srs, nframes, fps, rms)

    vocal_segments = []
    if "vocals" in stems:
        for a, b in segments_from_envelope(stems["vocals"], fps):
            vocal_segments.append({"start_t": round(a / fps, 2), "end_t": round(b / fps, 2),
                                   "start_frame": a, "end_frame": b})

    conductor = {
        "track": os.path.splitext(os.path.basename(master))[0],
        "fps": fps, "sr": sr, "duration": round(dur, 3), "n_frames": nframes,
        "tempo_bpm": round(tempo, 2), "biopulse_rate_hz": round(tempo / 60.0, 4),
        "stem_model": model,
        "beats":  [{"t": round(float(t), 3), "frame": int(round(t * fps))} for t in beats],
        "onsets": [{"t": round(float(t), 3), "frame": int(round(t * fps))} for t in onsets],
        "bands":  {k: v.tolist() for k, v in bands.items()},
        "stems":  {k: v.tolist() for k, v in stems.items()},
        "vocal_segments": vocal_segments,
        "caveats": ["tempo_bpm is a librosa estimate and may be an octave (x0.5/x2) off — verify by ear",
                    "vocals/drums/bass (htdemucs_ft) are clean; 'other' is the residual master-(v+d+b)",
                    "word-level lyric timing stays owner ear-annotation (sparse vocals defeat auto-alignment)"],
    }
    return master, y, sr, beats, bands, stems, conductor


def dashboard(y, sr, beats, bands, stems, conductor, png):
    plt.style.use("dark_background")
    n = 3
    fig, axs = plt.subplots(n, 1, figsize=(16, 11), constrained_layout=True)
    t = np.arange(conductor["n_frames"]) / conductor["fps"]
    tmax = float(t[-1])

    # 1) mel-spectrogram + beat grid
    M = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128), ref=np.max)
    librosa.display.specshow(M, sr=sr, x_axis="time", y_axis="mel", ax=axs[0], cmap="magma")
    for b in beats:
        axs[0].axvline(b, color="#66ffff", alpha=0.10, lw=0.4)
    axs[0].set_title(f"{conductor['track']}  —  mel-spectrogram + beat grid   "
                     f"(~{conductor['tempo_bpm']} BPM est · {conductor['stem_model'] or 'no'} stems)")
    axs[0].set_xlim(0, tmax)

    # 2) per-stem energy (+ shaded vocal-active regions)
    for seg in conductor.get("vocal_segments", []):
        axs[1].axvspan(seg["start_t"], seg["end_t"], color="#66ccff", alpha=0.06)
    for name, env in stems.items():
        axs[1].plot(t, env, label=name, color=STEM_COLORS.get(name, "#dddddd"), lw=0.8)
    axs[1].set_title("per-stem energy (htdemucs_ft — clean v/d/b · residual 'other' · shaded = vocals active)")
    axs[1].set_xlim(0, tmax); axs[1].set_ylim(0, 1.02); axs[1].set_ylabel("0..1")
    if stems:
        axs[1].legend(loc="upper right", ncol=len(stems), fontsize=8)

    # 3) frequency-band energy (off the master)
    for name, _, _ in BANDS:
        axs[2].plot(t, bands[name], label=name, lw=0.7)
    axs[2].set_title("frequency-band energy (off the master — artifact-free continuous drivers)")
    axs[2].set_xlim(0, tmax); axs[2].set_ylim(0, 1.02); axs[2].set_ylabel("0..1")
    axs[2].set_xlabel("time (s)")
    axs[2].legend(loc="upper right", ncol=len(BANDS), fontsize=8)

    fig.savefig(png, dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description="consolidated conductor track + dashboard")
    ap.add_argument("track")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--png", help="dashboard PNG path (default: analysis/<track>_dashboard.png)")
    args = ap.parse_args()

    master, y, sr, beats, bands, stems, conductor = build(args.track, args.fps)
    base = conductor["track"]
    adir = os.path.join(HERE, "analysis"); os.makedirs(adir, exist_ok=True)
    jpath = os.path.join(adir, f"{base}_conductor_{args.fps}fps.json")
    with open(jpath, "w") as f:
        json.dump(conductor, f)
    png = args.png or os.path.join(adir, f"{base}_dashboard.png")
    dashboard(y, sr, beats, bands, stems, conductor, png)

    print(f"[conduct] {base}: {conductor['stem_model']} stems={list(stems)}; "
          f"~{conductor['tempo_bpm']} BPM; {len(conductor['beats'])} beats, "
          f"{len(conductor['onsets'])} onsets; {len(BANDS)} bands x {conductor['n_frames']} frames")
    print(f"[conduct] conductor -> {jpath}")
    print(f"[conduct] dashboard -> {png}")


if __name__ == "__main__":
    main()
