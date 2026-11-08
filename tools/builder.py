"""Voxel construction of campus buildings from footprints + specs."""
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_erosion
import geom2d as G
from blocks import B

class Model:
    def __init__(self, x0, z0, nx, nz, ybase, ny):
        self.x0, self.z0, self.nx, self.nz, self.ybase, self.ny = x0, z0, nx, nz, ybase, ny
        self.vol = np.zeros((nx, nz, ny), dtype=np.uint16)
        self.X = x0 + np.arange(nx) + 0.5
        self.Z = z0 + np.arange(nz) + 0.5
        self.XX, self.ZZ = np.meshgrid(self.X, self.Z, indexing="ij")

    def set(self, mask, y, blk):
        yy = y - self.ybase
        if 0 <= yy < self.ny and mask.any():
            self.vol[mask, yy] = blk

    def fill(self, mask, y0, y1, blk):
        a, b = max(0, y0 - self.ybase), min(self.ny, y1 - self.ybase)
        if b > a and mask.any():
            self.vol[mask, a:b] = blk

    def get(self, y):
        return self.vol[:, :, y - self.ybase]

def _top_span(mask, axis, k):
    if k <= 0: return mask
    n = 2 * k + 1
    st = np.ones((n, 1), bool) if axis == 0 else np.ones((1, n), bool)
    return binary_erosion(mask, st, border_value=0)

def _roof(mask, y, spec, model, ridge_axis):
    kind = spec.get("roof", "flat")
    mat = B[spec.get("roof_mat", "concrete_lg")]
    alt = B[spec.get("roof_mat2", spec.get("roof_mat", "concrete_lg"))]
    rise = 1
    if kind in ("flat", "drum"):
        model.set(mask, y, mat)
        if kind == "drum":
            d = distance_transform_edt(mask)
            r = d[mask].max() if mask.any() else 2
            r0 = max(2.5, r * 0.42)
            drum = d > r0
            # clerestory ring, then a shallow dome
            model.fill(drum, y, y + 4, alt)
            model.set(drum & (d <= r0 + 1.0), y + 1, B["glass_lb"])
            for k in range(1, 5):
                inner = d > r0 + k * (r0 / 5.0)
                model.set(inner, y + 4 + k, mat)
            apex = d > r0 + 4 * (r0 / 5.0) + 1.5
            model.set(apex, y + 10, B["glass_lb"])
            return 11
        return 1
    if kind in ("gable", "gable_low", "shell"):
        ax = ridge_axis
        d = distance_transform_edt(mask)
        span = np.percentile(d[mask], 55) if mask.any() else 2
        if kind == "gable":       maxk = int(max(2, span))
        elif kind == "gable_low": maxk = int(max(1, span * 0.45))
        else:                     maxk = int(max(3, min(7.0, span * 0.55)))
        for k in range(1, maxk + 1):
            if kind == "shell":
                inset = int(round(span * (1 - np.sqrt(max(0.0, 1 - (k / maxk) ** 2)))))
            else:
                inset = k
            m = _top_span(mask, ax, inset)
            if not m.any() or m.sum() < 0.04 * mask.sum():
                break
            model.set(m, y + k, mat if k < maxk * 0.85 else alt)
            rise = k
        return rise
    if kind in ("hip", "radial"):
        d = distance_transform_edt(mask)
        span = d[mask].max() if mask.any() else 2
        maxk = int(max(2, span * (0.55 if kind == "radial" else 1.0)))
        for k in range(1, maxk + 1):
            m = d > k
            if not m.any(): break
            model.set(m, y + k, mat if (k % 2 or kind == "hip") else alt)
            rise = k
        return rise
    if kind == "shed":
        coord = model.XX if ridge_axis == 0 else model.ZZ
        cmax = coord[mask].max()
        d = distance_transform_edt(mask)
        maxk = int(max(1, np.percentile(d[mask], 50)))
        for k in range(1, maxk + 1):
            m = mask & (coord > cmax - max(1.5, maxk + 1 - k) - 0.5)
            if not m.any(): break
            model.set(m, y + k, mat)
            rise = k
        return rise
    model.set(mask, y, mat)
    return 1

def window_rhythm(mask, period, width, XX, ZZ):
    d = distance_transform_edt(mask)
    gz, gx = np.gradient(d)
    nn = np.hypot(gx, gz); nn[nn < 1e-6] = 1
    tx, tz = -gz / nn, gx / nn
    s = XX * tx + ZZ * tz
    f = np.mod(s, float(period))
    return (f < width) | (f > period - 0.30)

def build(model, mask, y0, spec, seed=0):
    rng = np.random.default_rng(seed)
    wall = B[spec.get("wall", "concrete_w")]
    wall2 = B[spec.get("wall2", "concrete_lg")]
    winb = B[spec.get("win", "glass_g")]
    floors = int(spec.get("floors", 2))
    sh = float(spec.get("storey", 3.4))
    skirt = int(spec.get("plinth", 1))
    P = np.argwhere(mask)
    if len(P) < 4:
        return y0
    ext_x = np.ptp(P[:, 0]); ext_z = np.ptp(P[:, 1])
    ridge = 0 if ext_x >= ext_z else 1
    if skirt:
        model.fill(mask, y0 - skirt, y0, B["smooth_stone"])
    wall_mask = G.ring(mask, 1)
    inner = G.erode(mask, 1)
    wm = wall_mask if inner.sum() else mask
    wr = window_rhythm(mask, spec.get("win_period", 3), spec.get("win_width", 2), model.XX, model.ZZ)
    wall_cells = wm & ~wr
    win_cells = wm & wr
    for f in range(floors):
        yb = y0 + int(round(f * sh))
        yt = y0 + int(round((f + 1) * sh))
        if f > 0:
            model.set(mask, yb, B["smooth_stone"])
        model.fill(wall_cells, yb + 1, yt, wall if f % 2 == 0 else wall2)
        model.fill(win_cells, yb + 1, min(yt, yb + 3), winb)
        model.fill(win_cells, min(yt, yb + 3), yt, wall)
    top = y0 + int(round(floors * sh))
    model.fill(wm, y0, min(y0 + 2, y0 + int(sh)), wall2)
    rise = _roof(mask, top, spec, model, ridge)
    pp = int(spec.get("parapet", 1))
    if pp:
        ring = G.ring(mask, 1)
        model.fill(ring, top, top + pp, wall2)
        model.set(ring, top + pp, B["smooth_stone"])
    if spec.get("roof_kit") and inner.any():
        # stair towers at two corners of the roof
        d0 = distance_transform_edt(inner)
        corners = np.argwhere(inner & (d0 <= 3.5))
        if len(corners) > 8:
            for t in range(2):
                c = corners[(t * 7919) % len(corners)]
                m4 = np.zeros_like(mask)
                x0, z0 = int(c[0]) - 1, int(c[1]) - 1
                m4[max(0, x0):x0 + 4, max(0, z0):z0 + 4] = True
                m4 &= inner
                model.fill(m4, top, top + pp + 3, wall2)
                model.set(m4, top + pp + 3, B["smooth_stone"])
        idx = np.argwhere(inner)
        for _ in range(int(2 + rng.integers(0, 4))):
            cx, cz = idx[rng.integers(0, len(idx))]
            m3 = np.zeros_like(mask)
            m3[max(0, cx - 1):cx + 2, max(0, cz - 1):cz + 2] = True
            m3 &= inner
            model.fill(m3, top + pp, top + pp + 2, B["concrete_g"])
            model.set(m3, top + pp + 2, B["iron"])
    if spec.get("rooflight") and inner.any():
        d = distance_transform_edt(inner)
        cl = inner & (d > np.percentile(d[inner], 60))
        model.set(cl, top, B["glass_lb"])
    return top + rise + pp

def entrance(model, mask, y0, wall_cell, normal, spec, gnd, w=3):
    """Cut a door in the wall at wall_cell, add a canopy slab and a stepped approach."""
    ix0, iz0 = int(wall_cell[0]), int(wall_cell[1])
    nx, nz = normal
    tx, tz = -nz, nx
    for i in range(-1, 2):
        ix = int(round(ix0 + tx * i)); iz = int(round(iz0 + tz * i))
        if 0 <= ix < model.nx and 0 <= iz < model.nz and mask[ix, iz]:
            model.fill(_one(model, ix, iz), y0, y0 + 3, B["glass_br"])
    for d in range(1, 4):
        for i in range(-2, 3):
            ix = int(round(ix0 + nx * d + tx * i)); iz = int(round(iz0 + nz * d + tz * i))
            if 0 <= ix < model.nx and 0 <= iz < model.nz:
                model.vol[ix, iz, min(model.ny - 1, y0 + 3 - model.ybase)] = B["concrete_w"]
    for s in range(1, 4):
        for i in range(-2, 3):
            ix = int(round(ix0 + nx * s + tx * i)); iz = int(round(iz0 + nz * s + tz * i))
            if 0 <= ix < model.nx and 0 <= iz < model.nz:
                gy = gnd + s - 1
                if gy < y0:
                    model.fill(_one(model, ix, iz), gy, y0, B["smooth_stone"])

def _one(model, ix, iz):
    m = np.zeros((model.nx, model.nz), bool)
    m[ix, iz] = True
    return m
