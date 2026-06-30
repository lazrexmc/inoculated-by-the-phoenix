#!/usr/bin/env python
r"""
comfy_upscale.py — upscale a still with an ESRGAN model (4x-UltraSharp / RealESRGAN) via ComfyUI.

The finishing step: take a hero still to delivery resolution, sharp. Native ComfyUI nodes
(UpscaleModelLoader -> ImageUpscaleWithModel), so it just needs the .pth in models/upscale_models/.
Input must be in ComfyUI/input/ (copy it, pass --in-name).

Run:
  python genai/comfy_upscale.py --in-name egg.png --out _scratch/egg_4k.png --model 4x-UltraSharp.pth
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse


def _post(server, path, payload):
    req = urllib.request.Request(f"http://{server}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _get(server, path):
    with urllib.request.urlopen(f"http://{server}{path}", timeout=120) as r:
        return r.read()


def graph(a):
    g = {
        "1": {"class_type": "LoadImage", "inputs": {"image": a.in_name}},
        "2": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": a.model}},
        "3": {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["2", 0], "image": ["1", 0]}},
    }
    last = "3"
    if a.scale and a.scale != 0:  # optional downscale of the model's native (usually 4x) output
        g["4"] = {"class_type": "ImageScaleBy", "inputs": {"image": ["3", 0], "upscale_method": "lanczos",
                                                            "scale_by": a.scale}}
        last = "4"
    g["9"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "ups", "images": [last, 0]}}
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-name", required=True, help="filename already inside ComfyUI/input/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="4x-UltraSharp.pth")
    ap.add_argument("--scale", type=float, default=0.0, help="post-scale factor on the 4x output (e.g. 0.5 -> 2x net)")
    ap.add_argument("--server", default="127.0.0.1:8188")
    a = ap.parse_args()
    try:
        _get(a.server, "/system_stats")
    except Exception:
        print(f"[upscale] ERROR: no ComfyUI server at {a.server}", file=sys.stderr); return 2
    cid = os.urandom(8).hex()
    pid = _post(a.server, "/prompt", {"prompt": graph(a), "client_id": cid}).get("prompt_id")
    if not pid:
        print("[upscale] ERROR queueing", file=sys.stderr); return 3
    print(f"[upscale] queued {pid} model={a.model}")
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
        print("[upscale] timeout", file=sys.stderr); return 4
    imgs = [im for o in hist.get("outputs", {}).values() for im in o.get("images", [])]
    if not imgs:
        print(f"[upscale] no image; status={hist.get('status')}", file=sys.stderr); return 5
    q = urllib.parse.urlencode({"filename": imgs[0]["filename"], "subfolder": imgs[0].get("subfolder", ""),
                                "type": imgs[0].get("type", "output")})
    blob = _get(a.server, f"/view?{q}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(blob)
    print(f"[upscale] saved -> {a.out} ({len(blob)//1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
