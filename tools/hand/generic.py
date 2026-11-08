"""Creative restyling of every unnamed building, by size and setting.

Real outline and position come from OSM or the Microsoft footprints; the look is creative
liberty, seeded by the footprint id so it is stable between runs.

Campus styles
  tiny   (< 60 m2)   guard huts, pump rooms, kiosks: one storey, painted walls, tin or slab roof
  small  (60-200)    stores, offices, sheds: tin-roofed sheds, flat-roofed offices with
                     sunshades and a black water tank, or tiled cottages
  medium (200-500)   two or three storey blocks with colour bands, sunshades, stair room, tanks
Village style (outside the campus outline)
  painted houses in assorted colours with gable tin roofs, front verandas on posts, some
  thatch, some two-storey concrete houses with a roof tank and rods sticking up.
"""
import sys, os, json, math, random
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from extrude import mask_of, osm_poly, ms_poly

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

CAMPUS_WALLS = ["white_concrete", "smooth_quartz", "white_terracotta", "smooth_sandstone", "light_blue_terracotta"]
CAMPUS_BANDS = ["red_terracotta", "light_gray_concrete", "blue_terracotta", "yellow_terracotta", "orange_terracotta"]
VILLAGE_WALLS = ["pink_terracotta", "light_blue_terracotta", "yellow_terracotta", "lime_terracotta", "white_terracotta",
                 "white_concrete", "orange_terracotta", "cyan_terracotta", "magenta_terracotta", "light_gray_concrete",
                 "bricks", "pink_concrete", "light_blue_concrete"]
TIN = ["iron_block", "light_gray_concrete", "weathered_cut_copper", "exposed_cut_copper", "blue_concrete",
       "red_concrete", "green_terracotta", "cyan_concrete"]


def axes(poly):
    P = np.array(poly)
    c = P.mean(0)
    _, _, vt = np.linalg.svd(P - c)
    return c, vt[0], vt[1]


class Gen:
    def __init__(self, poly, seed, kind, village=False, style=None):
        self.poly, self.kind, self.village, self.style = poly, kind, village, style
        self.r = random.Random(seed)

    def choose(self):
        r = self.r
        self.sunshade = None
        if self.style == "quarters":
            self.wall, self.trim = "white_terracotta", "red_terracotta"
            self.base = "orange_terracotta"
            self.storeys = r.choice([3, 4, 4, 5])
            self.roof, self.roof_mat, self.veranda, self.storey_h = "flat", None, False, 3
            self.sunshade = "brick_slab[type=top]"
            return
        if self.kind == "large" and not self.village:
            self.wall = r.choice(["white_concrete", "smooth_quartz", "smooth_sandstone", "white_terracotta"])
            self.trim = r.choice(["red_terracotta", "orange_terracotta", "blue_terracotta", "light_gray_concrete"])
            self.base = None
            self.storeys = r.choice([3, 4, 4, 5])
            self.roof = r.choice(["flat", "flat", "flat", "hip"])
            self.roof_mat = r.choice(["bricks", "red_terracotta"]) if self.roof == "hip" else None
            self.veranda, self.storey_h = False, 4
            self.sunshade = r.choice([None, "smooth_quartz_slab[type=top]", "smooth_stone_slab[type=top]"])
            return
        self.base = None
        if self.village:
            self.wall = r.choice(VILLAGE_WALLS)
            self.trim = r.choice(["white_concrete", "light_gray_concrete", "red_terracotta", "blue_terracotta"])
            self.storeys = 2 if (self.kind != "tiny" and r.random() < 0.18) else 1
            self.roof = "flat" if self.storeys == 2 else r.choice(["gable"] * 6 + ["thatch", "hip"])
            self.roof_mat = r.choice(TIN) if self.roof == "gable" else "hay_block" if self.roof == "thatch" else "bricks"
            self.veranda = self.storeys == 1 and r.random() < 0.6
            self.storey_h = 4
        else:
            self.wall = r.choice(CAMPUS_WALLS)
            self.trim = r.choice(CAMPUS_BANDS)
            if self.kind == "tiny":
                self.storeys = 1
                self.roof = r.choice(["flat", "gable", "gable"])
            elif self.kind == "small":
                self.storeys = r.choice([1, 1, 2])
                self.roof = r.choice(["flat", "flat", "gable", "hip"])
            else:
                self.storeys = r.choice([2, 2, 3])
                self.roof = r.choice(["flat", "flat", "flat", "hip"])
            self.roof_mat = r.choice(["iron_block", "light_gray_concrete", "red_concrete", "bricks"]) \
                if self.roof != "flat" else None
            if self.roof == "hip":
                self.roof_mat = r.choice(["bricks", "red_terracotta", "red_concrete"])
            self.veranda = self.storeys == 1 and self.kind != "tiny" and r.random() < 0.35
            self.storey_h = 4

    def commands(self, gy):
        self.choose()
        P = np.array(self.poly)
        x0, z0 = int(math.floor(P[:, 0].min())) - 4, int(math.floor(P[:, 1].min())) - 4
        x1, z1 = int(math.ceil(P[:, 0].max())) + 4, int(math.ceil(P[:, 1].max())) + 4
        nx, nz = x1 - x0 + 1, z1 - z0 + 1
        m = mask_of(self.poly, x0, z0, nx, nz)
        if m.sum() < 4:
            return []
        gs = [gy(x0 + i, z0 + k) for i, k in zip(*np.nonzero(m))]
        g = int(np.median(gs))
        H = self.storeys * self.storey_h
        c, ua, ub = axes(self.poly)
        X = np.arange(nx)[:, None] + x0 + 0.5
        Z = np.arange(nz)[None, :] + z0 + 0.5
        across = (X - c[0]) * ub[0] + (Z - c[1]) * ub[1]          # signed distance across the ridge
        half = np.abs(across[m]).max() + 0.5
        inner = m & ~binary_dilation(~m)
        edge = m & ~inner
        out = {}

        def put(i, k, y, b):
            out[(i, y, k)] = b

        # ---- foundation and clearing
        cmds = []
        clear = binary_dilation(m, iterations=2)
        for i, k in zip(*np.nonzero(clear)):
            X_, Z_ = x0 + i, z0 + k
            t = gy(X_, Z_)
            cmds.append(f"fill {X_} {min(t, g) + 1} {Z_} {X_} {max(t, g) + H + 14} {Z_} air")
            if m[i, k]:
                cmds.append(f"fill {X_} {min(t, g) - 3} {Z_} {X_} {g} {Z_} stone")
            elif t < g:
                cmds.append(f"fill {X_} {t} {Z_} {X_} {g} {Z_} dirt")
                cmds.append(f"setblock {X_} {g} {Z_} grass_block")
            elif t > g:
                cmds.append(f"setblock {X_} {g} {Z_} grass_block")
        r = self.r
        # door: the edge cell closest to the middle of the front (the side with positive `across`)
        front = [(i, k) for i, k in zip(*np.nonzero(edge)) if across[i, k] > half - 1.6]
        door = min(front, key=lambda p: abs((X[p[0], 0] - c[0]) * ua[0] + (Z[0, p[1]] - c[1]) * ua[1])) if front else None
        # ---- walls and floors
        for i, k in zip(*np.nonzero(m)):
            put(i, k, 0, "smooth_stone" if not self.village else "polished_andesite")
            if edge[i, k]:
                along = int(round((X[i, 0] - c[0]) * ua[0] + (Z[0, k] - c[1]) * ua[1]))
                for y in range(1, H + 1):
                    fy = (y - 1) % self.storey_h
                    b = self.wall
                    if y == 1 and not self.village:
                        b = self.trim if self.kind != "tiny" else self.wall
                    if fy in (1, 2) and along % 3 == 0 and y < H + 1:
                        b = "glass_pane" if self.village else "tinted_glass"
                    if fy == 0 and y > 1 and not self.village:
                        b = self.trim
                    if self.base and y <= self.storey_h and b != "tinted_glass":
                        b = self.base
                    put(i, k, y, b)
                    if self.sunshade and b == "tinted_glass" and fy == 2:
                        for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ii, kk = i + di, k + dk
                            if 0 <= ii < nx and 0 <= kk < nz and not m[ii, kk]:
                                put(ii, kk, y + 1, self.sunshade)
                                break
            else:
                for s in range(1, self.storeys):
                    put(i, k, 1 + s * self.storey_h, "smooth_stone")
        if door:
            i, k = door
            put(i, k, 1, "air"); put(i, k, 2, "air")
        # ---- night lights: invisible light blocks just under each ceiling
        for i, k in zip(*np.nonzero(inner)):
            if (x0 + i) % 5 == 0 and (z0 + k) % 5 == 0:
                for st in range(self.storeys):
                    put(i, k, (st + 1) * self.storey_h, "light[level=13]")
        # ---- roof
        top = H + 1
        if self.roof == "flat":
            for i, k in zip(*np.nonzero(m)):
                put(i, k, top, self.wall if edge[i, k] else "light_gray_concrete")
                if edge[i, k]:
                    put(i, k, top + 1, self.wall if self.village else self.trim)
            # black water tank (and rods on village houses)
            cells = list(zip(*np.nonzero(inner)))
            if len(cells) > 6:
                i, k = cells[r.randrange(len(cells))]
                for di in (0, 1):
                    for dk in (0, 1):
                        if inner[min(i + di, nx - 1), min(k + dk, nz - 1)]:
                            put(i + di, k + dk, top + 1, "black_concrete"); put(i + di, k + dk, top + 2, "black_concrete")
                if self.village:
                    for (i2, k2) in [p for p in zip(*np.nonzero(edge))][::7]:
                        put(i2, k2, top + 2, "iron_bars"); put(i2, k2, top + 3, "iron_bars")
                elif self.kind == "medium":
                    j, l = cells[r.randrange(len(cells))]
                    for di in range(-1, 2):
                        for dk in range(-1, 2):
                            if inner[min(max(j + di, 0), nx - 1), min(max(l + dk, 0), nz - 1)]:
                                for y in (top + 1, top + 2, top + 3):
                                    put(j + di, l + dk, y, self.wall)
        else:
            mo = binary_dilation(m)
            slope = 0.5 if self.roof != "thatch" else 0.8
            dist = distance_transform_edt(mo)
            for i, k in zip(*np.nonzero(mo)):
                if self.roof in ("gable", "thatch"):
                    h = int(math.floor((half + 1 - abs(across[i, k])) * slope))
                else:
                    h = int(math.floor((dist[i, k] - 1) * slope))
                y = top + max(h, 0)
                put(i, k, y, self.roof_mat)
                if self.roof in ("gable", "thatch") and edge[i, k]:
                    for yy in range(top, y):              # close the gable ends
                        put(i, k, yy, self.wall)
        # ---- veranda on the front for single-storey houses
        if self.veranda:
            ring = binary_dilation(m, iterations=2) & ~m
            for i, k in zip(*np.nonzero(ring)):
                if across[i, k] > half - 0.2 and across[i, k] < half + 2.6:
                    put(i, k, 0, "smooth_stone_slab" if not self.village else "polished_andesite")
                    put(i, k, self.storey_h, (self.roof_mat or "light_gray_concrete") if self.roof_mat not in (None, "hay_block") else "spruce_slab")
                    if across[i, k] > half + 1.4 and ((i + k) % 3 == 0):
                        for y in range(1, self.storey_h):
                            put(i, k, y, "spruce_fence" if self.village else "quartz_pillar")
        from vox import Vox
        ys = [y for (_, y, _) in out]
        v = Vox(nx, max(ys) + 1, nz)
        for (i, y, k), b in out.items():
            if 0 <= i < nx and 0 <= k < nz:
                v.a[i, y, k] = b if b != "air" else None
        cmds += v.commands(x0, g, z0)
        for (i, y, k), b in out.items():
            if b == "air":
                cmds.append(f"setblock {x0 + i} {g + y} {z0 + k} air")
        return cmds


# ------------------------------------------------------------------ selection
def hand_boxes():
    """Clearing boxes of every hand-built module, so generic restyling never touches them."""
    import importlib
    boxes = []
    for f in os.listdir(HERE):
        if not f.endswith(".py") or f in ("generic.py", "place.py", "restore.py", "readworld.py", "mcserver.py",
                                           "vox.py", "style.py", "kit.py", "extrude.py", "area.py", "side.py",
                                           "fplist.py", "smallgates.py", "genbatch.py", "env.py", "liveworld.py",
                                           "nightlights.py", "cleanup.py", "grounds.py", "leftovers.py", "audit.py",
                                           "lightlife.py", "worldedge.py", "fastworld.py", "interiors.py", "leaves.py",
                                           "life2.py", "restore.py", "topdown.py"):
            continue
        try:
            m = importlib.import_module(f[:-3])
        except Exception:
            continue
        if hasattr(m, "CLEAR"):
            if f[:-3] == "smallgates":
                continue
            boxes.append(tuple(m.CLEAR))
    return boxes


GROUND_BOXES = [(938, 805, 1052, 932), (942, 235, 1026, 339)]   # playing fields

SKIP_BOXES = [
    (370, 1120, 470, 1240),      # west academic cluster north of the Science Block (not hand-built yet)
    (1140, 420, 1320, 690),      # staff housing cluster (not hand-built yet)
]


def todo():
    rows = json.load(open(os.path.join(ROOT, "work", "remaining_inside.json")))
    inside = {(r[0], r[1]) for r in rows}
    hand = hand_boxes()
    jobs = []
    el = json.load(open(os.path.join(ROOT, "data/osm/campus_full.json")))["elements"]
    ms = json.load(open(os.path.join(ROOT, "data/model/ms_new.json")))
    done_osm = {1544302856, 1544302857, 1544302854, 1544302853, 361838504, 361838531, 361838528, 361838529, 361838530,
                1544302875, 361838499, 1544302874, 361838532, 361838476, 361838507, 361838509, 361838517, 1544302876,
                361838514, 1544302866, 1544302855, 361838670, 361838501, 361838658, 361838671, 1544302877,
                1544302859, 1544302858, 361838601}
    done_ms = {394, 427, 543, 128, 578, 694, 9, 352, 598, 599, 574, 404}
    drop = {tuple(d) for d in json.load(open(os.path.join(ROOT, "work", "dup_drop.json")))} \
        if os.path.exists(os.path.join(ROOT, "work", "dup_drop.json")) else set()
    cands = [("osm", e["id"]) for e in el if e["type"] == "way" and "building" in e.get("tags", {}) and e["id"] not in done_osm]
    cands += [("ms", i) for i in range(len(ms)) if i not in done_ms]
    for src, i in cands:
        if (src, i) in drop:
            continue
        poly = osm_poly(i) if src == "osm" else ms_poly(i)
        P = np.array(poly)
        cx, cz = P.mean(0)
        if any(b[0] - 3 <= cx <= b[2] + 3 and b[1] - 3 <= cz <= b[3] + 3 for b in hand):
            continue
        if any(b[0] <= cx <= b[2] and b[1] <= cz <= b[3] for b in GROUND_BOXES):
            continue
        style = "quarters" if (SKIP_BOXES[1][0] <= cx <= SKIP_BOXES[1][2] and SKIP_BOXES[1][1] <= cz <= SKIP_BOXES[1][3]) else None
        x, z = P[:, 0], P[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(z, 1)) - np.dot(z, np.roll(x, 1)))
        if area < 8:
            continue
        village = (src, i) not in inside
        kind = "tiny" if area < 60 else "small" if area < 200 else "medium" if area < 500 else "large"
        if village and kind in ("medium", "large"):
            kind = "small"
        jobs.append((src, i, poly, kind, village, float(cx), float(cz), style))
    return jobs


def seed_of(src, i):
    return int(i) + (0 if src == "osm" else 10 ** 10)
