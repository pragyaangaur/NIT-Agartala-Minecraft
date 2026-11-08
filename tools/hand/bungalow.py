"""Director's Bungalow, next to the International Guest House. Microsoft footprint 404.

Frames: JkbNik31wDE 5:22-5:26 (gate-house sign DIRECTOR'S BUNGALOW, caption "Director's
House"). Two storeys, white with yellow trim bands, a taller white stair tower, blue-tinted
windows; white compound wall with yellow capping. Placement rests on the 2022-23 Annual
Report ("next to the International Guest House") and the route in the video.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, ms_poly

NAME = "bungalow"
CLEAR = (1278, 1204, 1338, 1248)


def commands(gy):
    b = Building(ms_poly(404), storeys=2, storey_h=4, wall="white_concrete", band="yellow_concrete",
                 glass="light_blue_stained_glass", roof="flat", parapet="yellow_concrete",
                 roof_floor="white_concrete", win_every=3)
    return b.commands(gy)


CHECKS = []
