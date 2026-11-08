import sys; sys.path.insert(0,'tools')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import geo, dataset, overlay

def single_tile_mosaic(z, s, w, n, e, path):
    """Full-res mosaic at zoom z for a lon/lat box (no downscaling)."""
    img, meta = geo.fetch_esri_mosaic(z, s, w, n, e)
    img.save(path, quality=95)
    return meta

def crop(fname, meta, cx, cz, half_m, z, labels=(), out=None, scale=1):
    img = Image.open(fname).convert('RGB')
    px, py = overlay.world_to_mosaic_px(meta, cx, cz)
    r = half_m / (156543.03392 * np.cos(np.radians(23.84)) / (1 << z))
    box = (int(px - r), int(py - r), int(px + r), int(py + r))
    c = img.crop(box)
    if scale != 1:
        c = c.resize((c.size[0]*scale, c.size[1]*scale), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    for (x, zz, name) in labels:
        pts = [overlay.world_to_mosaic_px(meta, a, b) for a, b in zip(x, zz)]
        pts = [((a - box[0]) * scale, (b - box[1]) * scale) for a, b in pts]
        d.line(pts + [pts[0]], fill=(0, 255, 255), width=2)
        if name:
            mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
            d.rectangle([mx-2, my-8, mx+len(name)*6, my+8], fill=(0,0,0))
            d.text((mx, my-6), name[:34], fill=(255,255,0))
    if out: c.save(out)
    return c
