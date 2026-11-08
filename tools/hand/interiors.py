"""Furnish the inside of footprint-built buildings (extrude.Building) after build().

kinds
  hostel   central corridor along the long axis, rooms every 4 m with a bed against the
           outer wall, a desk with a chair and a lamp, a chest and a wardrobe
  mess     long tables with benches on both sides, a serving counter with food chests,
           barrels, smokers and a water cauldron along one wall, cakes on a few tables
  lab      science labs: rows of benches with brewing stands, cauldrons and pots, stools,
           a teacher's desk and a blackboard
Each kind furnishes every storey (or only the ones listed) inside the walls, leaving the
ceiling lights alone.
"""
import math, random
import numpy as np
from scipy.ndimage import binary_erosion

FOOD = ('[{Slot:0b,id:"minecraft:bread",count:64},{Slot:1b,id:"minecraft:baked_potato",count:32},'
        '{Slot:2b,id:"minecraft:cooked_chicken",count:24},{Slot:3b,id:"minecraft:pumpkin_pie",count:12},'
        '{Slot:4b,id:"minecraft:apple",count:32},{Slot:5b,id:"minecraft:cooked_mutton",count:24},'
        '{Slot:6b,id:"minecraft:cookie",count:48},{Slot:7b,id:"minecraft:melon_slice",count:32},'
        '{Slot:8b,id:"minecraft:mushroom_stew",count:1},{Slot:9b,id:"minecraft:beetroot_soup",count:1},'
        '{Slot:10b,id:"minecraft:cooked_salmon",count:16},{Slot:11b,id:"minecraft:cake",count:2}]')
BEDS = ["white", "light_blue", "blue", "red", "green", "orange", "gray", "cyan", "yellow", "purple"]
CARD = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}


def _axes(poly):
    P = np.array(poly); c = P.mean(0)
    _, _, vt = np.linalg.svd(P - c)
    return c, vt[0], vt[1]


def _card(vx, vz):
    return (int(np.sign(vx)), 0) if abs(vx) >= abs(vz) else (0, int(np.sign(vz)))


def furnish(b, kind, storeys=None, seed=0, counter_side=None):
    """b: a Building after build(). Returns absolute setblock commands."""
    x0, g, z0 = b.origin
    m = b.mask
    room = binary_erosion(m, iterations=1)          # inside the walls
    sh = b.storey_h
    rng = random.Random(seed)
    c, ua, ub = _axes(b.poly)
    out = []
    levels = range(b.storeys) if storeys is None else storeys
    cells = [tuple(p) for p in np.argwhere(room)]
    AL, AC = {}, {}
    for (i, k) in cells:
        X, Z = x0 + i + 0.5, z0 + k + 0.5
        AL[(i, k)] = (X - c[0]) * ua[0] + (Z - c[1]) * ua[1]
        AC[(i, k)] = (X - c[0]) * ub[0] + (Z - c[1]) * ub[1]
    half = max(abs(v) for v in AC.values()) if AC else 0
    for st in levels:
        fy = g + 1 + st * sh                        # floor slab; usable air fy+1 .. fy+sh-1
        y = fy + 1
        beds = []
        if kind == "hostel":
            wallb = b.wall
            for (i, k) in cells:
                X, Z = x0 + i, z0 + k
                al, ac = AL[(i, k)], AC[(i, k)]
                slot = int(math.floor(al)) % 4
                if abs(ac) < 1.0:
                    out.append(f"setblock {X} {fy} {Z} polished_andesite")
                    continue
                if slot == 0:
                    for yy in range(y, fy + sh):
                        out.append(f"setblock {X} {yy} {Z} {wallb}")
                    continue
                if abs(ac) < 2.0 and slot == 2:
                    continue                        # door gap to the corridor
                if abs(ac) < 2.0:
                    for yy in range(y, fy + sh):
                        out.append(f"setblock {X} {yy} {Z} {wallb}")
                    continue
                d = _card(ub[0] * np.sign(ac), ub[1] * np.sign(ac))
                outer = (i + d[0], k + d[1]) not in AC     # cell touches the outer wall
                if outer and slot == 1:
                    fi, fk = i - d[0], k - d[1]
                    if (fi, fk) in AC and int(math.floor(AL[(fi, fk)])) % 4 == 1 and abs(AC[(fi, fk)]) >= 2.0:
                        col = rng.choice(BEDS)
                        beds.append(f"setblock {x0 + fi} {y} {z0 + fk} {col}_bed[facing={CARD[d]},part=foot]")
                        beds.append(f"setblock {X} {y} {Z} {col}_bed[facing={CARD[d]},part=head]")
                elif outer and slot == 2:
                    out.append(f"setblock {X} {y} {Z} spruce_slab[type=top]")
                    if sh >= 4:
                        out.append(f"setblock {X} {y + 1} {Z} lantern")
                    back = CARD[(-d[0], -d[1])]
                    out.append(f"setblock {x0 + i - d[0]} {y} {z0 + k - d[1]} spruce_stairs[facing={CARD[d]}]")
                elif outer and slot == 3:
                    out.append(f"setblock {X} {y} {Z} chest[facing={CARD[(-d[0], -d[1])]}]")
                    if sh >= 4:
                        out.append(f"setblock {X} {y + 1} {Z} spruce_planks")
                elif slot == 3 and rng.random() < 0.5:
                    out.append(f"setblock {X} {fy} {Z} {rng.choice(['white_wool', 'light_gray_wool', 'brown_wool'])}")
        elif kind == "mess":
            colmin = {}
            for (i, k) in cells:
                colmin[i] = min(colmin.get(i, k), k)
            for (i, k) in cells:                    # clear old furniture, keep the ceiling lights
                for yy in range(y, fy + sh - 1):
                    out.append(f"setblock {x0 + i} {yy} {z0 + k} air")
            for (i, k) in cells:
                X, Z = x0 + i, z0 + k
                zmin = colmin[i]
                if k <= zmin + 1:                   # serving counter along the north wall
                    item = (X // 1) % 6
                    if k == zmin:
                        blk = ["chest[facing=south]" + "{Items:" + FOOD + "}", "barrel[facing=up]", "smoker[facing=south,lit=true]",
                               "chest[facing=south]" + "{Items:" + FOOD + "}", "furnace[facing=south,lit=true]", "water_cauldron[level=3]"][item]
                        out.append(f"setblock {X} {y} {Z} {blk}")
                        if sh >= 4 and item in (1, 4):
                            out.append(f"setblock {X} {y + 1} {Z} lantern")
                    else:
                        out.append(f"setblock {X} {y} {Z} smooth_quartz_slab[type=top]")
                        if X % 4 == 0:
                            out.append(f"setblock {X} {y + 1} {Z} {rng.choice(['cake', 'decorated_pot', 'flower_pot'])}")
                    continue
                if k <= zmin + 3 or Z % 13 == 0:
                    continue                        # queue space and cross aisles
                col = X % 5
                if col == 2:
                    out.append(f"setblock {X} {y} {Z} dark_oak_slab[type=top]")
                    if rng.random() < 0.06:
                        out.append(f"setblock {X} {y + 1} {Z} cake")
                elif col == 1:
                    out.append(f"setblock {X} {y} {Z} spruce_stairs[facing=west]")
                elif col == 3:
                    out.append(f"setblock {X} {y} {Z} spruce_stairs[facing=east]")
        elif kind == "lab":
            ks = [k for (_, k) in cells]
            zmin = min(ks)
            for (i, k) in cells:
                X, Z = x0 + i, z0 + k
                col, row = X % 6, Z % 9
                if row in (0, 8):
                    continue
                if col in (1, 2):
                    out.append(f"setblock {X} {y} {Z} polished_andesite")
                    if sh >= 4:
                        r = rng.random()
                        top = "brewing_stand" if r < 0.15 else "flower_pot" if r < 0.25 else "decorated_pot" if r < 0.3 \
                            else "cauldron" if r < 0.38 else None
                        if top and col == 1:
                            out.append(f"setblock {X} {y + 1} {Z} {top}")
                elif col == 3 and row % 2:
                    out.append(f"setblock {X} {y} {Z} spruce_stairs[facing=east]")
                elif col == 0 and row % 2:
                    out.append(f"setblock {X} {y} {Z} spruce_stairs[facing=west]")
        out += beds
    out += circulation(b, cells, AL, AC, ua, levels if storeys is None else storeys, sh, g, x0, z0)
    return out


def circulation(b, cells, AL, AC, ua, levels, sh, g, x0, z0):
    """A way in and a way up: clear a path from the front door to the corridor on the ground
    floor, and put a straight staircase at one end of the corridor on every floor."""
    out = []
    cellset = set(cells)
    if getattr(b, "door", None):
        ci, ck, want = b.door
        for lat in (-1, 0, 1):
            for t in range(1, 40):
                i = ci - want[0] * t + (lat if want[1] else 0)
                k = ck - want[1] * t + (lat if want[0] else 0)
                if (i, k) not in cellset:
                    if t > 2:
                        break
                    continue
                for yy in (g + 2, g + 3, g + 4):
                    out.append(f"setblock {x0 + i} {yy} {z0 + k} air")
                if abs(AC[(i, k)]) < 1.0:
                    break
    if b.storeys < 2:
        return out
    # a ladder up through every floor at the end of the corridor, against the end wall
    d = _card(ua[0], ua[1])
    corridor = sorted([c for c in cells if abs(AC[c]) < 1.0], key=lambda c: AL[c])
    for c in corridor:
        back = (c[0] - d[0], c[1] - d[1])
        if back not in cellset:
            i, k = c
            top = g + 1 + (b.storeys - 1) * sh
            for yy in range(g + 2, top + 3):
                out.append(f"setblock {x0 + i} {yy} {z0 + k} ladder[facing={CARD[d]}]")
            for yy in range(g + 2, top + 3):                 # keep the cell in front of it clear
                pass
            break
    return out
    run = [(start[0] + d[0] * j, start[1] + d[1] * j) for j in range(sh + 1)]
    top = b.storeys
    for st in range(top - 1):
        fy = g + 1 + st * sh
        for j, (i, k) in enumerate(run[:sh]):
            for yy in range(fy + 1, fy + sh + 3):
                if yy != fy + 1 + j:
                    out.append(f"setblock {x0 + i} {yy} {z0 + k} air")
            out.append(f"setblock {x0 + i} {fy + 1 + j} {z0 + k} stone_brick_stairs[facing={CARD[d]}]")
        i, k = run[sh]
        for yy in range(fy + sh + 1, fy + sh + 3):
            out.append(f"setblock {x0 + i} {yy} {z0 + k} air")
    return out
