"""Gate No. 2 (Ranir Bazar / Sankar Bazar) on the west edge and Gate No. 3 on the north-east.

Gate 2: official campus map (UG reporting guide 2024, Fig. 6) puts it at the west edge where
the campus road meets the village road; satellite junction at about x 182, z 1100. Look from
JkbNik31wDE 8:04-8:08 (the rear gate at the end of the conifer avenue): a white single-storey
guard room, two tall slender pillars with red caps, a black bar gate.
Gate 3: named in the 50th BWC minutes ("road from Rotary (near H4 qtr.) to gate no-3 and to
Market Complex"). No photo; placed where the market road leaves the campus outline (about
x 1478, z 336), in the same style as Gate 2. Its position is an inference.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

NAME = "smallgates"
CLEAR = (170, 1085, 1495, 1350)        # forceload covers both ends via GATES below
GATES = [  # (centre x, centre z, axis, half span, ground)
    (184, 1101, "z", 8, 75),
    (1478, 336, "x", 7, 72),
]


def gate(cx, cz, axis, half, g):
    cmds = []
    def P(u, y, w, blk):          # u along the span, w across the road
        x, z = (cx + w, cz + u) if axis == "z" else (cx + u, cz + w)
        cmds.append(f"setblock {x} {g + y} {z} {blk}")
    for u in range(-half - 6, half + 7):
        for w in range(-2, 3):
            for y in range(1, 9):
                P(u, y, w, "air")
    for s in (-1, 1):
        p = s * half
        for y in range(1, 8):                       # tall slender pillar
            P(p, y, 0, "white_concrete")
        P(p, 8, 0, "red_concrete"); P(p, 9, 0, "red_concrete_powder" if False else "red_terracotta")
        for u in range(1, half):                    # bar gate leaves, left part-open
            if s == 1 or u > 3:
                P(s * u, 1, 0, "iron_bars"); P(s * u, 2, 0, "iron_bars")
    # guard room on one side
    for u in range(half + 1, half + 6):
        for w in range(-2, 3):
            for y in range(1, 4):
                edge = u in (half + 1, half + 5) or w in (-2, 2)
                P(u, y, w, "white_concrete" if edge else "air")
            P(u, 4, w, "light_blue_terracotta")
        P(half + 3, 2, -2, "glass_pane"); P(half + 3, 2, 2, "glass_pane")
    P(half + 1, 1, 0, "air"); P(half + 1, 2, 0, "air")
    for u in range(-half - 6, -half):              # boundary wall on the far side
        P(u, 1, 0, "white_concrete"); P(u, 2, 0, "white_concrete")
    return cmds


def commands(gy):
    cmds = []
    for (cx, cz, axis, half, g) in GATES:
        cmds += gate(cx, cz, axis, half, g)
    return cmds


CHECKS = []
