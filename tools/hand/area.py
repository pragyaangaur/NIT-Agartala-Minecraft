"""Plot OSM footprints over the Esri crop for a world box: python3 tools/hand/area.py x0 z0 x1 z1 out.png"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image, ImageDraw
import geo
def world_to_px(x, z, meta):
    tx0, ty0, zz = meta; n = 1 << zz
    lat, lon = geo.lonlat(x, z)
    gx = (lon + 180.0) / 360.0 * (n * 256.0)
    gy = (1.0 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2.0 * (n * 256.0)
    return gx - tx0 * 256, gy - ty0 * 256
x0, z0, x1, z1 = map(int, sys.argv[1:5]); out = sys.argv[5]
S = float(sys.argv[6]) if len(sys.argv) > 6 else 3
img = Image.open("data/raw/esri_z18_campus.jpg").convert("RGB")
W, H = int((x1 - x0) * S), int((z1 - z0) * S)
xs = x0 + (np.arange(W) + 0.5) / S; zs = z0 + (np.arange(H) + 0.5) / S
XX, ZZ = np.meshgrid(xs, zs)
px, py = world_to_px(XX, ZZ, (197638, 113179, 18))
a = np.asarray(img)
crop = a[np.clip(py.astype(int), 0, a.shape[0]-1), np.clip(px.astype(int), 0, a.shape[1]-1)]
im = Image.fromarray(crop); d = ImageDraw.Draw(im)
el = json.load(open("data/osm/campus_full.json"))["elements"]
nodes = {e["id"]: (e["lat"], e["lon"]) for e in el if e["type"] == "node"}
for e in el:
    if e["type"] != "way": continue
    t = e.get("tags", {})
    g = e.get("geometry") or [{"lat": nodes[n][0], "lon": nodes[n][1]} for n in e.get("nodes", []) if n in nodes]
    if not g: continue
    x, z = geo.xy([p["lat"] for p in g], [p["lon"] for p in g])
    pts = [((a_ - x0) * S, (b_ - z0) * S) for a_, b_ in zip(x, z)]
    if "building" in t:
        d.line(pts, fill=(255, 255, 0), width=2)
        if t.get("name"):
            cx, cz = np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])
            d.text((cx, cz), t["name"] + f" {e['id']}", fill=(255, 255, 255))
    elif "highway" in t:
        d.line(pts, fill=(255, 80, 80), width=1)
step = 50 if S >= 2 else 100
for gx in range((x0 // step + 1) * step, x1, step):
    d.line([((gx - x0) * S, 0), ((gx - x0) * S, 12)], fill=(0, 255, 255)); d.text(((gx - x0) * S + 2, 0), str(gx), fill=(0, 255, 255))
for gz in range((z0 // step + 1) * step, z1, step):
    d.line([(0, (gz - z0) * S), (12, (gz - z0) * S)], fill=(0, 255, 255)); d.text((2, (gz - z0) * S + 2), str(gz), fill=(0, 255, 255))
im.save(out)
