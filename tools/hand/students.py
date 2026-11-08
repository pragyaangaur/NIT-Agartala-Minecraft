"""Seated students in the campus classrooms and offices, and the world spawn in Knowledge Park.

A seat is a chair (a wooden stair facing south) with a desk (a top slab) just north of it, as
furnish_all.py lays them out. About one campus seat in fourteen gets a student: an armour stand
in a dyed uniform with bent legs, lowered so its hips rest on the chair seat and its legs go under the desk. The
stands carry the tag nita_student, so a rerun removes the old ones first.
"""
import sys, os, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fastworld as fw, place, env
from mcserver import run, write_functions, forceload_cmds
from lightlife import SHIRTS, PANTS

Y0, Y1 = 56, 140
SPAWN = (580, 73, 1228)
SHARE = 0.07
DONE = [(834, 1155, 909, 1236)]          # the Library has readers from lightlife.py already


def seated(x, y, z, rng):
    book = 'mainhand:{id:"minecraft:book",count:1},' if rng.random() < 0.5 else ""
    return (f'summon armor_stand {x + 0.5} {y - 0.25} {z + 0.5} {{ShowArms:1b,NoBasePlate:1b,Invulnerable:1b,NoGravity:1b,'
            f'Tags:["nita_student"],Rotation:[180f,0f],equipment:{{{book}head:{{id:"minecraft:player_head",count:1}},'
            f'chest:{{id:"minecraft:leather_chestplate",count:1,components:{{"minecraft:dyed_color":{rng.choice(SHIRTS)}}}}},'
            f'legs:{{id:"minecraft:leather_leggings",count:1,components:{{"minecraft:dyed_color":{rng.choice(PANTS)}}}}},'
            f'feet:{{id:"minecraft:leather_boots",count:1,components:{{"minecraft:dyed_color":1908001}}}}}},'
            f'Pose:{{RightLeg:[-90f,0f,0f],LeftLeg:[-90f,0f,0f],RightArm:[-60f,0f,0f],LeftArm:[-55f,0f,0f],Head:[15f,0f,0f]}}}}')


def tile(tx, tz, rng):
    x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
    x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
    if x0 > x1 or z0 > z1:
        return []
    ids, names, lut = fw.load(place.WORLD, x0, Y0, z0, x1, Y1, z1)
    chair = np.array([n.split("[")[0].endswith("_stairs") and "facing=south" in n and "half=bottom" in n
                      and any(w in n for w in ("oak", "spruce", "birch", "jungle", "acacia")) for n in names])[ids]
    desk = np.array([n.split("[")[0].endswith("_slab") and "type=top" in n for n in names])[ids]
    seat = chair.copy(); seat[:, :, 1:] &= desk[:, :, :-1]; seat[:, :, 0] = False
    out = []
    for i, y, k in np.argwhere(seat):
        X, Z = x0 + i, z0 + k
        if not env.CAMPUS[X - 32, Z - 64] or any(a <= X <= c and b <= Z <= d for a, b, c, d in DONE):
            continue
        if rng.random() < SHARE:
            out.append(seated(X, Y0 + y, Z, rng))
    return out


def main():
    rng = random.Random(2711)
    cmds, total = [f"setworldspawn {SPAWN[0]} {SPAWN[1]} {SPAWN[2]}"], 0
    sessions = []
    for tx in range(8):
        for tz in range(9):
            c = tile(tx, tz, rng)
            if not c:
                continue
            x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
            x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
            kill = f"kill @e[type=minecraft:armor_stand,tag=nita_student,x={x0},y=-64,z={z0},dx={x1 - x0},dy=400,dz={z1 - z0}]"
            ids = write_functions(place.WORLD, f"st_{tx}_{tz}", [kill] + c)
            # one session per tile, with a wait, so the kill sees the old stands (see entclean.py)
            sessions.append(forceload_cmds(x0, z0, x1, z1) + [("sleep", 25)] + ["function " + f for f in ids] + ["forceload remove all"])
            total += len(c)
            print(f"tile {tx},{tz}: {len(c)} students", flush=True)
    print("total", total, flush=True)
    sessions[0] = cmds + sessions[0]
    for s in sessions:
        log = run(place.WORLD, s, wait_load=5, step_wait=1)
        bad = [l for l in log.splitlines() if "xception" in l or "<--" in l]
        if bad:
            print(bad[:3], flush=True)


if __name__ == "__main__":
    main()
