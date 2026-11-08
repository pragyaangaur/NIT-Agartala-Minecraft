"""CSE Department. OSM way 1544302853.

Frames: W7D6gLvjizM 2:02-2:22 (front from the approach road and close up), 2:24-2:32 (drone);
Commons photos of the front. A big white rounded frame projects from the front around dark
blue glass with three yellow panels; to its right a blue curtain wall with maroon piers, a
pink band and a yellow band; white end walls; maroon roof eaves; solar panels on the roof;
a black sign block reading DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING by the entrance,
on the side towards the Library (moved there on 7 Nov after checking in game).
The real building is turned about 45 degrees to face the round garden; here it faces south.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox
from style import Face, FLOOR, ROOF

NAME = "cse"
W, L, F = 54, 44, 0
S = 5
OX, OY, OZ = 776, 73, 1214
NY = 24
CLEAR = (754, 1196, 841, 1279)

WHITE = "smooth_quartz"
BLUE = "blue_stained_glass"
DARK = "black_stained_glass"
YEL = "yellow_concrete"
MAROON = "red_terracotta"
PINK = "pink_terracotta"
BASE = "brown_terracotta"


def build():
    v = Vox(W, NY, L + S)
    x0, x1, z0, z1 = 0, W - 1, 0, L - 1
    top = 17
    v.box(x0, x1, 1, top, z0, z1, WHITE)
    v.box(x0 + 1, x1 - 1, 2, top - 1, z0 + 1, z1 - 1, None)
    for fy in (1, 5, 9, 13):
        v.box(x0 + 1, x1 - 1, fy, fy, z0 + 1, z1 - 1, FLOOR)
    v.box(x0, x1, top, top, z0, z1, ROOF)
    v.box(x0, x1, 0, 0, z0, z1, FLOOR)
    # sides and back: white with window rows and a pink band under the eaves
    for side in ("north", "east", "west"):
        f = Face(v, side, x0, x1, z0, z1)
        for u in range(1, f.n - 1):
            if u % 4 != 0:
                for fy in (1, 5, 9, 13):
                    f.set(u, fy + 1, BLUE); f.set(u, fy + 2, BLUE)
            f.set(u, 15, PINK)
    # ---- south front, u = x (south face u runs east to west, so write x directly)
    zf = z1
    def put(x, y, b, out=0):
        v.set(x, y, zf + out, b)
    # left white blocks, lower
    for x in range(0, 9):
        for y in range(14, top + 2):
            v.set(x, y, zf, None)
            for z in range(z0, z1 + 1):
                if y <= top and x <= 8 and z >= z1 - 14:
                    v.set(x, y, z, None)
        for y in range(1, 14):
            put(x, y, WHITE)
        for y in (2, 3, 6, 7, 10, 11):
            if x in (2, 3, 6):
                put(x, y, BLUE)
    for x in range(0, 9):
        for z in range(z1 - 14, z1 + 1):
            v.set(x, 13, z, ROOF)
    # pink/red stair strip
    for x in range(9, 14):
        for y in range(1, top + 1):
            put(x, y, MAROON if x in (9, 13) else BLUE)
        put(x, 6, YEL); put(x, 12, PINK)
    # rounded white frame around blue glass with yellow panels
    fx0, fx1, fy0, fy1 = 14, 37, 6, 16
    for x in range(fx0, fx1 + 1):
        for y in range(fy0, fy1 + 1):
            edge = x in (fx0, fx0 + 1, fx1 - 1, fx1) or y in (fy0, fy1)
            corner = (x in (fx0, fx1)) and (y in (fy0, fy1))
            for out in (0, 1, 2):
                if edge and not corner:
                    put(x, y, WHITE, out)
            if not edge:
                put(x, y, YEL if x in (16, 25, 26, 35) else DARK if (x - fx0) % 5 == 0 else BLUE)
    # ground floor below the frame: dark brown wall, glass entrance
    for x in range(fx0, fx1 + 1):
        for y in range(1, fy0):
            put(x, y, BASE)
    for x in range(22, 31):
        for y in range(1, 5):
            put(x, y, "light_gray_stained_glass")
    # blue curtain wall with maroon piers, pink and yellow bands
    for x in range(fx1 + 1, 49):
        for y in range(1, top + 1):
            put(x, y, MAROON if x in (40, 41, 45, 46) else BLUE)
        if x not in (40, 41, 45, 46):
            put(x, 12, PINK); put(x, 6, YEL)
    # white end wall
    for x in range(49, W):
        for y in range(1, top + 1):
            put(x, y, WHITE)
    # maroon eaves along the top of the taller part, all round
    for x in range(9, W):
        put(x, top + 1, MAROON, 1)
        put(x, top + 1, MAROON)
    for side in ("north", "east"):
        f = Face(v, side, x0, x1, z0, z1)
        for u in range(f.n):
            f.set(u, top + 1, MAROON, 1)
            f.set(u, top + 1, MAROON)
    # solar panels on the roof
    for z in range(4, L - 8, 3):
        for x in range(14, W - 6):
            v.set(x, top + 1, z, "daylight_detector")
    # black sign block in front, on the Library side of the entrance
    for x in range(32, 37):
        for y in range(1, 6):
            put(x, y, "black_concrete", 3)
    for x in range(14, 40):
        for out in range(1, S):
            if v.get(x, 1, zf + out) is None:
                v.set(x, 0, zf + out, "polished_andesite")
    v.ents.append('summon text_display %SX% %SY% %SZ% {Rotation:[0f,0f],background:0,line_width:120,'
                  'text:{text:"DEPARTMENT\\nOF\\nCOMPUTER SCIENCE\\nAND\\nENGINEERING",color:"#ffffff"},'
                  'transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
                  'translation:[0f,0f,0f],scale:[1.1f,1.1f,1.1f]}}')
    return v


def export():
    v = build()
    cmds = v.commands(OX, OY, OZ)
    sx, sy, sz = OX + 34.5, OY + 2.2, OZ + L - 1 + 3 + 1.03
    cmds = [c.replace("%SX%", f"{sx:.2f}").replace("%SY%", f"{sy:.2f}").replace("%SZ%", f"{sz:.2f}") for c in cmds]
    return v, cmds


CHECKS = ["execute if block 802 85 1257 yellow_concrete run say CHECK cse yellow panel"]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    v, cmds = export()
    v.elevation("south", 10).save(os.path.join(out, "cse_south.png"))
    v.iso("sw", 6).save(os.path.join(out, "cse_iso.png"))
    print(len(cmds), "commands")
