"""Remove dropped items and every animal or monster, tile by tile, waiting about 25 s for each
tile's entities to load before killing (a kill sent straight after forceload sees nothing).
Keeps players, text displays (signs), paintings and armour stands (the students)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import place
from mcserver import run, forceload_cmds

KEEP = "type=!minecraft:player,type=!minecraft:text_display,type=!minecraft:painting,type=!minecraft:armor_stand"


def main(only=None):
    # one server session per tile: in a shared session only the first tile's entities loaded in time
    for tx in range(8):
        for tz in range(9):
            x0, z0 = max(tx * 256, 32), max(tz * 256, 64)
            x1, z1 = min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047)
            if x0 > x1 or z0 > z1 or (only and (tx, tz) not in only):
                continue
            cmds = forceload_cmds(x0, z0, x1, z1) + [("sleep", 25),
                    f"kill @e[{KEEP},x={x0},y=-64,z={z0},dx={x1 - x0},dy=400,dz={z1 - z0}]",
                    "forceload remove all"]
            log = run(place.WORLD, cmds, wait_load=5, step_wait=1)
            print(tx, tz, [l[33:] for l in log.splitlines() if "Killed" in l or "No entity" in l or "xception" in l], flush=True)


if __name__ == "__main__":
    only = {tuple(map(int, a.split(","))) for a in sys.argv[1:]} or None
    main(only)
