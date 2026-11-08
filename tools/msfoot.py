"""Microsoft Global ML Building Footprints: fetch and clip to the build area."""
import csv, gzip, io, json, math, os, urllib.request
import numpy as np

UA = "NITAgartala-Minecraft/1.0 (academic campus reconstruction; open data)"

def tilexy(lat, lon, z):
    n = 1 << z
    x = int((lon + 180.0) / 360.0 * n)
    r = math.radians(lat)
    y = int((1.0 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2.0 * n)
    return x, y

def quadkey(x, y, z):
    q = ""
    for i in range(z, 0, -1):
        d = 0
        mask = 1 << (i - 1)
        if x & mask: d += 1
        if y & mask: d += 2
        q += str(d)
    return q

def rows_for(lat, lon, z=9, csv_path="data/raw/ms_links.csv"):
    x, y = tilexy(lat, lon, z)
    q = quadkey(x, y, z)
    out = []
    for r in csv.DictReader(open(csv_path)):
        if r["QuadKey"] == q:
            out.append(r)
    return q, out

def fetch(q, rows, out="data/raw/ms_buildings.json"):
    polys = []
    for r in rows:
        try:
            req = urllib.request.Request(r["Url"], headers={"User-Agent": UA})
            raw = urllib.request.urlopen(req, timeout=300).read()
            txt = gzip.decompress(raw).decode("utf-8", "replace")
        except Exception as e:
            print("fail", r["Url"][-40:], e)
            continue
        for line in txt.splitlines():
            line = line.strip()
            if not line: continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            if j.get("type") != "Feature": continue
            g = j.get("geometry") or {}
            if g.get("type") != "Polygon": continue
            coords = g["coordinates"][0]
            polys.append(dict(id=j.get("properties", {}).get("id"),
                              confidence=j.get("properties", {}).get("confidence"),
                              coords=[(c[0], c[1]) for c in coords]))
    json.dump(polys, open(out, "w"))
    print(f"quadkey {q}: {len(rows)} parts -> {len(polys)} polygons -> {out}")
    return polys
