#!/usr/bin/env python
r"""
comfy_svd.py — image -> short video via Stable Video Diffusion (svd_xt) on the ComfyUI server.

The motion step of the pipeline: a locked hero still goes in, SVD animates it into a short clip
(camera/subject motion, no re-invention of content). Native ComfyUI SVD nodes + VideoHelperSuite for
the mp4 mux. The input image must already be in ComfyUI/input/ (copy it there, then pass --in-name).

SVD was trained at 1024x576; keep that aspect. 10GB VRAM (RTX 3080) handles ~14 frames @ 576p; raise
--frames at your own risk of OOM. Server must be up (see genai/README.md), ideally with svd already
free to load.

Run:
  python genai/comfy_svd.py --in-name phoenix_svd.png --out F:/.../_scratch/phoenix_motion.mp4 \
      --frames 14 --motion 110 --fps 7
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse

DEF_CKPT = "svd_xt.safetensors"


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
        "1": {"class_type": "ImageOnlyCheckpointLoader", "inputs": {"ckpt_name": a.ckpt}},
        "2": {"class_type": "LoadImage", "inputs": {"image": a.in_name}},
        "3": {"class_type": "SVD_img2vid_Conditioning",
              "inputs": {"clip_vision": ["1", 1], "init_image": ["2", 0], "vae": ["1", 2],
                         "width": a.width, "height": a.height, "video_frames": a.frames,
                         "motion_bucket_id": a.motion, "fps": a.fps, "augmentation_level": a.augmentation}},
        "4": {"class_type": "VideoLinearCFGGuidance", "inputs": {"model": ["1", 0], "min_cfg": a.min_cfg}},
        "5": {"class_type": "KSampler",
              "inputs": {"model": ["4", 0], "seed": a.seed, "steps": a.steps, "cfg": a.cfg,
                         "sampler_name": a.sampler, "scheduler": a.scheduler,
                         "positive": ["3", 0], "negative": ["3", 1], "latent_image": ["3", 2],
                         "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "VHS_VideoCombine",
              "inputs": {"images": ["6", 0], "frame_rate": float(a.fps), "loop_count": 0,
                         "filename_prefix": "ibtp_svd", "format": "video/h264-mp4",
                         "pix_fmt": "yuv420p", "crf": 19, "save_metadata": True,
                         "pingpong": False, "save_output": True}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-name", required=True, help="filename already inside ComfyUI/input/")
    ap.add_argument("--out", required=True, help="destination .mp4 path")
    ap.add_argument("--frames", type=int, default=14)
    ap.add_argument("--motion", type=int, default=110, help="motion_bucket_id (higher = more motion)")
    ap.add_argument("--fps", type=int, default=7)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=576)
    ap.add_argument("--augmentation", type=float, default=0.0)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--cfg", type=float, default=2.5)
    ap.add_argument("--min-cfg", type=float, default=1.0, dest="min_cfg")
    ap.add_argument("--sampler", default="euler")
    ap.add_argument("--scheduler", default="karras")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ckpt", default=DEF_CKPT)
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    if a.seed == 0:
        a.seed = int.from_bytes(os.urandom(4), "big")

    try:
        _get(a.server, "/system_stats")
    except Exception:
        print(f"[svd] ERROR: no ComfyUI server at {a.server}", file=sys.stderr); return 2

    cid = os.urandom(8).hex()
    resp = _post(a.server, "/prompt", {"prompt": graph(a), "client_id": cid})
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[svd] ERROR queueing: {resp}", file=sys.stderr); return 3
    print(f"[svd] queued {pid} frames={a.frames} motion={a.motion} fps={a.fps} {a.width}x{a.height} seed={a.seed}")

    deadline = time.time() + a.timeout
    hist = None
    while time.time() < deadline:
        try:
            h = json.loads(_get(a.server, f"/history/{pid}"))
        except Exception:
            h = {}
        if pid in h:
            hist = h[pid]; break
        time.sleep(2.0)
    if hist is None:
        print("[svd] ERROR: timed out", file=sys.stderr); return 4

    # VideoHelperSuite reports the muxed file under a "gifs" list; fall back to "images".
    vids, imgs = [], []
    for node_out in hist.get("outputs", {}).values():
        vids += node_out.get("gifs", [])
        imgs += node_out.get("images", [])
    pick = (vids or imgs)
    if not pick:
        print(f"[svd] ERROR: no video in result. status={hist.get('status')}", file=sys.stderr); return 5

    f0 = pick[0]
    q = urllib.parse.urlencode({"filename": f0["filename"], "subfolder": f0.get("subfolder", ""),
                                "type": f0.get("type", "output")})
    blob = _get(a.server, f"/view?{q}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(blob)
    print(f"[svd] saved -> {a.out} ({len(blob)//1024} KB; server file={f0['filename']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
