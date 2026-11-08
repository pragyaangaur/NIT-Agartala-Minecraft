"""Mechanical Engineering Department and the workshop sheds. OSM multipolygon 5385967
(outer 361838658, the way tagged "NIT Agartala"; courtyard 361838473).

Frames: JkbNik31wDE 5:00-5:06 (caption "Mechanical Engineering Department": two storeys, white
and grey, concrete jali screens on the upper floor, a heavy rust-maroon square porch frame);
W7D6gLvjizM 0:20, 0:40, 0:50 (inventory U4: rows of dark sawtooth north-light roofs, some
with solar panels). Built as a two-storey block round a courtyard with sawtooth roofs.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, rel_polys, clear_poly

NAME = "mechanical"
CLEAR = (455, 1258, 575, 1356)


def commands(gy):
    outer, inner = rel_polys(5385967)
    b = Building(outer[0], holes=inner, storeys=2, storey_h=5, wall="smooth_quartz", base="light_gray_concrete",
                 band="gray_concrete", roof="flat", parapet="smooth_quartz", roof_floor="gray_concrete", win_every=2)
    cmds = clear_poly(inner[0], gy, margin=0) + b.commands(gy)
    x0, g, z0 = b.origin
    top = g + 11
    m = b.mask
    for i, k in zip(*np.nonzero(m)):
        X, Z = x0 + i, z0 + k
        ph = X % 7
        if ph == 6:
            cmds.append(f"fill {X} {top} {Z} {X} {top + 3} {Z} light_gray_stained_glass")
        else:
            h = int(ph * 0.55)
            blk = "daylight_detector" if (Z % 11 < 4 and ph in (2, 3, 4)) else "polished_deepslate"
            cmds.append(f"setblock {X} {top + h} {Z} {blk}")
    return cmds


CHECKS = []
