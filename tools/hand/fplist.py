"""List OSM and Microsoft footprints mostly inside a box: python3 fplist.py x0 z0 x1 z1"""
import json, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools")); import geo
b = list(map(int, sys.argv[1:5]))
ms = json.load(open(os.path.join(ROOT, "data/model/ms_new.json")))
el = json.load(open(os.path.join(ROOT, "data/osm/campus_full.json")))["elements"]
nodes = {e["id"]: (e["lat"], e["lon"]) for e in el if e["type"] == "node"}
def inb(P): return ((P[:, 0] >= b[0]) & (P[:, 0] <= b[2]) & (P[:, 1] >= b[1]) & (P[:, 1] <= b[3])).mean() > 0.5
def area(P): x, z = P[:, 0], P[:, 1]; return 0.5 * abs(np.dot(x, np.roll(z, 1)) - np.dot(z, np.roll(x, 1)))
for e in el:
    if e["type"] == "way" and "building" in e.get("tags", {}):
        g = e.get("geometry") or [{"lat": nodes[n][0], "lon": nodes[n][1]} for n in e["nodes"] if n in nodes]
        x, z = geo.xy([p["lat"] for p in g], [p["lon"] for p in g]); P = np.c_[x, z]
        if inb(P): print("OSM", e["id"], e["tags"].get("name", ""), len(P), P.min(0).astype(int), P.max(0).astype(int), int(area(P)), {k: v for k, v in e["tags"].items() if k != "name"})
for i, m in enumerate(ms):
    P = np.array(m["pts"])
    if inb(P): print("MS", i, len(P), P.min(0).astype(int), P.max(0).astype(int), int(area(P)))
