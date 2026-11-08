"""Chemical Engineering Department. OSM way 361838670.

Frames: JkbNik31wDE 5:08-5:16 (caption; "CHEMICAL" painted in orange and "ENGINEERING" in
dark green on the end wall). Two storeys, white and light grey, grey-framed windows, lattice
vent panels, a paved forecourt.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from extrude import Building, osm_poly

NAME = "chemical"
CLEAR = (447, 1326, 502, 1370)


def commands(gy):
    b = Building(osm_poly(361838670), storeys=2, storey_h=4, wall="white_concrete", base="light_gray_concrete",
                 roof="flat", parapet="light_gray_concrete", roof_floor="light_gray_concrete", win_every=3)
    return b.commands(gy)


CHECKS = []
