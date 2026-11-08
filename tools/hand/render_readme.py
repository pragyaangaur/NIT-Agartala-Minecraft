"""Pictures for the README, rendered straight from the world save.

python3 render_readme.py [world] [out_dir]

  map_day.png      the whole model from above, coloured by block, with hill shading
  map_night.png    the same at night, glowing where the light blocks are
  iso_*.png        isometric views of parts of the campus
  inside_*.png     isometric cutaways: the roof sliced off just above one floor, so the furniture shows
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import binary_dilation
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fastworld as fw, place
from vox import colour

X0, Z0, X1, Z1 = 32, 64, 1887, 2047
Y0, Y1 = 56, 140
WORLD = sys.argv[1] if len(sys.argv) > 1 else place.WORLD
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(place.ROOT, "docs", "images")
SKY = (150, 190, 230)


def lut_colours(names):
    cols = np.zeros((len(names), 4), np.float32)
    for i, n in enumerate(names):
        if n == "air" or n.startswith("light") and n.split("[")[0] == "light":
            cols[i] = (0, 0, 0, 0)
        else:
            cols[i] = colour(n)
    return cols


def top_view(y_cut=None, box=(X0, Z0, X1, Z1)):
    """Top block colour and height per column, read in 256 x 256 tiles."""
    bx0, bz0, bx1, bz1 = box
    W, D = bx1 - bx0 + 1, bz1 - bz0 + 1
    rgb = np.zeros((D, W, 3), np.float32); hgt = np.zeros((D, W), np.float32); lights = np.zeros((D, W), np.float32)
    names, lut = ["air"], {"air": 0, "cave_air": 0, "void_air": 0}
    for x0 in range(bx0, bx1 + 1, 256):
        for z0 in range(bz0, bz1 + 1, 256):
            x1, z1 = min(x0 + 255, bx1), min(z0 + 255, bz1)
            yt = Y1 if y_cut is None else y_cut
            ids, names, lut = fw.load(WORLD, x0, Y0, z0, x1, yt, z1, names, lut)
            cols = lut_colours(names)
            alpha = cols[ids][..., 3] > 0                       # x, y, z
            is_light = np.array([n.split("[")[0] == "light" for n in names])[ids]
            ny = ids.shape[1]
            top = ny - 1 - np.argmax(alpha[:, ::-1, :], axis=1)  # x, z
            has = alpha.any(axis=1)
            c = cols[np.take_along_axis(ids, top[:, None, :], 1)[:, 0, :]][..., :3]
            c[~has] = SKY
            rgb[z0 - bz0:z1 - bz0 + 1, x0 - bx0:x1 - bx0 + 1] = c.transpose(1, 0, 2)
            hgt[z0 - bz0:z1 - bz0 + 1, x0 - bx0:x1 - bx0 + 1] = np.where(has, top, 0).T
            lights[z0 - bz0:z1 - bz0 + 1, x0 - bx0:x1 - bx0 + 1] = is_light.sum(axis=1).T
    return rgb, hgt, lights


def shade(rgb, hgt):
    gx = np.gradient(hgt, axis=1); gz = np.gradient(hgt, axis=0)
    s = np.clip(1.0 - 0.18 * gx - 0.18 * gz, 0.55, 1.25)       # light from the north-west
    f = 0.8 + 0.25 * (hgt - hgt.min()) / max(np.ptp(hgt), 1)
    return np.clip(rgb * (s * f)[..., None], 0, 255)


def maps():
    rgb, hgt, lights = top_view()
    day = shade(rgb, hgt)
    Image.fromarray(day.astype(np.uint8)).save(os.path.join(OUT, "map_day.png"))
    from scipy.ndimage import gaussian_filter
    g = gaussian_filter(lights.astype(np.float32), 3.5)
    g = np.sqrt(np.clip(g / max(np.percentile(g[g > 0], 97), 1e-6), 0, 1))
    night = day * (0.22 + 0.75 * g[..., None]) * np.array([1.0, 0.85, 0.6]) + np.stack([g * 90, g * 60, g * 20], -1)
    night[..., 2] += 18
    Image.fromarray(np.clip(night, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "map_night.png"))
    print("maps done", flush=True)


def iso(box, name, view="se", s=4, ytop=Y1):
    """Isometric picture of the exposed blocks in a box, painter's order."""
    x0, z0, x1, z1 = box
    # start a few blocks under the lowest ground in the box, so low land is not cut off
    ylow = int(min(place.gy(x, z) for x in range(x0, x1 + 1, 4) for z in range(z0, z1 + 1, 4))) - 3
    ids, names, lut = fw.load(WORLD, x0, ylow, z0, x1, ytop, z1)
    cols = lut_colours(names)
    vis = cols[ids][..., 3] > 0
    k = {"se": 0, "ne": 1, "nw": 2, "sw": 3}[view]
    ids = np.rot90(ids, k, axes=(0, 2)); vis = np.rot90(vis, k, axes=(0, 2))
    nx, ny, nz = ids.shape
    # only cells with a see-through neighbour on a visible face (top, +z, +x)
    exp = np.zeros_like(vis)
    exp[:, :-1, :] |= ~vis[:, 1:, :]; exp[:, -1, :] = True
    exp[:, :, :-1] |= ~vis[:, :, 1:]; exp[:, :, -1] = True
    exp[:-1, :, :] |= ~vis[1:, :, :]; exp[-1, :, :] = True
    xs, ys, zs = np.nonzero(vis & exp)
    order = np.lexsort((ys, xs + zs))
    h, q = 0.87 * s, 0.5 * s
    W = int((nx + nz) * h) + 40; H = int((nx + nz) * q + ny * s) + 40
    im = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(im)
    ox, oy = 20 + nz * h, 20 + ny * s + s
    for j in order:
        x, y, z = xs[j], ys[j], zs[j]
        r, g, b, _ = cols[ids[x, y, z]]
        X = ox + (x - z) * h; Y = oy + (x + z) * q - y * s
        d.polygon([(X - h, Y - s + q), (X, Y - s + 2 * q), (X, Y + 2 * q), (X - h, Y + q)], fill=(int(r * .82), int(g * .82), int(b * .82)))
        d.polygon([(X, Y - s + 2 * q), (X + h, Y - s + q), (X + h, Y + q), (X, Y + 2 * q)], fill=(int(r * .64), int(g * .64), int(b * .64)))
        d.polygon([(X, Y - s), (X + h, Y - s + q), (X, Y - s + 2 * q), (X - h, Y - s + q)], fill=(int(r), int(g), int(b)))
    a = np.asarray(im).astype(int)
    ys_, xs_ = np.nonzero(np.abs(a - np.array(SKY)).sum(-1) > 6)
    im = im.crop((max(xs_.min() - 12, 0), max(ys_.min() - 12, 0), xs_.max() + 12, ys_.max() + 12))
    im.save(os.path.join(OUT, (name if name.startswith("inside_") else f"iso_{name}") + ".png"))
    print("iso", name, im.size, flush=True)


def inside(box, y_cut, name, scale=6):
    rgb, hgt, _ = top_view(y_cut, box)
    img = np.clip(rgb * (0.75 + 0.25 * (hgt / max(hgt.max(), 1)))[..., None], 0, 255).astype(np.uint8)
    im = Image.fromarray(img).resize((img.shape[1] * scale, img.shape[0] * scale), Image.NEAREST)
    im.save(os.path.join(OUT, f"inside_{name}.png"))
    print("inside", name, flush=True)


def graphics():
    """Banner (day blending into night over the campus core) and lighter copies of the maps."""
    day = Image.open(os.path.join(OUT, "map_day.png")); night = Image.open(os.path.join(OUT, "map_night.png"))
    box = (380, 1000, 1180, 1250)                       # academic core (map pixel = world x - 32, z - 64)
    d = day.crop(box).resize((1600, 500), Image.LANCZOS); n = night.crop(box).resize((1600, 500), Image.LANCZOS)
    ramp = np.clip((np.arange(1600) - 700) / 400.0, 0, 1)[None, :, None]
    im = Image.fromarray((np.asarray(d) * (1 - ramp) + np.asarray(n) * ramp).astype(np.uint8))
    shade = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    for y in range(500):
        sd.line([(0, y), (1600, y)], fill=(10, 14, 24, int(200 * max(0, 1 - y / 230))))
    im = Image.alpha_composite(im.convert("RGBA"), shade).convert("RGB")
    dr = ImageDraw.Draw(im)
    try:
        big = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 64)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
    except OSError:
        big = small = ImageFont.load_default()
    dr.text((48, 40), "NIT Agartala in Minecraft", font=big, fill=(255, 255, 255))
    dr.text((52, 124), "The whole campus at 1 block = 1 metre   |   Java Edition 26.3", font=small, fill=(225, 232, 240))
    im.save(os.path.join(OUT, "banner.jpg"), quality=90)
    for nm in ("map_day", "map_night"):
        m = Image.open(os.path.join(OUT, nm + ".png")); m.thumbnail((1200, 1300), Image.LANCZOS)
        m.save(os.path.join(OUT, nm + ".jpg"), quality=88)
    print("graphics done", flush=True)


VIEWS = {
    "core": ((520, 1040, 760, 1280), "se", 3),        # Admin, SAC, Knowledge Park, both halls
    "library": ((820, 1140, 920, 1250), "se", 5),
    "rnt": ((770, 560, 1000, 800), "se", 3),
    "aryabhatta": ((440, 760, 680, 930), "se", 3),
    "maingate": ((622, 1612, 690, 1668), "se", 7),
    "sports": ((1030, 250, 1250, 385), "se", 3),
}
CUTS = {                                              # roof cut away just above one floor
    "classrooms": ((570, 1225, 630, 1290), 78),        # Administrative Block, ground floor
    "hostel": ((850, 620, 930, 700), 80),              # RNT towers, first floor
    "library": ((842, 1163, 901, 1220), 77),
    "seminar_hall": ((541, 1138, 580, 1185), 84),      # Swami Vivekananda Seminar Hall
    "village": ((100, 600, 200, 700), 72),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    what = sys.argv[3:] or ["maps", "iso", "inside"]
    picks = [w for w in what if w not in ("maps", "iso", "inside")]      # optional view names
    if "maps" in what:
        maps()
        graphics()
    if "iso" in what:
        for n, (b, v, s) in VIEWS.items():
            if not picks or n in picks:
                iso(b, n, v, s)
    if "inside" in what:
        for n, (b, y) in CUTS.items():
            if not picks or n in picks:
                iso(b, "inside_" + n, "se", 5, ytop=y)
