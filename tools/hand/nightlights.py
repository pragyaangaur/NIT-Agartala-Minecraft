"""Night lighting inside the hand-built buildings.

Scans each hand-built area in the working world and puts an invisible light block in every
fifth column where an air cell sits just under a ceiling with a floor three below (a room),
so rooms, porches and corridors glow through the windows at night.
"""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import generic, place
from readworld import read_box
from mcserver import write_functions, forceload_cmds

SOLID_SKIP = ("leaves", "light", "lantern", "glass", "bars", "fence", "wall", "carpet", "slab", "torch")


def solid(b):
    return b is not None and not any(s in b for s in SOLID_SKIP)


def commands_for(box):
    x0, z0, x1, z1 = box
    v = read_box(place.WORLD, x0, 60, z0, x1, 127, z1)
    a = v.a
    cmds = []
    nx, ny, nz = a.shape
    for i in range(0, nx):
        if (x0 + i) % 5:
            continue
        for k in range(0, nz):
            if (z0 + k) % 5:
                continue
            col = a[i, :, k]
            for y in range(3, ny - 1):
                if col[y] is None and col[y - 1] is None and col[y - 2] is None and solid(col[y + 1]) and solid(col[y - 3]):
                    cmds.append(f"setblock {x0 + i} {60 + y} {z0 + k} light[level=13]")
    return cmds


def all_commands():
    out = []
    for b in generic.hand_boxes():
        c = commands_for(b)
        out.append((b, c))
    return out
