"""Local projection and tile helpers for the NIT Agartala build.

World convention (Minecraft): +X = east, +Z = south, +Y = up. 1 block = 1 metre.
Origin (0,0) sits at the north-west corner of the padded build area.
"""
import math, os, json, io, time, urllib.request
import numpy as np

# --- build area -----------------------------------------------------------------
CAMPUS = dict(s=23.834615, n=23.850409, w=91.417145, e=91.433276)
MARGIN_M = 100.0
LAT0 = 23.85200                 # origin latitude (north edge)
LON0 = 91.41580                 # origin longitude (west edge)
M_PER_DEG_LAT = 111132.0
M_PER_DEG_LON = 111320.0 * math.cos(math.radians((CAMPUS['s'] + CAMPUS['n']) / 2))
BASE_Y = 64                     # world Y of the lowest terrain point

def xy(lat, lon):
    """WGS84 -> world (x east, z south) in metres, as float arrays or scalars."""
    x = (np.asarray(lon) - LON0) * M_PER_DEG_LON
    z = (LAT0 - np.asarray(lat)) * M_PER_DEG_LAT
    return x, z

def lonlat(x, z):
    return LAT0 - np.asarray(z) / M_PER_DEG_LAT, LON0 + np.asarray(x) / M_PER_DEG_LON

def bounds():
    """Integer build box (x0, z0, x1, z1) in blocks, exclusive upper."""
    xs, zs = xy([CAMPUS['s'], CAMPUS['n']], [CAMPUS['w'], CAMPUS['e']])
    x0 = int(math.floor(min(xs) - MARGIN_M)); x1 = int(math.ceil(max(xs) + MARGIN_M))
    z0 = int(math.floor(min(zs) - MARGIN_M)); z1 = int(math.ceil(max(zs) + MARGIN_M))
    return x0, z0, x1, z1

# --- web tiles ------------------------------------------------------------------
UA = "NITAgartala-Minecraft/1.0 (academic campus reconstruction; open data)"

def sloppy_request(url, tries=4, timeout=60):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(2 + 2 * i)
    raise last

def lon2tile(lon, z): return (lon + 180.0) / 360.0 * (1 << z)
def lat2tile(lat, z):
    r = math.radians(lat)
    return (1.0 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2.0 * (1 << z)

def tile_bounds(z, tx, ty):
    n = 1 << z
    def lon_of(t): return t / n * 360.0 - 180.0
    def lat_of(t):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * t / n))))
    return lat_of(ty + 1), lat_of(ty), lon_of(tx), lon_of(tx + 1)   # s,n,w,e

# Esri World Imagery (visual reference only, attribution required)
ESRI = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

def fetch_esri_mosaic(z, s, w, n, e, cache_dir="data/raw/esri"):
    """Mosaic Esri imagery covering the lon/lat box. Returns (rgb array, extent)."""
    from PIL import Image
    os.makedirs(cache_dir, exist_ok=True)
    tx0, tx1 = int(lon2tile(w, z)), int(lon2tile(e, z))
    ty0, ty1 = int(lat2tile(n, z)), int(lat2tile(s, z))
    nx, ny = tx1 - tx0 + 1, ty1 - ty0 + 1
    img = Image.new("RGB", (nx * 256, ny * 256))
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            p = f"{cache_dir}/esri_{z}_{tx}_{ty}.jpg"
            if not os.path.exists(p) or os.path.getsize(p) < 1000:
                raw = sloppy_request(ESRI.format(z=z, x=tx, y=ty))
                open(p, "wb").write(raw)
            try:
                img.paste(Image.open(p).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
            except Exception:
                pass
    return img, (tx0, ty0, z)

def mosaic_pixel_to_world(mosaic_meta, px, py):
    """Pixel coords in a fetch_esri_mosaic image -> world metres (float arrays)."""
    tx0, ty0, z = mosaic_meta
    n = 1 << z
    gx = tx0 * 256 + np.asarray(px)          # global pixel
    gy = ty0 * 256 + np.asarray(py)
    lon = gx / (n * 256.0) * 360.0 - 180.0
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * gy / (n * 256.0)))))
    return xy(lat, lon)     # NB: returns (x, z)

# --- Terrarium DEM --------------------------------------------------------------
TERRARIUM = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"

def fetch_dem(s, w, n, e, z=13, cache_dir="data/raw/terrarium"):
    from PIL import Image
    os.makedirs(cache_dir, exist_ok=True)
    tx0, tx1 = int(lon2tile(w, z)), int(lon2tile(e, z))
    ty0, ty1 = int(lat2tile(n, z)), int(lat2tile(s, z))
    nx, ny = tx1 - tx0 + 1, ty1 - ty0 + 1
    out = np.zeros((ny * 256, nx * 256), dtype=np.float32)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            p = f"{cache_dir}/terr_{z}_{tx}_{ty}.png"
            if not os.path.exists(p) or os.path.getsize(p) < 500:
                open(p, "wb").write(sloppy_request(TERRARIUM.format(z=z, x=tx, y=ty)))
            a = np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)
            h = a[..., 0] * 256.0 + a[..., 1] + a[..., 2] / 256.0 - 32768.0
            out[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = h
    return out, (tx0, ty0, z)

def dem_to_world(dem, meta, xs, zs):
    """Sample the DEM at world coords using inverse web-mercator per pixel."""
    tx0, ty0, z = meta
    n = 1 << z
    lat, lon = lonlat(xs, zs)
    gx = (lon + 180.0) / 360.0 * (n * 256.0)
    gy = (1.0 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2.0 * (n * 256.0)
    px = np.clip(gx - tx0 * 256, 0, dem.shape[1] - 1.001)
    py = np.clip(gy - ty0 * 256, 0, dem.shape[0] - 1.001)
    x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int)
    fx = px - x0; fy = py - y0
    return ((dem[y0, x0] * (1 - fx) + dem[y0, x0 + 1] * fx) * (1 - fy) +
            (dem[y0 + 1, x0] * (1 - fx) + dem[y0 + 1, x0 + 1] * fx) * fy)
