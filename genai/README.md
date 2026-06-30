# Gen-AI pipeline (`genai/`)

**The final look layer.** Turns *prompts + 3D bones* into film-grade stills and motion on the local
**RTX 3080** — no UI, no manual art. This is the HYBRID pipeline: Blender provides composition/structure,
the gen-AI provides the film-grade surface and motion. Lance directs by prompt; Claude produces the art.

> **Read `ProjectDocs/RUN_GUIDE.md` before generating** — it has the "have I done this already?" check,
> the locked looks, and the gotchas. Don't regenerate a locked look or rebuild an existing script.

## The stack (all local, free, on the 3080)
- **ComfyUI** `F:\genai\ComfyUI` (kept off the repo + off C:). venv `.venv` (Python 3.12, **torch
  2.6.0+cu124**; torchvision/torchaudio match). Server API on `127.0.0.1:8188`.
- **Stills:** Juggernaut-XL_v9 (cinematic SDXL fine-tune, default) + base SDXL.
- **Composition lock:** xinsir **ControlNet** depth + canny (+ `comfyui_controlnet_aux` preprocessors:
  DepthAnythingV2, Canny, pose).
- **Reference identity:** **IP-Adapter** SDXL (`ip-adapter[-plus]_sdxl_vit-h`) + CLIP-ViT-H image encoder.
- **Motion:** **SVD** `svd_xt` (img→~2s) and **Wan 2.2 TI2V-5B** (text+image→video, native ComfyUI nodes;
  umt5 text encoder + wan2.2 VAE) and AnimateDiff (alt motion path).
- **Smoothing:** **RIFE / FILM** frame interpolation (`ComfyUI-Frame-Interpolation`).
- **Finishing:** **4x-UltraSharp** + **RealESRGAN_x4plus** upscalers.
- **LoRA training:** **OneTrainer** at `F:\genai\OneTrainer` (own venv, torch 2.12+cu130) — train
  Egg/Tree/Phoenix LoRAs for cross-film consistency.

## Scripts (stdlib-only clients to the server API)
| Script | Job |
|---|---|
| `comfy_gen.py` | prompt → SDXL still (txt2img) |
| `comfy_img2img.py` | repaint a still (`--denoise`); the HYBRID restyle of a Blender render |
| `comfy_controlnet.py` | composition-locked repaint — `--canny-from <render>` (cv2 Canny) → xinsir-canny; or pass a depth PNG + `--controlnet …depth…` |
| `comfy_svd.py` | still → video (SVD); input must be in `ComfyUI/input/`, pass `--in-name` |
| `comfy_upscale.py` | upscale a still (4x-UltraSharp/RealESRGAN; `--scale` to post-downscale) |
| `contact_sheet.py` | montage stills → a labeled look-sheet (Pillow) |
| `dl_checkpoint.py` / `dl_models.py` / `dl_stack.py` | model downloaders (HF, cache on `F:\hf-cache`) |

## Run it
**1. Start the server once (leave running):**
```
F:\genai\ComfyUI\.venv\Scripts\python.exe F:\genai\ComfyUI\main.py --listen 127.0.0.1 --port 8188 --disable-smart-memory
```
`--disable-smart-memory` avoids a model-swap `IndexError`. **Restart the server after cloning new custom
nodes** (kill the listener on 8188, relaunch). The venv has no pip (uv venv) → `python -m ensurepip` first.

**2. Generate (any Python — stdlib only):**
```
python genai\comfy_gen.py --prompt "…" --out _scratch\x.png --w 1344 --h 768 --steps 34 --cfg 7
python genai\comfy_controlnet.py --canny-from _scratch\bones.png --control-name b.png --prompt "…" --out _scratch\locked.png
python genai\comfy_svd.py --in-name shot.png --out _scratch\shot.mp4 --frames 14 --motion 110
python genai\comfy_upscale.py --in-name hero.png --out _scratch\hero_2k.png --model 4x-UltraSharp.pth --scale 0.5
```

## Gotchas (full list in RUN_GUIDE §4)
- SVD/video caps at ~14 frames @576p on 10GB VRAM (more → OOM). 10GB is the binding constraint.
- comfy venv has `imageio_ffmpeg` (ffmpeg exe under `…/imageio_ffmpeg/binaries/`) but NOT `imageio`.
- SDXL won't tile a fine texture across a whole egg from a prompt → use img2img + gradient-map recolor.
- Heavy output never on C: → `_scratch` on F:.

## Where it fits
Proven end-to-end: Blender bones → `comfy_controlnet` lock → film-grade still → `comfy_svd` motion → a
moving Act I shot (`_scratch/shot_fi012_egg.mp4`). The six locked looks live in
`ProjectDocs/Reference/images/`; the look bible is `ProjectDocs/Reference/ART_DIRECTION.md`.
