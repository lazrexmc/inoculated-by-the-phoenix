# RUN_GUIDE — how we work (READ BEFORE ACTING)

*Last updated: 2026-06-30.*

**Why this file exists:** to stop the model (me) from quietly redoing work it already did — regenerating a
look that's already locked, rebuilding a script that already exists, re-solving a gotcha that's already
solved — and burning Lance's subscription tokens doing it. **Before you generate an image, write a
script, or build a beat, you run the check in §0 and report what already exists.** This guide is the
memory that makes that possible.

---

## 0. The "have I done this already?" protocol — DO THIS FIRST, EVERY TIME

Before spending tokens on a generation, a script, or a build, **check these five places and tell Lance
what you found** *before* you spend:

1. **Look bible** — `ProjectDocs/Reference/ART_DIRECTION.md` + `ProjectDocs/Reference/images/`.
   Is the look for this element already locked? If yes, **use it** — do not re-derive a palette/material.
2. **Scratch outputs** — `_scratch/` (Glob `ref_*.png`, `*.mp4`, `shot_*`, `mo_*`). Has this exact still
   or clip already been rendered? Versions are suffixed `_v2/_v3/...`; the **highest version is current.**
3. **Script inventory** — §1 below. Does a tool already exist for this job? **Use it; don't write a
   near-duplicate** (the #1 source of wasted tokens here).
4. **Memory** — the `.claude` auto-memory (loaded each session) + `ProjectDocs/MEMORY.md`. Is this
   decision / path / gotcha already recorded?
5. **Git log** — `git log --oneline -20`. Was this already committed?

Then **state what exists and propose the next step.** If the next step is a *multi-generation batch,
multi-file scripting job, or a full-act run*, get an explicit "go" first — see §6.

**Red-flag thoughts that mean STOP and check:** "let me just regenerate it slightly differently,"
"I'll write a quick script for this," "let me redo that look my way." All three usually mean the thing
already exists.

---

## 1. Script / tool inventory — reach for these, don't rebuild

**`genai/` (gen-AI pipeline — talks to the ComfyUI server API, stdlib only):**
| Script | Does | Use when |
|---|---|---|
| `comfy_gen.py` | prompt → SDXL/Juggernaut still (txt2img) | a brand-new still from a prompt |
| `comfy_img2img.py` | repaint an existing still (`--denoise`) | restyle/recolor while keeping composition |
| `comfy_controlnet.py` | composition-locked repaint (canny/depth from a render) | lock a Blender layout, repaint film-grade |
| `comfy_svd.py` | still → ~2s video (SVD svd_xt) | put motion on a locked still |
| `comfy_upscale.py` | upscale a still (4x-UltraSharp / RealESRGAN) | finishing to delivery resolution |
| `contact_sheet.py` | montage stills into a labeled look-sheet | a look-bible page / before-after |
| `dl_checkpoint.py` / `dl_models.py` / `dl_stack.py` | model downloaders (HF, cache on F:) | adding checkpoints / controlnets / video / upscalers |

**`blender/` (procedural bones — run headless: `E:\Software\blender.exe -b --factory-startup --python <s>`):**
| Script | Does |
|---|---|
| `bootstrap.py` | scene conventions (units, collections, camera) — imported by the others |
| `lookdev_tree.py` / `lookdev_swatch.py` | look-dev harnesses (Cycles/OptiX render to PNG) |
| `tier1_*` / `tier2_*` | hero assets/materials (egg, plateau, liquid starlight, first-light fx…) |
| `act1_scene.py` | Act I beat assembler (`assemble(beat)`, `--all DIR`) |
| `act1_first_light.py` | FI-001 First Light (gold spec on black + bloom; `--frames` = ignition seq) |
| `act1_genesis_anim.py` / `build_act1_animatic.py` | animated genesis / full-act animatic builder |
| `encode_mp4.py` | PNG sequence → MP4 (imageio-ffmpeg; `--audio` mux) |

**`audio/`** — Demucs stems + librosa frame-mapped analysis that drive animation from the album.

If a job needs a tool that's *almost* one of these, **extend the existing script** (add a flag) rather
than writing a parallel one.

---

## 2. The production pipeline (how one shot is made)

```
Blender bones (composition/camera)                      ← blender/  (the "3D bones")
   └─► comfy_controlnet.py (canny/depth lock)           ← composition can't drift
        └─► comfy_gen / comfy_img2img (film-grade look) ← Juggernaut surface
             └─► comfy_upscale.py (finish to res)
                  └─► comfy_svd.py  OR  Wan 2.2 (motion) ← still → moving shot
                       └─► RIFE/FILM VFI (smooth fps)
                            └─► encode/concat (ffmpeg)   ← the cut
```
Exception: **First Light** is Blender-native (a point on black is too little content for SDXL).
The gen-AI is the **final look layer**, not just concept (HYBRID: AI look over 3D bones).

---

## 3. Locked decisions — do NOT re-litigate or re-derive

- **Look bible locked** (`ART_DIRECTION.md`, 6 elements): First Light = the **album-lettering gold**
  through pure black on the chime. **Liquid starlight = flowing self-luminous light, NOT resin.** Tree =
  glowing canopy + starlight-pool reflection. Plateau/Eden = lush, water is liquid starlight. Phoenix =
  gold-into-fire raptor. **The Egg = a gem-scale skin (each scale a faceted gem) in fiery red + ancient
  gold, lit from within** (current hero: `_scratch/ref_egg_phoenix_v10.png`).
- **The gold through-line:** first photon and Phoenix fire are the **same gold** — one being's light.
- **Production approach:** HYBRID (AI look over 3D bones), **free-local first**. Claude produces the hero
  art; Lance directs by prompt. (Asset Spec §5 "owner hand-authors hero" is RETIRED.)
- **Pipeline proven end-to-end** (FI-012 egg: bones→ControlNet→SVD). Don't re-prove it.
- Canon constraints still bind (Treatment is source): Egg SEALED through Act I, one being/shared
  topology, liquid starlight is ONE material, trolls = distorted humanity, etc.

---

## 4. Gotchas — already solved, don't rediscover

- **Blender 5.x compositor** = `scene.compositing_node_group` (a node group) + a **Group Output** node;
  the old `scene.node_tree` / `Composite` node are GONE. **Glare** params are **input sockets**, and the
  type is a MENU socket taking the display name (`"Fog Glow"`, `"Streaks"`; quality `"High"`).
- `lookdev_tree.sun(name, rot, …)` — 2nd arg is **rotation_euler**, not a direction (wrong value = black
  frame). Horizontal surfaces need a near-vertical key.
- **ComfyUI venv has NO pip** (it's a uv venv) and **uv isn't on PATH** → bootstrap with
  `python -m ensurepip --upgrade` then use `-m pip`. Base 3.12 interpreter:
  `C:\Users\lance\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe`.
- **Server:** launch with **`--disable-smart-memory`** (avoids a model-swap IndexError). **Restart the
  server to load newly-cloned custom nodes** (kill the listener on 8188, relaunch).
- comfy venv has **`imageio_ffmpeg` but NOT `imageio`**. ffmpeg exe:
  `F:\genai\ComfyUI\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`.
- **SDXL won't tile a fine texture across a whole egg from a prompt** (it makes a smooth egg + texture
  elsewhere) → use **img2img on a textured source + a gradient-map recolor** (the egg's facet detail
  lives in luminance; recolor preserves it). This is how `ref_egg_phoenix_v10.png` was made.
- **Heavy output never on C:** (system drive, low space) — use **E:/F:** (D: ok; G:/H: are USB).
  Render/AI scratch → `F:\Inoculated by the Phoenix\_scratch`.

---

## 5. Environment & paths

- **ComfyUI:** `F:\genai\ComfyUI` · venv `F:\genai\ComfyUI\.venv` (Python 3.12, **torch 2.6.0+cu124**) ·
  server `…\.venv\Scripts\python.exe main.py --listen 127.0.0.1 --port 8188 --disable-smart-memory`.
- **Models** (`F:\genai\ComfyUI\models\`): `checkpoints/` (Juggernaut-XL_v9, sd_xl_base, svd_xt),
  `diffusion_models/` (wan2.2_ti2v_5B_fp16), `text_encoders/` (umt5_xxl_fp8), `vae/` (wan2.2_vae),
  `controlnet/` (xinsir depth+canny), `ipadapter/` (ip-adapter[-plus]_sdxl_vit-h), `clip_vision/`
  (CLIP-ViT-H-14), `upscale_models/` (4x-UltraSharp, RealESRGAN_x4plus), `animatediff_models/`.
- **Custom nodes:** ComfyUI-Manager, comfyui_controlnet_aux (depth/canny/pose preproc), ComfyUI_IPAdapter_plus,
  ComfyUI-Frame-Interpolation (RIFE/FILM), ComfyUI-AnimateDiff-Evolved, ComfyUI-VideoHelperSuite.
- **OneTrainer** (LoRA training): `F:\genai\OneTrainer` — its **own** venv (torch 2.12+cu130), isolated
  from ComfyUI. Use to train Egg/Tree/Phoenix LoRAs for cross-film consistency.
- **DCCs:** Blender `E:\Software\blender.exe` (5.1.2) · Houdini · UE5 · DaVinci Resolve (paths in memory).
- **Scratch:** `F:\Inoculated by the Phoenix\_scratch` (gitignored). Keepers → `ProjectDocs/Reference/images/`.

---

## 6. Checkpoint-before-spend rule

Before any run that spends meaningful tokens/compute — a **multi-image batch**, a **multi-file scripting
job**, a **full-act re-cut**, or a **big download** — first: (a) run §0, (b) summarize the plan and what
already exists, (c) get Lance's "go." One generation to test a look is fine; ten to brute-force one is the
thing to confirm first. When in doubt, show one result and ask before scaling.
