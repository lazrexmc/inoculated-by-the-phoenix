#!/usr/bin/env python
r"""
dl_stack.py — fetch the free upgrade stack into ComfyUI (off C:): upscale + IP-Adapter + Wan 2.2 5B.

Native ComfyUI 0.26 nodes already exist for Wan/LTX/Hunyuan/upscale — these only need weights. Each
target lists candidate (repo, filename) pairs and tries them until one lands (HF repos move around).
HF cache stays on F: per the drive policy. Run:
  F:\genai\ComfyUI\.venv\Scripts\python.exe genai/dl_stack.py
"""
import os, sys
os.environ.setdefault("HF_HOME", r"F:\hf-cache")
from huggingface_hub import hf_hub_download

ROOT = r"F:\genai\ComfyUI\models"

# (dest_subdir, final_name, [candidate (repo, filename) ...])
JOBS = [
    # --- IP-Adapter (SDXL) + its CLIP-ViT-H image encoder (reference-identity consistency) ---
    ("ipadapter", "ip-adapter_sdxl_vit-h.safetensors",
     [("h94/IP-Adapter", "sdxl_models/ip-adapter_sdxl_vit-h.safetensors")]),
    ("ipadapter", "ip-adapter-plus_sdxl_vit-h.safetensors",
     [("h94/IP-Adapter", "sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors")]),
    ("clip_vision", "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors",
     [("h94/IP-Adapter", "models/image_encoder/model.safetensors")]),
    # --- Upscalers ---
    ("upscale_models", "4x-UltraSharp.pth",
     [("Kim2091/UltraSharp", "4x-UltraSharp.pth"),
      ("lokCX/4x-Ultrasharp", "4x-UltraSharp.pth"),
      ("uwg/upscaler", "ESRGAN/4x-UltraSharp.pth")]),
    # --- Wan 2.2 TI2V-5B (text+image->video, fits a 10GB 3080 with offload; Comfy-Org repackaged) ---
    ("diffusion_models", "wan2.2_ti2v_5B_fp16.safetensors",
     [("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors")]),
    ("text_encoders", "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
     [("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors")]),
    ("vae", "wan2.2_vae.safetensors",
     [("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/vae/wan2.2_vae.safetensors")]),
]


def main():
    ok, fail = [], []
    for sub, name, cands in JOBS:
        dest = os.path.join(ROOT, sub); os.makedirs(dest, exist_ok=True)
        target = os.path.join(dest, name)
        if os.path.exists(target) and os.path.getsize(target) > 1_000_000:
            print(f"[dl] SKIP (exists) {sub}/{name}"); ok.append(name); continue
        landed = False
        for repo, fname in cands:
            try:
                print(f"[dl] {repo} :: {fname} -> {sub}/{name}")
                p = hf_hub_download(repo_id=repo, filename=fname, local_dir=dest)
                if os.path.abspath(p) != os.path.abspath(target):
                    if os.path.exists(target):
                        os.remove(target)
                    os.replace(p, target)
                print(f"[dl] OK -> {target} ({os.path.getsize(target)//(1024*1024)} MB)")
                ok.append(name); landed = True; break
            except Exception as e:
                print(f"[dl]   miss {repo}: {type(e).__name__}: {str(e)[:100]}")
        if not landed:
            fail.append((name, [c[0] for c in cands]))
    print(f"\n[dl] DONE ok={len(ok)} fail={len(fail)}")
    if fail:
        print(f"[dl] FAILED: {fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
