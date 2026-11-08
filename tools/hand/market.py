"""Market Complex, officially the Maharaja Bir Bikram Amenity Centre (map label 16, far
north-east; G+1 per the 2019-20 Annual Report). OSM way 1544302877 "Shopping Complex".

No video frame. Satellite: a ring of red-roofed blocks round a round central court with a
small round centre piece, centre about x 1555, z 302, outer radius about 26 m. Built as eight
two-storey wedge blocks with gaps between them and red hipped roofs.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly, clear_poly

NAME = "market"
CLEAR = (1520, 265, 1590, 340)
CX, CZ = 1555, 302


def wedge(a0, a1, r0, r1, n=6):
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((CX + r1 * math.cos(a), CZ + r1 * math.sin(a)))
    for k in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((CX + r0 * math.cos(a), CZ + r0 * math.sin(a)))
    return pts


def commands(gy):
    cmds = clear_poly(osm_poly(1544302877), gy, margin=2)
    g = None
    for k in range(8):
        a0 = k * 45 + 5
        b = Building(wedge(a0, a0 + 36, 13, 26), storeys=2, storey_h=4, wall="white_concrete",
                     base="light_gray_concrete", roof="hip", roof_mat="red_terracotta", slope=0.6, win_every=2,
                     ground=g)
        cmds += b.commands(gy, clear_margin=1)
        g = b.ground
    for x in range(CX - 13, CX + 14):
        for z in range(CZ - 13, CZ + 14):
            r = math.hypot(x - CX, z - CZ)
            if r <= 12.5:
                cmds.append(f"setblock {x} {g} {z} {'smooth_stone' if r > 3.5 else 'stone_bricks'}")
                if r <= 3:
                    cmds.append(f"setblock {x} {g + 1} {z} {'white_concrete' if r > 2 else 'grass_block'}")
    return cmds


CHECKS = []
