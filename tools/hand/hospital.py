"""NITA Hospital (Health Centre). OSM way 361838501.

Frames: JkbNik31wDE 3:52-3:54 (caption "NITA Hospital"). Low, white, green awnings over the
windows, a blue fascia board, fenced with green and white railings.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly

NAME = "hospital"
CLEAR = (880, 1046, 921, 1094)


def commands(gy):
    b = Building(osm_poly(361838501), storeys=2, storey_h=4, wall="white_concrete", band="green_terracotta",
                 roof="flat", parapet="blue_terracotta", roof_floor="light_gray_concrete", win_every=3)
    return b.commands(gy)


CHECKS = []
