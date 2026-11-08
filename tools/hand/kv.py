"""Kendriya Vidyalaya (central school on campus).

Frames: JkbNik31wDE 7:22-7:28 (sign KENDRIYA VIDYALAYA ... AGARTALA TRIPURA, caption). Three
storeys, white frame with horizontal orange-yellow and light blue bands, a covered bridge
linking two wings, a gate with blue pillars and globe lamps and yellow bar gates.
Footprint: Microsoft 574, the large flat-roofed building south-west of Aryabhatta. The match
rests on the route in the video (Aryabhatta, then the school, then the avenue to the rear
gate) and on the style, not on a sign seen from the air.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, ms_poly

NAME = "kv"
CLEAR = (298, 908, 404, 1040)


def commands(gy):
    bands = {}
    for fy in (1, 5, 9):
        bands[fy + 3] = "light_blue_concrete"
    bands[6] = "orange_concrete"; bands[7] = "orange_concrete"
    b = Building(ms_poly(574), storeys=3, storey_h=4, wall="white_concrete", roof="flat",
                 parapet="white_concrete", roof_floor="light_gray_concrete", win_every=3, bands=bands)
    return b.commands(gy)


CHECKS = []
