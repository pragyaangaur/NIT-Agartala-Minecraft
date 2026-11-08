"""Parse the Overpass dump into a clean, world-coordinate dataset."""
import json, math
import numpy as np
import geo

def load(path="data/osm/campus_full.json"):
    d = json.load(open(path))
    buildings, roads, nodes, others = [], [], [], []
    for el in d["elements"]:
        t = el.get("tags", {}) or {}
        if el["type"] == "node":
            x, z = geo.xy(el["lat"], el["lon"])
            nodes.append(dict(id=el["id"], x=float(x), z=float(z), tags=t))
            continue
        if "geometry" not in el:
            continue
        pts = [(float(geo.xy(p["lat"], p["lon"])[0]), float(geo.xy(p["lat"], p["lon"])[1])) for p in el["geometry"]]
        rec = dict(id=el["id"], type=el["type"], tags=t, pts=pts, closed=len(pts) > 2 and pts[0] == pts[-1])
        if "building" in t and len(pts) >= 4:
            buildings.append(rec)
        elif "highway" in t:
            roads.append(rec)
        else:
            others.append(rec)
    return buildings, roads, nodes, others

def area(poly):
    a = 0.0
    for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
        a += x0 * z1 - x1 * z0
    return abs(a) / 2

def centroid(poly):
    a = cx = cz = 0.0
    for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
        c = x0 * z1 - x1 * z0
        a += c; cx += (x0 + x1) * c; cz += (z0 + z1) * c
    if abs(a) < 1e-9:
        return float(np.mean([p[0] for p in poly])), float(np.mean([p[1] for p in poly]))
    return cx / (3 * a), cz / (3 * a)

def min_rect(poly):
    """Minimum-area bounding rectangle: returns (cx, cz, w, h, angle_deg)."""
    P = np.array(poly, float)
    best = None
    for i in range(len(P)):
        p0, p1 = P[i], P[(i + 1) % len(P)]
        d = p1 - p0
        n = np.hypot(*d)
        if n < 1e-6: continue
        u = d / n; v = np.array([-u[1], u[0]])
        pu = (P - p0) @ u; pv = (P - p0) @ v
        w, h = pu.max() - pu.min(), pv.max() - pv.min()
        if best is None or w * h < best[0]:
            c = p0 + u * (pu.max() + pu.min()) / 2 + v * (pv.max() + pv.min()) / 2
            ang = math.degrees(math.atan2(u[1], u[0]))
            best = (w * h, c[0], c[1], w, h, ang)
    return best[1], best[2], best[3], best[4], best[5]

def simplify_closed(pts, tol=0.12):
    """Remove near-duplicate and near-collinear points (metres)."""
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > tol:
            out.append(p)
    if len(out) > 3 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out.pop()
    if len(out) < 3:
        return out
    res = []
    n = len(out)
    for i in range(n):
        a, b, c = out[i - 1], out[i], out[(i + 1) % n]
        ab = (b[0] - a[0], b[1] - a[1]); bc = (c[0] - b[0], c[1] - b[1])
        lab = math.hypot(*ab); lbc = math.hypot(*bc)
        if lab < 1e-6 or lbc < 1e-6: continue
        cross = abs(ab[0] * bc[1] - ab[1] * bc[0]) / (lab * lbc)
        if cross > 0.02 or math.hypot(c[0] - a[0], c[1] - a[1]) > 40:
            res.append(b)
    return res if len(res) >= 3 else out

def kind(tags):
    b = tags.get("building", "yes")
    a = tags.get("amenity", "")
    if b in ("dormitory", "residential") or a in ("dormitory", "hostel"): return "hostel"
    if b in ("university", "college", "school", "faculty"): return "academic"
    if b in ("house", "detached", "hut", "yes", "roof", "garage", "shed", "farm", "barn"): return "generic"
    if b in ("canteen",): return "canteen"
    if b in ("hospital",): return "hospital"
    if b in ("commercial", "retail", "shop", "kiosk"): return "commercial"
    if b in ("auditorium", "stadium"): return "auditorium"
    return b
