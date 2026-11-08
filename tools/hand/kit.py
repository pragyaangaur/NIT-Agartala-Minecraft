"""Generic pieces for hostels, halls and smaller campus buildings."""
import math
from style import Face, FLOOR, ROOF


def block(v, x0, x1, z0, z1, top, wall, floors=None, floor_h=4):
    """Hollow block with floor slabs. Returns the list of floor levels."""
    floors = floors or list(range(1, top, floor_h))
    v.box(x0, x1, 1, top, z0, z1, wall)
    if x1 - x0 >= 2 and z1 - z0 >= 2:
        v.box(x0 + 1, x1 - 1, 2, top - 1, z0 + 1, z1 - 1, None)
        for fy in floors:
            v.box(x0 + 1, x1 - 1, fy, fy, z0 + 1, z1 - 1, FLOOR)
    v.box(x0, x1, 0, 0, z0, z1, FLOOR)
    return floors


def windows(v, x0, x1, z0, z1, floors, glass="tinted_glass", every=3, width=1, height=2, sides="nesw",
            skip_ends=1, frame=None):
    """Punch window rows into the walls of a box."""
    for s, name in (("n", "north"), ("e", "east"), ("s", "south"), ("w", "west")):
        if s not in sides:
            continue
        f = Face(v, name, x0, x1, z0, z1)
        for u in range(skip_ends, f.n - skip_ends):
            if (u - skip_ends) % every < width:
                for fy in floors:
                    for dy in range(1, 1 + height):
                        f.set(u, fy + dy, glass)
                    if frame:
                        f.set(u, fy + height + 1, frame, out=0)


def gable_roof(v, x0, x1, z0, z1, y, stairs="brick_stairs", full="bricks", ridge_axis="z", overhang=1,
               gable_wall=None):
    """Pitched roof over a box whose top wall layer is y-1. Ridge runs along ridge_axis."""
    if ridge_axis == "z":
        a0, a1 = x0 - overhang, x1 + overhang
        b0, b1 = z0 - overhang, z1 + overhang
    else:
        a0, a1 = z0 - overhang, z1 + overhang
        b0, b1 = x0 - overhang, x1 + overhang
    k = 0
    while a0 + k <= a1 - k:
        yy = y + k
        lo, hi = a0 + k, a1 - k
        for b in range(b0, b1 + 1):
            if lo == hi:
                put(v, ridge_axis, lo, yy, b, full.replace("bricks", "brick_slab") if full.endswith("bricks") else full)
            else:
                f1, f2 = ("east", "west") if ridge_axis == "z" else ("south", "north")
                put(v, ridge_axis, lo, yy, b, f"{stairs}[facing={f1}]")
                put(v, ridge_axis, hi, yy, b, f"{stairs}[facing={f2}]")
                for a in range(lo + 1, hi):
                    if hi - lo > 1:
                        put(v, ridge_axis, a, yy, b, full if a in (lo + 1, hi - 1) and b not in (b0, b1) else None, keep=True)
        # gable end walls
        if gable_wall:
            for a in range(lo + 1, hi):
                for b in (b0 + overhang, b1 - overhang):
                    put(v, ridge_axis, a, yy, b, gable_wall)
        k += 1
    return y + k


def put(v, axis, a, y, b, blk, keep=False):
    if blk is None:
        return
    if axis == "z":
        if keep and v.get(a, y, b) is not None:
            return
        v.set(a, y, b, blk)
    else:
        if keep and v.get(b, y, a) is not None:
            return
        v.set(b, y, a, blk)


def flat_roof(v, x0, x1, z0, z1, y, parapet="smooth_quartz", roof=ROOF):
    v.box(x0, x1, y, y, z0, z1, roof)
    for x in range(x0, x1 + 1):
        v.set(x, y + 1, z0, parapet); v.set(x, y + 1, z1, parapet)
    for z in range(z0, z1 + 1):
        v.set(x0, y + 1, z, parapet); v.set(x1, y + 1, z, parapet)


def balcony_corridor(f, u0, u1, floors, rail="smooth_quartz_slab", depth=2, floor_blk="smooth_stone"):
    """Open corridor along a facade: slab floors and a low rail at each upper level."""
    for fy in floors[1:]:
        for u in range(u0, u1 + 1):
            for d in range(1, depth + 1):
                f.set(u, fy, floor_blk, out=d)
            f.set(u, fy + 1, rail, out=depth)


def door(f, u, y=1, w=2, h=3, blk="light_gray_stained_glass"):
    for du in range(w):
        for dy in range(h):
            f.set(u + du, y + dy, blk)


def tree(v, x, y, z, h=6, r=3, log="oak_log", leaves="oak_leaves[persistent=true]"):
    for k in range(h):
        v.set(x, y + k, z, log)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dy in range(-2, 2):
                if dx * dx + dz * dz + (dy * 1.6) ** 2 <= r * r and v.get(x + dx, y + h + dy, z + dz) is None:
                    v.set(x + dx, y + h + dy, z + dz, leaves)
