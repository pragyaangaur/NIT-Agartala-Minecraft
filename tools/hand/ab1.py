"""Academic Block 1, the building with the NATIONAL INSTITUTE OF TECHNOLOGY AGARTALA sign.

Identified from W7D6gLvjizM: frontal view of the sign facade at 1:24-1:28 and 1:46-1:52,
drone views at 0:16, 0:20, 0:50, 0:58, 1:02, 1:12. The sign facade faces north onto the
fountain plaza; the long east facade runs along the main road. OSM way 1544302856.

Built axis-aligned (the real building is turned about 13 degrees) so the facade reads cleanly.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox, disk

NAME = "ab1"
# world placement: local (0, 0, 0) -> world (OX, OY, OZ). Local y 0 is the ground layer.
W, L = 33, 66            # building width (x) and length (z)
F = 6                    # local z of the north facade plane (space in front for the portico)
OX, OY, OZ = 577, 71, 1268 - F
NY = 24

WHITE = "smooth_quartz"
RED = "red_terracotta"
GLASS = "tinted_glass"
GREY = "light_gray_concrete"
ROOF = "white_concrete"
FLOOR = "smooth_stone"
PORCH = "polished_granite"

def build():
    v = Vox(W, NY, F + L)
    z0, z1 = F, F + L - 1
    # ---------------------------------------------------------------- shell
    v.box(0, W - 1, 1, 17, z0, z1, WHITE)          # solid mass, hollowed below
    v.box(1, W - 2, 2, 16, z0 + 1, z1 - 1, None)   # interior air
    for fy in (1, 5, 9, 13):                        # floors
        v.box(1, W - 2, fy, fy, z0 + 1, z1 - 1, FLOOR)
    v.box(0, W - 1, 17, 17, z0, z1, ROOF)           # roof slab
    for x in range(W):                              # parapet
        v.set(x, 18, z0, WHITE); v.set(x, 18, z1, WHITE)
    for z in range(z0, z1 + 1):
        v.set(0, 18, z, WHITE); v.set(W - 1, 18, z, WHITE)
    v.box(0, W - 1, 0, 0, z0, z1, FLOOR)            # ground slab

    north_facade(v)
    for side in ("east", "west"):
        long_facade(v, side)
    south_facade(v)
    roof(v)
    return v


def north_facade(v):
    z = F
    # left half, then mirror the facade layer to the right half
    def cell(x, y, b, zz=z):
        v.set(x, y, zz, b); v.set(W - 1 - x, y, zz, b)

    # stepped red tower mass: (y range, x range)
    steps = [((1, 5), (0, 8)), ((6, 8), (2, 8)), ((9, 12), (3, 8)), ((13, 19), (4, 8))]
    for (ya, yb), (xa, xb) in steps:
        for y in range(ya, yb + 1):
            for x in range(xa, xb + 1):
                cell(x, y, RED)
    # tower volume rising above the roof, 6 deep
    for x in range(4, 9):
        for y in range(17, 20):
            for zz in range(z, z + 6):
                cell(x, y, RED, zz)
    # white bands across the red
    for y, (xa, xb) in ((3, (0, 8)), (7, (2, 8)), (12, (3, 8))):
        for x in range(xa, xb + 1):
            cell(x, y, WHITE)
    # wing windows
    for ya in (6, 10, 14):
        for y in (ya, ya + 1):
            cell(1, y, GLASS)
    # central red panel with the round window
    for x in range(12, 17):
        for y in range(1, 17):
            cell(x, y, RED)
    for (x, y) in disk(16, 12, 3.3):
        v.set(x, y, z, WHITE)
    for (x, y) in disk(16, 12, 2.3):
        v.set(x, y, z, GLASS)
    # cream windows beside the panel
    for ya in (9, 13):
        for y in range(ya, ya + 3):
            for x in (10, 11):
                cell(x, y, GLASS)
    # ---- portico: recessed ground floor, two piers, canopy band
    for x in range(8, 17):
        for y in range(1, 8):
            cell(x, y, None)                          # open porch at facade plane
            cell(x, y, GREY if x < 12 else RED, z + 1)  # recessed wall
    # windows and door in the recessed wall
    for x in (9, 10):
        for y in (2, 3, 5, 6):
            cell(x, y, GLASS, z + 1)
    for x in range(14, 17):
        for y in (5, 6):
            cell(x, y, GLASS, z + 1)
    for x in range(15, 17):
        for y in (2, 3):
            cell(x, y, "light_gray_stained_glass", z + 1)
    for y in (2, 3, 5):
        cell(13, y, GLASS, z + 1)
    # piers
    for x in range(5, 8):
        for y in range(1, 8):
            for zz in range(z - 3, z):
                cell(x, y, WHITE, zz)
    for y in (2, 4, 6):                              # grey stripes on the pier fronts
        for x in (6, 7):
            cell(x, y, GREY, z - 3)
    # canopy band (sign) on top of the piers
    for x in range(5, 17):
        for y in (8, 9):
            for zz in range(z - 3, z + 1):
                cell(x, y, WHITE, zz)
    # porch floor and front step
    for x in range(5, 17):
        for zz in range(z - 4, z + 1):
            if v.get(x, 1, zz) is None:
                cell(x, 1, PORCH, zz)
    for x in range(8, 17):
        cell(x, 1, "polished_granite_stairs[facing=south]", z - 5)
    # sign text on the canopy band (world coordinates filled in at export)
    v.ents.append('summon text_display %CX% %CY% %CZ% {Rotation:[180f,0f],background:0,'
                  'text:{text:"NATIONAL INSTITUTE OF TECHNOLOGY AGARTALA",color:"#2a2a2a"},'
                  'transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
                  'translation:[0f,0f,0f],scale:[2.6f,2.6f,2.6f]}}')


def long_facade(v, side):
    """East or west facade: white piers, red spandrels in groups, red corner towers,
    and a red centre bay with a round window (east only)."""
    x = W - 1 if side == "east" else 0
    z0, z1 = F, F + L - 1
    # groups of bays between white towers
    for z in range(z0 + 1, z1):
        k = z - z0
        in_tower = k <= 3 or k >= L - 4
        if in_tower:
            for y in range(1, 20):
                v.set(x, y, z, RED)
            for y in (3, 7, 11, 15):
                v.set(x, y, z, WHITE)
            continue
        m = (k - 4) % 4                      # 0 = white pier, 1..3 = bay
        for fy in (1, 5, 9, 13):
            for dy in range(4):
                y = fy + dy
                if m == 0:
                    b = WHITE
                elif dy in (1, 2) and m in (1, 2):
                    b = GLASS
                elif fy == 1:
                    b = RED
                else:
                    b = RED if dy in (0, 3) else WHITE
                v.set(x, y, z, b)
    # corner tower tops above the roof
    xa, xb = (W - 4, W - 1) if side == "east" else (0, 3)
    for z in list(range(z0, z0 + 4)) + list(range(z1 - 3, z1 + 1)):
        for xx in range(xa, xb + 1):
            for y in range(17, 20):
                v.set(xx, y, z, RED)
    if side == "east":
        zc = F + L // 2
        for z in range(zc - 4, zc + 5):
            for y in range(1, 17):
                v.set(x, y, z, RED)
        for (z, y) in disk(zc, 12, 3.3):
            v.set(x, y, z, WHITE)
        for (z, y) in disk(zc, 12, 2.3):
            v.set(x, y, z, GLASS)
        for z in range(zc - 2, zc + 3):         # dark entrance below
            for y in range(1, 6):
                v.set(x, y, z, "gray_concrete" if y > 3 else "light_gray_stained_glass")


def south_facade(v):
    z = F + L - 1
    for x in range(1, W - 1):
        m = (x - 1) % 4
        for fy in (1, 5, 9, 13):
            for dy in range(4):
                y = fy + dy
                if m == 0:
                    b = WHITE
                elif dy in (1, 2):
                    b = GLASS
                elif fy == 1:
                    b = RED
                else:
                    b = RED if dy in (0, 3) else WHITE
                v.set(x, y, z, b)


def roof(v):
    import math
    za, zb = F + 18, F + 47
    cx, r = 16, 6.5
    for x in range(9, 24):
        h = math.sqrt(max(r * r - (x - cx) ** 2, 0))
        top = 17 + int(round(h * 0.75))
        for z in range(za, zb + 1):
            v.set(x, top, z, "light_gray_stained_glass")
            if z in (za, zb):
                for y in range(18, top + 1):
                    v.set(x, y, z, WHITE)
        for z in (za, zb):
            v.set(x, top, z, WHITE)
    # stair and lift rooms
    for (xa, za_, xb, zb_) in ((2, F + 6, 6, F + 10), (W - 7, F + L - 11, W - 3, F + L - 7), (2, F + L - 11, 6, F + L - 7)):
        v.box(xa, xb, 18, 20, za_, zb_, WHITE)
        v.box(xa, xb, 21, 21, za_, zb_, "smooth_quartz_slab")
    for (x, z) in ((12, F + 8), (20, F + 8), (12, F + 55), (20, F + 55), (27, F + 30), (5, F + 30)):
        v.set(x, 18, z, "white_concrete")


def export():
    v = build()
    cmds = v.commands(OX, OY, OZ)
    cx, cy, cz = OX + W / 2, OY + 8.35, OZ + F - 3 - 0.03
    cmds = [c.replace("%CX%", f"{cx:.2f}").replace("%CY%", f"{cy:.2f}").replace("%CZ%", f"{cz:.2f}") for c in cmds]
    return v, cmds


CHECKS = [
    "execute if block 593 81 1268 tinted_glass run say CHECK round window glass",
    "execute if block 577 75 1268 red_terracotta run say CHECK red tower",
    "execute if entity @e[type=text_display] run say CHECK sign text present",
    "execute if block 593 89 1300 light_gray_stained_glass run say CHECK skylight",
]


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("north", 10).save(os.path.join(out, "ab1_north.png"))
    v.elevation("east", 6).save(os.path.join(out, "ab1_east.png"))
    v.iso("ne", 7).save(os.path.join(out, "ab1_iso_ne.png"))
    print(len(cmds), "commands")


CLEAR = (565, 1250, 621, 1343)


def extra(gy):
    """Paved forecourt in front of the sign facade, cut level with the porch step.
    North of it the ground eases back up to the existing terrain."""
    cmds = []
    for x in range(568, 619):
        for z in range(1238, OZ + F):
            g = gy(x, z)
            if z >= 1255:
                t = OY
            else:
                t = OY + (1255 - z + 1) // 3
            if g <= t:
                if z >= 1255 and g == t:
                    pass
                elif z < 1255:
                    continue
            if g > t:
                cmds.append(f"fill {x} {t + 1} {z} {x} {g} {z} air")
            if z >= 1255:
                line = (x - 577) % 5 == 0 or (z - 1255) % 5 == 0
                cmds.append(f"setblock {x} {t} {z} {'white_terracotta' if line else 'pink_terracotta'}")
                if g < t:
                    cmds.append(f"fill {x} {g} {z} {x} {t - 1} {z} dirt")
            else:
                cmds.append(f"setblock {x} {t} {z} grass_block")
    return cmds
