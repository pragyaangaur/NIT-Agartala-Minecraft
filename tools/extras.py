"""Features digitised from Esri World Imagery (no OSM record). Source: visual digitisation.

Each entry records what was seen in the reference image so the provenance is auditable.
"""
import numpy as np

# Oval running ground: a bare-earth oval track around a lighter infield, north campus.
TRACK = dict(cx=960.0, cz=278.0, rx=72.0, rz=68.0, width=7.0,
             note="oval track of bare earth with a lighter infield, visible at 0.55 m/px in Esri World Imagery")
# Long red-tile hall east of the oval (large-span shed, ~145x80 m)
RED_HALL = dict(name="Indoor Stadium (unmapped)",
                pts=[(1035, 268), (1180, 268), (1180, 348), (1035, 348)],
                note="long pitched red roof, 145x80 m, immediately east of the oval ground")
# Circular hall with a red conical roof, diameter ~90 m
ROUND_HALL = dict(name="Circular Hall (unmapped)", cx=1247.0, cz=394.0, r=45.0,
                  note="circular building with a red conical/radial roof, ~90 m across, north campus")

def ellipse_ring_mask(nx, nz, x0, z0, cx, cz, rx, rz, w):
    X = x0 + np.arange(nx) + 0.5
    Z = z0 + np.arange(nz) + 0.5
    XX, ZZ = np.meshgrid(X, Z, indexing="ij")
    d = np.hypot((XX - cx) / rx, (ZZ - cz) / rz)
    din = np.hypot((XX - cx) / max(1e-3, rx - w), (ZZ - cz) / max(1e-3, rz - w))
    return (d <= 1.0) & (din > 1.0)

def ellipse_mask(nx, nz, x0, z0, cx, cz, rx, rz):
    X = x0 + np.arange(nx) + 0.5
    Z = z0 + np.arange(nz) + 0.5
    XX, ZZ = np.meshgrid(X, Z, indexing="ij")
    return np.hypot((XX - cx) / rx, (ZZ - cz) / rz) <= 1.0

def circle_poly(cx, cz, r, n=40):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [(cx + r * np.cos(t), cz + r * np.sin(t)) for t in a]
