"""Minimal NBT writer (big-endian, Java edition)."""
import struct, io
import numpy as np

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = 9, 10, 11, 12

def _s(v):
    b = v.encode("utf-8")
    return struct.pack(">H", len(b)) + b

class NBT:
    """Build NBT trees; root is always a named compound."""
    def __init__(self):
        self.buf = io.BytesIO()

    def _tag(self, tid, name, payload):
        self.buf.write(struct.pack(">B", tid)); self.buf.write(_s(name)); self.buf.write(payload)

    def root(self, name, d):
        self._tag(TAG_COMPOUND, name, self._compound(d))
        return self.buf.getvalue()

    def _compound(self, d):
        out = io.BytesIO()
        for k, v in d.items():
            out.write(_payload(k, v))
        out.write(struct.pack(">B", TAG_END))
        return out.getvalue()

def _payload(name, v):
    """Encode one named tag. Types are chosen by Python type / wrapper classes."""
    n = _s(name)
    if isinstance(v, Bool):
        return struct.pack(">B", TAG_BYTE) + n + struct.pack(">b", 1 if v.v else 0)
    if isinstance(v, B):
        return struct.pack(">B", TAG_BYTE) + n + struct.pack(">b", int(v.v))
    if isinstance(v, S):
        return struct.pack(">B", TAG_SHORT) + n + struct.pack(">h", int(v.v))
    if isinstance(v, I):
        return struct.pack(">B", TAG_INT) + n + struct.pack(">i", int(v.v))
    if isinstance(v, L):
        return struct.pack(">B", TAG_LONG) + n + struct.pack(">q", int(v.v))
    if isinstance(v, F):
        return struct.pack(">B", TAG_FLOAT) + n + struct.pack(">f", float(v.v))
    if isinstance(v, D):
        return struct.pack(">B", TAG_DOUBLE) + n + struct.pack(">d", float(v.v))
    if isinstance(v, Str):
        return struct.pack(">B", TAG_STRING) + n + _s(str(v.v))
    if isinstance(v, LA):
        a = np.asarray(v.v, dtype=">i8").tobytes()
        return struct.pack(">B", TAG_LONG_ARRAY) + n + struct.pack(">i", len(v.v)) + a
    if isinstance(v, IA):
        a = np.asarray(v.v, dtype=">i4").tobytes()
        return struct.pack(">B", TAG_INT_ARRAY) + n + struct.pack(">i", len(v.v)) + a
    if isinstance(v, C):
        return struct.pack(">B", TAG_COMPOUND) + n + _compound_body(v.v)
    if isinstance(v, Lst):
        return struct.pack(">B", TAG_LIST) + n + _list_body(v)
    if isinstance(v, dict):
        return struct.pack(">B", TAG_COMPOUND) + n + _compound_body(v)
    raise TypeError(f"unsupported {type(v)} for {name}")

def _compound_body(d):
    out = io.BytesIO()
    for k, v in d.items():
        out.write(_payload(k, v))
    out.write(struct.pack(">B", TAG_END))
    return out.getvalue()

# wrapper types
class B:  __slots__=("v",);
class B(B):  pass
def _mk(name):
    class _W:
        __slots__ = ("v",)
        def __init__(self, v): self.v = v
    _W.__name__ = name
    return _W
B   = _mk("B");   S  = _mk("S");  I = _mk("I");  L = _mk("L")
F   = _mk("F");   D  = _mk("D");  Str = _mk("Str"); IA = _mk("IA"); LA = _mk("LA")
C   = _mk("C")
class Bool(_mk("Bool")): pass

class Lst:
    __slots__ = ("tid", "items")
    def __init__(self, tid, items=()):
        self.tid = tid; self.items = list(items)

def compound_list(items):
    return Lst(TAG_COMPOUND, items)


def _list_body(lst):
    out = io.BytesIO()
    out.write(struct.pack(">B", lst.tid))
    out.write(struct.pack(">i", len(lst.items)))
    for it in lst.items:
        body = _val_body(lst.tid, it)
        out.write(body)
    return out.getvalue()

def _val_body(t, v):
    if t == TAG_COMPOUND: return _compound_body(v)
    if t == TAG_STRING:   return _s(str(v.v if isinstance(v, Str) else v))
    if t == TAG_LIST:     return _list_body(v)
    if t == TAG_BYTE:     return struct.pack(">b", int(v.v if hasattr(v, "v") else v))
    if t == TAG_SHORT:    return struct.pack(">h", int(v.v if hasattr(v, "v") else v))
    if t == TAG_INT:      return struct.pack(">i", int(v.v if hasattr(v, "v") else v))
    if t == TAG_LONG:     return struct.pack(">q", int(v.v if hasattr(v, "v") else v))
    if t == TAG_FLOAT:    return struct.pack(">f", float(v.v if hasattr(v, "v") else v))
    if t == TAG_DOUBLE:   return struct.pack(">d", float(v.v if hasattr(v, "v") else v))
    if t == TAG_INT_ARRAY:
        a = np.asarray(v.v if hasattr(v, "v") else v, dtype=">i4")
        return struct.pack(">i", a.size) + a.tobytes()
    if t == TAG_LONG_ARRAY:
        a = np.asarray(v.v if hasattr(v, "v") else v, dtype=">i8")
        return struct.pack(">i", a.size) + a.tobytes()
    if t == TAG_BYTE_ARRAY:
        a = np.asarray(v.v if hasattr(v, "v") else v, dtype=">i1")
        return struct.pack(">i", a.size) + a.tobytes()
    raise TypeError(f"val body {t}")
