"""Lighting and life pass (8 Nov).

Lighting
  inside   every enclosed room cell on a 3 m grid gets an invisible level-15 light under the
           ceiling, in every building on the map (found by scanning the world, so it covers
           hand-built, footprint-built and restyled buildings alike)
  campus   invisible lights over footpaths every 6 m and roads every 8 m, a softer grid over
           open campus ground every 12 m, and along village roads every 10 m
Life
  students: dressed armour stands (not mobs) in Knowledge Park, the round garden, the
  Library, both messes, the RNT Ground, the sports complex, the market, the main gate and
  outside the auditoriums
Clean-up
  every entity except players, signs (text displays), paintings and the armour stands is removed
"""
import sys, os, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fastworld as fw, place, env
from mcserver import run, write_functions, forceload_cmds

X0, Z0 = 32, 64
Y0, Y1 = 56, 140
SKIPSOLID = ("leaves", "light", "glass", "pane", "bars", "fence", "wall", "carpet", "torch", "lantern", "ladder",
             "grass", "fern", "flower", "bush", "sapling", "cane", "lily", "vine", "water", "slab", "stairs", "bed")

SPOTS = {   # name: (x0, z0, x1, z1, count, pose)   -- areas where people stand about
    "knowledge park": (548, 1205, 598, 1250, 14, "walk"),
    "round garden": (840, 1276, 884, 1320, 6, "walk"),
    "library reading hall": (862, 1179, 881, 1205, 8, "read"),
    "rnt dining hall": (895, 712, 960, 750, 12, "eat"),
    "aryabhatta mess": (540, 840, 590, 905, 6, "eat"),
    "rnt ground": (960, 830, 1030, 905, 12, "play"),
    "sports courtyard": (1100, 340, 1170, 372, 6, "walk"),
    "market": (1530, 278, 1580, 326, 8, "walk"),
    "main gate": (640, 1600, 675, 1628, 4, "walk"),
    "visvesvaraya forecourt": (614, 1106, 648, 1124, 5, "walk"),
    "vivekananda foyer": (545, 1172, 576, 1184, 4, "walk"),
    "civil forecourt": (636, 1050, 668, 1066, 4, "walk"),
}
SHIRTS = [0xFFFFFF, 0x3C4CAA, 0xB02E26, 0x1E1B1B, 0x5E7C16, 0xF9801D, 0x3AB3DA, 0xC74EBD, 0x9D9D97, 0xFED83D, 0x8932B8]
PANTS = [0x1D1D21, 0x3C44AA, 0x474F52, 0x835432, 0x1D1D21]


def person(x, y, z, rng, pose):
    rot = rng.randint(0, 359)
    hand = {"read": 'mainhand:{id:"minecraft:book",count:1},', "eat": 'mainhand:{id:"minecraft:bread",count:1},',
            "play": 'mainhand:{id:"minecraft:stick",count:1},'}.get(pose, rng.choice(["", "", 'mainhand:{id:"minecraft:book",count:1},']))
    arm = {"read": "RightArm:[-50f,0f,0f],LeftArm:[-50f,0f,0f],Head:[20f,0f,0f]",
           "eat": "RightArm:[-70f,0f,0f],Head:[10f,0f,0f]",
           "play": "RightArm:[-110f,0f,0f],LeftArm:[30f,0f,0f],RightLeg:[-20f,0f,0f],LeftLeg:[20f,0f,0f]",
           "walk": "RightArm:[20f,0f,0f],LeftArm:[-20f,0f,0f],RightLeg:[-15f,0f,0f],LeftLeg:[15f,0f,0f]"}[pose]
    return (f'summon armor_stand {x + 0.5} {y} {z + 0.5} {{ShowArms:1b,NoBasePlate:1b,Invulnerable:1b,'
            f'Tags:["nita_person"],Rotation:[{rot}f,0f],equipment:{{{hand}head:{{id:"minecraft:player_head",count:1}},'
            f'chest:{{id:"minecraft:leather_chestplate",count:1,components:{{"minecraft:dyed_color":{rng.choice(SHIRTS)}}}}},'
            f'legs:{{id:"minecraft:leather_leggings",count:1,components:{{"minecraft:dyed_color":{rng.choice(PANTS)}}}}},'
            f'feet:{{id:"minecraft:leather_boots",count:1,components:{{"minecraft:dyed_color":1908001}}}}}},Pose:{{{arm}}}}}')


def tile(tx, tz, rng):
    x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
    x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
    if x0 > x1 or z0 > z1:
        return []
    ids, names, lut = fw.load(place.WORLD, x0, Y0, z0, x1, Y1, z1)
    base = [n.split("[")[0] for n in names]
    air = np.array([b == "air" for b in base])[ids]
    solid = np.array([b != "air" and not any(s in b for s in SKIPSOLID) for b in base])[ids]
    out = []
    nx, ny, nz = ids.shape
    # inside: enclosed rooms
    for i in range(0, nx):
        if (x0 + i) % 3:
            continue
        for k in range(0, nz):
            if (z0 + k) % 3:
                continue
            a, s_ = air[i, :, k], solid[i, :, k]
            ok = a[3:-1] & a[2:-2] & a[1:-3] & s_[4:] & s_[:-4]
            for y in np.nonzero(ok)[0] + 3:
                out.append(f"setblock {x0 + i} {Y0 + y} {z0 + k} light[level=15]")
    # outside: footpaths, roads, open campus ground, village roads
    for i in range(nx):
        X = x0 + i
        for k in range(nz):
            Z = z0 + k
            gi, gk = X - X0, Z - Z0
            g = int(env.GY[gi, gk])
            lvl, h = None, 3
            if env.PATH[gi, gk] and X % 6 == 0 and Z % 6 == 0:
                lvl = 15
            elif env.CAMPUS_ROAD[gi, gk] and X % 8 == 0 and Z % 8 == 0:
                lvl, h = 15, 4
            elif env.ROAD[gi, gk] and not env.CAMPUS[gi, gk] and X % 10 == 0 and Z % 10 == 0:
                lvl, h = 13, 4
            elif env.CAMPUS[gi, gk] and X % 12 == 0 and Z % 12 == 0 and not env.ROAD[gi, gk]:
                lvl = 11
            if lvl:
                y = g + h - Y0
                if 0 <= y < ny and air[i, y, k]:
                    out.append(f"setblock {X} {g + h} {Z} light[level={lvl}]")
    # people
    for name, (a, b, c, d, n, pose) in SPOTS.items():
        if not (x0 <= a <= x1 and z0 <= b <= z1):
            continue
        placed, tries = 0, 0
        while placed < n and tries < n * 40:
            tries += 1
            X, Z = rng.randint(a, c), rng.randint(b, d)
            i, k = X - x0, Z - z0
            if not (0 <= i < nx and 0 <= k < nz):
                continue
            col = ids[i, :, k]
            for y in range(1, ny - 2):
                if solid[i, y - 1, k] and air[i, y, k] and air[i, y + 1, k]:
                    if pose in ("read", "eat") and not solid[i, min(y + 3, ny - 1), k] and not solid[i, min(y + 4, ny - 1), k]:
                        continue                         # indoor poses only under a roof
                    out.append(person(X, Y0 + y, Z, rng, pose)); placed += 1
                    break
    return out


def main():
    rng = random.Random(2026)
    sessions, cur = [], []
    for tx in range(8):
        for tz in range(9):
            c = tile(tx, tz, rng)
            if not c:
                continue
            x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
            x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
            kill = [f"kill @e[type=!minecraft:player,type=!minecraft:text_display,type=!minecraft:painting,"
                    f"type=!minecraft:armor_stand,x={x0},y=-64,z={z0},dx={x1 - x0},dy=400,dz={z1 - z0}]",
                    f"kill @e[type=minecraft:armor_stand,tag=nita_person,x={x0},y=-64,z={z0},dx={x1 - x0},dy=400,dz={z1 - z0}]"]
            ids = write_functions(place.WORLD, f"ll_{tx}_{tz}", kill + c)
            # wait for the tile's entities to load, or the kill inside the function sees nothing
            cur += forceload_cmds(x0, z0, x1, z1) + [("sleep", 25)] + ["function " + f for f in ids] + ["forceload remove all"]
            print(f"tile {tx},{tz}: {len(c)}", flush=True)
            if sum(1 for x in cur if x == "forceload remove all") >= 10:
                sessions.append(cur); cur = []
    if cur:
        sessions.append(cur)
    for n, part in enumerate(sessions):
        log = run(place.WORLD, part, wait_load=5)
        print(f"lightlife session {n + 1}/{len(sessions)}", [l for l in log.splitlines() if "Exception" in l or "<--" in l][:3], flush=True)


if __name__ == "__main__":
    main()
