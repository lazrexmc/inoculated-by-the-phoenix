# Blender asset production (`blender/`)

`bpy` scripts that build the film's assets, feeding the **Blender → Unreal Engine 5** pipeline
(Houdini for sims). The **canon constraints + the full build order live in
`../Inoculated_by_the_Phoenix_Asset_Spec.md`** — read §2 (global canon) before writing any asset.

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
   > These render bare **scaffolds** (flat emission, no bloom, proxy geo) — they prove the systems, not the look. Hero meshes/shaders/look-dev are hand-authored (§5) and solved at the style test.
3. **The 30-second style test** — the Act I creation slice (chimes → first river reveal → sprout). Solves starlight, holographic dissolve, pulse, palette, and feather rendering in one shot. Drive the pulse/FX from `audio/analysis/*.json` (tempo/onsets/RMS). **← NEXT. Do not start full production until this looks right.**
4. Tier-2 hero → Tier-3 populations → Tier-4 sims.

## Conventions (Asset Spec §3) — enforced by `bootstrap.py`

- Metric, 1 BU = 1 m · +Z up, -Y forward · apply transforms before export.
- Prefixes: `CHR_ ENV_ PROP_ FX_ MAT_ RIG_ GN_ NG_`.
- Collections: `CHR/ ENV/ PROP/ FX/ _StyleTest/`. One master `.blend` per major asset; never overwrite a known-good `.blend`.

> **Script vs. hand-author (§5):** script the *parametric/batch* parts (Tree stages, feather state-range, troll distortions, scene setup). **Hand-author the hero node graphs** (liquid starlight, Egg shell, Phoenix fire) and expose their inputs as node groups for Python to drive — don't author those shader graphs line-by-line in `bpy`.
