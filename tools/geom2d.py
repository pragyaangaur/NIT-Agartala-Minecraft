"""2-D raster helpers operating on the world grid."""
import numpy as np
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt, binary_erosion, label

def raster_poly(poly, x0, z0, nx, nz):
    """Boolean mask for a polygon (x,z metres) over the grid [x0..x0+nx) x [z0..z0+nz)."""
    xs = x0 + np.arange(nx) + 0.5
    zs = z0 + np.arange(nz) + 0.5
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    p = Path(np.asarray(poly, float))
    inside = p.contains_points(np.column_stack([X.ravel(), Z.ravel()]))
    return inside.reshape(nx, nz)

def raster_poly_sub(poly, x0, z0, nx, nz):
    """Rasterise into the bounding box of the polygon; returns (mask, bx0, bz0)."""
    P = np.asarray(poly, float)
    bx0 = int(np.floor(P[:, 0].min())) - 2
    bz0 = int(np.floor(P[:, 1].min())) - 2
    bx1 = int(np.ceil(P[:, 0].max())) + 2
    bz1 = int(np.ceil(P[:, 1].max())) + 2
    bx0 = max(bx0, x0); bz0 = max(bz0, z0)
    bx1 = min(bx1, x0 + nx); bz1 = min(bz1, z0 + nz)
    if bx1 <= bx0 or bz1 <= bz0:
        return np.zeros((1, 1), bool), bx0, bz0
    return raster_poly(poly, bx0, bz0, bx1 - bx0, bz1 - bz0), bx0, bz0

def raster_line(pts, width, x0, z0, nx, nz):
    """Rasterise a polyline with a given width (metres) as a mask."""
    xs = x0 + np.arange(nx) + 0.5
    zs = z0 + np.arange(nz) + 0.5
    m = np.zeros((nx, nz), bool)
    if len(pts) < 2:
        return m
    hw = max(0.35, width / 2.0)
    P = np.asarray(pts, float)
    for (ax, az), (bx, bz) in zip(P[:-1], P[1:]):
        lo_x = int(np.floor(min(ax, bx) - hw)) - x0
        hi_x = int(np.ceil(max(ax, bx) + hw)) - x0
        lo_z = int(np.floor(min(az, bz) - hw)) - z0
        hi_z = int(np.ceil(max(az, bz) + hw)) - z0
        lo_x = max(lo_x, 0); lo_z = max(lo_z, 0)
        hi_x = min(hi_x, nx); hi_z = min(hi_z, nz)
        if hi_x <= lo_x or hi_z <= lo_z:
            continue
        sx = xs[lo_x:hi_x][:, None]
        sz = zs[lo_z:hi_z][None, :]
        dx, dz = bx - ax, bz - az
        L2 = dx * dx + dz * dz
        if L2 < 1e-9:
            d2 = (sx - ax) ** 2 + (sz - az) ** 2
        else:
            t = ((sx - ax) * dx + (sz - az) * dz) / L2
            t = np.clip(t, 0, 1)
            d2 = (sx - (ax + t * dx)) ** 2 + (sz - (az + t * dz)) ** 2
        m[lo_x:hi_x, lo_z:hi_z] |= d2 <= hw * hw
    return m

def dilate(m, n=1):
    if n <= 0: return m
    return distance_transform_edt(~m) <= n

def erode(m, n=1):
    if n <= 0: return m
    return distance_transform_edt(m) > n

def ring(m, thick=1):
    return m & ~erode(m, thick)
