"""Academic Block 2, across the fountain plaza from Academic Block 1.

Frames: W7D6gLvjizM 0:16, 0:20 (drone, centre of view), 1:12 and 1:16 (east facade straight on).
Main facade faces east onto the plaza: red stair towers at both corners, a tall white tower
left of centre, red bands with small round windows, a round emblem over the entrance and a
glazed ground floor at the north end. OSM way 1544302857. Built axis-aligned.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox, disk
from style import *

NAME = "ab2"
W, L = 31, 52
F = 0
E = 4                                   # space east of the building for the entrance steps
OX, OY, OZ = 513, 75, 1213
NY = 26
CLEAR = (503, 1203, 543, 1275)


def build():
    v = Vox(W + E, NY, L)
    x0, x1, z0, z1 = 0, W - 1, 0, L - 1
    shell(v, x0, x1, z0, z1)
    east = Face(v, "east", x0, x1, z0, z1)
    north = Face(v, "north", x0, x1, z0, z1)
    south = Face(v, "south", x0, x1, z0, z1)
    west = Face(v, "west", x0, x1, z0, z1)

    # ---------------- east facade (u = z, 0 at the north end)
    bay_wall(east, 4, 16, red_spandrel=False, red_ground=False)
    east.rect(4, 16, 13, 16, RED)
    for u in (7, 10, 13):                       # small round windows in the red band
        east.rect(u, u + 1, 14, 15, GLASS)
    east.rect(5, 15, 1, 4, LGLASS)              # glazed ground floor
    for u in (5, 8, 11, 14):
        east.rect(u, u, 1, 4, WHITE)
    east.rect(4, 16, 5, 5, WHITE)
    # centre: red bands with round windows either side of a tall white tower
    east.rect(17, 33, 1, 8, WHITE)
    east.rect(17, 33, 9, 16, RED)
    for u in (18, 21, 30, 33):
        east.rect(u, u + 1, 12, 13, GLASS)
    for u in range(23, 28):
        for y in range(1, 24):
            east.set(u, y, WHITE, out=1)
            for d in range(0, 4):
                if y >= 17 or d == 0:
                    east.set(u, y, WHITE, out=-d)
    for y in (10, 11, 14, 15, 19, 20):
        east.set(25, y, GLASS, out=1)
    east.rect(23, 27, 24, 24, "smooth_quartz_slab", out=1)
    east.rect(23, 27, 24, 24, "smooth_quartz_slab")
    east.ring_window(25, 6, r_out=2.4, r_in=1.6, ring="gray_concrete", glass="white_concrete", out=1)
    east.rect(19, 21, 1, 3, LGLASS)            # entrances either side of the tower
    east.rect(29, 31, 1, 3, LGLASS)
    for u in range(18, 33):                     # steps down to the terrace
        if not 23 <= u <= 27:
            east.set(u, 1, "smooth_quartz_stairs[facing=west]", out=1)
    # south section: red bays
    bay_wall(east, 34, 47)
    # corner towers
    red_tower(east, 0, 3)
    red_tower(east, 48, 51)

    # ---------------- other faces
    bay_wall(north, 4, W - 5); red_tower(north, 0, 3); red_tower(north, W - 4, W - 1)
    bay_wall(south, 4, W - 5); red_tower(south, 0, 3); red_tower(south, W - 4, W - 1)
    bay_wall(west, 4, L - 5)
    roof_boxes(v, [(3, 20, 7, 24), (W - 9, 40, W - 5, 44)])
    for (x, z) in ((10, 8), (20, 8), (10, 30), (22, 30), (15, 44)):
        v.set(x, 18, z, "white_concrete")
    return v


def export():
    v = build()
    return v, v.commands(OX, OY, OZ)


def extra(gy):
    """Level a three-block apron round the building to its ground level."""
    cmds = []
    for x in range(OX - 4, OX + W + 1):
        for z in range(OZ - 4, OZ + L + 4):
            if OX <= x < OX + W and OZ <= z < OZ + L:
                continue
            if x >= OX + W:               # east side belongs to the plaza terrace
                continue
            g = gy(x, z)
            if g > OY:
                cmds.append(f"fill {x} {OY + 1} {z} {x} {g} {z} air")
                cmds.append(f"setblock {x} {OY} {z} {PAVE if x >= OX - 2 and z < OZ + L + 2 else 'grass_block'}")
    return cmds


CHECKS = ["execute if block 544 81 1238 white_concrete run say CHECK ab2 emblem"]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("east", 10).save(os.path.join(out, "ab2_east.png"))
    v.iso("se", 7).save(os.path.join(out, "ab2_iso_se.png"))
    print(len(cmds), "commands")
