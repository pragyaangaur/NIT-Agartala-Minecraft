import json, sys, time, urllib.parse, urllib.request

UA = "NITAgartala-Minecraft/1.0 (academic campus reconstruction; open data)"

def overpass(query, out, tries=4):
    url = "https://overpass-api.de/api/interpreter"
    for i in range(tries):
        try:
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r:
                raw = r.read()
            j = json.loads(raw)
            with open(out, "w") as f:
                json.dump(j, f)
            print(f"{out}: {len(j.get('elements', []))} elements, {len(raw)} bytes")
            return j
        except Exception as e:
            print(f"attempt {i+1} failed: {e}", file=sys.stderr)
            time.sleep(8 * (i + 1))
    raise SystemExit(f"FAILED {out}")

BBOX = "23.8337,91.4162,23.8513,91.4342"
Q = f"""[out:json][timeout:280];
(
  way["building"]({BBOX});
  way["highway"]({BBOX});
  way["landuse"]({BBOX});
  way["natural"]({BBOX});
  way["waterway"]({BBOX});
  way["leisure"]({BBOX});
  way["amenity"]({BBOX});
  way["barrier"]({BBOX});
  way["man_made"]({BBOX});
  way["power"]({BBOX});
  way["sport"]({BBOX});
  way["shop"]({BBOX});
  way["tourism"]({BBOX});
  way["place"]({BBOX});
  way["railway"]({BBOX});
  node["natural"="tree"]({BBOX});
  node["amenity"]({BBOX});
  node["man_made"]({BBOX});
  node["highway"="bus_stop"]({BBOX});
  relation["building"]({BBOX});
  relation["landuse"]({BBOX});
  relation["leisure"]({BBOX});
  relation["natural"="water"]({BBOX});
  relation["amenity"]({BBOX});
);
out geom;"""

if __name__ == "__main__":
    overpass(Q, "data/osm/campus_full.json")
