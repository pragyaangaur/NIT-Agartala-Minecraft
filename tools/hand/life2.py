"""Second life pass (7 Nov night), after a walk-through by the owner.

1. Duplicate footprints: Microsoft outlines that doubled an OSM one are cleared, and the kept
   building is rebuilt alone (fixes patchwork roofs such as the one west of RNT).
2. Ground: coarse dirt and podzol become grass; every open patch gets grass, ferns, tall grass,
   flowers, bushes and firefly bushes, with bamboo clumps in the village.
3. Roads: kerbs, asphalt and paver footpaths also inside hand-built areas and on campus tracks,
   but only where the old road surface is still there (conditional commands).
4. Street life: benches facing the road, bins beside lamps, cars parked on the footpaths.
5. Mobs: removed tile by tile (the spawn_mobs game rule is already off).
"""
import sys, os, json, math, random
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import env, generic, place
from extrude import mask_of, osm_poly, ms_poly
from mcserver import run, write_functions, forceload_cmds

X0, Z0, NX, NZ = env.X0, env.Z0, env.NX, env.NZ
ROOT = env.ROOT

TRACK = env.ROAD & (env.KIND == 2) & env.CAMPUS
ROAD2 = env.CAMPUS_ROAD | TRACK
inside2 = distance_transform_edt(env.ROAD)
KERB2 = ROAD2 & (inside2 <= 1.0)
near2 = distance_transform_edt(~ROAD2)
PATH2 = (~env.ROAD) & (near2 <= 2.2) & ~env.FOOT & ~binary_dilation(env.FOOT) & ~env.WATER & env.CAMPUS
FOOTWAY = env.ROAD & (env.KIND == 1) & env.CAMPUS
OLD_ROAD = ("light_gray_concrete", "gravel", "coarse_dirt", "dirt_path", "polished_andesite")

GREEN = [("grass_jungle", 30), ("grass", 25), ("tall_grass", 10), ("large_fern", 5), ("flower_default", 7),
         ("wildflower", 5), ("flower_plain", 4), ("bush", 6), ("firefly_bush", 3), ("jungle_bush", 3)]


def pick(rng, table):
    t = rng.random() * sum(w for _, w in table)
    for n, w in table:
        t -= w
        if t <= 0:
            return n
    return table[-1][0]


def dup_fixes():
    drop = json.load(open(os.path.join(ROOT, "work", "dup_drop.json")))
    pairs = json.load(open(os.path.join(ROOT, "work", "dup_pairs.json")))
    dropped = {tuple(d) for d in drop}
    keep = set()
    for a, b, c, d in pairs:
        for k in ((a, b), (c, d)):
            if k not in dropped:
                keep.add(k)
    by_tile = {}
    for (src, i) in dropped:
        poly = osm_poly(i) if src == "osm" else ms_poly(i)
        P = np.array(poly)
        x0, z0 = int(P[:, 0].min()) - 2, int(P[:, 1].min()) - 2
        m = binary_dilation(mask_of(poly, x0, z0, int(P[:, 0].max()) - x0 + 4, int(P[:, 1].max()) - z0 + 4), iterations=1)
        c = []
        for a, b in np.argwhere(m):
            X, Z = x0 + a, z0 + b
            t = place.gy(X, Z)
            c.append(f"fill {X} {t + 1} {Z} {X} {t + 34} {Z} air")
            c.append(f"setblock {X} {t} {Z} grass_block")
        cx, cz = P.mean(0)
        by_tile.setdefault((int(cx) // 256, int(cz) // 256), []).extend(c)
    jobs = {(j[0], j[1]): j for j in generic.todo()}
    rebuild = {}
    for k in keep:
        j = jobs.get(k)
        if j:
            c = generic.Gen(j[2], generic.seed_of(j[0], j[1]), j[3], j[4], j[7]).commands(place.gy)
            rebuild.setdefault((int(j[5]) // 256, int(j[6]) // 256), []).extend(c)
    return by_tile, rebuild


def tile(tx, tz, lamps):
    i0, k0 = max(tx * 256 - X0, 0), max(tz * 256 - Z0, 0)
    i1, k1 = min(tx * 256 - X0 + 256, NX), min(tz * 256 - Z0 + 256, NZ)
    if i0 >= i1 or k0 >= k1:
        return []
    rng = random.Random(9000 + tx * 37 + tz)
    c = []
    # ground: coarse dirt and podzol become grass, 32 m blocks
    for bx in range(tx * 256, tx * 256 + 256, 32):
        for bz in range(tz * 256, tz * 256 + 256, 32):
            if bx + 31 < X0 or bz + 31 < Z0 or bx >= X0 + NX or bz >= Z0 + NZ:
                continue
            for (ya, yb) in ((56, 80), (81, 100)):
                c.append(f"fill {bx} {ya} {bz} {bx + 31} {yb} {bz + 31} grass_block replace coarse_dirt")
                c.append(f"fill {bx} {ya} {bz} {bx + 31} {yb} {bz + 31} grass_block replace podzol")
    # roads everywhere on campus, conditional on the old surface
    for i in range(i0, i1):
        for k in range(k0, k1):
            X, Z, y = i + X0, k + Z0, int(env.GY[i, k])
            b = None
            if ROAD2[i, k] and (env.HAND[i, k] or TRACK[i, k]):
                if KERB2[i, k]:
                    b = "yellow_concrete" if ((X + Z) // 2) % 2 else "black_concrete"
                elif env.CENTRE[i, k] and (X + Z) % 6 < 3:
                    b = "white_concrete"
                else:
                    b = "gray_concrete"
                for old in OLD_ROAD:
                    c.append(f"execute if block {X} {y} {Z} {old} run setblock {X} {y} {Z} {b}")
            elif FOOTWAY[i, k] and env.HAND[i, k]:
                b = rng.choice(env.PAVERS)
                for old in OLD_ROAD:
                    c.append(f"execute if block {X} {y} {Z} {old} run setblock {X} {y} {Z} {b}")
            elif PATH2[i, k] and not env.PATH[i, k]:
                c.append(f"execute if block {X} {y} {Z} grass_block run setblock {X} {y} {Z} {rng.choice(env.PAVERS)}")
    # vegetation on every open patch
    for i in range(i0 + rng.randint(0, 3), i1, 4):
        for k in range(k0 + rng.randint(0, 3), k1, 4):
            ii, kk = min(i + rng.randint(-1, 1), NX - 1), min(k + rng.randint(-1, 1), NZ - 1)
            if env.ROAD[ii, kk] or env.WATER[ii, kk] or env.BM[ii, kk] or PATH2[ii, kk]:
                continue
            X, Z, y = ii + X0, kk + Z0, int(env.GY[ii, kk])
            f = pick(rng, GREEN)
            if not env.CAMPUS[ii, kk] and rng.random() < 0.05:
                f = "bamboo_vegetation"
            c.append(f"execute if block {X} {y} {Z} grass_block run place feature minecraft:{f} {X} {y + 1} {Z}")
    # benches, bins and parked cars on campus footpaths
    lamp_set = {(a, b) for a, b in lamps}
    for (a, b) in lamps:
        if not (i0 <= a < i1 and k0 <= b < k1):
            continue
        di, dk = env.toward_road(a, b)
        X, Z, y = a + X0, b + Z0, int(env.GY[a, b])
        bx, bz = X + dk, Z + di                                   # bin beside the lamp, along the road
        c.append(f"execute if block {bx} {y + 1} {bz} air run setblock {bx} {y + 1} {bz} cauldron")
        face = {(1, 0): "west", (-1, 0): "east", (0, 1): "north", (0, -1): "south"}[(di, dk)]
        for s in (5, 6):                                          # bench a few metres on, facing the road
            sx, sz = X + s * dk, Z + s * di
            c.append(f"execute if block {sx} {y + 1} {sz} air run setblock {sx} {y + 1} {sz} spruce_stairs[facing={face}]")
    cars = 0
    colours = ["white_concrete", "red_concrete", "light_gray_concrete", "black_concrete", "blue_concrete", "white_concrete",
               "light_gray_concrete", "yellow_concrete"]
    cand = [tuple(p) for p in np.argwhere(env.PATH[i0:i1, k0:k1] & (env.near_road[i0:i1, k0:k1] <= 1.2))]
    rng.shuffle(cand)
    used = set()
    for (a, b) in cand[:400]:
        a, b = a + i0, b + k0
        if cars >= 6:
            break
        di, dk = env.toward_road(a, b)
        along = (dk, di)
        cells = [(a + s * along[0] + w * di * -1, b + s * along[1] + w * dk * -1) for s in range(4) for w in (0, 1)]
        if not all(0 <= p < NX and 0 <= q < NZ and env.PATH[p, q] and (p, q) not in used for p, q in cells):
            continue
        if any(abs(p - la) + abs(q - lb) < 4 for p, q in cells for (la, lb) in lamp_set if abs(p - la) < 8 and abs(q - lb) < 8):
            continue
        col = rng.choice(colours)
        y = int(env.GY[a, b])
        for n, (p, q) in enumerate(cells):
            s = n // 2
            X, Z = p + X0, q + Z0
            c.append(f"setblock {X} {y + 1} {Z} {col}")
            c.append(f"setblock {X} {y + 2} {Z} {'black_stained_glass' if s in (1, 2) else col if s == 0 else 'air'}")
            used.add((p, q))
        cars += 1
    return c


def main():
    lamps = env.lamp_sites()
    clears, rebuild = dup_fixes()
    sessions, cur = [], []
    for tx in range(8):
        for tz in range(9):
            c = clears.get((tx, tz), []) + rebuild.get((tx, tz), []) + tile(tx, tz, lamps)
            if not c:
                continue
            c.append(f"kill @e[type=!minecraft:player,type=!minecraft:text_display,x={tx * 256 - 40},y=0,z={tz * 256 - 40},dx=336,dy=200,dz=336]")
            ids = write_functions(place.WORLD, f"life2_{tx}_{tz}", c)
            x0, z0 = max(tx * 256 - 40, 32), max(tz * 256 - 40, 64)
            x1, z1 = min(tx * 256 + 295, 1887), min(tz * 256 + 295, 2047)
            cur += forceload_cmds(x0, z0, x1, z1) + ["function " + f for f in ids] + ["forceload remove all"]
            print(f"tile {tx},{tz}: {len(c)} commands", flush=True)
            if sum(1 for x in cur if x == "forceload remove all") >= 8:
                sessions.append(cur); cur = []
    if cur:
        sessions.append(cur)
    for n, part in enumerate(sessions):
        log = run(place.WORLD, part, wait_load=6)
        bad = [l for l in log.splitlines() if "Exception" in l or "OutOfMemory" in l or "Unknown or incomplete" in l
               or "Can't find" in l or "Incorrect argument" in l]
        print(f"session {n + 1}/{len(sessions)} problems:", bad[:4], flush=True)
        if any("OutOfMemory" in l for l in bad):
            raise SystemExit("out of memory")


if __name__ == "__main__":
    main()
