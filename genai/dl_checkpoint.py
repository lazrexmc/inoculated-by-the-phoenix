#!/usr/bin/env python
r"""
dl_checkpoint.py — download a free fine-tuned SDXL checkpoint into ComfyUI (off C:).

Tries a list of ungated Hugging Face repos in order; for each, picks the largest .safetensors (the main
checkpoint, not a VAE/LoRA) and downloads it to ComfyUI/models/checkpoints/. Prints CKPT=<filename> so
the caller knows what to pass as --ckpt.

  F:\genai\ComfyUI\.venv\Scripts\python.exe genai/dl_checkpoint.py
"""
import os, sys
os.environ.setdefault("HF_HOME", r"F:\hf-cache")          # keep the HF cache off C:
from huggingface_hub import HfApi, hf_hub_download

DEST = r"F:\genai\ComfyUI\models\checkpoints"
CANDIDATES = [
    "RunDiffusion/Juggernaut-XL-v9",     # versatile cinematic fine-tune (primary)
    "SG161222/RealVisXL_V5.0",           # photoreal fallback (very reliable repo)
    "Lykon/dreamshaper-xl-1-0",          # artistic/fantasy fallback
]


def main():
    os.makedirs(DEST, exist_ok=True)
    api = HfApi()
    for repo in CANDIDATES:
        try:
            info = api.repo_info(repo, files_metadata=True)
            sts = [(s.rfilename, s.size or 0) for s in info.siblings
                   if s.rfilename.endswith(".safetensors")
                   and not any(k in s.rfilename.lower() for k in ("vae", "lora", "inpaint", "refiner"))]
            if not sts:
                print(f"[dl] {repo}: no checkpoint .safetensors"); continue
            fname = max(sts, key=lambda x: x[1])[0]
            gb = max(sts, key=lambda x: x[1])[1] / 1e9
            print(f"[dl] downloading {repo} :: {fname} (~{gb:.1f} GB)")
            p = hf_hub_download(repo_id=repo, filename=fname, local_dir=DEST)
            print(f"[dl] DONE -> {p}")
            print(f"[dl] CKPT={os.path.basename(p)}")
            return 0
        except Exception as e:
            print(f"[dl] {repo} failed: {e}")
    print("[dl] ALL CANDIDATES FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
