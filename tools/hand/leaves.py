"""Stop leaves decaying and clear dropped saplings, apples and sticks.

The generated forest's leaves were not marked persistent, and many sit more than six blocks
from a log, so they decayed on their own and dropped saplings. Every non-persistent leaf block
becomes persistent, tile by tile, and item entities on the ground are removed.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import place
from mcserver import run, forceload_cmds, write_functions

TYPES = ["jungle_leaves", "dark_oak_leaves", "oak_leaves", "mangrove_leaves", "birch_leaves", "acacia_leaves",
         "spruce_leaves", "azalea_leaves", "flowering_azalea_leaves", "cherry_leaves"]


def main():
    sessions, cur = [], []
    for tx in range(8):
        for tz in range(9):
            c = []
            for bx in range(tx * 256, tx * 256 + 256, 32):
                for bz in range(tz * 256, tz * 256 + 256, 32):
                    if bx + 31 < 32 or bz + 31 < 64 or bx > 1887 or bz > 2047:
                        continue
                    for (ya, yb) in ((60, 91), (92, 115)):
                        for t in TYPES:
                            c.append(f"fill {bx} {ya} {bz} {bx + 31} {yb} {bz + 31} {t}[persistent=true] replace {t}[persistent=false]")
            if not c:
                continue
            c.append(f"kill @e[type=item,x={tx * 256 - 40},y=0,z={tz * 256 - 40},dx=336,dy=200,dz=336]")
            ids = write_functions(place.WORLD, f"leaves_{tx}_{tz}", c)
            x0, z0 = max(tx * 256 - 8, 32), max(tz * 256 - 8, 64)
            x1, z1 = min(tx * 256 + 263, 1887), min(tz * 256 + 263, 2047)
            cur += forceload_cmds(x0, z0, x1, z1) + ["function " + f for f in ids] + ["forceload remove all"]
            if sum(1 for x in cur if x == "forceload remove all") >= 12:
                sessions.append(cur); cur = []
    if cur:
        sessions.append(cur)
    for n, part in enumerate(sessions):
        log = run(place.WORLD, part, wait_load=5)
        bad = [l for l in log.splitlines() if "Exception" in l or "Incorrect" in l or "Unknown" in l]
        print(f"leaves session {n + 1}/{len(sessions)}:", bad[:3], flush=True)


if __name__ == "__main__":
    main()
