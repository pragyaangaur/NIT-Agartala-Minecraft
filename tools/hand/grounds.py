"""Playing grounds: the RNT Ground and the stadium west of the ABV Sports Complex.

RNT Ground (caption JkbNik31wDE 4:20; W7D6gLvjizM 5:12): an open field south of the RNT
hostel with a cricket pitch, football goals and floodlight poles, a spectator stand on the
west side (light blue base, red stepped seating, flat dark roof on thin columns) and a
basketball court in the north-east corner (satellite).
Stadium (satellite; "football and cricket stadium" in the 2022-23 Annual Report): an oval
field with a running track round it, a cricket square and floodlights.
"""
import sys, os, math
import numpy as np
from matplotlib.path import Path
sys.path.insert(0, os.path.dirname(__file__))

NAME = "grounds"
BOXES = [(925, 220, 1040, 350), (930, 800, 1062, 935)]

RNT_POLY = [(946, 814), (1032, 810), (1048, 850), (1003, 928), (952, 914)]


def field(cmds, gy, inside, x0, z0, x1, z1, surf):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if inside(x, z):
                t = gy(x, z)
                cmds.append(f"fill {x} {t + 1} {z} {x} {t + 16} {z} air")
                cmds.append(f"setblock {x} {t} {z} {surf(x, z)}")


def pitch(cmds, gy, cx, cz, along="z"):
    for d in range(-11, 12):
        for w in (-1, 0, 1):
            x, z = (cx + w, cz + d) if along == "z" else (cx + d, cz + w)
            b = "white_concrete" if abs(d) == 9 else "smooth_sandstone"
            cmds.append(f"setblock {x} {gy(x, z)} {z} {b}")
    for d in (-10, 10):                      # stumps
        for w in (-1, 0, 1):
            x, z = (cx + w, cz + d) if along == "z" else (cx + d, cz + w)
            cmds.append(f"setblock {x} {gy(x, z) + 1} {z} birch_fence")


def goal(cmds, gy, cx, cz, along="x"):
    """Goal mouth 7 wide, 3 high, facing along the other axis."""
    g = gy(cx, cz)
    for w in range(-3, 4):
        x, z = (cx + w, cz) if along == "x" else (cx, cz + w)
        cmds.append(f"setblock {x} {g + 3} {z} white_concrete")
        if abs(w) == 3:
            cmds.append(f"fill {x} {g + 1} {z} {x} {g + 2} {z} white_concrete")
        else:
            pass


def flood(cmds, gy, x, z, face):
    g = gy(x, z)
    cmds.append(f"fill {x} {g + 1} {z} {x} {g + 18} {z} andesite_wall")
    dx, dz = face
    for s in (-1, 0, 1):
        px, pz = (x + s, z) if dz else (x, z + s)
        cmds.append(f"setblock {px + dx} {g + 19} {pz + dz} sea_lantern")
        cmds.append(f"setblock {px} {g + 19} {pz} iron_block")
    cmds.append(f"setblock {x} {g + 20} {z} iron_block")


def commands(gy):
    cmds = []
    rp = Path(RNT_POLY)
    field(cmds, gy, lambda x, z: rp.contains_point((x + 0.5, z + 0.5)), 940, 805, 1052, 932,
          lambda x, z: "grass_block" if (x // 4 + z // 4) % 2 else "moss_block")
    pitch(cmds, gy, 995, 866, "z")
    goal(cmds, gy, 990, 816, "x"); goal(cmds, gy, 992, 905, "x")
    for (x, z, f) in ((950, 818, (1, 0)), (1030, 815, (-1, 0)), (958, 910, (1, 0)), (1012, 920, (-1, 0))):
        flood(cmds, gy, x, z, f)
    # stand on the west side, facing east
    g = gy(953, 852)
    for z in range(836, 869):
        cmds.append(f"fill 949 {g + 1} {z} 958 {g + 12} {z} air")
        cmds.append(f"fill 949 {g} {z} 958 {g} {z} smooth_stone")
        for t in range(6):                                   # stepped red seating
            x = 956 - t
            cmds.append(f"fill {x} {g + 1} {z} {x} {g + 1 + t} {z} light_blue_concrete")
            cmds.append(f"setblock {x} {g + 2 + t} {z} red_terracotta")
        cmds.append(f"fill 949 {g + 1} {z} 950 {g + 8} {z} light_blue_concrete")
        cmds.append(f"fill 949 {g + 11} {z} 958 {g + 11} {z} gray_concrete")
        if z % 6 == 0:
            cmds.append(f"fill 958 {g + 1} {z} 958 {g + 10} {z} iron_bars")
        cmds.append(f"setblock 953 {g + 10} {z} light[level=12]")
    # basketball court in the north-east corner
    g = gy(1046, 826)
    for x in range(1036, 1058):
        for z in range(816, 838):
            line = x in (1036, 1057) or z in (816, 837) or z == 826
            cmds.append(f"fill {x} {gy(x, z) + 1} {z} {x} {gy(x, z) + 10} {z} air")
            cmds.append(f"setblock {x} {g} {z} {'white_concrete' if line else 'orange_terracotta'}")
    for z in (818, 835):
        cmds.append(f"fill 1047 {g + 1} {z} 1047 {g + 4} {z} andesite_wall")
        d = 1 if z == 818 else -1
        cmds.append(f"setblock 1047 {g + 4} {z + d} white_concrete")
        cmds.append(f"setblock 1047 {g + 3} {z + 2 * d} iron_bars")
    # stadium oval with track
    cx, cz, ax, az = 984, 287, 42, 52
    def ins(x, z):
        return ((x + 0.5 - cx) / ax) ** 2 + ((z + 0.5 - cz) / az) ** 2 <= 1
    def surf(x, z):
        e = ((x + 0.5 - cx) / ax) ** 2 + ((z + 0.5 - cz) / az) ** 2
        if e > 0.80:
            return "white_concrete" if abs(e - 0.90) < 0.012 else "terracotta"
        return "grass_block" if (z // 5) % 2 else "moss_block"
    field(cmds, gy, ins, cx - ax, cz - az, cx + ax, cz + az, surf)
    pitch(cmds, gy, cx, cz, "z")
    goal(cmds, gy, cx, cz - 40, "x"); goal(cmds, gy, cx, cz + 40, "x")
    for (x, z, f) in ((cx - 38, cz - 30, (1, 0)), (cx + 38, cz - 30, (-1, 0)), (cx - 38, cz + 30, (1, 0)), (cx + 38, cz + 30, (-1, 0))):
        flood(cmds, gy, x, z, f)
    return cmds


CHECKS = []
