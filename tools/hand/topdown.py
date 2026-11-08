"""Top-down colour map of a world box next to the satellite: python3 topdown.py x0 z0 x1 z1 out.png [scale]"""
import sys, os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from readworld import read_box
from vox import colour
import place
x0, z0, x1, z1 = map(int, sys.argv[1:5]); out = sys.argv[5]; S = int(sys.argv[6]) if len(sys.argv) > 6 else 3
v = read_box(place.WORLD, x0, 60, z0, x1, 125, z1)
a = v.a
nx, ny, nz = a.shape
img = np.zeros((nz, nx, 3), np.uint8)
for i in range(nx):
    for k in range(nz):
        col = a[i, :, k]
        for y in range(ny - 1, -1, -1):
            b = col[y]
            if b is not None and not b.startswith("light["):
                r, g, bb, al = colour(b)
                f = 0.65 + 0.35 * (y / ny)
                img[k, i] = (min(r * f, 255), min(g * f, 255), min(bb * f, 255))
                break
im = Image.fromarray(img).resize((nx * S, nz * S), Image.NEAREST)
sat = os.path.join(os.path.dirname(out), "_sat.png")
os.system(f'python3 "{HERE}/area.py" {x0} {z0} {x1} {z1} "{sat}" {S}')
s = Image.open(sat)
o = Image.new("RGB", (im.width * 2 + 10, im.height), "black"); o.paste(s, (0, 0)); o.paste(im, (im.width + 10, 0)); o.save(out)
