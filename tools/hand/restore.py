"""Copy a box of blocks from the pre-hand-build backup back into work/world_edit.

python3 restore.py x0 y0 z0 x1 y1 z1
Used when a clearing box clipped a neighbour.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from readworld import read_box
from mcserver import run, write_functions, forceload_cmds

BACKUP = os.path.join(ROOT, "archive", "v2_2026-11-07", "save_before_hand_builds")
WORLD = os.path.join(ROOT, "work", "world_edit")

x0, y0, z0, x1, y1, z1 = map(int, sys.argv[1:7])
v = read_box(BACKUP, x0, y0, z0, x1, y1, z1)
cmds = v.commands(x0, y0, z0, air_clear=True)
ids = write_functions(WORLD, "restore", cmds)
log = run(WORLD, forceload_cmds(x0, z0, x1, z1) + ["function " + i for i in ids] + ["forceload remove all"], wait_load=8)
print(len(cmds), "commands;", "errors:", [l for l in log.splitlines() if "rror" in l][:5])
