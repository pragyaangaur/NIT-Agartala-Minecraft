"""Read a box of blocks back out of a 26.3 world save into a Vox grid.

python3 readworld.py world_dir x0 y0 z0 x1 y1 z1 out_prefix
"""
import os, sys, struct, zlib, gzip, io
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vox import Vox


class R:
    def __init__(self, b): self.b, self.i = b, 0
    def take(self, n):
        v = self.b[self.i:self.i + n]; self.i += n; return v
    def tag(self, t):
        if t == 1: return struct.unpack(">b", self.take(1))[0]
        if t == 2: return struct.unpack(">h", self.take(2))[0]
        if t == 3: return struct.unpack(">i", self.take(4))[0]
        if t == 4: return struct.unpack(">q", self.take(8))[0]
        if t == 5: return struct.unpack(">f", self.take(4))[0]
        if t == 6: return struct.unpack(">d", self.take(8))[0]
        if t == 7:
            n = struct.unpack(">i", self.take(4))[0]; return self.take(n)
        if t == 8:
            n = struct.unpack(">H", self.take(2))[0]; return self.take(n).decode("utf-8", "replace")
        if t == 9:
            et = self.take(1)[0]; n = struct.unpack(">i", self.take(4))[0]
            return [self.tag(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                et = self.take(1)[0]
                if et == 0: return d
                n = struct.unpack(">H", self.take(2))[0]; k = self.take(n).decode()
                d[k] = self.tag(et)
        if t == 11:
            n = struct.unpack(">i", self.take(4))[0]
            return np.frombuffer(self.take(4 * n), ">i4")
        if t == 12:
            n = struct.unpack(">i", self.take(4))[0]
            return np.frombuffer(self.take(8 * n), ">i8")
        raise ValueError(t)


def read_chunk(region_dir, cx, cz, cache={}):
    rx, rz = cx >> 5, cz >> 5
    path = os.path.join(region_dir, f"r.{rx}.{rz}.mca")
    if path not in cache:
        cache[path] = open(path, "rb").read() if os.path.exists(path) else None
    data = cache[path]
    if data is None: return None
    idx = 4 * ((cx & 31) + (cz & 31) * 32)
    off = int.from_bytes(data[idx:idx + 3], "big")
    if off == 0: return None
    p = off * 4096
    ln = struct.unpack(">i", data[p:p + 4])[0]
    comp = data[p + 4]
    raw = data[p + 5:p + 4 + ln]
    raw = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw) if comp == 1 else raw
    r = R(raw); t = r.take(1)[0]; r.take(struct.unpack(">H", r.take(2))[0])
    return r.tag(t)


def state_name(p):
    if isinstance(p, str):
        return p.replace("minecraft:", "")
    name = p.get("Name") or p.get("id") or p.get("")
    props = p.get("Properties") or p.get("properties")
    name = name.replace("minecraft:", "")
    if props:
        name += "[" + ",".join(f"{k}={v}" for k, v in sorted(props.items())) + "]"
    return name


def section_blocks(sec):
    bs = sec.get("block_states") or {}
    pal = [state_name(p) for p in bs.get("palette", [])]
    data = bs.get("data")
    if data is None or len(pal) == 1:
        return np.full(4096, 0, int), pal
    bits = max(4, (len(pal) - 1).bit_length())
    per = 64 // bits
    u = data.astype(np.uint64)
    idx = np.zeros(4096, int)
    mask = np.uint64((1 << bits) - 1)
    for i in range(4096):
        idx[i] = int((u[i // per] >> np.uint64((i % per) * bits)) & mask)
    return idx, pal


def read_box(world, x0, y0, z0, x1, y1, z1):
    region = os.path.join(world, "dimensions", "minecraft", "overworld", "region")
    v = Vox(x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1)
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            ch = read_chunk(region, cx, cz)
            if ch is None: continue
            for sec in ch.get("sections", []):
                sy = sec["Y"]
                if (sy + 1) * 16 <= y0 or sy * 16 > y1: continue
                idx, pal = section_blocks(sec)
                if not pal: continue
                arr = np.array(pal, dtype=object)[idx].reshape(16, 16, 16)   # [y][z][x]
                for ly in range(16):
                    y = sy * 16 + ly
                    if not (y0 <= y <= y1): continue
                    for lz in range(16):
                        z = cz * 16 + lz
                        if not (z0 <= z <= z1): continue
                        for lx in range(16):
                            x = cx * 16 + lx
                            if not (x0 <= x <= x1): continue
                            b = arr[ly, lz, lx]
                            if b not in ("air", "cave_air", "void_air"):
                                v.a[x - x0, y - y0, z - z0] = b
    return v


if __name__ == "__main__":
    w = sys.argv[1]; x0, y0, z0, x1, y1, z1 = map(int, sys.argv[2:8]); out = sys.argv[8]
    v = read_box(w, x0, y0, z0, x1, y1, z1)
    for view in ("ne", "nw", "se"):
        v.iso(view, 5).save(f"{out}_{view}.png")
    v.elevation("north", 6).save(f"{out}_north.png")
    print("ok", v.shape)
