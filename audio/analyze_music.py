r"""
analyze_music.py — librosa music analysis -> a FRAME-MAPPED tempo/onset/energy track.

The film is music-locked, so the score should *drive* the animation rather than be matched to it
(Asset Spec §10: "the world breathes with the album"). This turns any track or stem into data the
Blender/Houdini side can read directly:

    tempo_bpm        -> NG_BioPulse Rate  (Rate Hz = tempo_bpm / 60)
    beats / onsets   -> frame numbers for ignition, impact FX, cuts (drums stem -> FX_Lightning, etc.)
    rms_per_frame    -> a 0..1 energy envelope sampled at the film's fps, to drive emission / scale /
                        NG_BioPulse Amplitude per frame (e.g. the guitar/'other' stem -> the Being's glow)

Output JSON is keyed by FRAME at the chosen fps, so a bpy script just indexes into it.

Run with the audio venv (Python 3.12):
  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" audio\analyze_music.py "F:\...\stems\htdemucs\Fear Inoculum\other.wav" --fps 24
"""
import os, json, argparse
import numpy as np
import librosa

HERE = os.path.dirname(os.path.abspath(__file__))


def analyze(path, fps=24):
    y, sr = librosa.load(path, mono=True)
    dur = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    tempo = float(np.atleast_1d(tempo)[0])
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=True)

    rms = librosa.feature.rms(y=y)[0]
    rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    nframes = int(dur * fps) + 1
    frame_t = np.arange(nframes) / fps
    rms_pf = np.interp(frame_t, rms_t, rms)
    peak = float(rms_pf.max()) or 1.0
    rms_pf = (rms_pf / peak).round(5)

    return {
        "file": os.path.basename(path),
        "sr": sr, "fps": fps, "duration": round(dur, 3),
        "tempo_bpm": round(tempo, 2),
        "biopulse_rate_hz": round(tempo / 60.0, 4),
        "beats":  [{"t": round(float(t), 3), "frame": int(round(t * fps))} for t in beats],
        "onsets": [{"t": round(float(t), 3), "frame": int(round(t * fps))} for t in onsets],
        "rms_per_frame": rms_pf.tolist(),
    }


def main():
    ap = argparse.ArgumentParser(description="librosa -> frame-mapped tempo/onset/energy track")
    ap.add_argument("path", help="audio file (a full track or a single stem .wav)")
    ap.add_argument("--fps", type=int, default=24, help="film frame rate to map onto")
    ap.add_argument("--out", help="output JSON path (default: audio/analysis/<name>.json)")
    args = ap.parse_args()

    data = analyze(args.path, args.fps)
    out = args.out or os.path.join(HERE, "analysis",
                                   os.path.splitext(os.path.basename(args.path))[0] + f"_{args.fps}fps.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=1)

    print(f"[analyze] {data['file']}: tempo={data['tempo_bpm']} BPM "
          f"(NG_BioPulse Rate={data['biopulse_rate_hz']} Hz), "
          f"{len(data['beats'])} beats, {len(data['onsets'])} onsets, "
          f"{len(data['rms_per_frame'])} frames @ {args.fps}fps")
    print(f"[analyze] -> {out}")


if __name__ == "__main__":
    main()
