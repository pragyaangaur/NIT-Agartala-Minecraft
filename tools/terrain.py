"""Terrain: SRTM/terrarium DEM -> smoothed 1 m height field in world metres."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
import geo

def load_dem(path="data/raw/dem_z13.npy", meta_path="data/raw/dem_z13_meta.json"):
    dem = np.load(path)
    meta = eval(open(meta_path).read())
    return dem, meta

def height_field(x0, z0, nx, nz, sigma_px=2.2):
    dem, meta = load_dem()
    dem_s = gaussian_filter(dem.astype(np.float32), sigma_px)
    xs = np.arange(x0, x0 + nx, dtype=np.float64) + 0.5
    zs = np.arange(z0, z0 + nz, dtype=np.float64) + 0.5
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    H = geo.dem_to_world(dem_s, meta, X, Z)
    return H.astype(np.float32)

def road_correction(H, road_mask_pts, radius=7.0, sigma=4.0):
    """Pull terrain toward a smoothed profile along roads, ramped outward."""
    from scipy.ndimage import gaussian_filter
    n = H.shape[0] * H.shape[1]
    C = np.zeros_like(H)
    W = np.zeros_like(H)
    for (px, pz, tgt) in road_mask_pts:
        pass
    return C, W

def relief_png(H, path, step=4):
    """Hillshaded relief for sanity checking."""
    from PIL import Image
    gy, gx = np.gradient(H[::step, ::step])
    az, alt = np.radians(315), np.radians(45)
    slope = np.arctan(np.hypot(gx, gy) / step)
    aspect = np.arctan2(-gx, gy)
    shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    lo, hi = np.percentile(H, [1, 99])
    norm = np.clip((H[::step, ::step] - lo) / max(1e-6, hi - lo), 0, 1)
    rgb = np.stack([norm * 0.55 + 0.25 * shade, norm * 0.5 + 0.3 * shade + 0.15, norm * 0.35 + 0.2 * shade + 0.05], -1)
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(path)
