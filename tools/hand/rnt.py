"""RNT Boys' Hostel and its Dining Hall.

Frames: W7D6gLvjizM 5:12 (drone over the RNT Ground, best overview), 5:14-5:26 (Dining Hall
roof and sign), JkbNik31wDE 5:44-6:22 (captions "RNT Boy's Hostel", "Top view from RNT").
Nine-storey towers in a grey frame with white infill, red roof edges and dark grey stair cores
capped in red, in two wings either side of a semicircular two-storey Dining Hall with a
rust-pink flat roof, a light grey wall with a parapet of small square openings, a projecting
entrance bay lettered DINING HALL, and open stairs at both ends. A tall slender tower stands
behind the hall.
Footprints: OSM way 1544302874 (Dining Hall); Microsoft footprints 427, 543, 128, 578, 694;
one west block digitised from the satellite (the third of three stepped blocks), and
Microsoft 500, the third slab of the east fan (fixed 7 Nov; it had the generic style).
Interiors (7 Nov): hostel rooms on every floor of every tower, the Dining Hall furnished as
a mess with food chests at the counter.
"""
import sys, os, math
import numpy as np
import interiors
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly, ms_poly, rect_poly

NAME = "rnt"
CLEAR = (770, 560, 1080, 800)


def tower(poly):
    return Building(poly, storeys=9, storey_h=3, wall="white_concrete", base="light_gray_concrete",
                    band="gray_concrete", roof="flat", parapet="red_concrete", roof_floor="pink_terracotta",
                    win_every=2)


def cores(b, n=3):
    """Dark grey stair cores rising above the roof, capped red, spaced along the long axis."""
    pts = np.array(b.poly)
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c)
    ax = vt[0]
    proj = (pts - c) @ ax
    lo, hi = proj.min(), proj.max()
    top = b.ground + b.storeys * b.storey_h + 1
    out = []
    for k in range(n):
        t = lo + (hi - lo) * (k + 1) / (n + 1)
        x, z = (c + t * ax).round().astype(int)
        out.append(f"fill {x - 2} {top} {z - 2} {x + 2} {top + 3} {z + 2} gray_concrete")
        out.append(f"fill {x - 2} {top + 4} {z - 2} {x + 2} {top + 4} {z + 2} red_concrete")
    return out


def commands(gy):
    cmds = []
    polys = [ms_poly(427), ms_poly(543), rect_poly(840, 762, 68, 15, -31), ms_poly(128), ms_poly(578), ms_poly(500)]
    for p in polys:
        b = tower(p)
        cmds += b.commands(gy) + cores(b) + interiors.furnish(b, 'hostel', seed=len(cmds))
    t = tower(ms_poly(694))
    cmds += t.commands(gy) + cores(t, 2) + interiors.furnish(t, 'hostel', seed=7)
    hall = Building(osm_poly(1544302874), storeys=2, storey_h=4, wall="light_gray_concrete",
                    glass="tinted_glass", roof="flat", parapet="light_gray_concrete",
                    roof_floor="pink_terracotta", win_every=3)
    cmds += hall.commands(gy) + interiors.furnish(hall, 'mess', storeys=[0, 1], seed=3)
    # entrance bay with the lettering, on the curved south front
    pts = np.array(hall.poly)
    cx = int(round(pts[:, 0].mean()))
    zs = pts[:, 1].max()
    g = hall.ground
    cmds.append(f"fill {cx - 4} {g + 1} {int(zs) - 2} {cx + 4} {g + 9} {int(zs) + 1} light_gray_concrete")
    cmds.append(f"fill {cx - 3} {g + 2} {int(zs) - 1} {cx + 3} {g + 8} {int(zs)} air")
    cmds.append(f"fill {cx - 2} {g + 1} {int(zs) + 1} {cx + 2} {g + 4} {int(zs) + 1} tinted_glass")
    cmds.append(f"fill {cx - 1} {g + 2} {int(zs) - 3} {cx + 1} {g + 4} {int(zs) + 1} air")
    cmds.append(f'summon text_display {cx + 0.5} {g + 5.6} {int(zs) + 2.03} {{Rotation:[0f,0f],background:0,'
                f'text:{{text:"DINING HALL",color:"#ffffff"}},transformation:{{left_rotation:[0f,0f,0f,1f],'
                f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2f,2f,2f]}}}}')
    # black water tanks on the roof
    for dx in (-18, 18):
        cmds.append(f"fill {cx + dx} {g + 10} {int(zs) - 20} {cx + dx + 1} {g + 11} {int(zs) - 19} black_concrete")
    return cmds


CHECKS = []
