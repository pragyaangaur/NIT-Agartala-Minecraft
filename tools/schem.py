"""Export a building region as a Sponge Schematic v3 (.schem) file."""
import os, gzip
import numpy as np
import nbt

def _varint(v, out):
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return

def write_schem(path, vol_sub, pal, ybase):
    """vol_sub: (W, L, H) palette indices [x, z, y]; y order is world up."""
    W, L, H = vol_sub.shape
    uniq = np.unique(vol_sub)
    used = [int(u) for u in uniq]
    pal_items = []
    remap = {}
    for i, u in enumerate(used):
        nm, pr = pal[u]
        d = {"Name": nbt.Str(nm)}
        if pr:
            d["Properties"] = {k: nbt.Str(v) for k, v in pr.items()}
        pal_items.append(d)
        remap[u] = i
    data = bytearray()
    for y in range(H):
        for z in range(L):
            for x in range(W):
                _varint(remap[int(vol_sub[x, z, y])], data)
    schem = {
        "Schematic": {
            "Version": nbt.I(3),
            "DataVersion": nbt.I(5023),
            "Width": nbt.S(W),
            "Height": nbt.S(H),
            "Length": nbt.S(L),
            "Offset": nbt.IA([0, 0, 0]),
            "Palettes": nbt.Lst(nbt.TAG_COMPOUND, [{"Palette": nbt.compound_list(pal_items)}]),
            "Blocks": nbt.IA(np.frombuffer(bytes(data), dtype=np.uint8).astype(np.int32)),
            "BlockEntities": nbt.compound_list([]),
        },
        "Metadata": {"Name": nbt.Str(os.path.basename(path)[:-6]),
                     "Author": nbt.Str("NIT Agartala 1:1 reconstruction"),
                     "Description": nbt.Str("1 block = 1 metre; origin at the SW corner of the bounding box")},
    }
    raw = nbt.NBT().root("Schematic", schem["Schematic"])
    with gzip.open(path, "wb") as f:
        f.write(raw)
    return len(used)
