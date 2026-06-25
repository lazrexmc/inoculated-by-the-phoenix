"""
bootstrap.py — scene conventions for *Inoculated by the Phoenix* asset production.

This is Build-Order step 1 (Asset Spec §9). Run it first in any fresh .blend, or import
it from other asset scripts. It enforces the Asset Spec §3 conventions so every asset
composes cleanly later in UE5:

  - Metric units, 1 Blender unit = 1 meter
  - +Z up / -Y forward (Blender default — kept explicit so nothing drifts)
  - The standard object-collection layout (CHR / ENV / PROP / FX / _StyleTest)
  - The naming prefixes (CHR_/ENV_/PROP_/FX_/MAT_/RIG_/GN_/NG_)
  - A sane, reverent default camera framing a hero asset near the origin

Usage
  - Live (recommended): VS Code "Blender Development" extension → "Blender: Run Script".
  - Headless / batch:    blender --background --python blender/bootstrap.py
  - From another script: `import bootstrap; bootstrap.setup_scene()`

Notes
  - Idempotent: safe to re-run; it reuses existing collections/camera.
  - Never calls sys.exit() inside Blender (Asset Spec §4) — it returns/raises instead.
  - Targets Blender 4.2+ (the APIs used here are stable across the 4.x / 5.x line).
"""

import bpy
import mathutils

# --- Asset Spec §3: naming prefixes -------------------------------------------------
PREFIX = {
    "char": "CHR_",       # characters / beings
    "env": "ENV_",        # environment
    "prop": "PROP_",      # props
    "fx": "FX_",          # effects / sim proxies
    "mat": "MAT_",        # materials
    "rig": "RIG_",        # armatures
    "geonode": "GN_",     # geometry-node groups
    "shadernode": "NG_",  # shader node groups
}

# --- Asset Spec §3: standard object collections -------------------------------------
COLLECTIONS = ["CHR", "ENV", "PROP", "FX", "_StyleTest"]


def name(kind: str, base: str) -> str:
    """Compose a convention-correct name, e.g. name('char', 'Eagle_Mature') -> 'CHR_Eagle_Mature'."""
    if kind not in PREFIX:
        raise ValueError(f"unknown asset kind {kind!r}; expected one of {sorted(PREFIX)}")
    return PREFIX[kind] + base


def set_units(scene=None):
    """Metric, 1 Blender unit = 1 meter (Asset Spec §3)."""
    scene = scene or bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"


def get_or_create_collection(coll_name: str, parent=None):
    """Return the named collection, creating + linking it under `parent` (or the scene) if absent."""
    coll = bpy.data.collections.get(coll_name)
    if coll is None:
        coll = bpy.data.collections.new(coll_name)
    target = parent.children if parent else bpy.context.scene.collection.children
    if coll.name not in target:
        target.link(coll)
    return coll


def ensure_collections(names=COLLECTIONS):
    """Create the standard collection layout; returns {name: collection}."""
    return {n: get_or_create_collection(n) for n in names}


def _aim_euler(from_loc, to_loc):
    """Rotation that points a camera's -Z toward `to_loc`, +Y up."""
    direction = mathutils.Vector(to_loc) - mathutils.Vector(from_loc)
    return direction.to_track_quat("-Z", "Y").to_euler()


def add_default_camera(cam_name="CAM_Default", location=(0.0, -12.0, 4.0), look_at=(0.0, 0.0, 1.5)):
    """A reverent camera ~12 m back and a little above, framing a hero asset near the origin."""
    existing = bpy.data.objects.get(cam_name)
    if existing and existing.type == "CAMERA":
        cam = existing
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_data.lens = 50  # mm — neutral, undistorted
        cam = bpy.data.objects.new(cam_name, cam_data)
        get_or_create_collection("ENV").objects.link(cam)
    cam.location = location
    cam.rotation_euler = _aim_euler(location, look_at)
    bpy.context.scene.camera = cam
    return cam


def setup_scene():
    """Apply every Asset Spec §3 convention to the current scene. Idempotent."""
    set_units()
    ensure_collections()
    if bpy.context.scene.camera is None:
        add_default_camera()
    print(f"[bootstrap] units=METRIC (1 BU = 1 m), +Z up; collections {COLLECTIONS}; camera ready.")
    return True


if __name__ == "__main__":
    setup_scene()
