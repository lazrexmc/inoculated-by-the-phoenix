#!/usr/bin/env python
r"""
comfy_img2img.py — the HYBRID step: AI repaints a 3D render, keeping its composition.

This is the "AI look over 3D bones" pipeline in its simplest form: a Blender render goes in as the
structure (camera, layout, what's-where, consistency), the AI repaints the *surface* to a film-grade
look via SDXL img2img. `--denoise` is the dial: low (~0.4) hugs the 3D tightly, high (~0.8) reinvents
more freely. The input image must already be in the ComfyUI `input/` folder (copy it there first).

Optional canny ControlNet (`--canny-from <img>`) locks the structure HARD during the repaint, so a
HIGHER `--denoise` can clean/re-render the surface without the composition drifting — e.g. erase
speckle on a recolored gem-scale egg while the scale grid stays exactly locked (no disco, no pole warp).

Run (server must be up — see genai/README.md):
  python genai/comfy_img2img.py --in-name hybrid_in.png --prompt "..." --out out.png --denoise 0.65
  python genai/comfy_img2img.py --in-name egg.png --canny-from egg.png --denoise 0.55 --cn-strength 0.65 ...
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse

DEF_CKPT = "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"   # free fine-tune; sd_xl_base_1.0.safetensors also available
COMFY_INPUT = r"F:\genai\ComfyUI\input"
NEG = ("text, watermark, signature, low quality, blurry, jpeg artifacts, deformed, ugly, "
       "oversaturated, flat, cartoon, childish, amateur")


def make_canny(src, dst, low, high):
    """cv2 Canny -> white edges on black, same size as src. For the optional ControlNet structure lock."""
    import cv2
    img = cv2.imread(src, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(src)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(dst, cv2.Canny(gray, low, high))


def _post(server, path, payload):
    req = urllib.request.Request(f"http://{server}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _get(server, path):
    with urllib.request.urlopen(f"http://{server}{path}", timeout=60) as r:
        return r.read()


def graph(a):
    g = {
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
    if a.cn_name:   # optional canny ControlNet structure-lock (holds geometry while a higher denoise cleans the surface)
        g["13"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": a.controlnet}}
        g["14"] = {"class_type": "LoadImage", "inputs": {"image": a.cn_name}}
        g["15"] = {"class_type": "ControlNetApplyAdvanced",
                   "inputs": {"positive": ["6", 0], "negative": ["7", 0], "control_net": ["13", 0],
                              "image": ["14", 0], "strength": a.cn_strength,
                              "start_percent": 0.0, "end_percent": 1.0}}
        g["3"]["inputs"]["positive"] = ["15", 0]
        g["3"]["inputs"]["negative"] = ["15", 1]
    return g


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
    # optional canny ControlNet structure-lock
    ap.add_argument("--canny-from", default=None, help="image to Canny into a structure-lock control map")
    ap.add_argument("--controlnet", default="xinsir-canny-sdxl.safetensors")
    ap.add_argument("--cn-strength", type=float, default=0.65, dest="cn_strength")
    ap.add_argument("--canny-low", type=int, default=80, dest="canny_low")
    ap.add_argument("--canny-high", type=int, default=200, dest="canny_high")
    ap.add_argument("--server", default="127.0.0.1:8188")
    a = ap.parse_args()
    if a.seed == 0:
        a.seed = int.from_bytes(os.urandom(4), "big")

    a.cn_name = None
    if a.canny_from:
        a.cn_name = "i2i_cn_" + os.path.splitext(os.path.basename(a.out))[0] + ".png"
        make_canny(a.canny_from, os.path.join(COMFY_INPUT, a.cn_name), a.canny_low, a.canny_high)
        print(f"[img2img] canny lock {a.canny_from} -> input/{a.cn_name} (cn_strength={a.cn_strength})")

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
