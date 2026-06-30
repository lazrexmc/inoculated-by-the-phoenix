# Gen-AI image pipeline (`genai/`)

**Lance's art-direction lever.** Turns a *prompt* into a finished image on the local **RTX 3080** — no
UI, no manual art. This is the practical answer to the division-of-labor change (Lance directs by prompt;
Claude produces the art): use it for concept frames, skies/HDRIs, textures, matte paintings, and
look-reference that Lance iterates on by prompt.

## What's where
- **ComfyUI install:** `F:\genai\ComfyUI` (kept *outside* the repo — heavy; drive policy = never on C:).
  - venv: `F:\genai\ComfyUI\.venv` (Python 3.12) · **torch 2.6.0+cu124** · **torchaudio 2.6.0+cu124** ·
    torchvision 0.21.0+cu124.
  - model: `F:\genai\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors` (SDXL base).
- **`genai/comfy_gen.py`** (in the repo): a stdlib-only client that talks to the ComfyUI **server API**,
  builds an SDXL txt2img graph, queues it, and writes the PNG where you ask.

## Use it (two steps)

**1. Start the ComfyUI server once (leave it running):**
```
F:\genai\ComfyUI\.venv\Scripts\python.exe F:\genai\ComfyUI\main.py --listen 127.0.0.1 --port 8188
```
It binds in ~10–15s (loads on first generation). The server scans `models/checkpoints/` at startup.

**2. Generate by prompt (any Python — stdlib only):**
```
python "F:\Inoculated by the Phoenix\genai\comfy_gen.py" ^
  --prompt "deep cosmic void, a single point of white-gold light, concentric ripples" ^
  --out "F:\Inoculated by the Phoenix\_scratch\concept.png" ^
  --w 1344 --h 768 --steps 30 --cfg 7.5
```
Flags: `--prompt` (required) · `--negative` · `--out` (required) · `--w/--h` (SDXL likes ~1MP: 1024×1024,
1344×768, 832×1216) · `--steps` (28–35) · `--cfg` (6–8) · `--seed` (0 = random) · `--sampler`
(default `dpmpp_2m`) · `--scheduler` (default `karras`) · `--batch` · `--ckpt` · `--server`.

## Gotcha already fixed
ComfyUI crashed at startup with `OSError: [WinError 127]` on `import torchaudio` — the installer had
paired **torch 2.6.0** with **torchaudio 2.11.0** (ABI mismatch). Fix that's already applied:
```
python -m uv pip install --python F:\genai\ComfyUI\.venv\Scripts\python.exe torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
```
If torch is ever upgraded, re-pin torch/torchvision/torchaudio to the **same** version + cu tag.

## Where it fits
First verified output: an Egg concept (deep glassy egg with a living nebula + tree inside). Outputs are
references/textures/concept — not final film frames; the film's hero look is the procedural Blender
pipeline (`blender/`). Gen-AI feeds art direction, skies, textures, and matte into that.

## Next (optional)
- Add a **refiner** pass (SDXL refiner) and an **img2img** mode to `comfy_gen.py` for polish/variations.
- Pull **ControlNet** (depth/canny) to art-direct gen-AI *from* the Blender renders (compose the two).
- text-to-3D (TripoSR / Hunyuan3D) for quick prop/creature blockouts.
