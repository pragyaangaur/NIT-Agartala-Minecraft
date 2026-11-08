"""Gargi Girls' Hostel complex.

No video frame is captioned Gargi. The likely match is the white hilltop cluster with red
hipped roofs at W7D6gLvjizM 5:00-5:10 (inventory U10), and the satellite shows red-brown
hipped roofs on the same footprints. OSM way 361838532 (named) plus the four blocks round it
(361838476, 361838507, 361838509, 361838517). Four storeys (the OSM tag of 15 levels was
rejected earlier on capacity grounds). The solar-panelled hall inside the main outline gets
the same roof, which is a known simplification.
"""
import sys, os
import interiors
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly

NAME = "gargi"
CLEAR = (1160, 755, 1380, 890)
WAYS = [361838532, 361838476, 361838507, 361838509, 361838517]


def commands(gy):
    cmds = []
    for w in WAYS:
        b = Building(osm_poly(w), storeys=4, storey_h=4, wall="smooth_quartz", base="white_concrete",
                     roof="hip", roof_mat="bricks", slope=0.55, win_every=4)
        cmds += b.commands(gy) + interiors.furnish(b, "hostel", seed=w % 97)
    return cmds


CHECKS = []
