"""The campus lake north of the International Guest House.

Missing from the first build (classified as forest). Outline digitised from the Esri
satellite; the official campus map (UG reporting guide 2024) draws the same plus-shaped lake
with the Guest House on its south shore. Open water in the south-west body, weedy shallow
arms to the north-west, north-east and south-east with lily pads and reeds.
"""
import sys, os, math, random
import numpy as np
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt, binary_dilation
sys.path.insert(0, os.path.dirname(__file__))

NAME = "lake"
PX = [(55, 520), (60, 490), (95, 455), (150, 420), (200, 400), (240, 380), (270, 345), (300, 315), (330, 285),
      (340, 255), (300, 225), (255, 195), (250, 180), (280, 195), (330, 215), (370, 215), (410, 205), (440, 200),
      (470, 215), (520, 225), (565, 225), (560, 250), (520, 262), (470, 260), (430, 250), (390, 255), (360, 285),
      (355, 330), (350, 370), (360, 400), (390, 430), (420, 470), (400, 480), (370, 455), (340, 430), (320, 430),
      (290, 445), (240, 470), (200, 500), (170, 520), (130, 540), (95, 550), (65, 545)]
POLY = [(1080 + x / 1.6, 880 + y / 1.6) for x, y in PX]
xs = [p[0] for p in POLY]; zs = [p[1] for p in POLY]
CLEAR = (int(min(xs)) - 4, int(min(zs)) - 4, int(max(xs)) + 4, int(max(zs)) + 4)
NATURAL = ("grass_block", "coarse_dirt", "podzol", "dirt", "moss_block", "mud")


def commands(gy):
    x0, z0, x1, z1 = CLEAR
    nx, nz = x1 - x0 + 1, z1 - z0 + 1
    p = Path(POLY)
    XX, ZZ = np.meshgrid(np.arange(nx) + x0 + 0.5, np.arange(nz) + z0 + 0.5, indexing="ij")
    m = p.contains_points(np.c_[XX.ravel(), ZZ.ravel()]).reshape(nx, nz)
    d = distance_transform_edt(m)
    shore = binary_dilation(m, iterations=4) & ~m
    dout = distance_transform_edt(~m)
    wl = int(np.percentile([gy(x0 + i, z0 + k) for i, k in np.argwhere(shore)], 15))
    rng = random.Random(11)
    c = []
    for i, k in np.argwhere(m):
        X, Z = x0 + i, z0 + k
        t = gy(X, Z)
        depth = 1 + min(3, int(d[i, k] / 3))
        top = max(t, wl) + 20
        for nat in NATURAL:
            c.append(f"execute if block {X} {t} {Z} {nat} run fill {X} {wl - depth} {Z} {X} {top} {Z} air")
        c.append(f"execute if block {X} {wl} {Z} air run fill {X} {wl - depth} {Z} {X} {wl} {Z} water")
        c.append(f"execute if block {X} {wl - depth - 1} {Z} #minecraft:dirt run setblock {X} {wl - depth - 1} {Z} mud")
        c.append(f"execute if block {X} {wl - depth - 1} {Z} stone run setblock {X} {wl - depth - 1} {Z} mud")
        weedy = not (1115 <= X <= 1260 and 1120 <= Z <= 1230)
        if (weedy and rng.random() < 0.18) or rng.random() < 0.03:
            c.append(f"execute if block {X} {wl} {Z} water run setblock {X} {wl + 1} {Z} lily_pad")
        if weedy and depth >= 2 and rng.random() < 0.3:
            c.append(f"execute if block {X} {wl - 1} {Z} water run setblock {X} {wl - 1} {Z} seagrass")
    for i, k in np.argwhere(shore):
        X, Z = x0 + i, z0 + k
        t = gy(X, Z)
        target = wl + int(round(dout[i, k]))          # gentle bank, one block per metre
        if t > target:
            for nat in NATURAL:
                c.append(f"execute if block {X} {t} {Z} {nat} run fill {X} {target + 1} {Z} {X} {t + 18} {Z} air")
                c.append(f"execute if block {X} {t} {Z} {nat} run setblock {X} {target} {Z} grass_block")
            t = target
        elif t < wl:
            c.append(f"fill {X} {t} {Z} {X} {wl - 1} {Z} dirt")
            c.append(f"setblock {X} {wl} {Z} grass_block")
            t = wl
        if dout[i, k] <= 1.5 and rng.random() < 0.35:
            c.append(f"execute if block {X} {t} {Z} grass_block run fill {X} {t + 1} {Z} {X} {t + rng.randint(1, 3)} {Z} sugar_cane")
    return c


CHECKS = []
