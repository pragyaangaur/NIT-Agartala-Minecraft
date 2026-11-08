"""Visvesvaraya Auditorium (the old auditorium). OSM way 361838514.

Frames: JkbNik31wDE 3:12-3:14 (sign VISVESVARAYA AUDITORIUM readable, caption).
Two-storey white front block: a navy fascia band carrying the name in white over a porch on
thin white round columns, an upper band of windows between pilasters, a big painted mural
board standing on the roof parapet; the hall behind; a fenced paved forecourt with a
starburst fountain over a small pool ringed by blue bollards. Faces the road to the south-east;
built axis-aligned facing south.
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox
from style import FLOOR

NAME = "visvesvaraya"
W, L, F = 40, 30, 0
S = 22
OX, OY, OZ = 611, 75, 1075
NY = 24
CLEAR = (600, 1058, 662, 1130)

WHITE = "smooth_quartz"
NAVY = "blue_concrete"


def build():
    v = Vox(W, NY, L + S)
    z1 = L - 1
    # hall behind, taller
    v.box(2, W - 3, 1, 14, 0, z1 - 8, WHITE)
    v.box(3, W - 4, 2, 13, 1, z1 - 9, None)
    v.box(2, W - 3, 14, 14, 0, z1 - 8, "white_concrete")
    v.box(0, W - 1, 0, 0, 0, z1, FLOOR)
    # front block, two storeys
    v.box(0, W - 1, 1, 11, z1 - 8, z1, WHITE)
    v.box(1, W - 2, 2, 10, z1 - 7, z1 - 1, None)
    v.box(1, W - 2, 6, 6, z1 - 7, z1 - 1, FLOOR)
    v.box(0, W - 1, 11, 11, z1 - 8, z1, "white_concrete")
    for x in range(W):
        v.set(x, 12, z1, WHITE)
    # ground floor: recessed dark glass behind the porch
    for x in range(4, W - 4):
        for y in range(1, 6):
            v.set(x, y, z1, "tinted_glass" if x % 5 else WHITE)
    # navy fascia band projecting over the porch
    for x in range(3, W - 3):
        for z in range(z1, z1 + 4):
            v.set(x, 6, z, NAVY)
            v.set(x, 7, z, NAVY if z == z1 + 3 else WHITE)
    for x in range(4, W - 4, 6):                   # thin round columns
        for y in range(1, 6):
            v.set(x, y, z1 + 3, "quartz_pillar")
    for x in range(3, W - 3):
        for z in range(z1 + 1, z1 + 4):
            v.set(x, 0, z, "polished_andesite")
    # upper windows between pilasters
    for x in range(1, W - 1):
        if x % 4 in (1, 2):
            for y in (8, 9):
                v.set(x, y, z1, "tinted_glass")
    # painted mural board on the parapet
    rnd = random.Random(7)
    pal = ["light_blue_concrete", "blue_concrete", "white_concrete", "red_concrete", "yellow_concrete",
           "orange_concrete", "cyan_concrete", "pink_concrete", "lime_concrete"]
    for x in range(8, W - 8):
        for y in range(13, 18):
            v.set(x, y, z1 - 1, rnd.choice(pal) if rnd.random() < 0.6 else "light_blue_concrete")
        v.set(x, 12, z1 - 1, "gray_concrete")
    # forecourt with the starburst fountain
    cx, cz = W // 2, z1 + 12
    for x in range(0, W):
        for z in range(z1 + 4, z1 + S - 1):
            v.set(x, 0, z, "polished_andesite" if (x + z) % 2 else "andesite")
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 4, cz + 5):
            r = math.hypot(x - cx, z - cz)
            if r <= 3.6:
                v.set(x, 0, z, "water")
            elif r <= 4.6:
                v.set(x, 0, z, "red_terracotta"); v.set(x, 1, z, "red_terracotta_slab" if False else "stone_brick_slab")
    for a in range(0, 360, 45):
        x = cx + int(round(5.6 * math.cos(math.radians(a)))); z = cz + int(round(5.6 * math.sin(math.radians(a))))
        v.set(x, 1, z, "light_blue_concrete")
    v.set(cx, 0, cz, "stone"); v.set(cx, 1, cz, "iron_block"); v.set(cx, 2, cz, "iron_block")
    for fac, (dx, dz) in (("north", (0, -1)), ("south", (0, 1)), ("east", (1, 0)), ("west", (-1, 0))):
        v.set(cx + dx, 3, cz + dz, f"lightning_rod[facing={fac}]")
    v.set(cx, 3, cz, "iron_block"); v.set(cx, 4, cz, "lightning_rod[facing=up]")
    # boundary fence along the road side with a gap for the gate
    for x in range(W):
        if abs(x - cx) > 3:
            v.set(x, 1, z1 + S - 1, "iron_bars")
    # ---- interior (7 Nov, creative): stage and screen at the north end, raked seating
    hx0, hx1, hz1 = 3, W - 4, z1 - 9
    for x in range(hx0, hx1 + 1):
        for z in range(1, 6):
            v.set(x, 1, z, "dark_oak_planks")
        v.set(x, 1, 6, "dark_oak_stairs[facing=north]")
    for x in range(9, W - 9):
        for y in range(4, 11):
            v.set(x, y, 1, "white_concrete")
    for x in range(8, W - 8):
        v.set(x, 3, 1, "black_concrete"); v.set(x, 11, 1, "black_concrete")
    for y in range(3, 12):
        v.set(8, y, 1, "black_concrete"); v.set(W - 9, y, 1, "black_concrete")
    for x in list(range(hx0, hx0 + 3)) + list(range(hx1 - 2, hx1 + 1)):
        for y in range(2, 13):
            v.set(x, y, 2, "blue_wool")
    v.set(W // 2 - 6, 2, 4, "lectern[facing=south]")
    for z in range(8, hz1 + 1):
        tier = (z - 8) // 2
        for x in range(hx0, hx1 + 1):
            for y in range(1, 1 + tier):
                v.set(x, y, z, "smooth_stone")
            if abs(x - W // 2) < 1.6 or x in (hx0, hx1):
                if tier > 0 and (z - 8) % 2 == 0:
                    v.set(x, tier, z, "stone_brick_stairs[facing=south]")
                else:
                    v.set(x, 1 + tier, z, "blue_carpet")
            elif (z - 8) % 2 == 0:
                v.set(x, 1 + tier, z, "dark_oak_stairs[facing=south]")
    for x in range(hx0, hx1 + 1):                        # doors from the front block's first floor
        for y in (7, 8, 9):
            if abs(x - W // 2) < 3:
                v.set(x, y, z1 - 8, None)
    for j in range(6):                                   # foyer staircase, ground to first floor
        x = 4 + j
        for z in (z1 - 3, z1 - 2):
            v.set(x, 1 + j, z, "stone_brick_stairs[facing=east]")
            for y in range(2 + j, 2 + j + 3):
                if y <= 9:
                    v.set(x, y, z, None)
    for x in range(W // 2 - 1, W // 2 + 2):              # front door
        for y in (1, 2, 3):
            v.set(x, y, z1, None)
    for z in (7, 8):                                     # side doors by the stage
        for y in (1, 2, 3):
            v.set(2, y, z, None); v.set(W - 3, y, z, None)
    for x in range(4, W - 4, 5):
        for z in range(3, z1 - 9, 5):
            v.set(x, 13, z, "light[level=14]")
        for y in (5, 10):
            for z in (z1 - 6, z1 - 3):
                v.set(x, y, z, "light[level=13]")
    v.ents.append('summon text_display %CX% %CY% %CZ% {Rotation:[0f,0f],background:0,'
                  'text:{text:"VISVESVARAYA AUDITORIUM",color:"#ffffff"},'
                  'transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
                  'translation:[0f,0f,0f],scale:[1.6f,1.6f,1.6f]}}')
    return v


def export():
    v = build()
    cmds = v.commands(OX, OY, OZ)
    cx, cy, cz = OX + W / 2, OY + 6.25, OZ + L - 1 + 4 + 0.03
    cmds = [c.replace("%CX%", f"{cx:.2f}").replace("%CY%", f"{cy:.2f}").replace("%CZ%", f"{cz:.2f}") for c in cmds]
    import newaud
    cmds.append(f"kill @e[type=painting,x={OX},y={OY},z={OZ},dx={W},dy=20,dz={L}]")
    cmds += newaud.paintings(OX, OY, OZ, 2, W - 3, range(9, L - 10, 4), (10,), 11)
    for x in (4, W - 6):
        cmds.append(f'summon painting {OX + x} {OY + 7} {OZ + 2} {{facing:0b,variant:"minecraft:{newaud.PAINTINGS[x % 40]}"}}')
    return v, cmds


def extra(gy):
    from extrude import osm_poly, clear_poly
    return clear_poly(osm_poly(361838514), gy)


CHECKS = []

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("south", 10).save(os.path.join(out, "visv_south.png"))
    print(len(cmds))
