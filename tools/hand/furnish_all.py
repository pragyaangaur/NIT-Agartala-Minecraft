"""Interiors for every building on the map that does not have a hand-made one yet.

The world is scanned tile by tile. A room is a connected patch of floor cells at one height
that have two air cells above a solid floor and a solid ceiling a few blocks up, mostly closed
in by walls. Each room is furnished by what it is likely to be:

  home        houses in the villages and the staff quarters: bed, wardrobe chest, crafting
              table, furnace, bookshelf, rug, potted plants
  classroom   campus rooms of 40 to 400 cells: rows of desks and chairs facing a dark board
              and a teacher's desk with a lectern
  office      smaller campus rooms: desks with lamps and chairs, bookshelves, a chest, plants
  hall        anything larger: benches along the walls and plants

Furniture only ever goes into air cells, keeps the ring next to every doorway clear, and
leaves wall-side cells free where a ladder goes. Ground floors without any doorway get one
cut through the wall, and buildings with more than one floor get a ladder through every
floor. Buildings that already have hand-made interiors are skipped.
"""
import sys, os, random
import numpy as np
from scipy.ndimage import label, distance_transform_cdt, binary_dilation
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fastworld as fw, place, env
from mcserver import run, write_functions, forceload_cmds

Y0, Y1 = 56, 140
SKIP = ("leaves", "light", "glass", "pane", "bars", "fence", "wall", "carpet", "torch", "lantern", "ladder",
        "grass", "fern", "flower", "bush", "sapling", "cane", "lily", "vine", "water", "slab", "stairs", "bed",
        "door", "sign", "pot", "chest", "barrel", "table", "lectern", "rod", "chain", "button", "plate", "rail")
DONE_BOXES = [(834, 1155, 909, 1236), (532, 1130, 590, 1196), (600, 1058, 662, 1130), (770, 560, 1080, 800),
              (420, 735, 690, 925), (1160, 755, 1380, 890), (420, 1218, 492, 1290),
              (1030, 250, 1250, 385)]           # library, both halls, RNT, Aryabhatta, Gargi, Science, sports
QUARTERS = (1140, 420, 1320, 690)
# share of a room's outline that must be wall; houses with a veranda joined to the room sit at
# about 0.5, so they were done in a second pass with RATIO = (0.4, 0.6)
RATIO = (0.6, 9.0)
DIRS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
OPP = {"north": "south", "south": "north", "west": "east", "east": "west"}
WOODS = ["oak", "spruce", "birch", "dark_oak", "jungle", "acacia"]
BEDS = ["red", "blue", "light_blue", "green", "yellow", "orange", "white", "cyan", "lime", "pink"]
RUGS = ["red", "blue", "cyan", "orange", "yellow", "lime", "light_blue", "magenta"]
PLANTS = ["potted_fern", "potted_bamboo", "potted_red_tulip", "potted_cactus", "potted_azalea_bush", "potted_oak_sapling"]


def in_box(x, z, boxes):
    return any(a <= x <= c and b <= z <= d for a, b, c, d in boxes)


def rooms_of_tile(ids, names):
    base = [n.split("[")[0] for n in names]
    air = np.array([b == "air" or b == "light" for b in base])[ids]
    solid = np.array([b != "air" and not any(s in b for s in SKIP) for b in base])[ids]
    nx, ny, nz = ids.shape
    # ceiling within 2..6 cells above the standing cell
    ceil = np.zeros_like(air)
    for h in range(2, 7):
        ceil[:, :ny - h, :] |= solid[:, h:, :]
    floor = np.zeros_like(air); floor[:, 1:, :] = solid[:, :-1, :]
    stand = np.zeros_like(air); stand[:, :-1, :] = air[:, :-1, :] & air[:, 1:, :]
    indoor = stand & floor & ceil
    wallish = solid | np.array([any(t in b for t in ("glass", "pane", "bars", "fence", "wall", "door")) for b in base])[ids]
    return indoor, air, solid, wallish


def furnish_tile(tx, tz, rng, stats):
    x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
    x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
    if x0 > x1 or z0 > z1:
        return []
    core = (x0, z0, x1, z1)
    # load a margin so buildings crossing the tile edge are seen whole; each room is
    # handled by the tile that holds its centre
    x0, z0, x1, z1 = max(x0 - 64, 32), max(z0 - 64, 64), min(x1 + 64, 1887), min(z1 + 64, 2047)
    ids, names, lut = fw.load(place.WORLD, x0, Y0, z0, x1, Y1, z1)
    indoor, air, solid, wallish = rooms_of_tile(ids, names)
    nx, ny, nz = ids.shape
    out = []
    taken = set()
    rooms = []                                  # (y, cells mask) per room
    for y in range(1, ny - 3):
        lab, n = label(indoor[:, y, :])
        if n == 0:
            continue
        sizes = np.bincount(lab.ravel())
        for r in range(1, n + 1):
            if sizes[r] < 9 or sizes[r] > 6000:
                continue
            m = lab == r
            ii, kk = np.nonzero(m)
            if ii.min() == 0 or kk.min() == 0 or ii.max() == nx - 1 or kk.max() == nz - 1:
                continue                         # crosses the tile edge, leave it
            cx, cz = x0 + int(ii.mean()), z0 + int(kk.mean())
            if in_box(cx, cz, DONE_BOXES) or not (core[0] <= cx <= core[2] and core[1] <= cz <= core[3]):
                continue
            ring = binary_dilation(m) & ~m
            wall = wallish[:, y + 1, :] & ring
            ratio = wall.sum() / ring.sum()
            if not (RATIO[0] <= ratio < RATIO[1]):
                continue                         # porch, arch or tree canopy, not a room
            if ratio < 0.6 and distance_transform_cdt(np.pad(m, 1), metric="taxicab").max() < 2:
                continue                         # a thin strip is a veranda
            if ratio < 0.6 and env.CAMPUS[min(max(cx - 32, 0), env.CAMPUS.shape[0] - 1), min(max(cz - 64, 0), env.CAMPUS.shape[1] - 1)] \
                    and not in_box(cx, cz, [QUARTERS]):
                continue                         # on campus a half-open space is a porch or arcade

            rooms.append((y, m, cx, cz, int(sizes[r])))
    # stacks: rooms directly over each other share (x, z) cells
    by_cell = {}
    for idx, (y, m, cx, cz, a) in enumerate(rooms):
        by_cell.setdefault((cx // 6, cz // 6), []).append(idx)
    for idx, (y, m, cx, cz, area) in enumerate(rooms):
        X = lambda i: x0 + i
        Z = lambda k: z0 + k
        Yw = Y0 + y
        d = distance_transform_cdt(np.pad(m, 1), metric="taxicab")[1:-1, 1:-1]
        ring = binary_dilation(m) & ~m
        # doorways: room cells next to a non-room air column that has no ceiling (outside)
        doors = []
        for i, k in zip(*np.nonzero(m & (d == 1))):
            for dn, (di, dk) in DIRS.items():
                a, b = i + di, k + dk
                if air[a, y, b] and air[a, y + 1, b] and not indoor[a, y, b]:
                    doors.append((i, k))
        g = int(env.GY[min(max(x0 + int(np.nonzero(m)[0].mean()) - 32, 0), env.GY.shape[0] - 1),
                       min(max(z0 + int(np.nonzero(m)[1].mean()) - 64, 0), env.GY.shape[1] - 1)])
        ground_floor = abs((Yw - 1) - g) <= 3
        # a door through the wall if a ground-floor room has none
        if ground_floor and not doors and area >= 9:
            best = None
            for i, k in zip(*np.nonzero(m & (d == 1))):
                for dn, (di, dk) in DIRS.items():
                    a, b, a2, b2 = i + di, k + dk, i + 2 * di, k + 2 * dk
                    if not (0 <= a2 < nx and 0 <= b2 < nz):
                        continue
                    if solid[a, y, b] and solid[a, y + 1, b] and air[a2, y, b2] and air[a2, y + 1, b2] \
                            and not indoor[a2, y, b2] and solid[a2, y - 1, b2]:
                        score = (dn == "south") * 2 + (dn in ("east", "west"))
                        if best is None or score > best[0]:
                            best = (score, i, k, a, b)
            if best:
                _, i, k, a, b = best
                out += [f"setblock {X(a)} {Yw} {Z(b)} air", f"setblock {X(a)} {Yw + 1} {Z(b)} air"]
                doors.append((i, k)); stats["doors"] += 1
        keep = np.zeros_like(m)
        for i, k in doors:
            keep[max(i - 2, 0):i + 3, max(k - 2, 0):k + 3] = True
        # a ladder to the room above, if there is one straight over this room
        above = [j for j in by_cell.get((cx // 6, cz // 6), []) if rooms[j][0] > y and rooms[j][0] - y <= 7]
        if above:
            j = min(above, key=lambda j: rooms[j][0])
            yu, mu = rooms[j][0], rooms[j][1]
            placed = False
            for i, k in zip(*np.nonzero(m & mu & (d == 1) & ~keep)):
                for dn, (di, dk) in DIRS.items():
                    a, b = i + di, k + dk
                    # wall behind the ladder on every level; the slab between floors gets cut
                    if all(solid[a, yy, b] for yy in range(y, yu + 1)) and \
                            all(air[i, yy, k] or solid[i, yy, k] for yy in range(y, yu)) and air[i, yu, k]:
                        face = OPP[dn]
                        for yy in range(y, yu):
                            out.append(f"setblock {X(i)} {Y0 + yy} {Z(k)} ladder[facing={face}]")
                        taken.add((i, k)); keep[max(i - 1, 0):i + 2, max(k - 1, 0):k + 2] = True
                        placed = True; stats["ladders"] += 1
                        break
                if placed:
                    break
        # never furnish the cell under a ladder from the room below
        for (i, k) in list(taken):
            keep[i, k] = True
        free = m & ~keep
        village = not env.CAMPUS[min(max(cx - 32, 0), env.CAMPUS.shape[0] - 1), min(max(cz - 64, 0), env.CAMPUS.shape[1] - 1)]
        kind = "home" if (village or in_box(cx, cz, [QUARTERS])) else \
            "hall" if area > 3000 else "openplan" if area > 400 else "classroom" if area >= 40 else "office"
        stats[kind] += 1
        wood = rng.choice(WOODS)

        def put(i, k, yy, b):
            if 0 <= i < nx and 0 <= k < nz and air[i, yy, k] and (i, yy, k) not in placed_cells:
                out.append(f"setblock {X(i)} {Y0 + yy} {Z(k)} {b}")
                placed_cells.add((i, yy, k))
                return True
            return False
        placed_cells = set()
        wallside = [(i, k) for i, k in zip(*np.nonzero(free & (d == 1)))]
        rng.shuffle(wallside)

        def wall_dir(i, k):
            for dn, (di, dk) in DIRS.items():
                if solid[i + di, y, k + dk] and solid[i + di, y + 1, k + dk]:
                    return dn
            return None
        if kind == "home":
            beds = 0
            for i, k in wallside:
                if beds >= max(1, area // 30):
                    break
                dn = wall_dir(i, k)
                if not dn:
                    continue
                di, dk = DIRS[dn]
                fi, fk = i - di, k - dk                    # foot cell, away from the wall
                if 0 <= fi < nx and 0 <= fk < nz and free[fi, fk] and (fi, y, fk) not in placed_cells \
                        and (i, y, k) not in placed_cells:
                    col = rng.choice(BEDS)
                    # head against the wall: the bed faces towards the wall
                    put(fi, fk, y, f"{col}_bed[facing={dn},part=foot]")
                    put(i, k, y, f"{col}_bed[facing={dn},part=head]")
                    beds += 1
            extras = ["chest[facing={f}]", "crafting_table", "furnace[facing={f}]", "bookshelf", "barrel[facing=up]",
                      "{w}_planks", "smoker[facing={f}]"]
            n = 0
            for i, k in wallside:
                if n >= min(len(extras), 2 + area // 12):
                    break
                dn = wall_dir(i, k)
                if dn and (i, y, k) not in placed_cells:
                    b = extras[n].format(f=OPP[dn], w=wood)
                    if put(i, k, y, b):
                        if b.endswith("_planks"):
                            put(i, k, y + 1, rng.choice(PLANTS))
                        n += 1
            centre = [(i, k) for i, k in zip(*np.nonzero(free & (d >= 2)))]
            rug = rng.choice(RUGS)
            for i, k in centre[: max(4, area // 4)]:
                put(i, k, y, f"{rug}_carpet")
        elif kind == "openplan":
            # big undivided floors: blocks of desks split by aisles, shelves on the walls, plants at crossings
            for i, k in zip(*np.nonzero(free & (d >= 2))):
                Xa, Za = X(i), Z(k)
                if Xa % 12 < 2 or Za % 12 < 2:
                    if Xa % 12 == 0 and Za % 12 == 0:
                        put(i, k, y, rng.choice(PLANTS))
                    continue
                if Za % 3 == 0 and m[i, k + 1] and not keep[i, k + 1]:
                    put(i, k, y, f"{wood}_slab[type=top]")
                    put(i, k + 1, y, f"{wood}_stairs[facing=south]")
                    if Xa % 5 == 0:
                        put(i, k, y + 1, "lantern")
            n = 0
            for i, k in wallside:
                dn = wall_dir(i, k)
                if dn and (X(i) + Z(k)) % 4 == 0 and n < area // 20:
                    if put(i, k, y, "bookshelf"):
                        put(i, k, y + 1, "bookshelf"); n += 1
        elif kind in ("classroom", "office"):
            # board on the north wall, teacher at the front, rows of desks behind
            if kind == "classroom":
                north = [(i, k) for i, k in zip(*np.nonzero(free & (d == 1))) if solid[i, y, k - 1] and solid[i, y + 1, k - 1]]
                for i, k in north[:10]:
                    put(i, k, y + 1, "dark_oak_trapdoor[facing=south,half=bottom,open=true]")
                    put(i, k, y + 2, "dark_oak_trapdoor[facing=south,half=bottom,open=true]")
                if north:
                    i, k = north[len(north) // 2]
                    put(i, k + 2, y, "lectern[facing=south]")
            for i, k in zip(*np.nonzero(free & (d >= 2))):
                Xa, Za = X(i), Z(k)
                if kind == "classroom":
                    if Za % 3 == 0 and Xa % 3 != 0 and m[i, k + 1] and not keep[i, k + 1]:
                        put(i, k, y, f"{wood}_slab[type=top]")
                        put(i, k + 1, y, f"{wood}_stairs[facing=south]")
                else:
                    if Za % 4 == 0 and Xa % 4 in (1, 2) and m[i, k + 1] and not keep[i, k + 1]:
                        put(i, k, y, f"{wood}_slab[type=top]")
                        put(i, k + 1, y, f"{wood}_stairs[facing=south]")
                        if Xa % 4 == 1:
                            put(i, k, y + 1, "lantern")
            n = 0
            for i, k in wallside:
                dn = wall_dir(i, k)
                if not dn or n >= max(3, area // 8):
                    continue
                b = rng.choice(["bookshelf", "bookshelf", f"chest[facing={OPP[dn]}]", rng.choice(PLANTS),
                                f"barrel[facing=up]", "bookshelf"])
                if put(i, k, y, b):
                    if b == "bookshelf":
                        put(i, k, y + 1, "bookshelf")
                    n += 1
        else:                                         # hall
            n = 0
            for i, k in wallside:
                dn = wall_dir(i, k)
                if not dn:
                    continue
                if (X(i) + Z(k)) % 7 < 3:
                    put(i, k, y, f"{wood}_stairs[facing={OPP[dn]}]")
                elif (X(i) + Z(k)) % 7 == 5 and n < 40:
                    put(i, k, y, rng.choice(PLANTS)); n += 1
        stats["rooms"] += 1
    return out


def main(only=None):
    rng = random.Random(1108)
    stats = {"openplan": 0, "rooms": 0, "doors": 0, "ladders": 0, "home": 0, "classroom": 0, "office": 0, "hall": 0}
    jobs = []
    for tx in range(8):
        for tz in range(9):
            if only and (tx, tz) not in only:
                continue
            c = furnish_tile(tx, tz, rng, stats)
            if c:
                jobs.append((tx, tz, c))
                print(f"tile {tx},{tz}: {len(c)}", flush=True)
    print(stats, flush=True)
    if "--dry" in sys.argv:
        return
    sessions, cur, n = [], [], 0
    for tx, tz, c in jobs:
        x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
        x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
        ids = write_functions(place.WORLD, f"fa_{tx}_{tz}", c)
        cur += forceload_cmds(x0, z0, x1, z1) + ["function " + f for f in ids] + ["forceload remove all"]
        n += 1
        if n % 8 == 0:
            sessions.append(cur); cur = []
    if cur:
        sessions.append(cur)
    for s, part in enumerate(sessions):
        log = run(place.WORLD, part, wait_load=5)
        print(f"furnish session {s + 1}/{len(sessions)}", [l for l in log.splitlines() if "Exception" in l or "<--" in l][:3], flush=True)


if __name__ == "__main__":
    only = {tuple(map(int, a.split(","))) for a in sys.argv[1:] if "," in a and "=" not in a} or None
    for a in sys.argv[1:]:
        if a.startswith("ratio="):
            RATIO = tuple(map(float, a[6:].split(",")))
    main(only)
