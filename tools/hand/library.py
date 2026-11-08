"""Central Library, the Golden Jubilee Knowledge Centre. OSM way 1544302854.

Frames: W7D6gLvjizM 2:02-2:14 (front from the approach road), 2:24-2:32 (drone);
Commons photo Knowledge_center.png (front close up).
Square plan with four mustard corner towers carrying vertical blue glass strips and white
caps; between the front towers a curved two-tier white portico on six white columns, maroon
walls with tall blue glass behind; cream body, flat roof with a small dome; a round glass
bay on the east side. Faces south onto the round garden.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox, disk
from style import Face, FLOOR, ROOF

NAME = "library"
W, L = 60, 58               # building x 0..59, z 0..57; portico projects south of z 57
F = 0
S = 9                       # space south of the building for the portico and steps
OX, OY, OZ = 842, 73, 1163
NY = 30
CLEAR = (834, 1155, 909, 1236)

MUST = "yellow_terracotta"
CREAM = "smooth_sandstone"
BLUE = "blue_stained_glass"
WHITE = "smooth_quartz"
MAROON = "red_terracotta"
COL = "quartz_pillar"
TOWER = 11
TTOP = 20


def build():
    v = Vox(W + 6, NY, L + S)
    x0, x1, z0, z1 = 0, W - 1, 0, L - 1
    # body
    v.box(x0, x1, 1, 15, z0, z1, CREAM)
    v.box(x0 + 1, x1 - 1, 2, 14, z0 + 1, z1 - 1, None)
    for fy in (1, 6, 11):
        v.box(x0 + 1, x1 - 1, fy, fy, z0 + 1, z1 - 1, FLOOR)
    v.box(x0, x1, 15, 15, z0, z1, ROOF)
    v.box(x0, x1, 0, 0, z0, z1, FLOOR)
    for side in ("north", "east", "west", "south"):
        f = Face(v, side, x0, x1, z0, z1)
        for u in range(f.n):
            if u % 4 in (1, 2):
                for y in (3, 4, 8, 9, 12, 13):
                    f.set(u, y, BLUE)
        for u in range(f.n):
            f.set(u, 16, CREAM)
    # corner towers
    for (tx, tz) in ((0, 0), (W - TOWER, 0), (0, L - TOWER), (W - TOWER, L - TOWER)):
        v.box(tx, tx + TOWER - 1, 1, TTOP, tz, tz + TOWER - 1, MUST)
        v.box(tx + 1, tx + TOWER - 2, 2, TTOP - 1, tz + 1, tz + TOWER - 2, None)
        v.box(tx - 1, tx + TOWER, TTOP + 1, TTOP + 1, tz - 1, tz + TOWER, WHITE)   # cap
        v.box(tx, tx + TOWER - 1, TTOP + 2, TTOP + 2, tz, tz + TOWER - 1, "smooth_quartz_slab")
        # vertical blue strips on the two outward faces
        cx, cz = tx + TOWER // 2, tz + TOWER // 2
        sx = x0 if tx == 0 else x1
        sz = z0 if tz == 0 else z1
        for y in range(2, TTOP):
            for d in (-1, 0, 1):
                v.set(sx, y, cz + d, BLUE)
                v.set(cx + d, y, sz, BLUE)
        # white cornice line under the cap
        for x in range(tx, tx + TOWER):
            v.set(x, TTOP, sz, WHITE)
        for z in range(tz, tz + TOWER):
            v.set(sx, TTOP, z, WHITE)
    # front between the towers: maroon wall with tall blue glass, recessed portico
    fz = z1
    for x in range(TOWER, W - TOWER):
        for y in range(1, 15):
            v.set(x, y, fz, MAROON)
        if (x - TOWER) % 4 in (1, 2):
            for y in range(2, 13):
                v.set(x, y, fz, BLUE)
    for x in range(W // 2 - 2, W // 2 + 2):
        for y in range(1, 5):
            v.set(x, y, fz, "light_blue_stained_glass")
    # curved portico: front edge bulges south
    cx = (W - 1) / 2
    half = W / 2 - TOWER
    def edge(x):
        t = (x - cx) / half
        return fz + 1 + int(round(6 * (1 - t * t)))
    for x in range(TOWER, W - TOWER):
        e = edge(x)
        for z in range(fz + 1, e + 1):
            v.set(x, 1, z, "polished_diorite")                       # porch floor
            for y in (9, 10):
                v.set(x, y, z, WHITE)                                 # lower canopy
        for y in (9, 10):
            v.set(x, y, e, WHITE)
        # upper tier: set back two blocks, balcony rail
        e2 = max(fz + 1, e - 2)
        for z in range(fz + 1, e2 + 1):
            for y in (14, 15):
                v.set(x, y, z, WHITE)
        v.set(x, 11, e, "red_nether_brick_wall")
        v.set(x, 1 + 0, e + 1, "polished_diorite_stairs[facing=north]")
        v.set(x, 0, e + 1, "polished_diorite")
    # six columns along the curve
    for k in range(6):
        x = int(round(TOWER + 2 + k * (W - 2 * TOWER - 5) / 5))
        e = edge(x)
        for y in range(2, 9):
            v.set(x, y, e - 1, COL)
    for x in (TOWER + 7, W - TOWER - 8):
        e = edge(x)
        for y in range(11, 14):
            v.set(x, y, e - 2, COL)
    # dome on the roof
    dcx, dcz, R = W // 2, L // 2, 6
    for x in range(dcx - R, dcx + R + 1):
        for z in range(dcz - R, dcz + R + 1):
            d = math.hypot(x - dcx, z - dcz)
            if d <= R:
                h = int(round(math.sqrt(R * R - d * d) * 0.8))
                v.box(x, x, 16, 16 + h, z, z, "smooth_sandstone" if d > R - 1.2 else "sandstone")
    for (x, z) in disk(dcx, dcz, 7.4):
        if v.get(x, 16, z) is None:
            v.set(x, 16, z, WHITE)
    # round glass bay on the east side
    bcz = L // 2
    for x in range(W, W + 6):
        for z in range(bcz - 7, bcz + 8):
            d = math.hypot(x - (W - 1), z - bcz)
            if d <= 6.6:
                for y in range(1, 15):
                    v.set(x, y, z, BLUE if d > 5.6 and y % 5 else WHITE if d > 5.6 else None)
                v.set(x, 15, z, WHITE); v.set(x, 0, z, FLOOR)
    # ---- interior (7 Nov, creative): stacks of bookshelves, a reading hall with tables,
    # chairs and lecterns with books, a circulation desk by the entrance, on all three floors
    import random
    rng = random.Random(4)
    for fy in (1, 6, 11):
        for x in range(1, W - 1):
            for z in range(1, L - 1):
                if v.get(x, fy, z) != FLOOR or v.get(x, fy + 1, z) is not None:
                    continue
                reading = 20 <= x <= 39 and 16 <= z <= 42
                if fy == 1 and 24 <= x <= 35 and z == L - 7 and not 28 <= x <= 31:
                    v.set(x, fy + 1, z, "dark_oak_slab[type=top]")          # circulation desk
                    if x % 3 == 0:
                        v.set(x, fy + 2, z, "lantern")
                    continue
                if fy == 1 and z >= L - 6:
                    continue                                                 # entrance lobby
                if reading:
                    m = x % 4
                    if m == 1 and z % 8 not in (0, 7):
                        v.set(x, fy + 1, z, "oak_slab[type=top]")
                        if rng.random() < 0.12:
                            v.set(x, fy + 2, z, "lantern" if rng.random() < 0.5 else "flower_pot")
                    elif m == 0 and z % 8 not in (0, 7) and z % 2:
                        v.set(x, fy + 1, z, "oak_stairs[facing=west]")
                    elif m == 2 and z % 8 not in (0, 7) and z % 2:
                        v.set(x, fy + 1, z, "oak_stairs[facing=east]")
                    elif m == 3 and z % 8 == 3:
                        v.set(x, fy + 1, z, "lectern[facing=west,has_book=true]")
                    elif z % 8 in (0, 7):
                        pass
                    continue
                if x % 6 in (1, 2) and z % 12 not in (0, 1) and 2 <= z <= L - 3 and 2 <= x <= W - 3:
                    for y in (fy + 1, fy + 2, fy + 3):
                        v.set(x, y, z, "bookshelf")
                elif x % 6 == 4 and z % 12 == 6:
                    v.set(x, fy + 1, z, "lectern[facing=south,has_book=true]")
    # a way in and a way up: open front door, ladder by the west wall through all floors
    for x in range(W // 2 - 2, W // 2 + 2):
        for y in (1, 2, 3):
            v.set(x, y, L - 1, None)
    for y in range(2, 14):
        v.set(1, y, 29, "ladder[facing=east]")
    for fy in (1, 6, 11):
        for z in (28, 29, 30):
            for y in range(fy + 1, fy + 4):
                v.set(2, y, z, None)
    for fy in (1, 6, 11):                                # brighter reading light
        for x in range(2, W - 2, 3):
            for z in range(2, L - 2, 3):
                if v.get(x, fy + 4, z) is None and v.get(x, fy, z) == FLOOR:
                    v.set(x, fy + 4, z, "light[level=15]")
    # sign text on the canopy fascia
    v.ents.append('summon text_display %CX% %CY% %CZ% {Rotation:[0f,0f],background:0,'
                  'text:{text:"GOLDEN JUBILEE KNOWLEDGE CENTRE",color:"#5a1e14"},'
                  'transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
                  'translation:[0f,0f,0f],scale:[2.4f,2.4f,2.4f]}}')
    return v


def export():
    v = build()
    cmds = v.commands(OX, OY, OZ)
    book = ('{Book:{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":'
            '{title:"Knowledge Centre",author:"NIT Agartala",pages:["Golden Jubilee Knowledge Centre, the Central Library of NIT Agartala.","Two floors of 2,282 sq m each, open to every student.","Please return books to the circulation desk."]}}}}')
    cmds = [c + book if c.startswith("setblock") and "lectern[" in c else c for c in cmds]
    e = L - 1 + 1 + 6           # front of the curved fascia at the centre
    cx, cy, cz = OX + W / 2, OY + 9.25, OZ + e + 1.03
    cmds = [c.replace("%CX%", f"{cx:.2f}").replace("%CY%", f"{cy:.2f}").replace("%CZ%", f"{cz:.2f}") for c in cmds]
    return v, cmds


CHECKS = ["execute if block 842 85 1163 yellow_terracotta run say CHECK library tower"]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("south", 8).save(os.path.join(out, "library_south.png"))
    v.iso("sw", 6).save(os.path.join(out, "library_iso.png"))
    print(len(cmds), "commands")
