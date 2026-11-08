import sys; sys.path.insert(0,'tools')
import numpy as np, json, math
from PIL import Image, ImageDraw
import geo, dataset, overlay

def shot(b, z=19, half=90, pad=20, cache="data/raw/esri19", outline=True, out=None):
    """Fetch full-res imagery around one building, draw its footprint, return PIL image."""
    cx, cz = dataset.centroid(b['pts'])
    s, w = geo.lonlat(cx - half - pad, cz + half + pad)
    n, e = geo.lonlat(cx + half + pad, cz - half - pad)
    img, meta = geo.fetch_esri_mosaic(z, s, w, n, e, cache_dir=cache)
    px, py = overlay.world_to_mosaic_px(meta, cx, cz)
    r = half / (156543.03392 * np.cos(np.radians(23.84)) / (1 << z))
    box = (int(px - r), int(py - r), int(px + r), int(py + r))
    c = img.crop(box).convert("RGB")
    if outline:
        d = ImageDraw.Draw(c)
        pts = [overlay.world_to_mosaic_px(meta, x, zz) for x, zz in b['pts']]
        pts = [(a - box[0], bb - box[1]) for a, bb in pts]
        d.line(pts + [pts[0]], fill=(0, 255, 255), width=1)
    if out: c.save(out)
    return c, (cx, cz)
