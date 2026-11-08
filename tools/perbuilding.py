"""Render each named building: top-down comparison with imagery, and an oblique view."""
import sys, os, json; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw
from specs import SPECS
import blocks, render, compare, dataset, specs, geo

X0, Z0, Y_BASE = 32, 64, 56

def load_vol(path="data/model/vol.npy"):
    return np.ascontiguousarray(np.load(path, mmap_mode="r"))

def named_buildings():
    B = dataset.load()[0]
    out = {}
    for b in B:
        n = b["tags"].get("name")
        if n and n not in out:
            out[n] = b
    try:
        rows = json.load(open("data/model/buildings.json"))["rows"]
        for r in rows:
            n = r.get("name")
            if n and n.startswith("Imagery:") and n not in out:
                pass
    except Exception:
        pass
    return out

def extent_for(b, min_m=90.0):
    P = np.array(b["pts"], float)
    w = P[:, 0].max() - P[:, 0].min(); h = P[:, 1].max() - P[:, 1].min()
    cx = (P[:, 0].max() + P[:, 0].min()) / 2; cz = (P[:, 1].max() + P[:, 1].min()) / 2
    s = max(min_m, 1.7 * max(w, h))
    return (cx - s / 2, cz - s / 2, cx + s / 2, cz + s / 2)

def top_extent(b, size=420):
    P = np.array(b["pts"], float)
    cx = (P[:, 0].max() + P[:, 0].min()) / 2; cz = (P[:, 1].max() + P[:, 1].min()) / 2
    s = max(110.0, 1.35 * max(np.ptp(P[:, 0]), np.ptp(P[:, 1])) + 30)
    return (cx - s / 2, cz - s / 2, cx + s / 2, cz + s / 2)

def _name_of(b):
    return b.get("tags", {}).get("name")

def oblique_for(vol, b, out, size=(760, 520), az=228.0, el=38.0):
    bb = extent_for(b, 90)
    i0 = max(0, int(bb[0]) - X0); i1 = min(vol.shape[0], int(bb[2]) - X0)
    j0 = max(0, int(bb[1]) - Z0); j1 = min(vol.shape[1], int(bb[3]) - Z0)
    sub = np.ascontiguousarray(vol[i0:i1, j0:j1, :])
    # ground level around the building
    top, H = render.topdown(sub, blocks.PALETTE, 0, 0, Y_BASE)
    g = float(np.nanmedian(H)) - Y_BASE
    P = np.array(b["pts"], float)
    cx = (P[:, 0].max() + P[:, 0].min()) / 2 - (X0 + i0)
    cz = (P[:, 1].max() + P[:, 1].min()) / 2 - (Z0 + j0)
    span = max(np.ptp(P[:, 0]), np.ptp(P[:, 1]))
    hgt = float(SPECS.get(_name_of(b), {}).get("floors", 2)) * float(SPECS.get(_name_of(b), {}).get("storey", 3.4))
    hgt = max(6.0, hgt)
    tgt = np.array([cx, g + hgt * 0.55, cz])
    dist = max(52.0, 1.55 * span + 18.0)
    ar = np.radians(az); er = np.radians(el)
    cam = tgt + np.array([np.cos(ar) * np.cos(er), np.sin(er), np.sin(ar) * np.cos(er)]) * dist
    cam[0] = np.clip(cam[0], 1, sub.shape[0] - 2)
    cam[1] = np.clip(cam[1], 1, sub.shape[2] - 2)
    cam[2] = np.clip(cam[2], 1, sub.shape[1] - 2)
    im = render.oblique(sub, blocks.PALETTE, cam, tgt, size=size,
                        fov=52.0, step=0.5, tmax=dist * 3.0 + 200)
    im.save(out)
    return im

def compare_one(vol, b, name, outdir="out/renders/buildings", ref_full=None):
    os.makedirs(outdir, exist_ok=True)
    safe = name.replace(" ", "_").replace("/", "-")
    bb = top_extent(b, 420)
    r = render.render_topdown(vol, blocks.PALETTE, X0, Z0, Y_BASE, bb).resize((420, 420), Image.LANCZOS)
    ref = compare.ref_crop(*bb, (420, 420))
    sheet = Image.new("RGB", (852, 448), (16, 16, 16))
    sheet.paste(ref, (0, 26)); sheet.paste(r, (432, 26))
    d = ImageDraw.Draw(sheet)
    d.text((5, 8), f"ESRI REF  -  {name}", fill=(255, 220, 60))
    d.text((437, 8), f"MINECRAFT  -  {name}", fill=(120, 255, 120))
    sheet.save(f"{outdir}/{safe}_compare.png")
    return sheet

def main():
    vol = load_vol()
    named = named_buildings()
    print(len(named), "named buildings")
    for name, b in sorted(named.items()):
        compare_one(vol, b, name)
        oblique_for(vol, b, f"out/renders/buildings/{name.replace(' ','_')}_iso.png")
        print(" ", name)

if __name__ == "__main__":
    main()
