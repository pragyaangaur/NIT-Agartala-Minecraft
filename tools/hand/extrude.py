"""Build buildings straight from footprint polygons, at any angle.

Each building: a polygon in world x/z, a number of storeys, wall and roof materials.
Walls follow the outline, windows run in rows, and the roof is either flat with a parapet
or a hipped roof made from the distance to the outline (it follows any plan shape).
"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, binary_dilation
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from vox import Vox

_EL = None
_MS = None


def osm_poly(way_id):
    global _EL
    import geo
    if _EL is None:
        _EL = json.load(open(os.path.join(ROOT, "data/osm/campus_full.json")))["elements"]
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in _EL if e["type"] == "node"}
    w = [e for e in _EL if e["type"] == "way" and e["id"] == way_id][0]
    g = w.get("geometry") or [{"lat": nodes[n][0], "lon": nodes[n][1]} for n in w["nodes"] if n in nodes]
    x, z = geo.xy([p["lat"] for p in g], [p["lon"] for p in g])
    return list(zip(x, z))


def ms_poly(i):
    global _MS
    if _MS is None:
        _MS = json.load(open(os.path.join(ROOT, "data/model/ms_new.json")))
    return [tuple(p) for p in _MS[i]["pts"]]


def rect_poly(cx, cz, length, width, angle_deg):
    """Rectangle centred at (cx, cz), long side at angle (degrees from +x towards +z)."""
    a = math.radians(angle_deg)
    ux, uz = math.cos(a), math.sin(a)
    vx, vz = -uz, ux
    h, w = length / 2, width / 2
    return [(cx + sx * h * ux + sy * w * vx, cz + sx * h * uz + sy * w * vz)
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def mask_of(poly, x0, z0, nx, nz):
    im = Image.new("L", (nx, nz), 0)
    ImageDraw.Draw(im).polygon([(x - x0 - 0.5, z - z0 - 0.5) for x, z in poly], fill=1, outline=1)
    return np.asarray(im, bool).T          # [x, z]


class Building:
    def __init__(self, poly, storeys=3, storey_h=4, wall="smooth_quartz", roof="hip",
                 roof_mat="bricks", glass="tinted_glass", base=None, band=None, slope=0.6,
                 win_every=3, parapet=None, roof_floor="white_concrete", ground=None, extra_h=0, holes=(), ridge=None, bands=None, detail=True, pilaster=None, shade="smooth_stone_slab[type=top]", entrance=True, roof_kit=True):
        self.poly, self.storeys, self.storey_h = poly, storeys, storey_h
        self.wall, self.roof, self.roof_mat, self.glass = wall, roof, roof_mat, glass
        self.base, self.band, self.slope, self.win_every = base, band, slope, win_every
        self.parapet = parapet or wall
        self.roof_floor = roof_floor
        self.ground = ground
        self.extra_h = extra_h
        self.holes = holes
        self.ridge = ridge
        self.bands = bands or {}
        self.detail, self.pilaster, self.shade = detail, pilaster, shade
        self.entrance, self.roof_kit = entrance, roof_kit
        self.door = None

    def bbox(self, margin=3):
        xs = [p[0] for p in self.poly]; zs = [p[1] for p in self.poly]
        return (int(math.floor(min(xs))) - margin, int(math.floor(min(zs))) - margin,
                int(math.ceil(max(xs))) + margin, int(math.ceil(max(zs))) + margin)

    def build(self, gy):
        x0, z0, x1, z1 = self.bbox()
        nx, nz = x1 - x0 + 1, z1 - z0 + 1
        m = mask_of(self.poly, x0, z0, nx, nz)
        for h in self.holes:
            hm = mask_of(h, x0, z0, nx, nz)
            m &= ~(hm & ~(binary_dilation(~hm)))      # keep the hole's own outline as wall
        if self.ground is None:
            gs = [gy(x0 + i, z0 + k) for i, k in zip(*np.nonzero(m))]
            self.ground = int(np.median(gs)) if gs else 70
        H = self.storeys * self.storey_h + self.extra_h
        ny = H + 25
        v = Vox(nx, ny, nz)
        inner = m & ~binary_dilation(~m)
        edge = m & ~inner
        floors = [1 + k * self.storey_h for k in range(self.storeys)]
        pil = self.pilaster or self.band or self.base or self.wall
        outs = {}
        for i, k in zip(*np.nonzero(m)):
            v.a[i, 0, k] = "smooth_stone"
            if edge[i, k]:
                # outward direction: first neighbour outside the footprint
                od = None
                for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ii, kk = i + di, k + dk
                    if not (0 <= ii < nx and 0 <= kk < nz) or not m[ii, kk]:
                        od = (di, dk); break
                out_x = od is not None and od[0] != 0
                along = (k if out_x else i) + (z0 if out_x else x0)
                outs[(i, k)] = (od, along)
                we = self.win_every
                win_slot = (along % we in (1, 2)) if (self.detail and we >= 4) else (along % we == 0)
                is_pil = self.detail and we >= 4 and along % we == 0 and along % (we * 2) == 0
                for y in range(1, H + 1):
                    b = self.wall
                    if self.base and y <= self.storey_h:
                        b = self.base
                    fy = (y - 1) % self.storey_h
                    if 1 <= fy <= 2 and y <= self.storeys * self.storey_h and win_slot:
                        b = self.glass
                    if self.band and fy == 0 and y > 1:
                        b = self.band
                    if y in self.bands and b != self.glass:
                        b = self.bands[y]
                    if is_pil:
                        b = pil
                    v.a[i, y, k] = b
                    if od and self.detail and self.shade and b == self.glass and fy == 2:
                        oi, ok = i + od[0], k + od[1]
                        if 0 <= oi < nx and 0 <= ok < nz and not m[oi, ok]:
                            v.a[oi, y + 1, ok] = self.shade
                    if od and is_pil and self.detail:
                        oi, ok = i + od[0], k + od[1]
                        if 0 <= oi < nx and 0 <= ok < nz and not m[oi, ok]:
                            v.a[oi, y, ok] = pil
            else:
                for fy in floors:
                    v.a[i, fy, k] = "smooth_stone"
                if self.detail and (x0 + i) % 3 == 0 and (z0 + k) % 3 == 0:
                    for st in range(self.storeys):
                        v.a[i, (st + 1) * self.storey_h, k] = "light[level=15]"
        # entrance: middle of the south-most (else east) facing wall run, with a canopy
        if self.detail and self.entrance and outs:
            for want in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                cand = [(i, k) for (i, k), (od, al) in outs.items() if od == want]
                if len(cand) >= 6:
                    cand.sort(key=lambda c: c[0] if want[1] else c[1])
                    ci, ck = cand[len(cand) // 2]
                    self.door = (ci, ck, want)
                    for dd in (-1, 0, 1):
                        ii, kk = (ci + dd, ck) if want[1] else (ci, ck + dd)
                        if (ii, kk) in outs:
                            for y in (1, 2, 3):
                                v.a[ii, y, kk] = "air" if y < 3 else "light_gray_stained_glass"
                            for d in (1, 2):
                                oi, ok = ii + want[0] * d, kk + want[1] * d
                                if 0 <= oi < nx and 0 <= ok < nz and not m[oi, ok]:
                                    v.a[oi, 4, ok] = "smooth_stone_slab[type=top]"
                                    v.a[oi, 0, ok] = "polished_andesite"
                                    v.a[oi, 3, ok] = "light[level=15]"
                    for dd in (-3, 3):                        # potted plants either side of the door
                        ii, kk = (ci + dd, ck) if want[1] else (ci, ck + dd)
                        oi, ok = ii + want[0], kk + want[1]
                        if 0 <= oi < nx and 0 <= ok < nz and not m[oi, ok] and v.a[oi, 1, ok] is None:
                            v.a[oi, 0, ok] = "polished_andesite"
                            v.a[oi, 1, ok] = "potted_fern" if dd < 0 else "potted_azalea_bush"
                    break
        top = H + 1
        if self.roof == "flat":
            for i, k in zip(*np.nonzero(m)):
                v.a[i, top - 1, k] = self.roof_floor if not edge[i, k] else self.wall
                if edge[i, k]:
                    v.a[i, top, k] = self.parapet
                    if self.detail:
                        v.a[i, top + 1, k] = "smooth_stone_slab"
            if self.detail and self.roof_kit:
                core = m & ~binary_dilation(~m, iterations=4)
                cells = [tuple(c) for c in np.argwhere(core)]
                if cells:
                    ci, ck = np.array(cells).mean(0).round().astype(int)
                    if not core[ci, ck]:
                        ci, ck = cells[len(cells) // 2]
                    for i in range(ci - 2, ci + 2):              # stair room
                        for k in range(ck - 2, ck + 1):
                            if 0 <= i < nx and 0 <= k < nz and m[i, k]:
                                for y in (top, top + 1, top + 2):
                                    v.a[i, y, k] = self.wall
                                v.a[i, top + 3, k] = "smooth_stone_slab"
                    for n, (i, k) in enumerate(cells[:: max(1, len(cells) // 3)][:3]):
                        if abs(i - ci) > 3 or abs(k - ck) > 3:     # black water tanks on stands
                            v.a[i, top, k] = "iron_bars"
                            v.a[i, top + 1, k] = "black_concrete"
                            v.a[i, top + 2, k] = "black_concrete"
        else:
            mo = binary_dilation(m)                                   # one-block eave
            d = distance_transform_edt(mo)
            dmax = d.max()
            for i, k in zip(*np.nonzero(mo)):
                h = int(round((d[i, k] - 1) * self.slope))
                y = top + h
                v.a[i, y, k] = self.ridge if (self.ridge and d[i, k] >= dmax - 1.5) else self.roof_mat
                if h > 0:
                    v.a[i, y - 1, k] = self.roof_mat
                if not m[i, k]:
                    continue
                for yy in range(top, y - 1):
                    if edge[i, k] and False:
                        v.a[i, yy, k] = self.wall
        self.v, self.origin, self.mask = v, (x0, self.ground, z0), m
        return v

    def inside_holes(self, X, Z):
        for h in self.holes:
            xs = [p[0] for p in h]; zs = [p[1] for p in h]
            if min(xs) <= X <= max(xs) and min(zs) <= Z <= max(zs):
                return True
        return False

    def commands(self, gy, clear_margin=3):
        v = self.build(gy)
        x0, g, z0 = self.origin
        nx, ny, nz = v.shape
        cmds = []
        big = binary_dilation(self.mask, iterations=clear_margin) if clear_margin > 0 else self.mask.copy()
        for i, k in zip(*np.nonzero(big)):
            X, Z = x0 + i, z0 + k
            t = gy(X, Z)
            cmds.append(f"fill {X} {g + 1} {Z} {X} {max(g, t) + 30} {Z} air")
            if self.mask[i, k] or self.inside_holes(X, Z):
                cmds.append(f"fill {X} {min(t, g) - 6} {Z} {X} {g} {Z} {'stone' if self.mask[i, k] else 'grass_block'}")
            elif t > g:
                cmds.append(f"setblock {X} {g} {Z} grass_block")
            elif t < g:
                cmds.append(f"fill {X} {t + 1} {Z} {X} {g - 1} {Z} dirt")
                cmds.append(f"setblock {X} {g} {Z} grass_block")
        cmds += v.commands(x0, g, z0)
        return cmds


def clear_poly(poly, gy, margin=3, height=40):
    """Remove an old generated building: clear above ground over an outline plus margin."""
    b = Building(poly)
    x0, z0, x1, z1 = b.bbox(margin + 1)
    m = mask_of(poly, x0, z0, x1 - x0 + 1, z1 - z0 + 1)
    if margin > 0:
        m = binary_dilation(m, iterations=margin)
    cmds = []
    for i, k in zip(*np.nonzero(m)):
        X, Z = x0 + i, z0 + k
        t = gy(X, Z)
        cmds.append(f"fill {X} {t + 1} {Z} {X} {t + height} {Z} air")
        cmds.append(f"setblock {X} {t} {Z} grass_block")
    return cmds


def rel_polys(rel_id):
    """Outer and inner rings of an OSM multipolygon fetched into data/osm/relations/."""
    import geo
    d = json.load(open(os.path.join(ROOT, f"data/osm/relations/{rel_id}.json")))["elements"]
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in d if e["type"] == "node"}
    rel = [e for e in d if e["type"] == "relation"][0]
    ways = {e["id"]: e for e in d if e["type"] == "way"}
    outer, inner = [], []
    for m in rel["members"]:
        w = ways.get(m["ref"])
        if not w:
            continue
        x, z = geo.xy([nodes[n][0] for n in w["nodes"]], [nodes[n][1] for n in w["nodes"]])
        (outer if m.get("role") == "outer" else inner).append(list(zip(x, z)))
    return outer, inner


def clear_box(x0, z0, x1, z1, gy, height=45):
    """Strip everything above the terrain in a box (old generated buildings, trees)."""
    cmds = []
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            t = gy(x, z)
            cmds.append(f"fill {x} {t + 1} {z} {x} {t + height} {z} air")
            cmds.append(f"setblock {x} {t} {z} grass_block")
    return cmds
