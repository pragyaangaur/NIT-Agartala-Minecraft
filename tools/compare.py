"""Side-by-side: voxel top-down render vs Esri imagery at the same extent."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import geo, render, blocks

META = (197638, 113179, 18)

def ref_crop(x0, z0, x1, z1, size):
    img = Image.open("data/raw/esri_z18_campus.jpg").convert("RGB")
    import overlay
    px0, py0 = overlay.world_to_mosaic_px(META, x0, z0)
    px1, py1 = overlay.world_to_mosaic_px(META, x1, z1)
    box = (int(min(px0, px1)), int(min(py0, py1)), int(max(px0, px1)), int(max(py0, py1)))
    return img.crop(box).resize(size, Image.LANCZOS)

def side_by_side(vol, bbox, out, size=(700, 700), title=""):
    x0, z0, x1, z1 = bbox
    r = render.render_topdown(vol, blocks.PALETTE, 32, 64, 56, bbox)
    r = r.resize(size, Image.LANCZOS)
    ref = ref_crop(x0, z0, x1, z1, size)
    W = size[0] * 2 + 12
    sheet = Image.new("RGB", (W, size[1] + 26), (18, 18, 18))
    sheet.paste(ref, (0, 26)); sheet.paste(r, (size[0] + 12, 26))
    d = ImageDraw.Draw(sheet)
    d.text((6, 8), f"ESRI REFERENCE  {title}", fill=(255, 220, 60))
    d.text((size[0] + 18, 8), f"MINECRAFT RENDER  {title}", fill=(120, 255, 120))
    sheet.save(out)
    return sheet
