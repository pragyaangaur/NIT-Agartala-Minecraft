"""Remove leftovers of the old generated buildings that sat above the clearing height.

Finds, inside every hand-built module's clearing box, iron bars with air under them
(old rooftop rails), and reports any block above y 100 that is not part of a known tall build.
"""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import generic, place
from readworld import read_box
from mcserver import run, write_functions, forceload_cmds


def scan():
    cmds, loads = [], []
    for b in generic.hand_boxes():
        x0, z0, x1, z1 = b
        v = read_box(place.WORLD, x0, 60, z0, x1, 127, z1)
        a = v.a
        hits = 0
        for x, y, z in np.argwhere(a != None):
            blk = a[x, y, z]
            if blk.startswith("iron_bars") and y > 0 and a[x, y - 1, z] is None:
                cmds.append(f"setblock {x0 + x} {60 + y} {z0 + z} air"); hits += 1
        if hits:
            loads.append(b)
            print(b, hits, "floating iron bars")
    return cmds, loads


if __name__ == "__main__":
    cmds, loads = scan()
    if cmds:
        ids = write_functions(place.WORLD, "cleanup", cmds)
        c = []
        for (x0, z0, x1, z1) in loads:
            c += forceload_cmds(x0, z0, x1, z1) + ["function " + i for i in ids] + ["forceload remove all"]
        run(place.WORLD, c, wait_load=5)
    print(len(cmds), "removed")
