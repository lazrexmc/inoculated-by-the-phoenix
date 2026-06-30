# Blender asset production (`blender/`)

`bpy` scripts that build the film's assets, feeding the **Blender → Unreal Engine 5** pipeline
(Houdini for sims). The **canon constraints + the full build order live in
`../Inoculated_by_the_Phoenix_Asset_Spec.md`** — read §2 (global canon) before writing any asset.

> **Before producing:** read `../ProjectDocs/RUN_GUIDE.md` (the anti-repeat protocol) and the look bible
> `../ProjectDocs/Reference/ART_DIRECTION.md`. The Blender bones now feed the HYBRID gen-AI pipeline
> (`../genai/`) — Blender = composition/structure, gen-AI = the film-grade surface and motion.

## Environment (Asset Spec §4)

**Blender 5.1.2 is installed at `E:\Software\blender.exe`** (Python 3.13). Scripts here are
**tested headlessly** against it before hand-off:
```
"E:\Software\blender.exe" --background --factory-startup --python blender/<script>.py
```
For the **interactive** workflow in VS Code:

1. **"Blender Development" extension** (Jacques Lucke). `Ctrl+Shift+P → Blender: Start` → point it at `E:\Software\blender.exe`. Runs code in a live Blender, streams output here, supports breakpoints. Enable `blender.addon.reloadOnSave`.
2. **`pip install fake-bpy-module`** into the VS Code interpreter for `bpy`/`mathutils` autocomplete (stubs only).
3. Silence Blender's `bpy.props` Pylance noise in workspace settings:
   ```json
   "python.analysis.diagnosticSeverityOverrides": { "reportInvalidTypeForm": "none" }
   ```

## Running

- **Live (recommended):** open a script, `Blender: Run Script`.
- **Headless / batch / testing:** `"E:\Software\blender.exe" --background --factory-startup --python blender/bootstrap.py`

## Build order (Asset Spec §9)

1. ✅ **`bootstrap.py`** — scene conventions (units, collections, naming, camera). *Verified in Blender 5.1.2.* Run/import first.
2. ✅ **Tier-1 foundations** (all built + headless-verified; previews in `previews/`):
   - `tier1_env_tree.py` — `ENV_Tree` growth system (sprout→mid→mature→wounded→regrown) from one param set.
   - `tier1_mat_liquid_starlight.py` — `MAT_LiquidStarlight` (`NG_LiquidStarlight`) scaffold; drivable inputs exposed.
   - `tier1_ng_biopulse.py` — `NG_BioPulse` heartbeat driver (makes the starlight breathe).
   - `tier1_fx_feather.py` — `FX_Feather` + `MAT_Feather_StateRange` (one `State` 0..1: ash→starlight→ember).
   - `tier1_chr_onebeing.py` — `RIG_OneBeing` (22-bone) + `CHR_OneBeing` placeholder proxy (bound + posed).
   > These began as bare scaffolds; the hero look is now produced **by Claude** (procedural + prompt-driven gen-AI), NOT hand-authored by the owner — see the division-of-labor note below.
3. ✅ **`MAT_LiquidStarlight`** (`tier1_mat_liquid_starlight.py`): Voronoi star-field (white cores + thin gold rims + bloom halos), time-driven flow. **Owner correction (2026-06-30): liquid starlight reads as FLOWING self-luminous LIGHT, NOT a resin/gel** — a river of moving star-points that glows brighter than the dark (see `../ProjectDocs/Reference/ART_DIRECTION.md` §3). Present with `lookdev_swatch.py`.
4. ✅ **ACT I built end-to-end** (first-pass hero stills, audited FI-001..025): `tier1_chr_egg.py` (`CHR_Egg`+`MAT_EggShell_Iridescent`, sealed), `tier2_env_plateau.py` (`ENV_Plateau`+`MAT_Plateau_Rock`), `tier2_env_water.py` (river), `tier2_env_cosmos.py`, `tier2_fx_firstlight.py`, and `act1_scene.py` (the **Act I assembler**: plateau+Tree+springs+Egg+cradle+`FX_Shadow_Deceiver`+`FX_InoculationGlow`, renders a still per beat). **`act1_first_light.py`** builds the LOCKED FI-001 First Light (the *Fear Inoculum* album-lettering gold spec on pure black + compositor fog-glow bloom + a 6-point chime starburst; `--frames` renders the ignition keyed to the downbeat); `act1_genesis_anim.py` is the earlier genesis-ripple animation. Look-dev via `lookdev_tree.py`/`lookdev_swatch.py`. See `../ProjectDocs/Acts/Act_I_BUILD_NOTES.md`.
5. **Now (2026-06-30): the look is locked and the HYBRID pipeline is proven** (Blender bones → `../genai/comfy_controlnet.py` lock → film-grade still → `comfy_svd.py`/Wan motion). Next: the **film-grade re-cut of Act I** beat-by-beat through that pipeline (the procedural scaffolds are the bones, not the deliverable). Then Tier-3 populations → Tier-4 sims.

**Rendering notes:** Cycles on OptiX (RTX 3080). `lookdev_tree.sun(name, rot, energy, color)` — the 2nd arg is a **rotation_euler**, not a direction; a horizontal surface needs a near-vertical key (small X tilt), a vertical object a larger X tilt (wrong rotation = black frame). This Blender build has **no FFmpeg codec** → render PNG sequences and encode with `encode_mp4.py` (`imageio-ffmpeg`, muxes synced audio).

## Conventions (Asset Spec §3) — enforced by `bootstrap.py`

- Metric, 1 BU = 1 m · +Z up, -Y forward · apply transforms before export.
- Prefixes: `CHR_ ENV_ PROP_ FX_ MAT_ RIG_ GN_ NG_`.
- Collections: `CHR/ ENV/ PROP/ FX/ _StyleTest/`. One master `.blend` per major asset; never overwrite a known-good `.blend`.

> **Division of labor (supersedes Asset Spec §5):** Lance is a prompt-writer with no art/3D/UI training and **cannot hand-author hero art**, so the §5 "owner hand-authors the hero" assumption is **retired**. **Claude produces the finished hero art** — (a) hero procedural shaders/materials/geo here in `bpy` (expose inputs as node groups so Python/the conductor can drive them), and (b) **prompt-driven gen-AI** (`../genai/comfy_gen.py` → ComfyUI/SDXL) that Lance art-directs by prompt. Never defer a "hero pass" to Lance; bring the look up and present renders for his prompt-feedback.
