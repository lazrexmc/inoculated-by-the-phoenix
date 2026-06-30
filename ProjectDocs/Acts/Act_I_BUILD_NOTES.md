# Act I — "Fear Inoculum" — Build Notes (first production pass)

**Date:** 2026-06-29 · **Engine:** Blender 5.1.2 (Cycles/OptiX, RTX 3080) · **Status:** genesis→false-peace
arc represented as hero stills; back-half FX and full-act animation still to come.

This pass took Act I from "opening assets only" to **the entire act visualized in canon order**, built
against the audited **FI-001 … FI-025** shot list (see the master shot list + `Act_I_Fear_Inoculum.md`).
Lance directs by prompt; Claude produces the art. These are first-pass hero stills for prompt-feedback,
not final frames.

Contact sheet: `ProjectDocs/Acts/Act_I_contact_sheet.png` (regenerate via `_scratch/montage.py`).

## Assets built this pass

| Asset | Script | Canon role | Status |
|---|---|---|---|
| **CHR_Egg + MAT_EggShell_Iridescent** | `blender/tier1_chr_egg.py` | the sealed protagonist; iridescent shell that never settles; SEALED every frame of Act I; `Phase`+`Glow` inputs | hero first-pass (leans opal-pastel; tunable to darker/neon on prompt) |
| **ENV_Plateau + MAT_Plateau_Rock** | `blender/tier2_env_plateau.py` | the sacred Mesopotamian ground under FI-007→FI-025; starlight veins in crevices; rim dissolves to void | hero first-pass |
| **Twin springs** | `act1_scene.build_twin_springs` | the two mythic springs at the sprout; share `MAT_LiquidStarlight` (DNA) | strong — reads as liquid-starlight pools |
| **CHR_Creator_Cradle** | `act1_scene.build_creator_cradle` | the Holding Device — primordial light given a cradle ring + warm under-glow | placeholder design (own pass later) |
| **FX_Shadow_Deceiver** | `act1_scene.build_shadow_deceiver` | the formless fog antagonist; low ground-bank that rings the plateau; NEVER a form | first-pass volumetric |
| **FX_InoculationGlow** | `act1_scene.build_inoculation_glow` | the Egg's outward light that PASSIVELY repels the shadow; `flare` 0..1 drives the FI-023 climax | first-pass |
| **act1_scene assembler** | `blender/act1_scene.py` | composes plateau+Tree+springs+Egg+cradle+shadow+glow per FI beat; renders any beat | working |

Pre-existing and reused: `FX_FirstLight` (FI-001), `ENV_Cosmos` (FI-002/3), `ENV_Water` river (FI-005,
now wearing the hero starlight), `ENV_Tree` sprout/mid stages (FI-006/011/012), `MAT_LiquidStarlight`
(hero), `NG_BioPulse`, `NG_HoloDissolve`, `FX_Feather`. `lookdev_swatch.py` is the hero material-ball
harness.

## Beats visualized (hero stills, in `_scratch/`)
- **FI-001** `act1_01_firstlight.png` — point of light + concentric ripples in the void.
- **FI-002/3** `act1_02_cosmos.png` — stars ignite into a spiral galaxy. *(stars still read as uniform white blobs — Tier-2 polish flagged.)*
- **FI-005** `act1_05_river.png` — the first starlight river (hero `MAT_LiquidStarlight`).
- **FI-007** `act1_07_plateau.png` — the sacred plateau as a domed landmass in the void.
- **FI-006** `act1_FI006_sprout.png` — the fragile sprout rising between two starlight springs.
- **FI-012** `act1_FI012_egg.png` — the sealed Egg in the Creator's ring above the Tree (the creation tableau).
- **FI-017** `act1_FI017_shadow.png` — the first shadow: a subtle low mist darkening the plateau edges.
- **FI-023** `act1_FI023_climax.png` — the inoculation: the Egg's light flares and repels the dark.
- **FI-025** `act1_FI025_peace.png` — the false peace: tree, springs, Egg as a soft orb.

## Canon obeyed
- Egg **sealed every frame** (glow only, never a crack — the only hatch is Pneuma).
- Inoculation is **passive** (light repels the shadow; no hatchling, no motion).
- Deceiver is a **sense/fog, never a form/character**.
- Sprout and Tree are **one asset** (`ENV_Tree` growth stages); all springs/rivers share `MAT_LiquidStarlight`.
- Act ends on a **false peace** (shadow repelled, not destroyed).

## Gaps still to build (from the audit, by priority)
1. **FI-004 world-forming** — mist-planet→solid transition, **FX_Lightning**, and **FX_CreationSeam_Crack**
   (the ONE wound in reality; debuts at the L1 lightning ~0:18, persists faintly forever).
2. **FX_CreationRipples** (Houdini) — the physics-writing waves of chimes 1–3.
3. **Ocean-birth splash** (FI-007, 0:36 thunder) + **whole-planet water-network view** (FI-008 "all waters are one").
4. **ENV_Cosmos hero polish** — varied cool→gold star tint, points not blobs, de-blown core.
5. **Hero `MAT_LiquidStarlight` on the Tree** (currently placeholder teal emission) + **NG_BioPulse** pulse wired to the drum tempo.
6. **CHR_Creator_Cradle** real design pass.
7. **Full-act animation** — Act I is **~10.5 min**; this pass is stills. Next: music-synced motion
   (see pipeline below), genesis opening first, then batch-render the rest unattended.

## Gen-AI pipeline (Lance's prompt lever) — ONLINE
- **ComfyUI** installed at `F:\genai\ComfyUI` (torch 2.6 + CUDA 12.4, RTX 3080); SDXL base checkpoint local.
- **`genai/comfy_gen.py`** — prompt→image client (stdlib, talks to the ComfyUI server API). Use it to
  generate concept frames / skies / textures / matte by prompt to art-direct any beat.

## Lessons (so future passes don't repeat them)
- `lookdev_tree.sun()`'s **2nd arg is `rotation_euler`, not a direction/location.** Default sun shines −Z
  (down). **Horizontal** surfaces (plateau) need a **near-vertical** key (small X tilt); **vertical**
  objects (Tree) want a larger X tilt. Wrong rotation = black frame.
- This Blender build has **no FFmpeg** codec → render PNG sequences, encode via `imageio-ffmpeg`.
- World volume-scatter glow works at the Tree's scale but can over-darken huge enveloping volumes — keep
  the Shadow a **low thin bank**, not a tall box around the camera.
