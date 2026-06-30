#!/usr/bin/env python
r"""
comfy_gen.py — prompt-driven SDXL image generation via the ComfyUI server API.

This is Lance's lever: he directs by prompt, this turns a prompt into a finished image on the
RTX 3080. No UI required. Talks to a running ComfyUI server (default 127.0.0.1:8188) over its
HTTP API, builds an SDXL txt2img graph, queues it, waits, and writes the PNG where you ask.

Server (launch once, leave running):
  F:\genai\ComfyUI\.venv\Scripts\python.exe F:\genai\ComfyUI\main.py --listen 127.0.0.1 --port 8188

Generate:
  python F:\genai\comfy_gen.py --prompt "deep cosmic void, a single point of white light" ^
      --out "F:\Inoculated by the Phoenix\_scratch\concept_firstlight.png" --w 1344 --h 768 --steps 30

Stdlib only (urllib/json) so it runs under any Python.
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse, urllib.error

DEF_CKPT = "sd_xl_base_1.0.safetensors"
NEG_DEFAULT = ("text, watermark, signature, logo, frame, border, blurry, lowres, jpeg artifacts, "
               "deformed, extra limbs, bad anatomy, cartoon, oversaturated, ugly")


def _post(server, path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"http://{server}{path}", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _get(server, path):
    with urllib.request.urlopen(f"http://{server}{path}", timeout=30) as r:
        return r.read()


def server_up(server):
    try:
        _get(server, "/system_stats"); return True
    except Exception:
        return False


def graph(args, client_id):
    """SDXL txt2img API graph."""
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": args.ckpt}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": args.w, "height": args.h, "batch_size": args.batch}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": args.prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": args.negative, "clip": ["4", 1]}},
        "3": {"class_type": "KSampler",
              "inputs": {"seed": args.seed, "steps": args.steps, "cfg": args.cfg,
                         "sampler_name": args.sampler, "scheduler": args.scheduler, "denoise": 1.0,
                         "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
                         "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "ibtp", "images": ["8", 0]}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default=NEG_DEFAULT)
    ap.add_argument("--out", required=True, help="destination PNG path")
    ap.add_argument("--w", type=int, default=1024)
    ap.add_argument("--h", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--sampler", default="dpmpp_2m")
    ap.add_argument("--scheduler", default="karras")
    ap.add_argument("--ckpt", default=DEF_CKPT)
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    if args.seed == 0:
        args.seed = int.from_bytes(os.urandom(4), "big")  # avoid Date/random caveats; per-run vary

    if not server_up(args.server):
        print(f"[comfy_gen] ERROR: no ComfyUI server at {args.server}. Launch main.py first.", file=sys.stderr)
        return 2

    client_id = os.urandom(8).hex()
    resp = _post(args.server, "/prompt", {"prompt": graph(args, client_id), "client_id": client_id})
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[comfy_gen] ERROR queueing: {resp}", file=sys.stderr); return 3
    print(f"[comfy_gen] queued prompt_id={pid} seed={args.seed} {args.w}x{args.h} steps={args.steps}")

    deadline = time.time() + args.timeout
    hist = None
    while time.time() < deadline:
        try:
            h = json.loads(_get(args.server, f"/history/{pid}"))
        except Exception:
            h = {}
        if pid in h:
            hist = h[pid]; break
        time.sleep(1.5)
    if hist is None:
        print("[comfy_gen] ERROR: timed out waiting for result", file=sys.stderr); return 4

    images = []
    for node_out in hist.get("outputs", {}).values():
        images += node_out.get("images", [])
    if not images:
        print(f"[comfy_gen] ERROR: no image in result. status={hist.get('status')}", file=sys.stderr); return 5

    img = images[0]
    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""),
                                "type": img.get("type", "output")})
    blob = _get(args.server, f"/view?{q}")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(blob)
    print(f"[comfy_gen] saved -> {args.out} ({len(blob)//1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
