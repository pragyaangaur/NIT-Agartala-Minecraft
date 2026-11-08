"""Headless renderer for the voxel model: top-down orthographic and oblique views."""
import numpy as np
from numba import njit
import blocks

# rough sRGB colour for every block used by the palette
C = {
 "minecraft:stone": (0.50, 0.50, 0.50), "minecraft:deepslate": (0.30, 0.30, 0.32),
 "minecraft:dirt": (0.53, 0.40, 0.27), "minecraft:grass_block": (0.42, 0.60, 0.28),
 "minecraft:coarse_dirt": (0.44, 0.34, 0.23), "minecraft:podzol": (0.37, 0.26, 0.13),
 "minecraft:sand": (0.86, 0.82, 0.66), "minecraft:gravel": (0.51, 0.49, 0.48),
 "minecraft:clay": (0.62, 0.64, 0.68), "minecraft:mud": (0.25, 0.22, 0.20),
 "minecraft:packed_mud": (0.58, 0.44, 0.33), "minecraft:water": (0.18, 0.32, 0.70),
 "minecraft:red_sand": (0.75, 0.45, 0.20), "minecraft:moss_block": (0.34, 0.45, 0.16),
 "minecraft:rooted_dirt": (0.55, 0.43, 0.32), "minecraft:short_grass": (0.40, 0.55, 0.25),
 "minecraft:fern": (0.35, 0.50, 0.22), "minecraft:poppy": (0.55, 0.15, 0.12),
 "minecraft:dandelion": (0.85, 0.75, 0.15),
 "minecraft:oak_leaves": (0.28, 0.44, 0.16), "minecraft:dark_oak_leaves": (0.19, 0.35, 0.11),
 "minecraft:jungle_leaves": (0.24, 0.45, 0.13), "minecraft:birch_leaves": (0.45, 0.60, 0.26),
 "minecraft:oak_log": (0.36, 0.28, 0.17), "minecraft:dark_oak_log": (0.24, 0.17, 0.09),
 "minecraft:jungle_log": (0.32, 0.24, 0.13), "minecraft:spruce_log": (0.26, 0.18, 0.11),
 "minecraft:white_concrete": (0.85, 0.87, 0.88), "minecraft:light_gray_concrete": (0.60, 0.62, 0.63),
 "minecraft:gray_concrete": (0.30, 0.31, 0.33), "minecraft:black_concrete": (0.08, 0.08, 0.09),
 "minecraft:red_concrete": (0.56, 0.16, 0.14), "minecraft:orange_concrete": (0.86, 0.42, 0.10),
 "minecraft:yellow_concrete": (0.94, 0.79, 0.17), "minecraft:lime_concrete": (0.44, 0.68, 0.12),
 "minecraft:cyan_concrete": (0.09, 0.50, 0.55), "minecraft:light_blue_concrete": (0.24, 0.53, 0.82),
 "minecraft:brown_concrete": (0.35, 0.22, 0.13), "minecraft:pink_concrete": (0.88, 0.51, 0.60),
 "minecraft:magenta_concrete": (0.74, 0.31, 0.74), "minecraft:purple_concrete": (0.44, 0.20, 0.55),
 "minecraft:blue_concrete": (0.15, 0.22, 0.48), "minecraft:green_concrete": (0.32, 0.40, 0.15),
 "minecraft:terracotta": (0.60, 0.36, 0.24), "minecraft:white_terracotta": (0.82, 0.70, 0.62),
 "minecraft:light_gray_terracotta": (0.53, 0.42, 0.39), "minecraft:gray_terracotta": (0.23, 0.16, 0.14),
 "minecraft:black_terracotta": (0.15, 0.09, 0.07), "minecraft:red_terracotta": (0.56, 0.21, 0.16),
 "minecraft:orange_terracotta": (0.64, 0.35, 0.17), "minecraft:brown_terracotta": (0.30, 0.19, 0.12),
 "minecraft:bricks": (0.57, 0.34, 0.30), "minecraft:stone_bricks": (0.48, 0.48, 0.48),
 "minecraft:mossy_stone_bricks": (0.40, 0.44, 0.36), "minecraft:chiseled_stone_bricks": (0.46, 0.46, 0.46),
 "minecraft:smooth_stone": (0.62, 0.62, 0.61), "minecraft:smooth_stone_slab": (0.62, 0.62, 0.61),
 "minecraft:andesite": (0.52, 0.52, 0.51), "minecraft:polished_andesite": (0.51, 0.51, 0.50),
 "minecraft:diorite": (0.74, 0.74, 0.73), "minecraft:polished_diorite": (0.76, 0.76, 0.75),
 "minecraft:granite": (0.60, 0.44, 0.37), "minecraft:polished_granite": (0.61, 0.42, 0.35),
 "minecraft:cobblestone": (0.48, 0.48, 0.47), "minecraft:mossy_cobblestone": (0.40, 0.44, 0.34),
 "minecraft:sandstone": (0.83, 0.79, 0.63), "minecraft:cut_sandstone": (0.84, 0.80, 0.64),
 "minecraft:quartz_block": (0.92, 0.90, 0.86), "minecraft:smooth_quartz": (0.93, 0.91, 0.87),
 "minecraft:deepslate_tiles": (0.22, 0.22, 0.23), "minecraft:polished_blackstone": (0.22, 0.20, 0.22),
 "minecraft:iron_block": (0.85, 0.85, 0.85), "minecraft:copper_block": (0.72, 0.45, 0.35),
 "minecraft:tuff": (0.39, 0.39, 0.35), "minecraft:calcite": (0.88, 0.88, 0.86),
 "minecraft:glass": (0.70, 0.85, 0.95), "minecraft:white_stained_glass": (0.85, 0.87, 0.88),
 "minecraft:light_gray_stained_glass": (0.60, 0.62, 0.63), "minecraft:gray_stained_glass": (0.30, 0.31, 0.33),
 "minecraft:black_stained_glass": (0.08, 0.08, 0.09), "minecraft:brown_stained_glass": (0.35, 0.22, 0.13),
 "minecraft:cyan_stained_glass": (0.09, 0.50, 0.55), "minecraft:light_blue_stained_glass": (0.24, 0.53, 0.82),
 "minecraft:green_stained_glass": (0.32, 0.40, 0.15), "minecraft:blue_stained_glass": (0.15, 0.22, 0.48),
 "minecraft:red_stained_glass": (0.56, 0.16, 0.14),
 "minecraft:oak_planks": (0.63, 0.51, 0.32), "minecraft:dark_oak_planks": (0.25, 0.17, 0.09),
 "minecraft:spruce_planks": (0.45, 0.33, 0.19), "minecraft:birch_planks": (0.77, 0.70, 0.50),
 "minecraft:oak_fence": (0.63, 0.51, 0.32), "minecraft:iron_bars": (0.55, 0.55, 0.55),
 "minecraft:white_wool": (0.93, 0.93, 0.93), "minecraft:cobblestone_wall": (0.48, 0.48, 0.47),
 "minecraft:stone_brick_stairs": (0.48, 0.48, 0.48), "minecraft:bedrock": (0.35, 0.35, 0.35),
}

def palette_rgb(pal):
    out = np.zeros((len(pal), 3), np.float32)
    for i, (name, props) in enumerate(pal):
        c = C.get(name, (0.6, 0.3, 0.6))
        out[i] = c
    return out

def topdown(vol, pal, x0, z0, ybase, sub=None, shade=True):
    """Top-most block and its height for each column (chunked to bound memory)."""
    if sub is None:
        sub = (slice(None), slice(None))
    v0 = vol[sub]
    nx, nz, ny = v0.shape
    top = np.zeros((nx, nz), np.uint16)
    H = np.full((nx, nz), np.nan, np.float32)
    for i in range(0, nx, 128):
        v = v0[i:i + 128]
        nz_mask = v != 0
        any_ = nz_mask.any(axis=2)
        idx = ny - 1 - np.argmax(nz_mask[:, :, ::-1], axis=2)
        flat = np.take_along_axis(v, idx[..., None], axis=2)[..., 0]
        top[i:i + 128] = np.where(any_, flat, 0)
        H[i:i + 128] = np.where(any_, idx + ybase, np.nan)
    return top, H

def shade_rgb(rgb, H, sun_az=315.0, sun_alt=45.0, strength=0.40):
    from scipy.ndimage import gaussian_filter
    Hn = np.nan_to_num(H, nan=np.nanmin(H) if not np.all(np.isnan(H)) else 0)
    Hs = gaussian_filter(Hn, 1.2)
    gy, gx = np.gradient(Hs)
    az = np.radians(sun_az); alt = np.radians(sun_alt)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    sh = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    sh = np.clip(sh, 0.0, 1.0)
    fac = (1 - strength) + strength * (sh / max(1e-3, np.sin(alt)))
    fac = np.clip(fac, 0.62, 1.35)
    return np.clip(rgb * 1.05 * fac[..., None], 0, 1)

def render_topdown(vol, pal, x0, z0, ybase, bbox, ppm=1.0, upscale=1, shade=True):
    """bbox in world metres (x0,z0,x1,z1); returns uint8 RGB, north up."""
    X0, Z0, X1, Z1 = bbox
    w = int(round((X1 - X0) * ppm)); h = int(round((Z1 - Z0) * ppm))
    i0 = int(X0) - x0; i1 = i0 + int(np.ceil((X1 - X0)))
    j0 = int(Z0) - z0; j1 = j0 + int(np.ceil((Z1 - Z0)))
    i0 = max(i0, 0); j0 = max(j0, 0)
    i1 = min(i1, vol.shape[0]); j1 = min(j1, vol.shape[1])
    top, H = topdown(vol, pal, x0, z0, ybase, sub=(slice(i0, i1), slice(j0, j1)))
    pal_rgb = palette_rgb(pal)
    rgb = pal_rgb[top]
    if shade:
        rgb = shade_rgb(rgb, H)
    # rgb is indexed [x, z]; PIL wants [row=z, col=x] so that +X is right and +Z is down
    img = np.clip(rgb * 255, 0, 255).astype(np.uint8).transpose(1, 0, 2)
    from PIL import Image
    im = Image.fromarray(img)
    if (im.size[0], im.size[1]) != (w, h):
        im = im.resize((w, h), Image.LANCZOS)
    return im

# ------------------------------------------------------------------ oblique
@njit(cache=True, fastmath=True)
def _raycast(vol, ox, oy, oz, dx, dy, dz, W, Hh, ux, uy, uz, vx, vy, vz,
             su, sv, tmax, step, ids, depths, axes):
    nx, nz, ny = vol.shape
    for py in range(Hh):
        for px in range(W):
            ou = (px - W * 0.5) * su
            ov = (py - Hh * 0.5) * sv
            rdx = dx + ux * ou + vx * ov
            rdy = dy + uy * ou + vy * ov
            rdz = dz + uz * ou + vz * ov
            n = np.sqrt(rdx * rdx + rdy * rdy + rdz * rdz)
            rdx /= n; rdy /= n; rdz /= n
            t = 0.0
            hit = -1
            axv = 2
            pgx = 1 << 30; pgy = 1 << 30; pgz = 1 << 30
            while t < tmax:
                gx = int(np.floor(ox + rdx * t))
                gy = int(np.floor(oy + rdy * t))
                gz = int(np.floor(oz + rdz * t))
                if gx >= 0 and gx < nx and gz >= 0 and gz < nz and gy >= 0 and gy < ny:
                    b = vol[gx, gz, gy]
                    if b != 0:
                        hit = b
                        adx = rdx if rdx >= 0 else -rdx
                        ady = rdy if rdy >= 0 else -rdy
                        adz = rdz if rdz >= 0 else -rdz
                        if ady >= adx and ady >= adz: axv = 2
                        elif adx >= adz: axv = 0
                        else: axv = 1
                        break
                pgx = gx; pgy = gy; pgz = gz
                t += step
            ids[py, px] = hit
            depths[py, px] = t
            axes[py, px] = axv

def oblique(vol, pal, cam, target, size=(800, 600), fov=45.0, step=0.6, tmax=None):
    """Perspective camera. cam/target are (x,y,z) in volume index space."""
    W, Hh = size
    cam = np.array(cam, float); target = np.array(target, float)
    d = target - cam; d /= np.linalg.norm(d)
    up = np.array([0.0, 1.0, 0.0])
    right = np.cross(d, up); right /= np.linalg.norm(right)
    up2 = np.cross(right, d)
    f = 1.0 / np.tan(np.radians(fov) / 2)
    su = 2.0 / (W * f); sv = 2.0 / (Hh * f)
    ids = np.full((Hh, W), -1, np.int64)
    dep = np.zeros((Hh, W), np.float32)
    axes = np.full((Hh, W), 2, np.int32)
    if tmax is None:
        tmax = 4.0 * np.linalg.norm(np.array(vol.shape, float))
    _raycast(vol, cam[0], cam[1], cam[2], d[0], d[1], d[2], W, Hh,
             right[0], right[1], right[2], up2[0], up2[1], up2[2],
             su, sv, tmax, step, ids, dep, axes)
    pal_rgb = palette_rgb(pal)
    rgb = np.ones((Hh, W, 3), np.float32) * np.array([0.72, 0.82, 0.93])
    m = ids >= 0
    rgb[m] = pal_rgb[ids[m]]
    # flat face shading from the crossing axis, lit from the north-west-above
    L = np.array([-0.45, 0.82, -0.36]); L /= np.linalg.norm(L)
    NX_ = np.zeros((Hh, W)); NY_ = np.zeros((Hh, W)); NZ_ = np.zeros((Hh, W))
    m0 = axes == 0; m1 = axes == 1; m2 = axes == 2
    NX_[m0] = np.sign(d[0]); NY_[m2] = np.sign(d[1]); NZ_[m1] = np.sign(d[2])
    nxy = np.sqrt(NX_**2 + NY_**2 + NZ_**2); nxy[nxy < 1e-6] = 1
    dot = np.clip((NX_ * L[0] + NY_ * L[1] + NZ_ * L[2]) / nxy, 0, 1)
    shade = 0.42 + 0.62 * dot
    rgb *= shade[..., None]
    # distance haze
    haze = np.clip(dep / max(1.0, tmax * 0.85), 0, 1) * 0.22
    rgb = rgb * (1 - haze[..., None]) + np.array([0.72, 0.82, 0.93]) * haze[..., None]
    rgb = np.clip(rgb, 0, 1)
    from PIL import Image
    return Image.fromarray((rgb * 255).astype(np.uint8))

def downsample(vol, k):
    nx, nz, ny = vol.shape
    nx2, nz2, ny2 = nx // k, nz // k, ny // k
    v = vol[:nx2 * k, :nz2 * k, :ny2 * k]
    v = v.reshape(nx2, k, nz2, k, ny2, k)
    # priority: prefer non-air, then higher palette index (walls before leaves is arbitrary)
    out = v.max(axis=(1, 3, 5))
    return out
