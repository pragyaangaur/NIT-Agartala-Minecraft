"""Generic restyling batches for place.py: genbatch_<n> modules are generated on the fly.

python3 genbatch.py run [x0 z0 x1 z1]   places every job (optionally only inside a box),
in spatial tiles so each server forceload stays small.
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generic, place
from mcserver import run, write_functions, forceload_cmds


def main(box=None, only=None):
    jobs = generic.todo()
    if box:
        jobs = [j for j in jobs if box[0] <= j[5] <= box[2] and box[1] <= j[6] <= box[3]]
    tiles = {}
    for j in jobs:
        tiles.setdefault((int(j[5]) // 256, int(j[6]) // 256), []).append(j)
    commands = []
    total = 0
    for (tx, tz), js in sorted(tiles.items()):
        cmds = []
        for (src, i, poly, kind, village, cx, cz, style) in js:
            if only and not (kind == 'large' or style):
                continue
            cmds += generic.Gen(poly, generic.seed_of(src, i), kind, village, style).commands(place.gy)
        ids = write_functions(place.WORLD, f"gen_{tx}_{tz}", cmds)
        import numpy as np
        allp = np.concatenate([np.array(j[2]) for j in js])
        bx0, bz0 = allp.min(0).astype(int) - 6
        bx1, bz1 = allp.max(0).astype(int) + 6
        commands += forceload_cmds(max(bx0, 32), max(bz0, 64), min(bx1, 1887), min(bz1, 2047))
        commands += ["function " + f for f in ids]
        commands.append("forceload remove all")
        total += len(cmds)
        print(f"tile {tx},{tz}: {len(js)} buildings, {len(cmds)} commands", flush=True)
    log = run(place.WORLD, commands, wait_load=6)
    errs = [l for l in log.splitlines() if "rror" in l or "Unknown" in l]
    print(len(jobs), "buildings,", total, "commands; errors:", errs[:5])


if __name__ == "__main__":
    if sys.argv[1] == "skipped":
        main(None, only=True)
    else:
        box = list(map(int, sys.argv[2:6])) if len(sys.argv) > 5 else None
        main(box)
