"""Guest House (the institute guest house by the lake). OSM way 1544302876.

Frames: W7D6gLvjizM 2:34-3:26 (drone; 2:42 front, 3:10 back terraces), JkbNik31wDE 5:30-5:32
(caption "Guest House"). Two four-storey white wings set at a slight V with open balcony
corridors banded in red, low bright red hipped roofs, a five-storey central tower with a red
pyramid roof, a red pyramid porch canopy, and a red-paved loop drive round a round lawn.
The lake lies behind it to the north-west.
The OSM outline includes shadow, so the wings are redrawn from the satellite.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, rect_poly, osm_poly, clear_poly

NAME = "guesthouse"
CLEAR = (1165, 1165, 1275, 1250)


def commands(gy):
    cmds = clear_poly(osm_poly(1544302876), gy)
    wing = dict(storeys=4, storey_h=4, wall="smooth_quartz", band="red_concrete", roof="hip",
                roof_mat="red_concrete", slope=0.35, win_every=2)
    a = Building(rect_poly(1197, 1222, 42, 13, -37), **wing)
    b = Building(rect_poly(1240, 1197, 46, 13, -27), **wing)
    cmds += a.commands(gy)
    b.ground = a.ground
    cmds += b.commands(gy)
    t = Building(rect_poly(1218, 1212, 12, 12, -32), storeys=5, storey_h=4, wall="smooth_quartz",
                 roof="hip", roof_mat="red_concrete", slope=0.7, win_every=2, ground=a.ground)
    cmds += t.commands(gy, clear_margin=0)
    p = Building(rect_poly(1223, 1221, 8, 7, -32), storeys=1, storey_h=4, wall="smooth_quartz",
                 glass="smooth_quartz", roof="hip", roof_mat="red_concrete", slope=0.6, ground=a.ground)
    cmds += p.commands(gy, clear_margin=0)
    # loop drive and lawn
    g = a.ground
    cx, cz = 1233, 1232
    for x in range(cx - 11, cx + 12):
        for z in range(cz - 11, cz + 12):
            r = ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5
            if r <= 10.5:
                cmds.append(f"fill {x} {g + 1} {z} {x} {g + 8} {z} air")
                cmds.append(f"setblock {x} {g} {z} {'grass_block' if r <= 4.5 else 'red_terracotta' if r > 5 else 'stone_bricks'}")
    return cmds


CHECKS = []
