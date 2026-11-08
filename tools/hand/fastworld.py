"""Fast, numpy-based reading of a 26.3 world box: block ids per cell plus one shared name table.

load(world, x0, y0, z0, x1, y1, z1) -> (ids[int32, x, y, z], names[list of str])
names[0] is always "air". Block states are kept ("oak_leaves[distance=3,...]").
"""
import os, struct, zlib, gzip
import numpy as np
from readworld import R, state_name

_cache = {}


def _region(world, rx, rz):
    p = os.path.join(world, "dimensions", "minecraft", "overworld", "region", f"r.{rx}.{rz}.mca")
    if p not in _cache:
        _cache[p] = open(p, "rb").read() if os.path.exists(p) else None
    return _cache[p]


def clear_cache():
    _cache.clear()


def chunk(world, cx, cz):
    data = _region(world, cx >> 5, cz >> 5)
    if data is None:
        return None
    idx = 4 * ((cx & 31) + (cz & 31) * 32)
    off = int.from_bytes(data[idx:idx + 3], "big")
    if off == 0:
        return None
    p = off * 4096
    ln = struct.unpack(">i", data[p:p + 4])[0]
    comp = data[p + 4]
    raw = data[p + 5:p + 4 + ln]
    raw = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw) if comp == 1 else raw
    r = R(raw); t = r.take(1)[0]; r.take(struct.unpack(">H", r.take(2))[0])
    return r.tag(t)


def unpack(data, n_pal):
    bits = max(4, (n_pal - 1).bit_length())
    per = 64 // bits
    u = np.asarray(data).astype(np.int64).view(np.uint64)
    sh = (np.arange(per, dtype=np.uint64) * np.uint64(bits))
    vals = (u[:, None] >> sh[None, :]) & np.uint64((1 << bits) - 1)
    return vals.reshape(-1)[:4096].astype(np.int32)


def load(world, x0, y0, z0, x1, y1, z1, names=None, lut=None):
    names = names if names is not None else ["air"]
    lut = lut if lut is not None else {"air": 0, "cave_air": 0, "void_air": 0}
    out = np.zeros((x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1), np.int32)
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            ch = chunk(world, cx, cz)
            if ch is None:
                continue
            for sec in ch.get("sections", []):
                sy = sec["Y"]
                if (sy + 1) * 16 <= y0 or sy * 16 > y1:
                    continue
                bs = sec.get("block_states") or {}
                pal = [state_name(p) for p in bs.get("palette", [])]
                if not pal:
                    continue
                g = []
                for nm in pal:
                    if nm not in lut:
                        lut[nm] = len(names); names.append(nm)
                    g.append(lut[nm])
                g = np.array(g, np.int32)
                d = bs.get("data")
                idx = np.zeros(4096, np.int32) if d is None or len(pal) == 1 else unpack(d, len(pal))
                arr = g[idx].reshape(16, 16, 16)            # [y, z, x]
                ys, zs, xs = sy * 16, cz * 16, cx * 16
                ya, yb = max(y0, ys), min(y1, ys + 15)
                za, zb = max(z0, zs), min(z1, zs + 15)
                xa, xb = max(x0, xs), min(x1, xs + 15)
                if ya > yb or za > zb or xa > xb:
                    continue
                blk = arr[ya - ys:yb - ys + 1, za - zs:zb - zs + 1, xa - xs:xb - xs + 1]
                out[xa - x0:xb - x0 + 1, ya - y0:yb - y0 + 1, za - z0:zb - z0 + 1] = blk.transpose(2, 0, 1)
    return out, names, lut
