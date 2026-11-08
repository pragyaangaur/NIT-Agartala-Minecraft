"""The domed round building north-west of the SAC Building (name not readable in any frame).

Frames: W7D6gLvjizM 0:20, 0:24-0:46; SqZLoYQonbc 2:36-2:48 (inventory U1). A cylinder of
about three storeys, pale teal below and white above with continuous window rings, a flat dark
roof with a raised parapet ring and a big teal faceted dome in the middle. Microsoft footprint 9.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from extrude import clear_poly, ms_poly

NAME = "dome"
CLEAR = (486, 1186, 522, 1220)


def commands(gy):
    cmds = clear_poly(ms_poly(9), gy, margin=0)
    cx, cz, R = 503, 1200, 11
    g = int(sorted(gy(cx + dx, cz + dz) for dx in (-8, 0, 8) for dz in (-8, 0, 8))[4])
    for x in range(cx - R - 1, cx + R + 2):
        for z in range(cz - R - 1, cz + R + 2):
            r = math.hypot(x - cx, z - cz)
            if r > R + 0.5:
                continue
            cmds.append(f"fill {x} {g - 5} {z} {x} {g} {z} stone")
            cmds.append(f"fill {x} {g + 1} {z} {x} {g + 25} {z} air")
            if r > R - 0.6:
                for y in range(1, 13):
                    blk = "light_blue_terracotta" if y <= 6 else "white_concrete"
                    if y % 4 in (2, 3):
                        blk = "tinted_glass"
                    cmds.append(f"setblock {x} {g + y} {z} {blk}")
                cmds.append(f"setblock {x} {g + 13} {z} gray_concrete")
                cmds.append(f"setblock {x} {g + 14} {z} white_concrete")
            else:
                for y in (1, 5, 9):
                    cmds.append(f"setblock {x} {g + y} {z} smooth_stone")
                cmds.append(f"setblock {x} {g + 13} {z} gray_concrete")
            d = r
            if d <= 6.5:
                h = int(round(math.sqrt(max(6.5 ** 2 - d * d, 0)) * 0.9))
                cmds.append(f"fill {x} {g + 14} {z} {x} {g + 14 + h} {z} prismarine")
    return cmds


CHECKS = []
