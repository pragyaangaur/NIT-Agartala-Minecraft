"""Whole-world audit: find and fix blocks that float, would break, or would fall.

Checks, per 256 m tile with a 48 m overlap:
  floating   solid pieces not connected to the ground (3D connected components)
  plants     grass, flowers, ferns, bushes, saplings, sugar cane without proper support
  beds       bed halves without their partner
  hanging    hanging lanterns with nothing above, carpets/lily pads/cakes with nothing below
  gravity    sand, gravel and concrete powder with air below
python3 audit.py report   -> counts only
python3 audit.py fix      -> writes and runs the fix commands
"""
import sys, os, json
import numpy as np
from scipy.ndimage import label
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fastworld as fw
import place
from mcserver import run, write_functions, forceload_cmds

Y0, Y1 = 56, 140
SOIL = ("grass_block", "dirt", "podzol", "coarse_dirt", "moss_block", "mud", "rooted_dirt", "farmland", "dirt_path")
PLANTS = ("short_grass", "tall_grass", "fern", "large_fern", "dandelion", "poppy", "blue_orchid", "allium",
          "azure_bluet", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip", "oxeye_daisy", "cornflower",
          "lily_of_the_valley", "sunflower", "lilac", "rose_bush", "peony", "bush", "firefly_bush", "sweet_berry_bush",
          "dead_bush", "wildflowers", "pink_petals", "leaf_litter", "short_dry_grass", "tall_dry_grass",
          "oak_sapling", "dark_oak_sapling", "jungle_sapling", "birch_sapling", "spruce_sapling", "acacia_sapling",
          "cherry_sapling", "mangrove_propagule", "azalea", "flowering_azalea", "bamboo", "bamboo_sapling",
          "brown_mushroom", "red_mushroom", "torchflower", "pitcher_plant")
NONSOLID = ("air", "light", "water", "lava") + PLANTS + ("sugar_cane", "lily_pad", "seagrass", "tall_seagrass",
            "vine", "glow_lichen", "cobweb")
GRAVITY = {"sand": "smooth_sandstone", "red_sand": "smooth_red_sandstone", "gravel": "andesite",
           "suspicious_sand": "smooth_sandstone", "suspicious_gravel": "andesite"}


def base(n):
    return n.split("[")[0].split("{")[0]


def classify(names):
    b = [base(n) for n in names]
    cat = {
        "air": np.array([x in ("air",) for x in b]),
        "light": np.array([x == "light" for x in b]),
        "water": np.array([x in ("water", "seagrass", "tall_seagrass", "kelp", "kelp_plant") for x in b]),
        "soil": np.array([x in SOIL for x in b]),
        "plant": np.array([x in PLANTS for x in b]),
        "cane": np.array([x == "sugar_cane" for x in b]),
        "lily": np.array([x == "lily_pad" for x in b]),
        "needs_below": np.array([x.endswith("_carpet") or x in ("cake", "flower_pot", "decorated_pot", "brewing_stand")
                                 or x.startswith("potted_") or (x == "lantern" and "hanging=false" in n)
                                 for x, n in zip(b, names)]),
        "hanging": np.array([x == "lantern" and "hanging=true" in n for x, n in zip(b, names)]),
        "gravity": np.array([x in GRAVITY or x.endswith("_concrete_powder") for x in b]),
        "bed_head": np.array([x.endswith("_bed") and "part=head" in n for x, n in zip(b, names)]),
        # a bed foot facing north is the default state, which the save stores with no properties
        "bed_foot": np.array([x.endswith("_bed") and ("part=foot" in n or "[" not in n) for x, n in zip(b, names)]),
        "upper": np.array(["half=upper" in n for n in names]),
    }
    cat["solid"] = ~np.array([x in NONSOLID for x in b])
    return cat, b


FACE = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}


def audit_tile(world, tx, tz, margin=48):
    x0, z0 = max(tx * 256 - margin, 32), max(tz * 256 - margin, 64)
    x1, z1 = min(tx * 256 + 255 + margin, 1887), min(tz * 256 + 255 + margin, 2047)
    if x0 >= x1 or z0 >= z1:
        return {}, []
    ids, names, lut = fw.load(world, x0, Y0, z0, x1, Y1, z1)
    cat, b = classify(names)
    C = {k: v[ids] for k, v in cat.items()}
    core = np.zeros(ids.shape[::2], bool)                      # cells this tile owns
    cx0, cz0 = max(tx * 256, 32) - x0, max(tz * 256, 64) - z0
    core[cx0:cx0 + 256, cz0:cz0 + 256] = True
    fixes = {}

    def put(i, y, k, blk, why):
        if core[i, k]:
            fixes[(x0 + i, Y0 + y, z0 + k)] = (blk, why)

    # floating: connected components of anything not air/light, ground = bottom layer
    occ = ~(C["air"] | C["light"])
    lab, n = label(occ)
    grounded = set(np.unique(lab[:, 0, :])) - {0}
    if n:
        sizes = np.bincount(lab.ravel(), minlength=n + 1)
        bad = np.setdiff1d(np.arange(1, n + 1), list(grounded))
        badmask = np.isin(lab, bad)
        for i, y, k in np.argwhere(badmask):
            put(i, y, k, "air", "floating")
    below = np.zeros_like(ids); below[:, 1:, :] = ids[:, :-1, :]
    above = np.zeros_like(ids); above[:, :-1, :] = ids[:, 1:, :]
    Bsoil, Bsame = cat["soil"][below], (below == ids)
    Bwater, Bsolid = cat["water"][below], cat["solid"][below]
    Asolid = cat["solid"][above] | np.array([x in ("iron_bars", "chain", "andesite_wall") or x.endswith("_fence")
                                            or x.endswith("_wall") or x.endswith("slab") for x in b])[above]
    # plants need soil (or the lower half of themselves)
    m = C["plant"] & ~Bsoil & ~(C["upper"] & Bsame)
    for i, y, k in np.argwhere(m):
        put(i, y, k, "air", "plant without soil")
    # sugar cane: base on soil next to water, or on more cane
    W = C["water"]
    nearw = np.zeros_like(W)
    nearw[1:, :, :] |= W[:-1]; nearw[:-1] |= W[1:]; nearw[:, :, 1:] |= W[:, :, :-1]; nearw[:, :, :-1] |= W[:, :, 1:]
    nb = np.zeros_like(W); nb[:, 1:, :] = nearw[:, :-1, :]               # water beside the block below
    canebase = C["cane"] & ~Bsame
    m = canebase & ~(Bsoil & nb)
    bad_cane = np.argwhere(m)
    for i, y, k in bad_cane:
        yy = y
        while yy < ids.shape[1] and C["cane"][i, yy, k]:
            put(i, yy, k, "air", "sugar cane without water"); yy += 1
    for i, y, k in np.argwhere(C["lily"] & ~Bwater):
        put(i, y, k, "air", "lily pad without water")
    for i, y, k in np.argwhere(C["needs_below"] & ~Bsolid):
        put(i, y, k, "air", "nothing underneath")
    for i, y, k in np.argwhere(C["hanging"] & ~Asolid):
        put(i, y, k, "air", "hanging lantern with nothing above")
    for i, y, k in np.argwhere(C["gravity"] & ~Bsolid):
        nm = b[ids[i, y, k]]
        put(i, y, k, GRAVITY.get(nm, nm.replace("_concrete_powder", "_concrete")), "would fall")
    # beds: each half must have its partner in the facing direction
    for part, other, sign in (("bed_head", "bed_foot", -1), ("bed_foot", "bed_head", 1)):
        for i, y, k in np.argwhere(C[part]):
            nm = names[ids[i, y, k]]
            f = nm.split("facing=")[1].split(",")[0].split("]")[0] if "facing=" in nm else "north"
            dx, dz = FACE[f]
            ii, kk = i + sign * dx, k + sign * dz
            inside = 0 <= ii < ids.shape[0] and 0 <= kk < ids.shape[2]
            ok = inside and cat[other][ids[ii, y, kk]]
            if not ok and part == "bed_foot" and inside and b[ids[ii, y, kk]] == "air":
                # an earlier pass removed the head of a whole bed; put it back
                put(ii, y, kk, f"{b[ids[i, y, k]]}[facing={f},part=head]", "bed head restored")
                continue
            if not ok:
                put(i, y, k, "air", "half a bed")
    return fixes, None


def main(mode):
    world = place.WORLD
    allfix = {}
    for tx in range(8):
        for tz in range(9):
            f, _ = audit_tile(world, tx, tz)
            allfix.update(f)
    from collections import Counter
    c = Counter(why for (_, why) in allfix.values())
    print(len(allfix), dict(c))
    json.dump({f"{x},{y},{z}": v for (x, y, z), v in list(allfix.items())[:200000]},
              open(os.path.join(place.ROOT, "work", "audit_last.json"), "w"))
    if mode != "fix" or not allfix:
        return allfix
    by_tile = {}
    for (x, y, z), (blk, why) in allfix.items():
        by_tile.setdefault((x // 256, z // 256), []).append(f"setblock {x} {y} {z} {blk}")
    sessions, cur = [], []
    for (tx, tz), c in sorted(by_tile.items()):
        ids_ = write_functions(world, f"audit_{tx}_{tz}", c)
        cur += forceload_cmds(max(tx * 256, 32), max(tz * 256, 64), min(tx * 256 + 255, 1887), min(tz * 256 + 255, 2047))
        cur += ["function " + i for i in ids_] + ["forceload remove all"]
        if sum(1 for x in cur if x == "forceload remove all") >= 12:
            sessions.append(cur); cur = []
    if cur:
        sessions.append(cur)
    for n, part in enumerate(sessions):
        log = run(world, part, wait_load=5)
        print(f"audit fix session {n + 1}/{len(sessions)}", [l for l in log.splitlines() if "Exception" in l][:2], flush=True)
    fw.clear_cache()
    return allfix


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "report")
