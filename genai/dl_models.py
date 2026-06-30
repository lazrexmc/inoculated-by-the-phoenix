#!/usr/bin/env python
r"""
dl_models.py — fetch the free ControlNet + video models into ComfyUI (off C:).

Downloads a fixed job list of Hugging Face files into the right ComfyUI model folders. Ungated repos
work with no token; gated ones (e.g. SVD) will log FAIL unless HF_TOKEN is set — that's fine, the rest
still land. Run:
  F:\genai\ComfyUI\.venv\Scripts\python.exe genai/dl_models.py
"""
import os, sys
os.environ.setdefault("HF_HOME", r"F:\hf-cache")
from huggingface_hub import hf_hub_download

ROOT = r"F:\genai\ComfyUI\models"
# (repo, filename, dest_subdir, friendly_rename)
JOBS = [
    # ControlNet for SDXL (xinsir — higher quality than the diffusers official ones). Lock 3D composition.
    ("xinsir/controlnet-depth-sdxl-1.0", "diffusion_pytorch_model.safetensors", "controlnet", "xinsir-depth-sdxl.safetensors"),
    ("xinsir/controlnet-canny-sdxl-1.0", "diffusion_pytorch_model.safetensors", "controlnet", "xinsir-canny-sdxl.safetensors"),
    # Image-to-video: AnimateDiff SDXL motion adapter (ungated, reuses Juggernaut) ...
    ("guoyww/animatediff-motion-adapter-sdxl-beta", "diffusion_pytorch_model.safetensors", "animatediff_models", "mm_sdxl_v10_beta.safetensors"),
    # ... and SVD (better I2V, but GATED — needs HF_TOKEN + license accept; logs FAIL otherwise).
    ("stabilityai/stable-video-diffusion-img2vid-xt", "svd_xt.safetensors", "checkpoints", "svd_xt.safetensors"),
]


def main():
    ok, fail = [], []
    for repo, fname, sub, rename in JOBS:
        dest = os.path.join(ROOT, sub); os.makedirs(dest, exist_ok=True)
        target = os.path.join(dest, rename)
        if os.path.exists(target) and os.path.getsize(target) > 1_000_000:
            print(f"[dl] SKIP (exists) {rename}"); ok.append(rename); continue
        try:
            print(f"[dl] {repo} :: {fname} -> {sub}/{rename}")
            p = hf_hub_download(repo_id=repo, filename=fname, local_dir=dest)
            if os.path.abspath(p) != os.path.abspath(target):
                if os.path.exists(target):
                    os.remove(target)
                os.rename(p, target)
            print(f"[dl] OK -> {target} ({os.path.getsize(target)//(1024*1024)} MB)")
            ok.append(rename)
        except Exception as e:
            print(f"[dl] FAIL {repo}: {type(e).__name__}: {e}")
            fail.append((repo, str(e)[:120]))
    print(f"[dl] DONE. ok={ok}")
    if fail:
        print(f"[dl] failed={fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
