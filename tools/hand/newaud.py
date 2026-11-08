"""Swami Vivekananda Seminar Hall (OSM "New Auditorium", way 1544302866), north of Knowledge Park.

Frames: W7D6gLvjizM 0:16 (from the plaza side) and 1:02 (from above). A cream three-storey
front block faces south onto the plaza, with red frames round the window groups, a round
window over the entrance, a flat roof with a pink tiled terrace and a grey pyramid skylight,
and two red stair towers that rise above the roof with white box tops. Behind it the hall
itself runs north under a pale green curved metal roof. The Oct 2025 Wi-Fi survey and the
2022-23 Annual Report (seminar hall with stage, lighting, sound and seating) name it.
Inside (creative, 7 Nov): foyer, then a raked auditorium of red seats facing a stage at the
north end with a big screen, red curtains, lecterns, and paintings on the side walls.
Built axis-aligned facing south.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox, disk

NAME = "newaud"
W, L, F = 40, 48, 0
S = 6
OX, OY, OZ = 541, 75, 1138
NY = 30
CLEAR = (532, 1130, 590, 1196)

CREAM = "smooth_sandstone"
WALL2 = "white_terracotta"
RED = "red_terracotta"
GREEN = "lime_terracotta"
FLOOR = "smooth_stone"
HZ = 31                      # hall from z 0 to HZ, front block HZ+1 .. L-1
HH = 15                      # hall wall height


def build():
    v = Vox(W, NY, L + S)
    z1 = L - 1
    # ---------------- hall
    v.box(0, W - 1, 0, 0, 0, HZ, FLOOR)
    v.box(0, W - 1, 1, HH, 0, HZ, CREAM)
    v.box(1, W - 2, 1, HH, 1, HZ - 1, None)
    for x in range(W):                                   # red base band and windows high up
        for z in (0,):
            v.set(x, 1, z, RED)
    for z in range(0, HZ + 1):
        for x in (0, W - 1):
            v.set(x, 1, z, RED)
            if z % 6 in (2, 3):
                for y in (10, 11, 12):
                    v.set(x, y, z, "tinted_glass")
            if z % 6 == 0:
                for y in range(2, HH + 1):
                    v.set(x, y, z, WALL2)            # pilasters
    # curved pale green roof, ridge along z
    cx = (W - 1) / 2
    for x in range(-1, W + 1):
        dx = (x - cx) / (W / 2 + 1)
        h = int(round(6 * math.sqrt(max(1 - dx * dx, 0))))
        for z in range(-1, HZ + 1):
            v.set(x, HH + 1 + h, z, GREEN if (z % 8) else "green_terracotta")
            for y in range(HH + 1, HH + 1 + h):
                if z in (-1, 0, HZ):
                    v.set(x, y, z, CREAM)          # gable ends
    # ---------------- front block (three storeys)
    v.box(0, W - 1, 0, 0, HZ + 1, z1, FLOOR)
    v.box(0, W - 1, 1, 12, HZ + 1, z1, CREAM)
    v.box(1, W - 2, 1, 11, HZ + 2, z1 - 1, None)
    for fy in (5, 9):
        v.box(1, W - 2, fy, fy, HZ + 2, z1 - 1, FLOOR)
    v.box(0, W - 1, 12, 12, HZ + 1, z1, "pink_terracotta")    # roof terrace
    for x in range(W):
        v.set(x, 13, z1, CREAM); v.set(x, 13, HZ + 1, CREAM)
    for z in range(HZ + 1, z1 + 1):
        v.set(0, 13, z, CREAM); v.set(W - 1, 13, z, CREAM)
    for x in range(1, W - 1):                              # terrace tile grid
        for z in range(HZ + 2, z1):
            if x % 4 == 0 or z % 4 == 0:
                v.set(x, 12, z, "white_terracotta")
    # grey pyramid skylight on the terrace
    px, pz = 26, HZ + 8
    for r in range(4):
        for x in range(px - 3 + r, px + 4 - r):
            for z in range(pz - 3 + r, pz + 4 - r):
                v.set(x, 13 + r, z, "gray_stained_glass" if r < 3 else "gray_concrete")
    # south facade: red frames round window groups, round window over the entrance
    def F_(x, y, b):
        v.set(x, y, z1, b)
    for x in range(W):
        for y in range(1, 13):
            F_(x, y, CREAM)
    for (a, b) in ((3, 12), (27, 36)):                   # red-framed window groups
        for x in range(a, b + 1):
            for y in range(2, 12):
                edge = x in (a, b) or y in (2, 11) or y in (5, 8)
                F_(x, y, RED if edge else "tinted_glass")
    for (x, y) in disk(19, 7, 4.3):
        F_(x, y, RED)
    for (x, y) in disk(19, 7, 3.3):
        F_(x, y, "white_concrete")
    for (x, y) in disk(19, 7, 2.4):
        F_(x, y, "light_blue_stained_glass")
    for x in range(16, 23):                              # entrance, canopy and steps
        for y in (1, 2, 3):
            F_(x, y, None)
        for z in range(z1 + 1, z1 + 4):
            v.set(x, 4, z, "smooth_quartz_slab[type=top]")
        v.set(x, 0, z1 + 4, "polished_andesite")
        v.set(x, 1, z1 + 4, None)
    for x in range(14, 25):
        for z in range(z1 + 1, z1 + S):
            v.set(x, 0, z, "polished_andesite")
    # red stair towers at the front corners, rising above the roof, white box tops
    for (tx, tz) in ((0, z1 - 5), (W - 6, z1 - 5)):
        v.box(tx, tx + 5, 1, 17, tz, tz + 5, RED)
        v.box(tx + 1, tx + 4, 2, 16, tz + 1, tz + 4, None)
        v.box(tx, tx + 5, 18, 19, tz, tz + 5, "white_concrete")
        for y in range(3, 16, 3):
            v.set(tx + 2, y, tz + 5, "tinted_glass"); v.set(tx + 3, y, tz + 5, "tinted_glass")
    # ---------------- interior: foyer and auditorium
    for x in range(1, W - 1):                            # foyer floor and a reception desk
        for z in range(HZ + 2, z1):
            v.set(x, 0, z, "polished_diorite")
    for x in range(14, 25):
        v.set(x, 1, HZ + 6, "dark_oak_slab[type=top]")
    v.set(19, 2, HZ + 6, "lantern")
    for x in range(18, 22):                              # doors from the foyer's first floor onto the top of the rake
        for y in (6, 7, 8):
            v.set(x, y, HZ, None); v.set(x, y, HZ + 1, None)
    for j in range(5):                                   # foyer staircase, ground to first floor
        x = 8 + j
        for z in (z1 - 3, z1 - 2):
            v.set(x, 1 + j, z, "stone_brick_stairs[facing=east]")
            for y in range(2 + j, 2 + j + 3):
                if y <= 8:
                    v.set(x, y, z, None)
    for z in (9, 10):                                    # side doors at the front of the hall, by the stage
        for y in (1, 2, 3):
            v.set(0, y, z, None); v.set(W - 1, y, z, None)
        v.set(0, 4, z, "light[level=15]"); v.set(W - 1, 4, z, "light[level=15]")
    # stage at the north end
    for x in range(1, W - 1):
        for z in range(1, 8):
            v.set(x, 1, z, "dark_oak_planks")
        v.set(x, 1, 8, "dark_oak_stairs[facing=north]")
    for x in range(8, W - 8):                            # screen on the north wall
        for y in range(4, 12):
            v.set(x, y, 1, "white_concrete")
    for x in range(7, W - 7):
        v.set(x, 3, 1, "black_concrete"); v.set(x, 12, 1, "black_concrete")
    for y in range(3, 13):
        v.set(7, y, 1, "black_concrete"); v.set(W - 8, y, 1, "black_concrete")
    for x in list(range(2, 6)) + list(range(W - 6, W - 2)):    # red curtains
        for y in range(2, 14):
            v.set(x, y, 2, "red_wool")
    v.set(12, 2, 5, "lectern[facing=south]"); v.set(W - 13, 2, 5, "lectern[facing=south]")
    for x in range(14, 26):                              # speakers' table
        v.set(x, 2, 4, "dark_oak_slab[type=top]")
        if x % 2:
            v.set(x, 2, 3, "dark_oak_stairs[facing=north]")
    # raked seating, rising to the south, red seats facing the stage
    for z in range(10, HZ):
        tier = (z - 10) // 4
        for x in range(1, W - 1):
            for y in range(1, 1 + tier):
                v.set(x, y, z, "smooth_stone")
            aisle = x in (1, 2, W - 3, W - 2) or abs(x - cx) < 1.6
            if aisle:
                if tier > 0 and (z - 10) % 4 == 0:
                    v.set(x, tier, z, "stone_brick_stairs[facing=south]")
                else:
                    v.set(x, 1 + tier, z, "red_carpet")
            elif (z - 10) % 2 == 0:
                v.set(x, 1 + tier, z, "red_nether_brick_stairs[facing=south]")
    # lights along the hall ceiling
    for x in range(3, W - 3, 5):
        for z in range(3, HZ, 5):
            v.set(x, HH - 1, z, "light[level=14]")
    for x in range(3, W - 3, 5):
        for z in range(HZ + 3, z1, 5):
            for y in (4, 8, 11):
                v.set(x, y, z, "light[level=13]")
    return v


PAINTINGS = ["kebab", "aztec", "alban", "aztec2", "bomb", "plant", "wasteland", "pool", "courbet", "sea", "sunset",
             "creebet", "wanderer", "graham", "match", "bust", "stage", "void", "skull_and_roses", "wither",
             "fighters", "earth", "wind", "water", "fire", "baroque", "humble", "meditative", "prairie_ride",
             "unpacked", "backyard", "bouquet", "cavebird", "changing", "cotan", "endboss", "fern", "lowmist",
             "orb", "owlemons", "passage", "pond", "sunflowers", "tides"]


def paintings(ox, oy, oz, x_west, x_east, zs, ys, rng_seed=1):
    """Paintings on both side walls of a hall: west wall faces east (3b), east wall faces west (1b)."""
    import random
    r = random.Random(rng_seed)
    out = []
    for z in zs:
        for y in ys:
            out.append(f'summon painting {ox + x_west + 1} {oy + y} {oz + z} {{facing:3b,variant:"minecraft:{r.choice(PAINTINGS)}"}}')
            out.append(f'summon painting {ox + x_east - 1} {oy + y} {oz + z} {{facing:1b,variant:"minecraft:{r.choice(PAINTINGS)}"}}')
    return out


def export():
    v = build()
    cmds = v.commands(OX, OY, OZ)
    cmds.append(f"kill @e[type=painting,x={OX},y={OY},z={OZ},dx={W},dy=20,dz={L}]")
    cmds += paintings(OX, OY, OZ, 0, W - 1, range(13, HZ, 5), (9,), 3)
    for x in (9, 13, W - 14, W - 10):                    # paintings beside the screen too
        cmds.append(f'summon painting {OX + x} {OY + 7} {OZ + 2} {{facing:0b,variant:"minecraft:{PAINTINGS[x % len(PAINTINGS)]}"}}')
    cmds.append('summon text_display %.2f %.2f %.2f {Rotation:[0f,0f],background:0,text:{text:"SWAMI VIVEKANANDA SEMINAR HALL",color:"#7a1f12"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.3f,1.3f,1.3f]}}' % (OX + 19.5, OY + 4.6, OZ + L + 3 + 0.03))
    return v, cmds


def extra(gy):
    from extrude import osm_poly, clear_poly
    return clear_poly(osm_poly(1544302866), gy, margin=2)


CHECKS = ["execute if block 561 80 1139 white_concrete run say CHECK newaud screen"]

if __name__ == "__main__":
    out = sys.argv[1]
    v, cmds = export()
    v.iso("se", 7).save(os.path.join(out, "newaud_se.png"))
    v.iso("sw", 7).save(os.path.join(out, "newaud_sw.png"))
    print(len(cmds))
