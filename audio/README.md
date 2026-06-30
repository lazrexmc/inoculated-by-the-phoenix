# Music-sync pipeline (`audio/`)

The film is **music-locked** to *Fear Inoculum*, so the score should *drive* the animation, not be
matched to it after the fact (Asset Spec §10 — "the world breathes with the album"). This folder turns
the master tracks into data the Blender/Houdini/UE5 side reads directly.

> **Source audio is copyrighted** (Tool — *Fear Inoculum*) and lives in `FearInoculum_Resolve/Audio/*.mp3`,
> which is **git-ignored**. The venv and all generated stems/analysis here are git-ignored too — only the
> **scripts** + `requirements.txt` in this folder are tracked.

## The honest reality (read this first)

Source separation **cannot** cleanly pull a specific part out of a dense mix like *Fear Inoculum* — there
is no model that isolates "Danny's mandala pad" or "that synth vs. Adam's guitar." So:

| Tool | Good for | NOT good for |
|---|---|---|
| **Demucs stems** | broad, **bleed-tolerant family intensity** envelopes (overall drum/bass/vocal/guitar energy) | clean isolated parts; the 4-stem `other` is a junk drawer (guitar + synths + pad + bleed) |
| **Frequency bands** (off the master) | **artifact-free** continuous drivers (sub→brilliance energy) | naming *which instrument* — it's energy by pitch range, not by player |
| **librosa** beats/onsets/tempo | rhythmic **event frames** + a tempo ballpark | exact tempo (octave errors happen — verify by ear) |
| **The owner's ear-annotations** (in the Treatment) | the **authoritative event track** — the one source no algorithm matches | nothing; this is ground truth |

Use stems + bands as **continuous control signals** (intensity, where a little bleed doesn't matter) and
the owner's annotations for **precise events** (a pad enters, a lyric hits).

## Environment

System Python is **3.14** (too new for PyTorch wheels), so the ML tools run in a dedicated **Python 3.12
venv** (via [`uv`]) at `audio\.venv\`. GPU: **NVIDIA RTX 3080** (CUDA, torch `cu124`). Caches are
redirected off C: (`UV_CACHE_DIR`, `TORCH_HOME` → `F:\…`). Rebuild from `requirements.txt`:

```bat
uv venv "audio\.venv" --python 3.12
uv pip install --python "audio\.venv\Scripts\python.exe" torch torchaudio --index-url https://download.pytorch.org/whl/cu124
uv pip install --python "audio\.venv\Scripts\python.exe" -r audio\requirements.txt
```

Run everything with `audio\.venv\Scripts\python.exe`.

## Scripts

**`separate_stems.py`** (Demucs) — split a track into stems mapped onto the **Four Instruments**:
```bat
audio\.venv\Scripts\python.exe audio\separate_stems.py "Fear Inoculum" --model htdemucs_ft   # canonical
```
**`htdemucs_ft` is the canonical source** — owner-verified: **vocals / drums / bass come out clean**. The
dense **guitar/synth/pad** layer can't be cleanly isolated by *any* model (or a mixing desk on a stereo
master), so we don't trust its rough `other`; we build `other` as a **residual** instead (next). Output →
`audio\stems\<model>\<track>\*.wav`.

**`residual_other.py`** — define `other = master − (vocals + drums + bass)` from the clean ft stems — a
fuller, more controllable "other" than the model's direct stem (measured ~25% different). Net Four
Instruments: **vocals**=story · **drums**=weather/impact · **bass**=light/mood (clean stems) ·
**other / bands**=the Being's guitar energy.

**`analyze_bands.py`** (librosa) — artifact-free **frequency-band energy** envelopes off the master
(sub/bass/low_mid/mid/high_mid/presence/brilliance), per film frame.

**`analyze_music.py`** (librosa) — quick single-file tempo/beats/onsets + `rms_per_frame` for one track or stem.

**`conduct.py`** — the **consolidated conductor track + visual dashboard**. Fuses per-stem energy
(htdemucs_ft + residual `other`), frequency bands, beats/onsets/tempo, and **`vocal_segments`** (when
Maynard is singing → story-beat regions) into one frame-keyed JSON, and renders a PNG dashboard
(mel-spectrogram + beat grid · per-stem energy w/ shaded vocal regions · band energy) you can eyeball:
```bat
audio\.venv\Scripts\python.exe audio\conduct.py "Fear Inoculum" --fps 24
```
→ `audio\analysis\<track>_conductor_24fps.json` (+ `_dashboard.png`). The JSON also carries a `caveats`
list so downstream code doesn't treat the estimates as gospel.

How a `bpy` script uses it: index the per-frame arrays by `frame` → drive `NG_BioPulse` Rate
(`biopulse_rate_hz`) / Amplitude (a stem or band envelope), and place FX on `onsets[].frame`.

## Status & next

- ✅ **Stem source settled: `htdemucs_ft`** (owner-verified clean vocals/drums/bass; `other` = residual).
  Act I (*Fear Inoculum*) separated, band-analyzed, conductor + dashboard built (~123 BPM, 1251 beats,
  vocal-activity segments, 7 bands @ 24 fps). `blender/anim_music_drive.py` drives the Tree's glow from it
  (verified: emission swings 0.8→4.0 with the guitar/residual envelope).
- ✅ **Word-level lyric forced-alignment deferred** — *Fear Inoculum*'s vocals are sparse (long
  instrumental gaps) which defeats auto-aligners; the owner's ear-annotation in the Treatment stays the
  authoritative lyric→timecode source. `vocal_segments` give the singing *regions* automatically — enough.
- ⬜ A `bpy` importer that reads `analysis/*_conductor_*.json` to drive `NG_BioPulse` + FX in the **style
  test** — the music layer's payoff, wired during the visual build (next focus).

[`uv`]: https://docs.astral.sh/uv/
