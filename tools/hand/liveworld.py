"""Run the whole 'bring it to life' pass in one server session.

python3 liveworld.py [buildings]
  buildings: also rerun every generic building (adds interior night lights to all of them)
Order per 256 m tile: generic buildings (optional), roads/footpaths/lamps/water, palms,
tree species and glass; then grounds; then night lights in hand-built buildings.
"""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import env, generic, place, grounds, nightlights
from mcserver import run, write_functions, forceload_cmds


def main(with_buildings):
    lamps, poles = env.lamp_sites(), env.pole_sites()
    jobs = generic.todo() if with_buildings else []
    by_tile = {}
    for j in jobs:
        by_tile.setdefault((int(j[5]) // 256, int(j[6]) // 256), []).append(j)
    commands = []
    for tx in range(8):
        for tz in range(9):
            c = []
            for (src, i, poly, kind, village, cx, cz, style) in by_tile.get((tx, tz), []):
                c += generic.Gen(poly, generic.seed_of(src, i), kind, village, style).commands(place.gy)
            c += env.tile_commands(tx, tz, lamps, poles)
            c += env.palms_for_tile(tx, tz, lamps)
            c += env.tree_and_glass(tx, tz)
            if not c:
                continue
            ids = write_functions(place.WORLD, f"live_{tx}_{tz}", c)
            x0, z0 = max(tx * 256 - 40, 32), max(tz * 256 - 40, 64)
            x1, z1 = min(tx * 256 + 295, 1887), min(tz * 256 + 295, 2047)
            commands += forceload_cmds(x0, z0, x1, z1) + ["function " + f for f in ids] + ["forceload remove all"]
            print(f"tile {tx},{tz}: {len(c)} commands", flush=True)
    gc = grounds.commands(place.gy)
    ids = write_functions(place.WORLD, "grounds", gc)
    commands += forceload_cmds(925, 220, 1065, 340) + forceload_cmds(925, 800, 1065, 935)
    commands += ["function " + f for f in ids] + ["forceload remove all"]
    # run in sessions of about ten tiles so the server never builds up memory
    chunks, cur = [], []
    for c in commands:
        cur.append(c)
        if c == "forceload remove all" and sum(1 for x in cur if x == "forceload remove all") >= 10:
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    for n, part in enumerate(chunks):
        log = run(place.WORLD, part, wait_load=6)
        bad = [l for l in log.splitlines() if "rror" in l or "Unknown" in l or "Exception" in l]
        print(f"session {n + 1}/{len(chunks)} errors:", bad[:5], flush=True)
        if any("OutOfMemory" in l for l in bad):
            raise SystemExit("out of memory, stopping")
    # night lights need the finished buildings, so read the world after the first session
    nl = []
    for b, c in nightlights.all_commands():
        if c:
            ids = write_functions(place.WORLD, f"nl_{len(nl)}", c)
            nl += forceload_cmds(*b) + ["function " + f for f in ids] + ["forceload remove all"]
    print("night light functions:", len(nl))
    log = run(place.WORLD, nl, wait_load=4)
    print("errors:", [l for l in log.splitlines() if "rror" in l or "Unknown" in l][:5])


if __name__ == "__main__":
    main("buildings" in sys.argv)
