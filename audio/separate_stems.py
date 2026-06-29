r"""
separate_stems.py — Demucs stem separation for the Four Instruments (Asset Spec §10).

Splits a Fear Inoculum master track into drums / bass / vocals / other, which map onto the
film's "Four Instruments" staging so each stem can drive its own visual layer:

    drums  -> world / weather   (sky, storm, lightning, impact FX)
    bass   -> light & mood
    vocals -> story beats        (the Being's voice / the lyric moments)
    other  -> the Being & the energy of objects   (guitars/synths -> CHR_OneBeing + NG_BioPulse)

The isolated **vocals** stem is also the clean input for lyric forced-alignment (auto-timecoding).

MUST be run with the project audio venv (Python 3.12 — system Python 3.14 is too new for torch):
  "F:\Inoculated by the Phoenix\audio\.venv\Scripts\python.exe" audio\separate_stems.py "Fear Inoculum"
  (track = a name in FearInoculum_Resolve\Audio, or a full path; --model htdemucs_6s for 6 stems)
"""
import sys, os, subprocess, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = r"F:\Inoculated by the Phoenix\FearInoculum_Resolve\Audio"
OUT_DIR = os.path.join(HERE, "stems")

FOUR_INSTRUMENTS = [
    ("drums",  "DRUMS  -> world / weather (sky, storm, lightning, impact)"),
    ("bass",   "BASS   -> light & mood"),
    ("vocals", "VOCALS -> story beats (the Being's voice / lyric moments) [+ forced-alignment input]"),
    ("other",  "OTHER  -> the Being & energy of objects (guitars/synths -> CHR_OneBeing + NG_BioPulse)"),
]


def resolve(track):
    if os.path.isfile(track):
        return track
    for ext in (".mp3", ".wav", ".flac", ".m4a", ".aif", ".aiff"):
        p = os.path.join(AUDIO_DIR, track + ext)
        if os.path.isfile(p):
            return p
    raise SystemExit(f"[stems] track not found: {track!r} (looked in {AUDIO_DIR})")


def main():
    ap = argparse.ArgumentParser(description="Demucs stem separation -> Four Instruments")
    ap.add_argument("track", help="track name (in Audio dir) or a full audio path")
    ap.add_argument("--model", default="htdemucs", help="htdemucs (4-stem) | htdemucs_6s (6-stem)")
    ap.add_argument("--device", default="cuda", help="cuda | cpu")
    args = ap.parse_args()

    src = resolve(args.track)
    os.makedirs(OUT_DIR, exist_ok=True)
    cmd = [sys.executable, "-m", "demucs", "-n", args.model, "-d", args.device, "-o", OUT_DIR, src]
    print("[stems] running:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    subprocess.run(cmd, check=True)

    name = os.path.splitext(os.path.basename(src))[0]
    print("\n[stems] Four Instruments (Asset Spec §10):")
    for _, desc in FOUR_INSTRUMENTS:
        print("   " + desc)
    print(f"\n[stems] output -> {os.path.join(OUT_DIR, args.model, name)}\\{{drums,bass,vocals,other}}.wav")


if __name__ == "__main__":
    main()
