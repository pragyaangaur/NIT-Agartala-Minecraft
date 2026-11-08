"""Make the world end cleanly at the model's edge.

1. The overworld generator becomes flat grass (stone to y 68, dirt, grass at y 72), no
   structures, no lakes, no features, so chunks generated beyond the model are plain fields
   with no animals, villages or loose sand.
2. Chunks entirely outside the model area (x 32..1887, z 64..2047) are deleted from the region,
   entity and poi files, so the vanilla countryside already generated there goes away.
3. A world border is set round the model.
"""
import os, sys, struct, gzip, glob, io
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import place
from mcserver import run

CX0, CX1, CZ0, CZ1 = 32 >> 4, 1887 >> 4, 64 >> 4, 2047 >> 4     # chunks kept: 2..117, 4..127


def w_str(b, s):
    e = s.encode(); b.write(struct.pack(">H", len(e))); b.write(e)


def w_named(b, tid, name, writer):
    b.write(bytes([tid])); w_str(b, name); writer(b)


def compound(items):
    def wr(b):
        for tid, name, fn in items:
            w_named(b, tid, name, fn)
        b.write(b"\x00")
    return wr


def s(v):
    return lambda b: w_str(b, v)


def i32(v):
    return lambda b: b.write(struct.pack(">i", v))


def i64(v):
    return lambda b: b.write(struct.pack(">q", v))


def byte(v):
    return lambda b: b.write(struct.pack(">b", v))


def lst_compounds(comps):
    def wr(b):
        b.write(bytes([10])); b.write(struct.pack(">i", len(comps)))
        for c in comps:
            c(b)
    return wr


def lst_empty():
    return lambda b: (b.write(bytes([0])), b.write(struct.pack(">i", 0)))


def noise(settings, preset, dim):
    return compound([(8, "settings", s(settings)),
                     (10, "biome_source", compound([(8, "preset", s(preset)), (8, "type", s("minecraft:multi_noise"))])),
                     (8, "type", s("minecraft:noise"))])


def write_gen(path, seed, dataversion):
    flat = compound([
        (10, "settings", compound([
            (9, "layers", lst_compounds([
                compound([(8, "block", s("minecraft:bedrock")), (3, "height", i32(1))]),
                compound([(8, "block", s("minecraft:stone")), (3, "height", i32(132))]),
                compound([(8, "block", s("minecraft:dirt")), (3, "height", i32(3))]),
                compound([(8, "block", s("minecraft:grass_block")), (3, "height", i32(1))]),
            ])),
            (8, "biome", s("minecraft:plains")),
            (1, "lakes", byte(0)),
            (1, "features", byte(0)),
            (9, "structure_overrides", lst_empty()),
        ])),
        (8, "type", s("minecraft:flat")),
    ])
    nether = compound([(8, "settings", s("minecraft:nether")),
                       (10, "biome_source", compound([(8, "preset", s("minecraft:nether")), (8, "type", s("minecraft:multi_noise"))])),
                       (8, "type", s("minecraft:noise"))])
    end = compound([(8, "settings", s("minecraft:end")),
                    (10, "biome_source", compound([(8, "type", s("minecraft:the_end"))])),
                    (8, "type", s("minecraft:noise"))])
    root = compound([
        (10, "data", compound([
            (1, "bonus_chest", byte(0)),
            (4, "seed", i64(seed)),
            (1, "generate_structures", byte(0)),
            (10, "dimensions", compound([
                (10, "minecraft:overworld", compound([(10, "generator", flat), (8, "type", s("minecraft:overworld"))])),
                (10, "minecraft:the_nether", compound([(10, "generator", nether), (8, "type", s("minecraft:the_nether"))])),
                (10, "minecraft:the_end", compound([(10, "generator", end), (8, "type", s("minecraft:the_end"))])),
            ])),
        ])),
        (3, "DataVersion", i32(dataversion)),
    ])
    b = io.BytesIO()
    b.write(bytes([10])); w_str(b, ""); root(b)
    with gzip.open(path, "wb") as f:
        f.write(b.getvalue())


def prune(world):
    n = 0
    for kind in ("region", "entities", "poi"):
        for f in glob.glob(os.path.join(world, "dimensions/minecraft/overworld", kind, "r.*.mca")):
            rx, rz = map(int, os.path.basename(f).split(".")[1:3])
            data = bytearray(open(f, "rb").read())
            if len(data) < 8192:
                continue
            changed = False
            for lz in range(32):
                for lx in range(32):
                    cx, cz = rx * 32 + lx, rz * 32 + lz
                    if CX0 <= cx <= CX1 and CZ0 <= cz <= CZ1:
                        continue
                    i = 4 * (lx + lz * 32)
                    if data[i:i + 4] != b"\x00\x00\x00\x00":
                        data[i:i + 4] = b"\x00\x00\x00\x00"; data[4096 + i:4096 + i + 4] = b"\x00\x00\x00\x00"
                        changed = True; n += 1
            if changed:
                keep = any(data[i:i + 4] != b"\x00\x00\x00\x00" for i in range(0, 4096, 4))
                if keep:
                    open(f, "wb").write(data)
                else:
                    os.remove(f)
    return n


if __name__ == "__main__":
    w = place.WORLD
    p = os.path.join(w, "data/minecraft/world_gen_settings.dat")
    raw = gzip.open(p).read()
    i = raw.index(b"seed") + 4
    seed = struct.unpack(">q", raw[i:i + 8])[0]
    write_gen(p, seed, 5023)
    print("pruned chunk entries:", prune(w))
    log = run(w, ["worldborder center 960 1056", "worldborder set 1984", "worldborder warning distance 8",
                  "forceload add -40 1000 -20 1020", "forceload remove all"], wait_load=4)
    print([l[40:200] for l in log.splitlines() if "border" in l.lower() or "rror" in l or "xception" in l][:6])
