"""Place a hand-built building into work/world_edit through the server.

python3 tools/hand/place.py ab1 [more names...]

For each building module it clears the old generated building in a box around it,
lays a stone foundation under the new footprint, then runs the build commands.
"""
import sys, os, importlib, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from mcserver import run, write_functions, forceload_cmds

GY = np.load(os.path.join(ROOT, "data/model/gy.npy"))      # ground y per column, index [x-32, z-64]
BM = np.load(os.path.join(ROOT, "data/model/bmask.npy"))   # old generated building mask
X0, Z0 = 32, 64
WORLD = os.path.join(ROOT, "work", "world_edit")


def gy(x, z):
    i = min(max(x - X0, 0), GY.shape[0] - 1); k = min(max(z - Z0, 0), GY.shape[1] - 1)
    return int(GY[i, k])


def clear_cmds(box, footprint, floor_y, top=140):
    """box: (x0, z0, x1, z1) area to clear of the old building and trees.
    footprint: (x0, z0, x1, z1) of the new building (foundation goes here)."""
    bx0, bz0, bx1, bz1 = box
    cmds = []
    # everything well above any terrain: bulk clear in slabs of layers
    lo = 76
    area = (bx1 - bx0 + 1) * (bz1 - bz0 + 1)
    step = max(1, 32000 // area)
    for y in range(lo, top + 1, step):
        cmds.append(f"fill {bx0} {y} {bz0} {bx1} {min(y + step - 1, top)} {bz1} air")
    fx0, fz0, fx1, fz1 = footprint
    for x in range(bx0, bx1 + 1):
        for z in range(bz0, bz1 + 1):
            g = gy(x, z)
            inside = fx0 <= x <= fx1 and fz0 <= z <= fz1
            if inside:
                continue
            if g + 1 <= lo - 1:
                cmds.append(f"fill {x} {g + 1} {z} {x} {lo - 1} {z} air")
            if BM[x - X0, z - Z0]:
                cmds.append(f"setblock {x} {g} {z} grass_block")
    # foundation under the new footprint, up to the floor layer
    cmds.append(f"fill {fx0} {floor_y + 1} {fz0} {fx1} {lo - 1} {fz1} air")
    cmds.append(f"fill {fx0} {min(floor_y, 60)} {fz0} {fx1} {floor_y} {fz1} stone")
    return cmds


def main(names):
    commands = []
    for name in names:
        m = importlib.import_module(name)
        if hasattr(m, "commands"):
            bx0, bz0, bx1, bz1 = m.CLEAR
            cmds = [f"kill @e[type=text_display,x={bx0},y=50,z={bz0},dx={bx1 - bx0},dy=90,dz={bz1 - bz0}]"] + m.commands(gy)
            ids = write_functions(WORLD, name, cmds)
            x0, z0, x1, z1 = m.CLEAR
            commands += forceload_cmds(x0 - 8, z0 - 8, x1 + 8, z1 + 8)
            commands += ["function " + i for i in ids]
            commands += getattr(m, "CHECKS", [])
            print(name, len(cmds), "commands in", len(ids), "functions")
            continue
        v, build = m.export()
        nx, ny, nz = v.shape
        fp = (m.OX, m.OZ + m.F, m.OX + m.W - 1, m.OZ + m.F + m.L - 1)
        box = getattr(m, "CLEAR", (fp[0] - 10, fp[1] - 10, fp[2] + 10, fp[3] + 10))
        pre = clear_cmds(box, fp, m.OY) if getattr(m, "FOUNDATION", True) else []
        kill = [f"kill @e[type=text_display,x={box[0]},y=60,z={box[1]},dx={box[2]-box[0]},dy=80,dz={box[3]-box[1]}]"] if pre else []
        cmds = (m.extra(gy) if hasattr(m, "extra") else []) + pre + kill + build   # old-outline clear first, so it cannot drop grass on the new floors
        ids = write_functions(WORLD, name, cmds)
        x0, z0, x1, z1 = box
        commands += forceload_cmds(x0 - 8, z0 - 8, x1 + 8, z1 + 8)
        commands += ["function " + i for i in ids]
        commands += getattr(m, "CHECKS", [])
        print(name, len(cmds), "commands in", len(ids), "functions")
    commands.append("forceload remove all")
    log = run(WORLD, commands, wait_load=10)
    keep = [l for l in log.splitlines() if re.search(r"rror|Unknown|Couldn|Expected|Invalid|nita|CHECK|Failed|exception", l)]
    print("\n".join(keep[-60:]))


if __name__ == "__main__":
    main(sys.argv[1:])
