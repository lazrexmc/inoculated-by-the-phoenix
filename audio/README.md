# Music-sync pipeline (`audio/`)

The film is **music-locked** to *Fear Inoculum*, so the score should *drive* the animation, not be
matched to it after the fact (Asset Spec §10 — "the world breathes with the album"). This folder turns
the master tracks into data the Blender/Houdini/UE5 side can read directly.

> **Source audio is copyrighted** (Tool — *Fear Inoculum*) and lives in `FearInoculum_Resolve/Audio/*.mp3`,
> which is **git-ignored**. The venv and all generated stems/analysis here are git-ignored too — only
> the **scripts** in this folder are tracked.

## Environment

System Python is **3.14** (too new for PyTorch wheels), so the ML tools run in a dedicated **Python
3.12 venv** created with [`uv`], at `audio\.venv\`. GPU: **NVIDIA RTX 3080** (CUDA — torch `cu124`).

```
audio\.venv\Scripts\python.exe        # the interpreter to run everything below
```

Installed: `torch 2.6+cu124`, `torchaudio`, `demucs 4.0.1`, `librosa 0.11`, `soundfile`, `numpy`.
Caches are redirected off the C: drive (`UV_CACHE_DIR`, `TORCH_HOME` → `F:\…`) — see the drive policy
in project memory.

## 1. Stem separation — `separate_stems.py` (Demucs)

Splits a master track into **drums / bass / vocals / other**, which map onto the film's **Four
Instruments** staging so each stem drives its own visual layer:

| stem | Four Instruments → drives |
|---|---|
| `drums` | **world / weather** — sky, storm, lightning, impact FX |
| `bass` | **light & mood** |
| `vocals` | **story beats** — the lyric moments (and the clean input for lyric forced-alignment) |
| `other` | **the Being & the energy of objects** — guitars/synths → `CHR_OneBeing` + `NG_BioPulse` |

```bat
audio\.venv\Scripts\python.exe audio\separate_stems.py "Fear Inoculum"
```
Output → `audio\stems\htdemucs\<track>\{drums,bass,vocals,other}.wav` (use `--model htdemucs_6s` for a
6-stem split that also isolates guitar/piano).

## 2. Frame-mapped analysis — `analyze_music.py` (librosa)

Turns any track or stem into a JSON keyed by **film frame** (default 24 fps):

```bat
audio\.venv\Scripts\python.exe audio\analyze_music.py "audio\stems\htdemucs\Fear Inoculum\other.wav" --fps 24
```

Produces `audio\analysis\<name>_<fps>fps.json` with:

| field | feeds |
|---|---|
| `tempo_bpm`, `biopulse_rate_hz` | `NG_BioPulse` Rate (Hz = BPM/60) |
| `beats[]`, `onsets[]` (each `{t, frame}`) | ignition / impact-FX / cut frames (drums stem → `FX_Lightning` etc.) |
| `rms_per_frame[]` (0..1 envelope) | per-frame emission / scale / `NG_BioPulse` Amplitude (guitar stem → the Being's glow) |

A bpy script reads this JSON and indexes by `frame` to drive animation — that's how the world ends up
*played by the band* rather than hand-keyed.

## Status & next

- ✅ Demucs + librosa env stood up; **Act I (*Fear Inoculum*) separated** into 4 stems and analyzed
  (`other`: 161.5 BPM, `drums`/`vocals`: 117.5 BPM, frame-mapped @ 24 fps).
- ⬜ **Lyric forced-alignment** — run an aligner (WhisperX is the Windows-friendly + GPU choice over
  aeneas) on the isolated **vocals** stem + the known lyrics to auto-generate the lyric→timecode map
  the owner has been setting by ear, and cross-check it.
- ⬜ A `bpy` importer that reads `analysis/*.json` to drive `NG_BioPulse` and FX timing in the style test.

[`uv`]: https://docs.astral.sh/uv/
