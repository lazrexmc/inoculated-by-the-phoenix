#!/usr/bin/env python
r"""
contact_sheet.py — assemble labeled images into a grid (a look-dev contact sheet / look bible page).

Generic util: give it (path, label) pairs and it lays them out in a padded grid with captions, each
image letterboxed to a common cell so mixed aspect ratios sit cleanly together. Run with any Python
that has Pillow (e.g. the ComfyUI venv):
  F:\genai\ComfyUI\.venv\Scripts\python.exe genai/contact_sheet.py
"""
import os
from PIL import Image, ImageDraw, ImageFont


def make(items, out, cols=3, cell=(640, 384), pad=12, label_h=30, bg=(8, 8, 10)):
    rows = (len(items) + cols - 1) // cols
    W = cols * cell[0] + (cols + 1) * pad
    H = rows * (cell[1] + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arialbd.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    for i, (path, label) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (cell[0] + pad)
        y = pad + r * (cell[1] + label_h + pad)
        try:
            im = Image.open(path).convert("RGB")
            im.thumbnail(cell, Image.LANCZOS)
            sheet.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
        except Exception as e:
            draw.text((x + 4, y + 4), f"MISSING {os.path.basename(path)}", fill=(200, 80, 80), font=font)
        draw.text((x + 4, y + cell[1] + 6), label, fill=(232, 212, 150), font=font)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sheet.save(out)
    print(f"[contact_sheet] saved -> {out} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    S = r"F:/Inoculated by the Phoenix/_scratch"
    items = [
        (S + "/ref_first_light_blender.png",        "FI-001  First Light  (lettering-gold / black)"),
        (S + "/ref_liquid_starlight_river_v2.png",  "Liquid Starlight  (flowing light, not resin)"),
        (S + "/ref_egg_phoenix_v11.png",            "The Egg  (gem-scales: gold / ruby / ivory, lit within)"),
        (S + "/ref_tree_of_life.png",               "Tree of Life  (glowing canopy + reflection)"),
        (S + "/ref_plateau_eden_v2.png",            "Plateau / Eden  (starlight river)"),
        (S + "/ref_phoenix.png",                    "The Phoenix  (gold-into-fire, rising)"),
    ]
    make(items, S + "/lookdev_contact_sheet.png")
