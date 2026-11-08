"""Land-cover classification from the Esri World Imagery mosaic (visual reference)."""
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter, label, binary_opening, binary_closing, gaussian_filter
from scipy import ndimage

def load_mosaic(path="data/raw/esri_z18_campus.jpg"):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    return a

def features(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    V = a.max(-1); mn = a.min(-1)
    S = (V - mn) / np.maximum(V, 1e-3)
    exg = 2 * g - r - b              # excess green
    varm = np.sqrt(np.maximum(uniform_filter(a[..., 0] ** 2, 5) - uniform_filter(a[..., 0], 5) ** 2, 0) +
                   np.maximum(uniform_filter(a[..., 1] ** 2, 5) - uniform_filter(a[..., 1], 5) ** 2, 0))
    return dict(r=r, g=g, b=b, V=V, S=S, exg=exg, tex=varm)

def classify(a, water_v=0.26, water_s=0.62):
    f = features(a)
    water = (f['V'] < water_v) & (f['S'] < water_s) & (f['exg'] < 0.16) & (f['tex'] < 0.035)
    water = binary_closing(water, np.ones((3, 3)))
    lab, n = label(water)
    sizes = ndimage.sum(water, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool); keep[1:] = sizes >= 120      # >= ~36 m^2
    water = keep[lab]
    veg = (f['exg'] > 0.030) & (~water)
    bright_veg = veg & (f['V'] > 0.34)
    dark_veg = veg & (f['V'] <= 0.34)
    built = (~veg) & (~water) & (f['V'] > 0.30) & (f['S'] < 0.30)
    bare = (~veg) & (~water) & (~built)
    return dict(water=water, veg=veg, dark_veg=dark_veg, bright_veg=bright_veg,
                built=built, bare=bare, feats=f)

def colourise(c):
    out = np.zeros(c['water'].shape + (3,), np.uint8)
    out[c['bare']] = (170, 140, 95)
    out[c['bright_veg']] = (110, 175, 70)
    out[c['dark_veg']] = (35, 95, 45)
    out[c['built']] = (205, 205, 205)
    out[c['water']] = (30, 80, 190)
    return out
