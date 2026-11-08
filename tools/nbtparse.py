"""NBT reader that returns trees made of tools.nbt wrapper objects (re-emittable)."""
import gzip, struct, io
import numpy as np
import nbt as N

class R:
    def __init__(self, buf):
        self.b = buf; self.i = 0
    def take(self, n):
        v = self.b[self.i:self.i + n]; self.i += n; return v
    def u1(self): return self.take(1)[0]
    def i2(self): return struct.unpack(">h", self.take(2))[0]
    def u2(self): return struct.unpack(">H", self.take(2))[0]
    def i4(self): return struct.unpack(">i", self.take(4))[0]
    def i8(self): return struct.unpack(">q", self.take(8))[0]
    def f4(self): return struct.unpack(">f", self.take(4))[0]
    def f8(self): return struct.unpack(">d", self.take(8))[0]
    def s(self):
        n = self.u2(); return self.take(n).decode("utf-8")

def _val(r, t):
    if t == 0: return None
    if t == 1: return N.B(struct.unpack(">b", r.take(1))[0])
    if t == 2: return N.S(r.i2())
    if t == 3: return N.I(r.i4())
    if t == 4: return N.L(r.i8())
    if t == 5: return N.F(r.f4())
    if t == 6: return N.D(r.f8())
    if t == 7:
        n = r.i4(); return N.IA(list(r.take(n)))
    if t == 8: return N.Str(r.s())
    if t == 9:
        tt = r.u1(); n = r.i4()
        return N.Lst(tt, [_val(r, tt) for _ in range(n)])
    if t == 10: return _compound(r)
    if t == 11:
        n = r.i4(); return N.IA(list(np.frombuffer(r.take(4 * n), dtype=">i4")))
    if t == 12:
        n = r.i4(); return N.LA(np.frombuffer(r.take(8 * n), dtype=">i8").copy())
    raise ValueError(f"tag {t}")

def _compound(r):
    out = {}
    while True:
        t = r.u1()
        if t == 0: return out
        name = r.s()
        out[name] = _val(r, t)

def load(path):
    raw = open(path, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    r = R(raw)
    t = r.u1(); name = r.s()
    return name, _val(r, t)

def save(path, name, tree, gz=True):
    raw = N.NBT().root(name, tree)
    if gz:
        with gzip.open(path, "wb") as f: f.write(raw)
    else:
        open(path, "wb").write(raw)
