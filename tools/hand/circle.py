"""Round garden in front of the Library and CSE, with its links.

Frames: W7D6gLvjizM 2:02-2:12 (from the approach road), 2:24-2:32 (drone); satellite for the
position (centre about x 862, z 1298, outer radius about 27 m, cross paths on the diagonals).
A ring road, grass quarters split by two diagonal paths, a paved centre with a round blue
basin, lamp posts along the paths, a straight link north to the Library porch and a paved
forecourt to the CSE entrance.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox

NAME = "circle"
OX, OY, OZ = 786, 73, 1225          # local y 0 = world 73 = surface
W, L, F = 116, 108, 0               # x 786..901, z 1225..1332
NY = 8
CX, CZ = 862 - OX, 1298 - OZ
CLEAR = (786, 1225, 901, 1332)
FOUNDATION = False                  # only resurface what this module draws

ROAD = "light_gray_concrete"
PATH = "smooth_stone"
KERB = "terracotta"


def lamp(v, x, z):
    v.set(x, 1, z, "stone_brick_wall")
    for y in range(2, 5):
        v.set(x, y, z, "iron_bars")
    v.set(x, 5, z, "sea_lantern")


def build():
    v = Vox(W, NY, L)
    lamps = []
    for x in range(W):
        for z in range(L):
            dx, dz = x - CX, z - CZ
            r = math.hypot(dx, dz)
            b = None
            if r <= 27:
                if r > 22.5:
                    b = ROAD
                elif r > 21.8:
                    b = KERB
                else:
                    a1 = abs(dx - dz) / math.sqrt(2)          # distance from each diagonal
                    a2 = abs(dx + dz) / math.sqrt(2)
                    diamond = abs(dx) + abs(dz) <= 8
                    if r <= 3:
                        b = "water"
                    elif r <= 3.8:
                        b = "light_blue_terracotta"
                    elif diamond or a1 <= 1.6 or a2 <= 1.6:
                        b = PATH
                    else:
                        b = "grass_block"
            # link north to the Library porch (centre x 871)
            elif 1229 <= OZ + z <= 1272 and 868 <= OX + x <= 874:
                b = ROAD
            # CSE forecourt and its link to the ring
            elif 1258 <= OZ + z <= 1267 and 786 <= OX + x <= 840:
                b = "polished_andesite" if (OX + x) % 4 else PATH
            elif 1262 <= OZ + z <= 1282 and abs((OX + x - 835) - (OZ + z - 1262)) <= 3 and OX + x >= 835:
                b = ROAD
            # approach road to the south-east, with a planted median
            elif OZ + z >= 1316:
                t = (OX + x - 878) - (OZ + z - 1316) * 0.6
                if abs(t) <= 7:
                    b = "grass_block" if abs(t) <= 1.2 else ROAD
                    if abs(t) <= 0.6 and (OZ + z) % 9 == 0:
                        lamps.append((x, z))
            if b is not None:
                v.set(x, 0, z, b)
    for k in range(4):                                  # lamps along the cross paths
        for s in (-14, -9, 9, 14):
            a = math.radians(45 + 90 * k)
            x = int(round(CX + s * math.cos(a) * 0.7071 + 2.2 * math.cos(a + math.pi / 2)))
            z = int(round(CZ + s * math.sin(a) * 0.7071 + 2.2 * math.sin(a + math.pi / 2)))
            if v.get(x, 0, z) == "grass_block":
                lamps.append((x, z))
    for (x, z) in lamps:
        lamp(v, x, z)
    for z in range(1229 - OZ, 1272 - OZ, 8):            # lamps beside the Library link
        lamp(v, 867 - OX, z); lamp(v, 875 - OX, z)
    return v


def export():
    v = build()
    return v, v.commands(OX, OY, OZ)


def extra(gy):
    """Bring the ground under every drawn cell to the garden level, clear above it."""
    v = build()
    cmds = []
    nx, ny, nz = v.shape
    for x in range(nx):
        for z in range(nz):
            if v.a[x, 0, z] is None:
                continue
            wx, wz = OX + x, OZ + z
            g = gy(wx, wz)
            if 806 <= wx <= 814 and 1259 <= wz <= 1261:
                continue                                  # CSE sign block
            near_cse = wx <= 840 and wz <= 1261
            top = OY + 3 if near_cse else max(g, OY) + 16      # high enough to remove old trees
            cmds.append(f"fill {wx} {OY + 1} {wz} {wx} {top} {wz} air")
            if g < OY:
                cmds.append(f"fill {wx} {g} {wz} {wx} {OY - 1} {wz} dirt")
    return cmds


CHECKS = ["execute if block 862 73 1298 water run say CHECK circle basin"]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.iso("ne", 4).save(os.path.join(out, "circle_iso.png"))
    print(len(cmds), "commands")
