"""ECE Building (ECE and EE departments). OSM way 361838504.

Frames: JkbNik31wDE 0:48-0:56 (entrance close up, "ECE & EE DEPARTMENT" caption), 2:04-2:08
(front from the road); Commons photo ECE_Building_nit_agartala.jpg.
A long seven-storey slab: two tan base floors, then five floors of orange piers with cream
window strips; a white-framed blue glass atrium in the middle with a tall tan portal; white
balcony frames on both wings; overhanging roof eaves with an orange fascia.
The real slab is turned about 30 degrees to face the road to the south-south-east; here it
faces south.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox
from style import Face, FLOOR, ROOF

NAME = "ece"
W, L, F = 78, 26, 0
S = 8
OX, OY, OZ = 733, 68, 1387
NY = 30
CLEAR = (724, 1362, 820, 1434)

TAN = "white_terracotta"
CREAM = "smooth_quartz"
ORANGE = "orange_terracotta"
GLASS = "tinted_glass"
BLUE = "blue_stained_glass"
WHITE = "white_concrete"
FLOORS = (1, 5, 9, 12, 15, 18, 21)
TOP = 24


def facade(f, u0, u1):
    """Tan base floors, orange cornice, orange piers with cream window strips above."""
    for u in range(u0, u1 + 1):
        for y in range(1, 9):
            f.set(u, y, TAN)
        if (u - u0) % 4 in (1, 2):
            for y in (2, 3, 6, 7):
                f.set(u, y, GLASS)
        f.set(u, 9, ORANGE); f.set(u, 9, ORANGE, out=1)
        m = (u - u0) % 3
        for fy in FLOORS[2:]:
            for dy in range(3):
                y = fy + dy + (1 if fy == 9 else 0)
                if y > TOP - 1:
                    continue
                if m == 0:
                    f.set(u, y, ORANGE)
                elif dy in (1, 2) and m == 1:
                    f.set(u, y, GLASS)
                else:
                    f.set(u, y, CREAM)
        f.set(u, TOP, ORANGE, out=1)
        f.set(u, TOP, ORANGE)


def build():
    v = Vox(W + 2, NY, L + S)
    x0, x1, z0, z1 = 1, W, 0, L - 1
    v.box(x0, x1, 1, TOP, z0, z1, CREAM)
    v.box(x0 + 1, x1 - 1, 2, TOP - 1, z0 + 1, z1 - 1, None)
    for fy in FLOORS:
        v.box(x0 + 1, x1 - 1, fy, fy, z0 + 1, z1 - 1, FLOOR)
    v.box(x0, x1, TOP, TOP, z0, z1, ROOF)
    v.box(x0, x1, 0, 0, z0, z1, FLOOR)
    faces = {s: Face(v, s, x0, x1, z0, z1) for s in ("north", "south", "east", "west")}
    for s, f in faces.items():
        facade(f, 0, f.n - 1)
    south = faces["south"]                 # u = 0 at the east end, as seen from outside
    n = south.n
    c0, c1 = n // 2 - 9, n // 2 + 8        # central section
    # white piers and blue curtain wall
    for u in range(c0, c1 + 1):
        for y in range(1, TOP + 2):
            south.set(u, y, WHITE if u - c0 < 3 or c1 - u < 3 else BLUE)
        south.set(u, TOP + 1, WHITE)
    # tan portal projecting from the atrium
    p0, p1 = c0 + 4, c1 - 4
    for u in range(p0, p1 + 1):
        for y in range(1, 12):
            edge = u - p0 < 2 or p1 - u < 2 or y >= 10
            for out in range(1, 5):
                south.set(u, y, TAN if edge else None, out=out)
        for y in range(1, 9):
            if not (u - p0 < 2 or p1 - u < 2):
                south.set(u, y, BLUE)
        south.set(u, 0, "pink_terracotta", out=5)
        for out in range(1, 5):
            south.set(u, 0, "polished_granite", out=out)
    for u in range(p0 + 2, p1 - 1):
        for out in range(1, 5):
            south.set(u, 1, None, out=out)
    # white balcony frames on each wing
    for uc in (n // 4, 3 * n // 4):
        for u in range(uc - 3, uc + 4):
            for y in range(13, 21):
                edge = u in (uc - 3, uc + 3) or y in (13, 20)
                for out in (1, 2):
                    if edge:
                        south.set(u, y, WHITE, out=out)
                if not edge:
                    south.set(u, y, "light_gray_concrete")
            south.set(u, 14, "iron_bars", out=2)
    # green sign board on posts, left of the entrance
    for u in range(c1 + 3, c1 + 9):
        for y in (3, 4):
            south.set(u, y, "green_concrete", out=6)
    for u in (c1 + 3, c1 + 8):
        for y in (1, 2):
            south.set(u, y, "dark_oak_fence", out=6)
    return v


def export():
    v = build()
    return v, v.commands(OX - 1, OY, OZ)


def extra(gy):
    cmds = []
    for x in range(OX - 2, OX + W + 2):
        for z in range(OZ + L, OZ + L + 10):
            cmds.append(f"setblock {x} {OY} {z} {'pink_terracotta' if abs(x - (OX + W // 2)) <= 12 else 'grass_block'}")
    return cmds


CHECKS = ["execute if block 772 70 1412 blue_stained_glass run say CHECK ece atrium"]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("south", 7).save(os.path.join(out, "ece_south.png"))
    v.iso("sw", 5).save(os.path.join(out, "ece_iso.png"))
    print(len(cmds), "commands")
