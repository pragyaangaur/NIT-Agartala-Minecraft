"""Science Block. OSM multipolygon 5385969 (outer 361838466, courtyard 361838468).

Frames: W7D6gLvjizM 0:36-0:46 (drone, the big grey courtyard block south of the domed round
building). Five storeys of rooms in a ring round an open light-well courtyard, white walls
with a grid of windows, a weathered dark grey roof. Rebuilt on 7 Nov as one clean ring: the
whole site is cleared first, the courtyard is open to the sky with a lawn and a path.
"""
import sys, os
import interiors
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, rect_poly, clear_box

NAME = "science"
CLEAR = (420, 1218, 492, 1290)
OUT = (430, 1222, 481, 1261)          # outer walls (inclusive), stops short of Mechanical
HOLE = (445, 1235, 467, 1248)         # courtyard


def commands(gy):
    x0, z0, x1, z1 = OUT
    h0, k0, h1, k1 = HOLE
    outer = [(x0, z0), (x1 + 1, z0), (x1 + 1, z1 + 1), (x0, z1 + 1)]
    hole = [(h0, k0), (h1 + 1, k0), (h1 + 1, k1 + 1), (h0, k1 + 1)]
    cmds = clear_box(x0 - 4, z0 - 4, x1 + 4, z1 + 2, gy, height=50)
    b = Building(outer, holes=[hole], storeys=5, storey_h=4, wall="smooth_quartz", band="light_gray_concrete",
                 roof="flat", parapet="light_gray_concrete", roof_floor="gray_concrete", win_every=2)
    cmds += b.commands(gy, clear_margin=0) + interiors.furnish(b, 'lab', seed=5)
    g = b.ground
    for x in range(h0 + 1, h1):                      # courtyard lawn with a cross path and a tree
        for z in range(k0 + 1, k1):
            cmds.append(f"fill {x} {g + 1} {z} {x} {g + 24} {z} air")
            path = x == (h0 + h1) // 2 or z == (k0 + k1) // 2
            cmds.append(f"setblock {x} {g} {z} {'polished_andesite' if path else 'grass_block'}")
    cx, cz = (h0 + h1) // 2 + 4, (k0 + k1) // 2 + 4
    cmds.append(f"fill {cx} {g + 1} {cz} {cx} {g + 5} {cz} oak_log")
    cmds.append(f"fill {cx - 2} {g + 5} {cz - 2} {cx + 2} {g + 7} {cz + 2} oak_leaves[persistent=true] replace air")
    for (x, z) in ((h0 + 1, (k0 + k1) // 2), (h1 - 1, (k0 + k1) // 2), ((h0 + h1) // 2, k0 + 1), ((h0 + h1) // 2, k1 - 1)):
        cmds.append(f"fill {x} {g + 1} {z} {x} {g + 2} {z} air")      # doors from the courtyard
    return cmds


CHECKS = []
