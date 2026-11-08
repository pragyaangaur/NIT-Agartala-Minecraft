"""Hand-built buildings: a voxel grid, preview renders, and /fill command export.

Local frame: x east, y up, z south, all in blocks. Air is None.
"""
import json, os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(__file__)
_COL = json.load(open(os.path.join(HERE, "block_colors.json")))

# texture name used for the preview colour, when it differs from the block id
_TEX = {
    "smooth_quartz": "quartz_block_bottom", "quartz_block": "quartz_block_side",
    "smooth_stone": "smooth_stone", "smooth_stone_slab": "smooth_stone",
    "grass_block": "grass_block_top", "oak_leaves": "oak_leaves",
    "smooth_sandstone": "sandstone_top", "smooth_red_sandstone": "red_sandstone_top",
    "quartz_pillar": "quartz_pillar", "water": "blue_concrete",
}


def colour(block):
    base = block.split("[")[0]
    stem = base
    for suf in ("_slab", "_stairs", "_pane", "_wall", "_fence"):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
    if stem.endswith("brick"):
        stem += "s"
    # furniture and wood shapes borrow the colour of the block they are made of
    if stem in ("oak", "spruce", "birch", "dark_oak", "jungle", "acacia", "mangrove", "cherry"):
        stem += "_planks"
    elif stem.endswith("_bed") or stem.endswith("_carpet"):
        stem = stem.rsplit("_", 1)[0] + "_wool"
    elif stem in ("chest", "barrel", "lectern", "crafting_table"):
        stem = "oak_planks"
    elif stem.startswith("potted_") or stem == "decorated_pot":
        stem = "terracotta"
    elif stem == "water_cauldron":
        stem = "cauldron"
    elif stem == "quartz":
        stem = "quartz_block"
    elif stem == "lava":
        return (230, 110, 20, 1.0)
    name = _TEX.get(stem, stem)
    for cand in (name, name + "_side", name + "_top", name + "_block", base):
        if cand in _COL:
            c = _COL[cand]
            if base.endswith("_leaves") or base == "grass_block":
                return (70, 120, 50, 1.0)
            return tuple(c[:3]) + (max(c[3], 0.5),)
    return (255, 0, 255, 1.0)


class Vox:
    def __init__(self, nx, ny, nz):
        self.a = np.full((nx, ny, nz), None, dtype=object)
        self.ents = []           # extra raw commands, appended as they are

    @property
    def shape(self):
        return self.a.shape

    def box(self, x0, x1, y0, y1, z0, z1, b):
        """Inclusive box. Coordinates are clipped to the grid."""
        nx, ny, nz = self.a.shape
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        x0, y0, z0 = max(x0, 0), max(y0, 0), max(z0, 0)
        x1, y1, z1 = min(x1, nx - 1), min(y1, ny - 1), min(z1, nz - 1)
        if x0 <= x1 and y0 <= y1 and z0 <= z1:
            self.a[x0:x1 + 1, y0:y1 + 1, z0:z1 + 1] = b

    def set(self, x, y, z, b):
        nx, ny, nz = self.a.shape
        if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
            self.a[x, y, z] = b

    def get(self, x, y, z):
        nx, ny, nz = self.a.shape
        if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
            return self.a[x, y, z]
        return None

    def mirror_x(self):
        """Copy the west half onto the east half (x -> nx-1-x)."""
        nx = self.a.shape[0]
        for x in range(nx // 2):
            self.a[nx - 1 - x] = self.a[x]

    # ------------------------------------------------------------ export
    def commands(self, ox, oy, oz, air_clear=False):
        """Greedy box-merge per layer -> list of /fill and /setblock commands."""
        cmds = []
        a = self.a
        nx, ny, nz = a.shape
        for y in range(ny):
            done = np.zeros((nx, nz), bool)
            layer = a[:, y, :]
            for x in range(nx):
                for z in range(nz):
                    b = layer[x, z]
                    if done[x, z] or (b is None and not air_clear):
                        continue
                    # grow along z
                    z1 = z
                    while z1 + 1 < nz and not done[x, z1 + 1] and layer[x, z1 + 1] == b:
                        z1 += 1
                    # grow along x
                    x1 = x
                    while x1 + 1 < nx and all(not done[x1 + 1, k] and layer[x1 + 1, k] == b for k in range(z, z1 + 1)):
                        x1 += 1
                    done[x:x1 + 1, z:z1 + 1] = True
                    blk = "air" if b is None else b
                    X0, Y, Z0, X1, Z1 = ox + x, oy + y, oz + z, ox + x1, oz + z1
                    if (X0, Z0) == (X1, Z1):
                        cmds.append(f"setblock {X0} {Y} {Z0} {blk}")
                    else:
                        cmds.append(f"fill {X0} {Y} {Z0} {X1} {Y} {Z1} {blk}")
        for e in self.ents:
            cmds.append(e)
        return cmds

    # ------------------------------------------------------------ previews
    def elevation(self, face, scale=8):
        """Orthographic view of one face: 'north','south','east','west'. Depth-shaded."""
        a = self.a
        nx, ny, nz = a.shape
        if face == "north":   W, D, get = nx, nz, lambda u, d, y: a[nx - 1 - u, y, d]
        elif face == "south": W, D, get = nx, nz, lambda u, d, y: a[u, y, nz - 1 - d]
        elif face == "west":  W, D, get = nz, nx, lambda u, d, y: a[d, y, u]
        else:                 W, D, get = nz, nx, lambda u, d, y: a[nx - 1 - d, y, nz - 1 - u]
        img = np.zeros((ny, W, 3))
        img[:] = (150, 190, 230)
        for u in range(W):
            for y in range(ny):
                acc = np.zeros(3); t = 1.0
                for d in range(D):
                    b = get(u, d, y)
                    if b is None:
                        continue
                    r, g, bb, al = colour(b)
                    shade = 1.0 - min(d, 12) * 0.03
                    acc += t * al * np.array((r, g, bb)) * shade
                    t *= (1 - al)
                    if t < 0.05:
                        break
                img[ny - 1 - y, u] = acc + t * img[ny - 1 - y, u]
        im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
        return im.resize((W * scale, ny * scale), Image.NEAREST)

    def iso(self, view="ne", scale=6):
        """Isometric render seen from a corner: 'ne', 'nw', 'se' or 'sw'."""
        a = self.a
        k = {"se": 0, "ne": 1, "nw": 2, "sw": 3}[view]
        a = np.rot90(a, k, axes=(0, 2))
        nx, ny, nz = a.shape
        s = scale
        W = int((nx + nz) * s * 0.87) + 60
        H = int((nx + nz) * s * 0.5 + ny * s) + 60
        im = Image.new("RGB", (W, H), (150, 190, 230))
        d = ImageDraw.Draw(im)
        ox = 20 + nz * s * 0.87
        oy = 20 + ny * s + s
        h = 0.87 * s; q = 0.5 * s
        cells = [(x, y, z) for x in range(nx) for z in range(nz) for y in range(ny) if a[x, y, z] is not None]
        cells.sort(key=lambda c: (c[0] + c[2], c[1]))
        for x, y, z in cells:
            r, g, bb, al = colour(a[x, y, z])
            X = ox + (x - z) * h
            Y = oy + (x + z) * q - y * s
            top = [(X, Y - s), (X + h, Y - s + q), (X, Y - s + 2 * q), (X - h, Y - s + q)]
            # visible faces in this frame: top, south (+z, left) and east (+x, right)
            left = [(X - h, Y - s + q), (X, Y - s + 2 * q), (X, Y + 2 * q), (X - h, Y + q)]
            right = [(X, Y - s + 2 * q), (X + h, Y - s + q), (X + h, Y + q), (X, Y + 2 * q)]
            d.polygon(left, fill=(int(r * .82), int(g * .82), int(bb * .82)))
            d.polygon(right, fill=(int(r * .64), int(g * .64), int(bb * .64)))
            d.polygon(top, fill=(r, g, bb))
        return im


def disk(cx, cy, r):
    """Integer cells (dx, dy) inside a circle of radius r around a cell centre."""
    out = []
    R = int(np.ceil(r))
    for dx in range(-R, R + 1):
        for dy in range(-R, R + 1):
            if dx * dx + dy * dy <= r * r + 0.3:
                out.append((cx + dx, cy + dy))
    return out
