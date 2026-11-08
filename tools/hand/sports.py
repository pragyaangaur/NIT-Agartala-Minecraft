"""Bharat Ratna Atal Bihari Vajpayee (ABV) Sports Complex.

Frames: SqZLoYQonbc 2:04 (entrance sign), 1:30, 1:50; W7D6gLvjizM 5:36-5:52 (drone, best 5:42),
6:28-7:12 (courtyard and interior). A long grey stone-tiled entrance building with curved
ends and a tall central portal; behind it two long halls with red low-curved roofs (the
left one with a dark glazed strip along the roof) and a round arena with a red conical roof,
a blue radial skylight and a ring of dark glazing.
Footprints: Microsoft 352 (left hall), 598 (middle hall), 599 (entrance building); the arena
is a circle measured from the satellite (centre about x 1212, z 330, radius about 29 m).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, ms_poly, clear_poly, clear_box, rect_poly

NAME = "sports"
CLEAR = (1028, 248, 1252, 387)
STONE = "light_gray_concrete"


def commands(gy):
    cmds = clear_box(1030, 250, 1250, 385, gy)
    a = Building(rect_poly(1069, 307, 80, 46, 90), storeys=1, storey_h=12, wall=STONE, roof="hip", roof_mat="red_concrete",
                 slope=0.3, ridge="black_stained_glass", win_every=3)
    cmds += a.commands(gy)
    b = Building(ms_poly(598), storeys=1, storey_h=12, wall=STONE, roof="hip", roof_mat="red_concrete",
                 slope=0.3, win_every=3, ground=a.ground)
    cmds += b.commands(gy)
    c = Building(ms_poly(599), storeys=2, storey_h=4, wall=STONE, base="polished_andesite", roof="flat",
                 parapet=STONE, roof_floor="light_gray_concrete", win_every=4, ground=a.ground)
    cmds += c.commands(gy, clear_margin=1)
    g = a.ground
    # arena
    cx, cz, R = 1212, 330, 29
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            r = math.hypot(x - cx, z - cz)
            if r > R + 1.5:
                continue
            cmds.append(f"fill {x} {g + 1} {z} {x} {g + 40} {z} air")
            cmds.append(f"fill {x} {g - 4} {z} {x} {g} {z} stone")
            if r > R + 0.5:
                cmds.append(f"setblock {x} {g} {z} {STONE}")
                continue
            h = 13 + int(round((R + 1 - r) * 0.33))
            if r > R - 1:
                for y in range(1, h):
                    blk = "tinted_glass" if 8 <= y <= 10 or (y in (3, 4) and (x + z) % 4 == 0) else STONE
                    cmds.append(f"setblock {x} {g + y} {z} {blk}")
            elif r < 20 and r > 8:
                step = int((r - 8) / 3)                    # tiered seating
                cmds.append(f"fill {x} {g + 1} {z} {x} {g + 1 + step} {z} smooth_stone")
            h = 13 + int(round((R + 1 - r) * 0.33))
            roof = 'light_blue_stained_glass' if r <= 6 else 'red_concrete'
            # two blocks thick, so each step of the cone meets the next ring on a face
            # (a one-block skin touches only at edges and reads as floating)
            cmds.append(f"fill {x} {g + h - 1} {z} {x} {g + h} {z} {roof}")
    # trees round the complex, on open ground clear of the buildings, the arena and the forecourt
    import numpy as np
    from extrude import mask_of
    from scipy.ndimage import binary_dilation
    bx0, bz0 = 1030, 250
    occ = np.zeros((221, 136), bool)
    for poly in (a.poly, b.poly, c.poly):
        occ |= mask_of(poly, bx0, bz0, 221, 136)
    occ = binary_dilation(occ, iterations=6)
    for x in range(1036, 1248, 8):
        for z in range(254, 384, 8):
            if occ[x - bx0, z - bz0] or math.hypot(x - cx, z - cz) < R + 7 or (1100 <= x <= 1165 and z >= 345):
                continue
            t = gy(x, z)
            cmds.append(f"place feature minecraft:{'oak' if (x + z) % 3 else 'birch'} {x} {t + 1} {z}")
    # entrance sign
    cmds.append(f'summon text_display 1131.5 {g + 9.2} 364.1 {{Rotation:[0f,0f],background:0,'
                f'text:{{text:"BHARAT RATNA ATAL BIHARI VAJPAYEE (ABV) SPORTS COMPLEX",color:"#ffffff"}},'
                f'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],'
                f'scale:[1.2f,1.2f,1.2f]}}}}')
    return cmds


CHECKS = []
