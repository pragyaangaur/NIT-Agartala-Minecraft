"""Fountain plaza between Academic Block 1 and 2.

Frames: W7D6gLvjizM 0:16, 1:12, 1:16, 1:18-1:22 (fountain close-up).
Pink paving on a five-metre grid of light lines, a sunken round court of darker red paving
with dark stone steps, a pale blue basin with a statue on a dark plinth, four planters,
benches, big shade trees, and a curved terrace step up to Academic Block 2.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox
from style import PAVE, PAVE_LINE

NAME = "plaza"
OX, OY, OZ = 544, 71, 1195       # local y 0 = world 71 (AB1 forecourt level)
W, L, F = 57, 60, 0              # x 544..600, z 1195..1254
NY = 14
CX, CZ = 571 - OX, 1233 - OZ     # fountain centre (local)
PL = 2                           # plaza surface layer (world 73)
TER = 4                          # terrace surface layer (world 75, AB2 ground)
CLEAR = (544, 1195, 600, 1254)

DARK = "polished_deepslate"
DARK_ST = "polished_deepslate_stairs"


def tree(v, x, y, z, h=7, r=4):
    for k in range(h):
        v.set(x, y + k, z, "oak_log")
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dy in range(-2, 2):
                d = dx * dx + dz * dz + (dy * 1.6) ** 2
                if d <= r * r and v.get(x + dx, y + h + dy, z + dz) is None:
                    v.set(x + dx, y + h + dy, z + dz, "oak_leaves[persistent=true]")


def build():
    v = Vox(W, NY, L)
    for x in range(W):
        for z in range(L):
            wx, wz = OX + x, OZ + z
            dx, dz = x - CX, z - CZ
            r = math.hypot(dx, dz)
            v.box(x, x, 0, PL - 1, z, z, "dirt")
            top = PL
            # curved terrace in front of Academic Block 2: west of an arc round the fountain
            arc = math.hypot(x - (CX + 30), z - CZ)
            if arc > 44 and x < 14:
                v.box(x, x, PL, TER - 1, z, z, "dirt")
                top = TER
            elif arc > 42.5 and x < 16:
                # steps up to the terrace
                v.set(x, PL, z, "dirt")
                v.set(x, PL + 1, z, DARK_ST + "[facing=east]")
                top = None
            if top is not None:
                v.set(x, top, z, PAVE_LINE if (wx - 577) % 5 == 0 or (wz - 1255) % 5 == 0 else PAVE)
            # step down to the Academic Block 1 forecourt at the south edge
            if z >= L - 2:
                v.box(x, x, 0, PL + 1, z, z, None)
                v.set(x, 0, z, "dirt")
                if z == L - 2:
                    v.set(x, 1, z, DARK_ST + "[facing=north]")
                else:
                    v.set(x, 0, z, "dirt"); v.set(x, 1, z, None)
                    v.set(x, 0, z, PAVE_LINE if (wx - 577) % 5 == 0 else PAVE)
            # sunken round court
            if r <= 12.5:
                v.set(x, PL, z, None)
                v.set(x, PL - 1, z, "red_terracotta" if r > 5.5 else "polished_andesite")
            elif r <= 13.8:
                v.set(x, PL, z, DARK_ST + "[facing=%s]" % stairs_facing(dx, dz))
    # fountain basin and statue
    for x in range(W):
        for z in range(L):
            r = math.hypot(x - CX, z - CZ)
            if r <= 5.5 and r > 4.6:
                v.set(x, PL - 1, z, DARK); v.set(x, PL, z, "smooth_stone_slab")
            elif r <= 4.6:
                v.set(x, PL - 1, z, "water")
                v.set(x, PL - 2, z, "light_blue_terracotta")
    v.box(CX - 1, CX + 1, PL - 1, PL + 2, CZ - 1, CZ + 1, DARK)
    v.box(CX, CX, PL + 3, PL + 5, CZ, CZ, "gold_block")
    v.set(CX, PL + 6, CZ, "gold_block")
    # planters on the diagonals and benches round the court
    for a in (45, 135, 225, 315):
        px = CX + int(round(15.5 * math.cos(math.radians(a))))
        pz = CZ + int(round(15.5 * math.sin(math.radians(a))))
        v.box(px - 1, px + 1, PL + 1, PL + 1, pz - 1, pz + 1, DARK)
        v.box(px, px, PL + 1, PL + 1, pz, pz, "grass_block")
        v.set(px, PL + 2, pz, "flowering_azalea")
    for a in range(0, 360, 30):
        bx = CX + int(round(18 * math.cos(math.radians(a))))
        bz = CZ + int(round(18 * math.sin(math.radians(a))))
        if v.get(bx, PL, bz) in (PAVE, PAVE_LINE):
            v.set(bx, PL + 1, bz, "polished_blackstone_slab")
    # shade trees (the big tree north-east of the fountain, two by the terrace)
    for (x, z, h, rr) in ((CX + 13, CZ - 15, 8, 6), (CX + 16, CZ - 2, 7, 5), (6, 12, 6, 4), (8, 50, 6, 4)):
        base = TER + 1 if v.get(x, TER, z) in (PAVE, PAVE_LINE) else PL + 1
        v.box(x - 1, x + 1, base - 1, base - 1, z - 1, z + 1, "grass_block")
        tree(v, x, base, z, h, rr)
    return v


def stairs_facing(dx, dz):
    # stairs climb outward from the sunken court
    if abs(dx) > abs(dz):
        return "east" if dx > 0 else "west"
    return "south" if dz > 0 else "north"


def export():
    v = build()
    return v, v.commands(OX, OY, OZ, air_clear=False)


CHECKS = ["execute if block 571 72 1233 polished_deepslate run say CHECK plaza plinth",
          "execute if block 568 72 1233 water run say CHECK plaza water"]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.iso("ne", 6).save(os.path.join(out, "plaza_iso.png"))
    print(len(cmds), "commands")
