"""Aryabhatta Hostel: the oval ring of red-roofed wings round a central garden.

Footprints: OSM ways 361838531 (named Arybhatta Hostel), 361838528, 361838529, 361838530,
1544302875, 361838499, and Microsoft footprint 394 for the south pair OSM lacks. All sit on
one oval ring road. Satellite: hipped red-brown tile roofs. Commons photos
(NIT_AGARTALA_ARYABHATTA_HOSTEL_VIEW_FROM_OUT, Hostel_Aryabhatta): white three-storey
wings with even window rows, a paved courtyard with a circular path and lamp posts.
"""
import sys, os
import interiors
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly, ms_poly

NAME = "aryabhatta"
CLEAR = (420, 735, 690, 925)
WAYS = [361838531, 361838528, 361838529, 361838530, 1544302875, 361838499]


def buildings():
    out = []
    for w in WAYS:
        out.append(Building(osm_poly(w), storeys=3, storey_h=4, wall="smooth_quartz", base="white_concrete",
                            roof="hip", roof_mat="bricks", slope=0.55, win_every=4))
    out.append(Building(ms_poly(394), storeys=3, storey_h=4, wall="smooth_quartz", base="white_concrete",
                        roof="hip", roof_mat="bricks", slope=0.55, win_every=4))
    return out


def commands(gy):
    cmds = []
    bs = buildings()
    for n, b in enumerate(bs):
        cmds += b.commands(gy)
        if n == len(bs) - 1:
            # Aryabhatta Mess (two messes, ground and first floor, per the anti-ragging roster).
            # Which block holds it is not known; the south block by the entrance is a guess.
            cmds += interiors.furnish(b, "mess", storeys=[0, 1], seed=n)
            cmds += interiors.furnish(b, "hostel", storeys=[2], seed=n)
        else:
            cmds += interiors.furnish(b, "hostel", seed=n)
    return cmds


CHECKS = ["execute if block 520 74 790 air run say CHECK arya probe"]
