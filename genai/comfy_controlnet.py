#!/usr/bin/env python
r"""
comfy_controlnet.py — composition-locked repaint: Blender bones -> film-grade frame that obeys them.

The consistency backbone of the hybrid pipeline. A control map derived from the 3D layout (canny edges
of a Blender render, or a depth map rendered from Blender) drives an xinsir ControlNet so Juggernaut
repaints the SURFACE to film grade while the COMPOSITION cannot drift — the Egg stays the Egg, the
camera/layout stays put. This is what scales the look from one-off stills to consistent sequences.

There is no preprocessor node on the server, so the control map is prepared HERE (offline) and uploaded:
  - --canny-from <render.png>  : cv2 Canny edges of a Blender render -> xinsir-canny  (composition by outline)
  - (depth)                    : pass a Blender-rendered depth PNG as --control-name + --controlnet depth

Run (canny lock from a Blender egg scaffold):
  python genai/comfy_controlnet.py --canny-from "_scratch/act1_FI012_egg.png" --control-name egg_canny.png ^
    --controlnet xinsir-canny-sdxl.safetensors --prompt "..." --out "_scratch/cn_egg.png"

Server must be up (see genai/README.md).
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse

DEF_CKPT = "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
COMFY_INPUT = r"F:\genai\ComfyUI\input"
NEG = ("text, watermark, signature, low quality, blurry, jpeg artifacts, deformed, ugly, oversaturated, "
       "flat, cartoon, childish, amateur")


def _round8(n):
    return max(8, int(round(n / 8.0)) * 8)


def make_canny(src, dst, w, h, low, high):
    """cv2 Canny of a Blender render -> white edges on black, sized to (w,h). Returns (w,h)."""
    import cv2, numpy as np
    img = cv2.imread(src, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(src)
    if not w or not h:
        H, W = img.shape[:2]
        scale = min(1.0, (1024 * 1024) / float(W * H)) ** 0.5  # ~1MP cap for SDXL
        w, h = _round8(W * scale), _round8(H * scale)
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, low, high)               # uint8, white edges on black
    cv2.imwrite(dst, edges)
    return w, h


def _post(server, path, payload):
    req = urllib.request.Request(f"http://{server}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _get(server, path):
    with urllib.request.urlopen(f"http://{server}{path}", timeout=60) as r:
        return r.read()


def graph(a):
    return {
        "4":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": a.ckpt}},
        "10": {"class_type": "LoadImage", "inputs": {"image": a.control_name}},
        "11": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": a.controlnet}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"text": a.prompt, "clip": ["4", 1]}},
        "7":  {"class_type": "CLIPTextEncode", "inputs": {"text": a.negative, "clip": ["4", 1]}},
        "12": {"class_type": "ControlNetApplyAdvanced",
               "inputs": {"positive": ["6", 0], "negative": ["7", 0], "control_net": ["11", 0],
                          "image": ["10", 0], "strength": a.strength,
                          "start_percent": a.start, "end_percent": a.end}},
        "5":  {"class_type": "EmptyLatentImage", "inputs": {"width": a.w, "height": a.h, "batch_size": 1}},
        "3":  {"class_type": "KSampler",
               "inputs": {"seed": a.seed, "steps": a.steps, "cfg": a.cfg, "sampler_name": a.sampler,
                          "scheduler": a.scheduler, "denoise": 1.0, "model": ["4", 0],
                          "positive": ["12", 0], "negative": ["12", 1], "latent_image": ["5", 0]}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9":  {"class_type": "SaveImage", "inputs": {"filename_prefix": "cn", "images": ["8", 0]}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--control-name", required=True, help="control-map filename inside ComfyUI/input/")
    ap.add_argument("--canny-from", default=None, help="Blender render to Canny into the control map first")
    ap.add_argument("--controlnet", default="xinsir-canny-sdxl.safetensors")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default=NEG)
    ap.add_argument("--out", required=True)
    ap.add_argument("--w", type=int, default=0)
    ap.add_argument("--h", type=int, default=0)
    ap.add_argument("--strength", type=float, default=0.8)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=1.0)
    ap.add_argument("--canny-low", type=int, default=80, dest="canny_low")
    ap.add_argument("--canny-high", type=int, default=200, dest="canny_high")
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

    if a.canny_from:
        dst = os.path.join(COMFY_INPUT, a.control_name)
        w, h = make_canny(a.canny_from, dst, a.w, a.h, a.canny_low, a.canny_high)
        a.w, a.h = w, h
        print(f"[controlnet] canny {a.canny_from} -> {dst} ({w}x{h})")
    if not a.w or not a.h:
        a.w, a.h = 1024, 1024

    try:
        _get(a.server, "/system_stats")
    except Exception:
        print(f"[controlnet] ERROR: no ComfyUI server at {a.server}", file=sys.stderr); return 2

    cid = os.urandom(8).hex()
    pid = _post(a.server, "/prompt", {"prompt": graph(a), "client_id": cid}).get("prompt_id")
    if not pid:
        print("[controlnet] ERROR queueing", file=sys.stderr); return 3
    print(f"[controlnet] queued {pid} cn={a.controlnet} strength={a.strength} {a.w}x{a.h} seed={a.seed}")

    deadline = time.time() + 600
    hist = None
    while time.time() < deadline:
        try:
            h = json.loads(_get(a.server, f"/history/{pid}"))
        except Exception:
            h = {}
        if pid in h:
            hist = h[pid]; break
        time.sleep(1.5)
    if hist is None:
        print("[controlnet] timeout", file=sys.stderr); return 4
    imgs = [im for o in hist.get("outputs", {}).values() for im in o.get("images", [])]
    if not imgs:
        print(f"[controlnet] no image; status={hist.get('status')}", file=sys.stderr); return 5
    q = urllib.parse.urlencode({"filename": imgs[0]["filename"], "subfolder": imgs[0].get("subfolder", ""),
                                "type": imgs[0].get("type", "output")})
    blob = _get(a.server, f"/view?{q}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(blob)
    print(f"[controlnet] saved -> {a.out} ({len(blob)//1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
