"""Write a voxel volume as an Anvil (region) world. Minecraft Java 26.3."""
import os, zlib, struct, time
import numpy as np
from numba import njit
import nbt

DATA_VERSION = 5023
MIN_SECTION, MAX_SECTION = -4, 19
MIN_Y = MIN_SECTION * 16            # -64

@njit(cache=True)
def _pack(idx_flat, bpe, out_len):
    out = np.zeros(out_len, dtype=np.uint64)
    for i in range(idx_flat.shape[0]):
        v = np.uint64(idx_flat[i])
        bit = i * bpe
        j = bit >> 6
        off = bit & 63
        out[j] |= np.uint64(v << np.uint64(off))
        if off + bpe > 64:
            out[j + 1] |= np.uint64(v >> np.uint64(64 - off))
    return out

@njit(cache=True)
def _heightmap(col_top):
    n = col_top.shape[0]; per = 7; bits = 9
    out = np.zeros((n + per - 1) // per, dtype=np.int64)
    for i in range(n):
        v = np.int64(max(0, col_top[i] - MIN_Y))
        out[i // per] |= v << np.int64((i % per) * bits)
    return out

def _pal_entry(pal, u):
    """26.3 block-state palette entry: compound with lowercase id/properties."""
    nm, pr = pal[u]
    d = {"id": nbt.Str(nm)}
    if pr:
        d["properties"] = {k: nbt.Str(v) for k, v in pr.items()}
    return d

def chunk_nbt(blk312, cx, cz, pal):
    """blk312: (16,16,16) uint16 palette indices, indexed [y][z][x]."""
    uniq = np.unique(blk312)
    if len(uniq) == 1 and uniq[0] == 0:
        return None
    items = [_pal_entry(pal, u) for u in uniq]
    bs = {"palette": nbt.compound_list(items)}
    if len(uniq) > 1:
        remap = np.zeros(int(uniq.max()) + 1, dtype=np.int16)
        remap[uniq] = np.arange(len(uniq), dtype=np.int16)
        idx = remap[blk312].reshape(-1).astype(np.int64)
        bpe = max(4, int(np.ceil(np.log2(max(2, len(uniq))))))
        bs["data"] = nbt.LA(_pack(idx, bpe, (idx.size * bpe + 63) // 64))
    return bs

def chunk_bytes(vol, cx, cz, pal, ybase, ox=0, oz=0):
    """vol indexed [x, z, y] with y index 0 == ybase."""
    x0, z0 = cx * 16 - ox, cz * 16 - oz
    sub = vol[x0:x0 + 16, z0:z0 + 16, :]
    if sub.shape[0] != 16 or sub.shape[1] != 16:
        raise ValueError("volume does not cover chunk")
    a = np.transpose(sub, (2, 1, 0))                    # [y][z][x]
    nz_y = np.nonzero((a != 0).any(axis=(1, 2)))[0]
    if len(nz_y) == 0:
        return None
    sec_items = []
    for yabs in range(ybase + nz_y.min(), ybase + nz_y.max() + 1):
        pass
    first = (ybase + nz_y.min()) // 16
    last = (ybase + nz_y.max()) // 16
    for sY in range(first, last + 1):
        lo, hi = sY * 16 - ybase, sY * 16 - ybase + 16
        blk = np.zeros((16, 16, 16), dtype=np.uint16)
        slo, shi = max(lo, 0), min(hi, a.shape[0])
        if shi > slo:
            blk[slo - lo:shi - lo] = a[slo:shi]
        bs = chunk_nbt(blk, cx, cz, pal)
        if bs is None:
            continue
        sec_items.append({"Y": nbt.B(sY), "block_states": bs,
                          "biomes": {"palette": nbt.Lst(nbt.TAG_STRING, [nbt.Str("minecraft:forest")])}})
    # fill everything below the modelled volume with stone / bedrock
    if sec_items:
        firsts = min(e["Y"].v for e in sec_items)
        for sY in range(0, firsts):
            nm = "minecraft:bedrock" if sY == 0 else "minecraft:stone"
            sec_items.append({"Y": nbt.B(sY),
                              "block_states": {"palette": nbt.compound_list([{"id": nbt.Str(nm)}])},
                              "biomes": {"palette": nbt.Lst(nbt.TAG_STRING, [nbt.Str("minecraft:forest")])}})
    if not sec_items:
        return None
    solid = a != 0
    topy = np.zeros(256, dtype=np.int64)
    for i in range(16):
        for j in range(16):
            nzz = np.nonzero(solid[:, i, j])[0]
            topy[i * 16 + j] = ybase + nzz[-1] if len(nzz) else MIN_Y
    hm = _heightmap(topy)
    nsec = MAX_SECTION - MIN_SECTION + 1
    sec_items.sort(key=lambda e: e["Y"].v)
    chunk = {
        "DataVersion": nbt.I(DATA_VERSION),
        "xPos": nbt.I(cx), "yPos": nbt.I(MIN_SECTION), "zPos": nbt.I(cz),
        "Status": nbt.Str("minecraft:full"),
        "LastUpdate": nbt.L(0), "InhabitedTime": nbt.L(0),
        "isLightOn": nbt.Bool(False),
        "sections": nbt.compound_list(sec_items),
        "Heightmaps": {"MOTION_BLOCKING": nbt.LA(hm), "WORLD_SURFACE": nbt.LA(hm),
                       "OCEAN_FLOOR": nbt.LA(hm), "MOTION_BLOCKING_NO_LEAVES": nbt.LA(hm)},
        "block_entities": nbt.compound_list([]),
        "block_ticks": nbt.compound_list([]),
        "fluid_ticks": nbt.compound_list([]),
        "structures": {"starts": {}, "References": {}},
        "PostProcessing": nbt.Lst(nbt.TAG_LIST, [nbt.Lst(nbt.TAG_SHORT, []) for _ in range(nsec)]),
    }
    return zlib.compress(nbt.NBT().root("", chunk), 6)

def write_region(path, rx, rz, chunks):
    buf = bytearray(8192)
    sec = 2
    for (lx, lz), data in chunks.items():
        n = (len(data) + 5 + 4095) // 4096
        if n > 255:
            raise ValueError("chunk too big")
        i = 4 * (lx + lz * 32)
        buf[i:i + 3] = sec.to_bytes(3, "big")
        buf[i + 3] = n
        buf += struct.pack(">iB", len(data) + 1, 2) + data
        buf += b"\x00" * (n * 4096 - (len(data) + 5))
        sec += n
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(buf)

def write_world(vol, pal, outdir, name, ybase, x0, z0, spawn, levelname, verbose=True, region_cb=None):
    """vol[x,z,y], x index 0 == world x0, likewise z. Bounds must be multiples of 16."""
    assert x0 % 16 == 0 and z0 % 16 == 0
    nx, nz, ny = vol.shape
    assert nx % 16 == 0 and nz % 16 == 0
    x1, z1 = x0 + nx, z0 + nz
    wdir = os.path.join(outdir, name)
    os.makedirs(os.path.join(wdir, "region"), exist_ok=True)
    t0 = time.time(); nchunks = 0
    for rx in range(x0 // 512, (x1 - 1) // 512 + 1):
        for rz in range(z0 // 512, (z1 - 1) // 512 + 1):
            chunks = {}
            for cx in range(rx * 32, rx * 32 + 32):
                if cx * 16 < x0 or cx * 16 >= x1: continue
                for cz in range(rz * 32, rz * 32 + 32):
                    if cz * 16 < z0 or cz * 16 >= z1: continue
                    d = chunk_bytes(vol, cx, cz, pal, ybase, ox=x0, oz=z0)
                    if d is not None:
                        chunks[(cx & 31, cz & 31)] = d
            if chunks:
                write_region(os.path.join(wdir, "region", f"r.{rx}.{rz}.mca"), rx, rz, chunks)
                nchunks += len(chunks)
                if verbose:
                    print(f"  r.{rx}.{rz}: {len(chunks)} chunks ({time.time()-t0:.0f}s, {nchunks} total)", flush=True)
                if region_cb: region_cb(rx, rz)
    import gzip
    d = {"Data": {
        "DataVersion": nbt.I(DATA_VERSION), "version": nbt.I(19133),
        "LevelName": nbt.Str(levelname), "generatorName": nbt.Str("default"),
        "LastPlayed": nbt.L(0), "Time": nbt.L(6000), "DayTime": nbt.L(6000),
        "SpawnX": nbt.I(spawn[0]), "SpawnY": nbt.I(spawn[1]), "SpawnZ": nbt.I(spawn[2]),
        "GameType": nbt.I(1), "Difficulty": nbt.B(1), "DifficultyLocked": nbt.Bool(False),
        "allowCommands": nbt.Bool(True), "initialized": nbt.Bool(True), "hardcore": nbt.Bool(False),
        "raining": nbt.Bool(False), "thundering": nbt.Bool(False),
        "rainTime": nbt.I(0), "thunderTime": nbt.I(0), "clearWeatherTime": nbt.I(0),
        "GameRules": {"doDaylightCycle": nbt.Str("true"), "doWeatherCycle": nbt.Str("false"),
                      "doMobSpawning": nbt.Str("false"), "keepInventory": nbt.Str("true")},
        "WorldGenSettings": {"seed": nbt.L(20261106), "generate_features": nbt.Bool(True),
            "bonus_chest": nbt.Bool(False),
            "dimensions": {"minecraft:overworld": {"type": nbt.Str("minecraft:overworld"),
                "generator": {"type": nbt.Str("minecraft:noise"),
                    "biome_source": {"type": nbt.Str("minecraft:multi_noise"), "preset": nbt.Str("minecraft:overworld")},
                    "settings": nbt.Str("minecraft:overworld")}}}},
        "Version": {"Name": nbt.Str("26.3"), "Id": nbt.I(DATA_VERSION), "Snapshot": nbt.Bool(False)},
    }}
    with gzip.open(os.path.join(wdir, "level.dat"), "wb") as f:
        f.write(nbt.NBT().root("", d))
    print(f"world written: {wdir}  {nchunks} chunks", flush=True)
    return wdir
