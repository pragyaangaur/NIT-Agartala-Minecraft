"""Food court on the old-campus road between Knowledge Park and the Visvesvaraya Auditorium.
OSM way 361838671.

Frames: JkbNik31wDE 3:02-3:08 (caption "food court"). About four storeys, tan or mustard walls
with deep vertical fins and white window infill, a long mustard-yellow canopy band over the
ground floor and a light blue signboard.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly

NAME = "foodcourt"
CLEAR = (622, 1162, 690, 1206)


def commands(gy):
    b = Building(osm_poly(361838671), storeys=4, storey_h=4, wall="smooth_sandstone", base="yellow_terracotta",
                 band="yellow_terracotta", glass="tinted_glass", roof="flat", parapet="smooth_sandstone",
                 roof_floor="light_gray_concrete", win_every=2)
    return b.commands(gy)


CHECKS = []
