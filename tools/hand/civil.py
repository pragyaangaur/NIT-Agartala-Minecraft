"""Civil Engineering Department. OSM way 1544302855.

Frames: JkbNik31wDE 3:16-3:22 (sign CIVIL ENGINEERING DEPARTMENT, caption); Commons photo
Civil_Building_NIT_Agartala.png. Four storeys, white with grey; a slab with deep square
window bays; a curved glazed corner tower with ribbon windows and a round rooftop rail beside
the entrance; a long white fascia with the name over a full-height glass entrance; a
semicircular drive round an oval clipped-hedge island in front (south).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly

NAME = "civil"
CLEAR = (570, 975, 700, 1075)


def commands(gy):
    b = Building(osm_poly(1544302855), storeys=4, storey_h=4, wall="smooth_quartz", band="light_gray_concrete",
                 glass="tinted_glass", roof="flat", parapet="smooth_quartz", roof_floor="light_gray_concrete",
                 win_every=3)
    cmds = b.commands(gy)
    g = b.ground
    # curved glazed tower east of the entrance
    tx, tz, R = 664, 1036, 5.5
    for x in range(tx - 6, tx + 7):
        for z in range(tz - 6, tz + 7):
            r = math.hypot(x - tx, z - tz)
            if r <= R:
                edge = r > R - 1.1
                for y in range(1, 19):
                    blk = ("light_blue_stained_glass" if (y % 4) else "smooth_quartz") if edge else ("smooth_stone" if y % 4 == 1 else "air")
                    cmds.append(f"setblock {x} {g + y} {z} {blk}")
                cmds.append(f"setblock {x} {g + 19} {z} {'iron_bars' if edge else 'smooth_quartz'}")
    # entrance: white fascia with the name, glass below, facing south
    ex, ez = 642, 1046
    cmds.append(f"fill {ex - 9} {g + 1} {ez + 1} {ex + 9} {g + 7} {ez + 3} air")
    cmds.append(f"fill {ex - 9} {g + 1} {ez} {ex + 9} {g + 5} {ez} light_gray_stained_glass")
    cmds.append(f"fill {ex - 10} {g + 6} {ez} {ex + 10} {g + 7} {ez + 3} smooth_quartz")
    cmds.append(f"fill {ex + 10} {g + 1} {ez + 1} {ex + 10} {g + 5} {ez + 3} smooth_quartz")
    cmds.append(f'summon text_display {ex + 0.5} {g + 6.25} {ez + 4.03} {{Rotation:[0f,0f],background:0,'
                f'text:{{text:"CIVIL ENGINEERING DEPARTMENT",color:"#1d3a7a"}},transformation:{{left_rotation:[0f,0f,0f,1f],'
                f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.5f,1.5f,1.5f]}}}}')
    # oval hedge island in the semicircular drive
    cx, cz = 652, 1058
    for x in range(cx - 13, cx + 14):
        for z in range(cz - 8, cz + 9):
            e = ((x - cx) / 13) ** 2 + ((z - cz) / 8) ** 2
            if e <= 1:
                cmds.append(f"fill {x} {g + 1} {z} {x} {g + 6} {z} air")
                t = ((x - cx) / 6) ** 2 + ((z - cz) / 3) ** 2
                if t <= 1:
                    cmds.append(f"setblock {x} {g} {z} grass_block")
                    if t > 0.55:
                        cmds.append(f"setblock {x} {g + 1} {z} oak_leaves[persistent=true]")
                else:
                    cmds.append(f"setblock {x} {g} {z} light_gray_concrete")
    return cmds


CHECKS = []
