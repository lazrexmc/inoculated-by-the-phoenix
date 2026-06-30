#!/usr/bin/env python
r"""
comfy_img2img.py — the HYBRID step: AI repaints a 3D render, keeping its composition.

This is the "AI look over 3D bones" pipeline in its simplest form: a Blender render goes in as the
structure (camera, layout, what's-where, consistency), the AI repaints the *surface* to a film-grade
look via SDXL img2img. `--denoise` is the dial: low (~0.4) hugs the 3D tightly, high (~0.8) reinvents
more freely. The input image must already be in the ComfyUI `input/` folder (copy it there first).

Run (server must be up — see genai/README.md):
  python genai/comfy_img2img.py --in-name hybrid_in.png --prompt "..." --out out.png --denoise 0.65
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse

DEF_CKPT = "sd_xl_base_1.0.safetensors"
NEG = ("text, watermark, signature, low quality, blurry, jpeg artifacts, deformed, ugly, "
       "oversaturated, flat, cartoon, childish, amateur")


def _post(server, path, payload):
    req = urllib.request.Request(f"http://{server}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _get(server, path):
    with urllib.request.urlopen(f"http://{server}{path}", timeout=30) as r:
        return r.read()


def graph(a):
    return {
        "4":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": a.ckpt}},
        "10": {"class_type": "LoadImage", "inputs": {"image": a.in_name}},
        "11": {"class_type": "VAEEncode", "inputs": {"pixels": ["10", 0], "vae": ["4", 2]}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"text": a.prompt, "clip": ["4", 1]}},
        "7":  {"class_type": "CLIPTextEncode", "inputs": {"text": a.negative, "clip": ["4", 1]}},
        "3":  {"class_type": "KSampler",
               "inputs": {"seed": a.seed, "steps": a.steps, "cfg": a.cfg, "sampler_name": a.sampler,
                          "scheduler": a.scheduler, "denoise": a.denoise, "model": ["4", 0],
                          "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["11", 0]}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9":  {"class_type": "SaveImage", "inputs": {"filename_prefix": "hybrid", "images": ["8", 0]}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-name", required=True, help="filename already inside ComfyUI/input/")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default=NEG)
    ap.add_argument("--out", required=True)
    ap.add_argument("--denoise", type=float, default=0.65)
    ap.add_argument("--steps", type=int, default=34)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sampler", default="dpmpp_2m")
    ap.add_argument("--scheduler", default="karras")
    ap.add_argument("--ckpt", default=DEF_CKPT)
    ap.add_argument("--server", default="127.0.0.1:8188")
    a = ap.parse_args()
    if a.seed == 0:
        a.seed = int.from_bytes(os.urandom(4), "big")
    try:
        _get(a.server, "/system_stats")
    except Exception:
        print(f"[img2img] ERROR: no ComfyUI server at {a.server}", file=sys.stderr); return 2

    cid = os.urandom(8).hex()
    pid = _post(a.server, "/prompt", {"prompt": graph(a), "client_id": cid}).get("prompt_id")
    if not pid:
        print("[img2img] ERROR queueing", file=sys.stderr); return 3
    print(f"[img2img] queued {pid} denoise={a.denoise} seed={a.seed}")
    deadline = time.time() + 600
    hist = None
    while time.time() < deadline:
        h = json.loads(_get(a.server, f"/history/{pid}"))
        if pid in h:
            hist = h[pid]; break
        time.sleep(1.5)
    if not hist:
        print("[img2img] timeout", file=sys.stderr); return 4
    imgs = [im for o in hist.get("outputs", {}).values() for im in o.get("images", [])]
    if not imgs:
        print(f"[img2img] no image; status={hist.get('status')}", file=sys.stderr); return 5
    q = urllib.parse.urlencode({"filename": imgs[0]["filename"], "subfolder": imgs[0].get("subfolder", ""),
                                "type": imgs[0].get("type", "output")})
    blob = _get(a.server, f"/view?{q}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(blob)
    print(f"[img2img] saved -> {a.out} ({len(blob)//1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
