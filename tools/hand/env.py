"""Bring the outdoors to life: roads, footpaths, lamps, water edges, tree variety, glass.

Works on the model grids (ground height, road mask and kind, water) in 256 m tiles.
Campus roads (inside the campus outline) get dark asphalt, yellow-and-black striped kerbs as
in the tour videos, a dashed centre line on the wider roads, multicoloured paver footpaths
and double-arm street lamps. Village roads get plain asphalt and wooden poles with lanterns.
Ponds and the lake get reeds and lily pads. Trees are mixed into several species, palms line
the campus roads, and tinted window glass becomes grey stained glass so lit rooms show at
night. Hand-built areas keep their own ground and are skipped for kerbs and footpaths.
"""
import sys, os, json, math, random
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt
from matplotlib.path import Path
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import geo, generic

X0, Z0 = 32, 64
GY = np.load(os.path.join(ROOT, "data/model/gy.npy"))
ROAD = np.load(os.path.join(ROOT, "data/model/road_mask.npy"))
KIND = np.load(os.path.join(ROOT, "data/model/road_kind.npy"))
WATER = np.load(os.path.join(ROOT, "data/model/water.npy"))
BM = np.load(os.path.join(ROOT, "data/model/bmask.npy"))
NX, NZ = GY.shape


def campus_mask():
    out = json.load(open(os.path.join(ROOT, "data/osm/campus_outline.json")))["elements"]
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in out if e["type"] == "node"}
    w = [e for e in out if e["type"] == "way"][0]
    g = w.get("geometry") or [{"lat": nodes[n][0], "lon": nodes[n][1]} for n in w["nodes"]]
    x, z = geo.xy([p["lat"] for p in g], [p["lon"] for p in g])
    p = Path(np.c_[x, z])
    XX, ZZ = np.meshgrid(np.arange(NX) + X0 + 0.5, np.arange(NZ) + Z0 + 0.5, indexing="ij")
    return p.contains_points(np.c_[XX.ravel(), ZZ.ravel()]).reshape(NX, NZ)


CAMPUS = campus_mask()
HAND = np.zeros((NX, NZ), bool)
for (a, b, c, d) in generic.hand_boxes():
    HAND[max(a - X0, 0):max(c - X0 + 1, 0), max(b - Z0, 0):max(d - Z0 + 1, 0)] = True
# every footprint we know of, so footpaths and lamps keep off buildings
FOOT = BM.copy()
BIGROAD = ROAD & (KIND >= 3)
CAMPUS_ROAD = BIGROAD & CAMPUS
inside_road = distance_transform_edt(ROAD)
KERB = CAMPUS_ROAD & (inside_road <= 1.0)
near_road = distance_transform_edt(~CAMPUS_ROAD)
PATH = (~ROAD) & (near_road <= 2.2) & ~FOOT & ~binary_dilation(FOOT, iterations=1) & ~WATER & CAMPUS & ~HAND
CENTRE = CAMPUS_ROAD & (KIND >= 4) & (inside_road >= 2.6)
PAVERS = ["pink_terracotta", "yellow_terracotta", "white_terracotta", "pink_terracotta", "light_gray_terracotta",
          "red_terracotta"]


def gy(i, k):
    return int(GY[i, k])


def lamp_sites():
    """Footpath cells next to a campus kerb, spaced about 24 m apart."""
    rng = random.Random(3)
    cand = PATH & (near_road <= 1.5)
    pts = np.argwhere(cand)
    rng.shuffle(pts := [tuple(p) for p in pts])
    chosen = []
    grid = {}
    for (i, k) in pts:
        key = (i // 24, k // 24)
        ok = True
        for di in (-1, 0, 1):
            for dk in (-1, 0, 1):
                for (a, b) in grid.get((key[0] + di, key[1] + dk), []):
                    if (a - i) ** 2 + (b - k) ** 2 < 22 ** 2:
                        ok = False
        if ok:
            chosen.append((i, k)); grid.setdefault(key, []).append((i, k))
    return chosen


def pole_sites():
    rng = random.Random(5)
    cand = (~ROAD) & (distance_transform_edt(~(BIGROAD & ~CAMPUS)) <= 1.5) & ~FOOT & ~WATER & ~CAMPUS
    pts = [tuple(p) for p in np.argwhere(cand)]
    rng.shuffle(pts)
    chosen, grid = [], {}
    for (i, k) in pts:
        key = (i // 36, k // 36)
        if all((a - i) ** 2 + (b - k) ** 2 >= 34 ** 2 for di in (-1, 0, 1) for dk in (-1, 0, 1)
               for (a, b) in grid.get((key[0] + di, key[1] + dk), [])):
            chosen.append((i, k)); grid.setdefault(key, []).append((i, k))
    return chosen


def toward_road(i, k):
    best, bd = (1, 0), 99
    for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for s in range(1, 4):
            ii, kk = i + di * s, k + dk * s
            if 0 <= ii < NX and 0 <= kk < NZ and ROAD[ii, kk]:
                if s < bd:
                    best, bd = (di, dk), s
                break
    return best


def lamp(i, k):
    X, Z, y = i + X0, k + Z0, gy(i, k)
    di, dk = toward_road(i, k)
    c = [f"fill {X} {y + 1} {Z} {X} {y + 6} {Z} andesite_wall", f"setblock {X} {y + 7} {Z} polished_andesite_slab"]
    for s in (1, -1):                                  # double arm along the road
        ax, az = X + s * dk, Z + s * di
        c.append(f"setblock {ax} {y + 7} {az} iron_bars")
        c.append(f"setblock {ax} {y + 6} {az} lantern[hanging=true]")
    c.append(f"setblock {X + di} {y + 7} {Z + dk} iron_bars")
    c.append(f"setblock {X + di} {y + 6} {Z + dk} lantern[hanging=true]")
    return c


def pole(i, k):
    X, Z, y = i + X0, k + Z0, gy(i, k)
    di, dk = toward_road(i, k)
    return [f"fill {X} {y + 1} {Z} {X} {y + 7} {Z} spruce_fence",
            f"setblock {X} {y + 8} {Z} spruce_slab",
            f"setblock {X + di} {y + 7} {Z + dk} spruce_fence",
            f"setblock {X + di} {y + 6} {Z + dk} lantern[hanging=true]"]


def palm(i, k, rng):
    X, Z, y = i + X0, k + Z0, gy(i, k)
    h = rng.randint(6, 8)
    c = [f"fill {X} {y + 1} {Z} {X} {y + h} {Z} jungle_log", f"setblock {X} {y + h + 1} {Z} jungle_leaves[persistent=true]"]
    for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        n = 3 if di == 0 or dk == 0 else 2
        for s in range(1, n + 1):
            yy = y + h + (1 if s == 1 else 0) - (1 if s == n else 0)
            c.append(f"setblock {X + di * s} {yy} {Z + dk * s} jungle_leaves[persistent=true]")
    return c


def tile_commands(tx, tz, lamps, poles):
    i0, k0 = tx * 256 - X0, tz * 256 - Z0
    i1, k1 = i0 + 256, k0 + 256
    i0, k0 = max(i0, 0), max(k0, 0)
    i1, k1 = min(i1, NX), min(k1, NZ)
    if i0 >= i1 or k0 >= k1:
        return []
    rng = random.Random(tx * 1000 + tz)
    c = []
    for i in range(i0, i1):
        for k in range(k0, k1):
            X, Z, y = i + X0, k + Z0, gy(i, k)
            if HAND[i, k]:
                continue
            if ROAD[i, k]:
                kd = KIND[i, k]
                if CAMPUS_ROAD[i, k]:
                    if KERB[i, k]:
                        b = "yellow_concrete" if ((X + Z) // 2) % 2 else "black_concrete"
                    elif CENTRE[i, k] and (X + Z) % 6 < 3:
                        b = "white_concrete"
                    else:
                        b = "gray_concrete"
                elif kd >= 3:
                    b = "gray_concrete"
                elif kd == 2:
                    b = "dirt_path"
                else:
                    b = "polished_andesite" if CAMPUS[i, k] else "dirt_path"
                c.append(f"setblock {X} {y} {Z} {b}")
            elif PATH[i, k]:
                c.append(f"setblock {X} {y} {Z} {rng.choice(PAVERS)}")
                c.append(f"setblock {X} {y + 1} {Z} air")
            elif WATER[i, k]:
                d = 0
                if rng.random() < 0.05:
                    c.append(f"setblock {X} {y + 1} {Z} lily_pad")
            else:
                if 0 < i < NX - 1 and 0 < k < NZ - 1 and WATER[i - 1:i + 2, k - 1:k + 2].any() and not BM[i, k]:
                    if rng.random() < 0.3:
                        c.append(f"setblock {X} {y} {Z} grass_block")
                        c.append(f"fill {X} {y + 1} {Z} {X} {y + rng.randint(1, 3)} {Z} sugar_cane")
    for (i, k) in lamps:
        if i0 <= i < i1 and k0 <= k < k1:
            c += lamp(i, k)
    for (i, k) in poles:
        if i0 <= i < i1 and k0 <= k < k1:
            c += pole(i, k)
    return c


def palms_for_tile(tx, tz, lamps):
    """Palms halfway between neighbouring lamps on the wider campus roads."""
    rng = random.Random(77 + tx * 31 + tz)
    c = []
    for (i, k) in lamps:
        if not (tx * 256 - X0 <= i < tx * 256 - X0 + 256 and tz * 256 - Z0 <= k < tz * 256 - Z0 + 256):
            continue
        di, dk = toward_road(i, k)
        for s in (11, -11):
            ii, kk = i + s * dk, k + s * di
            if 0 <= ii < NX and 0 <= kk < NZ and PATH[ii, kk] and rng.random() < 0.7:
                c += palm(ii, kk, rng)
    return c


SPECIES = [None, None, None, None, ("oak_leaves", "oak_log"), ("oak_leaves", "oak_log"),
           ("mangrove_leaves", "mangrove_log"), ("dark_oak_leaves", "dark_oak_log"),
           ("flowering_azalea_leaves", "oak_log"), ("cherry_leaves", "cherry_log")]


def tree_and_glass(tx, tz):
    """Fill-replace in 32 m blocks: mix tree species, and swap tinted glass for grey stained glass."""
    c = []
    for bx in range(tx * 256, tx * 256 + 256, 32):
        for bz in range(tz * 256, tz * 256 + 256, 32):
            if bx + 31 < X0 or bz + 31 < Z0 or bx >= X0 + NX or bz >= Z0 + NZ:
                continue
            r = random.Random(bx * 7919 + bz)
            sp = r.choice(SPECIES)
            for (ya, yb) in ((62, 93), (94, 125)):
                if sp:
                    c.append(f"fill {bx} {ya} {bz} {bx + 31} {yb} {bz + 31} {sp[0]}[persistent=true] replace jungle_leaves")
                    c.append(f"fill {bx} {ya} {bz} {bx + 31} {yb} {bz + 31} {sp[1]} replace jungle_log")
                c.append(f"fill {bx} {ya} {bz} {bx + 31} {yb} {bz + 31} gray_stained_glass replace tinted_glass")
    return c
