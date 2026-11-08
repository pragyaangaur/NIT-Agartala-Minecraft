"""Side-by-side helper: python3 side.py out.png img1 img2 ... (scaled to the same height)."""
import sys
from PIL import Image
out, paths = sys.argv[1], sys.argv[2:]
ims = [Image.open(p).convert("RGB") for p in paths]
H = max(i.height for i in ims)
ims = [i.resize((int(i.width * H / i.height), H), Image.NEAREST) for i in ims]
o = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) - 1), H), "black")
x = 0
for i in ims:
    o.paste(i, (x, 0)); x += i.width + 10
o.save(out)
