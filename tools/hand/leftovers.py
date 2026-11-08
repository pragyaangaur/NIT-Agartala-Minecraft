"""Find leftover fragments of earlier builds: built blocks more than 3 above the ground that lie
outside every known footprint (hand-built boxes, restyled footprints, lamps, fields)."""
import sys, os, json
import numpy as np
from scipy.ndimage import binary_dilation, label
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fastworld as fw, generic, place, env
from extrude import mask_of

X0, Z0, NX, NZ = 32, 64, 1856, 1984
known = np.zeros((NX, NZ), bool)
for (a, b, c, d) in generic.hand_boxes():
    known[max(a - X0, 0):max(c - X0 + 1, 0), max(b - Z0, 0):max(d - Z0 + 1, 0)] = True
for j in generic.todo():
    P = np.array(j[2]); x0, z0 = int(P[:, 0].min()) - 1, int(P[:, 1].min()) - 1
    m = mask_of(j[2], x0, z0, int(P[:, 0].max()) - x0 + 3, int(P[:, 1].max()) - z0 + 3)
    i, k = np.nonzero(m)
    ok = (x0 + i - X0 >= 0) & (x0 + i - X0 < NX) & (z0 + k - Z0 >= 0) & (z0 + k - Z0 < NZ)
    known[x0 + i[ok] - X0, z0 + k[ok] - Z0] = True
known = binary_dilation(known, iterations=4)
SOFT = ("leaves", "_log", "light", "lantern", "andesite_wall", "iron_bars", "spruce_fence", "sugar_cane", "bamboo",
        "grass", "fern", "bush", "flower", "sapling", "slab", "sea_lantern", "jungle_wood", "mangrove_roots", "vine",
        "azalea", "propagule", "cauldron", "stairs", "concrete", "glass")
def soft(n):
    return n == "air" or any(s in n for s in SOFT)

found = np.zeros((NX, NZ), bool)
for tx in range(8):
    for tz in range(9):
        x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
        x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
        if x0 > x1 or z0 > z1: continue
        ids, names, lut = fw.load(place.WORLD, x0, 56, z0, x1, 140, z1)
        hard = ~np.array([soft(n.split("[")[0]) for n in names])
        H = hard[ids]
        g = env.GY[x0 - X0:x1 - X0 + 1, z0 - Z0:z1 - Z0 + 1]
        ys = np.arange(ids.shape[1])[None, :, None] + 56
        tall = (H & (ys > (g[:, None, :] + 3))).any(1)
        found[x0 - X0:x1 - X0 + 1, z0 - Z0:z1 - Z0 + 1] = tall
sus = found & ~known
lab, n = label(sus)
out = []
for c in range(1, n + 1):
    idx = np.argwhere(lab == c)
    if len(idx) < 4: continue
    (a, b), (cc, d) = idx.min(0), idx.max(0)
    out.append([int(a + X0), int(b + Z0), int(cc + X0), int(d + Z0), int(len(idx))])
out.sort(key=lambda r: -r[4])
json.dump(out, open(os.path.join(place.ROOT, "work", "leftovers.json"), "w"))
print(len(out), out[:25])
