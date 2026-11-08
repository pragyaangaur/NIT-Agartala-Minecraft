"""Main gate, on the boulevard south of the roundabout. Position from the satellite (the gate
structure's shadow where the dual carriageway narrows at the boundary, about x 652, z 1633).

Frames: JkbNik31wDE 0:34-0:38 (close up), 8:24-8:36 (straight on); SqZLoYQonbc 0:02.
Two weathered white guard-room piers with light blue N.I.T AGARTALA signs, stacked rust-red
slab cornices on short white columns above them with small red domes, a thick grey lintel
with raised white letters NATIONAL INSTITUTE OF TECHNOLOGY AGARTALA, and a big terracotta dome
on an arched octagonal drum in the middle. Black bar gates, white boundary walls with black
name boards either side.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox

NAME = "maingate"
W, L, F = 44, 9, 0
OX, OY, OZ = 634, 0, 1629          # OY set from the ground in export()
NY = 26
CLEAR = (626, 1622, 678, 1642)

WHITE = "white_concrete"
RUST = "red_terracotta"
DOME = "orange_terracotta"
BEAM = "gray_terracotta"


def build():
    v = Vox(W, NY, L)
    cx = W // 2
    zc = 4
    piers = (cx - 12, cx + 8)              # each pier 5 wide
    for p in piers:
        v.box(p, p + 4, 1, 5, zc - 2, zc + 2, WHITE)
        v.box(p + 1, p + 3, 1, 4, zc - 1, zc + 1, None)
        v.set(p + 2, 1, zc + 2, None); v.set(p + 2, 2, zc + 2, None)            # door
        for z in (zc - 2, zc + 2):
            v.set(p + 1, 3, z, "tinted_glass")
            v.box(p + 1, p + 3, 4, 4, z, z, "light_blue_concrete")              # sign board
        # stacked cornices on short columns
        v.box(p - 1, p + 5, 6, 6, zc - 3, zc + 3, RUST)
        for (dx, dz) in ((0, -2), (4, -2), (0, 2), (4, 2)):
            v.set(p + dx, 7, zc + dz, WHITE); v.set(p + dx, 8, zc + dz, WHITE)
        v.box(p, p + 4, 9, 9, zc - 2, zc + 2, RUST)
    # lintel beam across both piers
    v.box(piers[0] - 1, piers[1] + 5, 10, 11, zc - 3, zc + 3, BEAM)
    v.box(piers[0] - 1, piers[1] + 5, 10, 10, zc - 3, zc - 3, RUST)
    v.box(piers[0] - 1, piers[1] + 5, 10, 10, zc + 3, zc + 3, RUST)
    # small domes over the piers
    for p in piers:
        dx0 = p + 2
        v.box(dx0 - 1, dx0 + 1, 12, 12, zc - 1, zc + 1, DOME)
        v.set(dx0, 13, zc, DOME); v.set(dx0, 14, zc, "lightning_rod[facing=up]")
    # central dome on an arched octagonal drum
    for x in range(cx - 5, cx + 6):
        for z in range(zc - 5, zc + 6):
            r = math.hypot(x - cx, z - zc)
            if r <= 3.6:
                for y in range(12, 15):
                    arch = r > 2.6 and (x == cx or z == zc) and y < 14
                    v.set(x, y, z, None if (r < 2.6 or arch) else RUST)
            if r <= 4.8:
                v.set(x, 15, z, WHITE)
            if r <= 4.5:
                h = int(round(math.sqrt(max(4.5 ** 2 - r * r, 0)) * 0.95))
                for y in range(16, 16 + h + 1):
                    v.set(x, y, z, DOME)
    top = max(y for y in range(NY) if v.get(cx, y, zc))
    v.set(cx, top + 1, zc, WHITE); v.set(cx, top + 2, zc, "lightning_rod[facing=up]")
    v.set(cx, 18, zc - 4, "white_concrete")             # emblem medallion
    # bar gates (left open in the middle) and side bar gates
    for x in list(range(piers[0] + 5, piers[0] + 9)) + list(range(piers[1] - 4, piers[1])):
        for y in (1, 2):
            v.set(x, y, zc, "iron_bars")
    # boundary walls with black name boards
    for x in list(range(0, piers[0])) + list(range(piers[1] + 5, W)):
        v.set(x, 1, zc, WHITE); v.set(x, 2, zc, WHITE)
    for x in list(range(2, 9)) + list(range(W - 9, W - 2)):
        v.set(x, 2, zc - 1, "black_concrete"); v.set(x, 3, zc - 1, "black_concrete")
        v.set(x, 3, zc, WHITE)
    for x in range(piers[0], piers[1] + 5):
        v.set(x, 0, zc, "gray_concrete")
    return v


def export():
    import place
    g = int(sorted(place.gy(x, z) for x in range(OX + 10, OX + 34, 4) for z in (OZ + 2, OZ + 6))[5])
    global OY
    OY = g
    v = build()
    cmds = v.commands(OX, OY, OZ)
    cx = OX + W // 2 + 0.5
    txt = ('{{Rotation:[{r}f,0f],background:0,text:{{text:"NATIONAL INSTITUTE OF TECHNOLOGY AGARTALA",color:"{c}"}},'
           'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],'
           'scale:[{s}f,{s}f,{s}f]}}}}')
    zc = OZ + 4
    cmds.append(f"summon text_display {cx} {OY + 11.15} {zc + 3 + 1.03} " + txt.format(r=0, c="#ffffff", s=1.9))
    cmds.append(f"summon text_display {cx} {OY + 11.15} {zc - 3 - 0.03} " + txt.format(r=180, c="#ffffff", s=1.9))
    for x0 in (OX + 2, OX + W - 9):
        cmds.append(f"summon text_display {x0 + 3.5} {OY + 2.35} {zc - 1 - 0.03} " + txt.format(r=180, c="#ffffff", s=0.45))
    for p in (OX + W // 2 - 12, OX + W // 2 + 8):
        for (zz, r) in ((zc + 2 + 1.02, 0), (zc - 2 - 0.02, 180)):
            cmds.append(f'summon text_display {p + 2.5} {OY + 4.05} {zz} {{Rotation:[{r}f,0f],background:0,'
                        f'text:{{text:"N.I.T\\nAGARTALA",color:"#ffffff"}},transformation:{{left_rotation:[0f,0f,0f,1f],'
                        f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.5f,0.5f,0.5f]}}}}')
    return v, cmds


CHECKS = []

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("south", 14).save(os.path.join(out, "gate_south.png"))
    print(len(cmds), OY)
