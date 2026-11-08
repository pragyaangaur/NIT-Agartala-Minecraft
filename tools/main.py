"""Build the NIT Agartala voxel model and write the Minecraft world."""
import sys, os, json, json as _json, math, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt, label, binary_opening
from PIL import Image
import geo, dataset, geom2d as G, blocks, builder, anvil, specs, terrain

X0, Z0 = 32, 64
NX, NZ = 1856, 1984
Y_BASE, NY = 56, 112          # world y 56 .. 167
VOL = "data/model/vol.npy"

def log(*a):
    print(*a, flush=True)

# ---------------------------------------------------------------- imagery class
def world_to_px(x, z, meta):
    tx0, ty0, zz = meta; n = 1 << zz
    lat, lon = geo.lonlat(x, z)
    gx = (lon + 180.0) / 360.0 * (n * 256.0)
    gy = (1.0 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2.0 * (n * 256.0)
    return gx - tx0 * 256, gy - ty0 * 256

def imagery_layers(meta=(197638, 113179, 18)):
    """Downsample the imagery classification to the world grid."""
    a = np.asarray(Image.open("data/raw/esri_z18_campus.jpg").convert("RGB"), dtype=np.float32) / 255.0
    V = a.max(-1)
    from scipy.ndimage import uniform_filter
    m = [uniform_filter(a[..., i], 5) for i in range(3)]
    tex = np.sqrt(sum(np.maximum(uniform_filter(a[..., i] ** 2, 5) - m[i] ** 2, 0) for i in range(3)))
    X = X0 + np.arange(NX) + 0.5; Z = Z0 + np.arange(NZ) + 0.5
    XX, ZZ = np.meshgrid(X, Z, indexing="ij")
    px, py = world_to_px(XX, ZZ, meta)
    pxi = np.clip(px.astype(int), 0, a.shape[1] - 1); pyi = np.clip(py.astype(int), 0, a.shape[0] - 1)
    return dict(rgb=a[pyi, pxi], V=V[pyi, pxi], tex=tex[pyi, pxi])

# ---------------------------------------------------------------- terrain
def build_terrain(logf=log):
    H = np.load("data/raw/H_raw.npy")
    Bld, Roads, Nodes, Others = dataset.load()
    Bld = [b for b in Bld]
    # --- roads
    road_mask = np.zeros((NX, NZ), bool)
    road_kind = np.zeros((NX, NZ), np.uint8)
    W = {"primary": 8.0, "secondary": 7.0, "tertiary": 6.0, "residential": 5.0,
         "unclassified": 4.5, "service": 3.5, "track": 3.0, "footway": 1.6,
         "path": 1.4, "cycleway": 1.6, "steps": 2.0, "living_street": 5.0, "trunk": 9.0}
    order = {"footway": 0, "path": 1, "cycleway": 2, "track": 3, "service": 4, "unclassified": 5,
             "residential": 6, "tertiary": 7, "secondary": 8, "primary": 9, "trunk": 10}
    rk = {"footway": 1, "path": 1, "cycleway": 1, "steps": 1, "track": 2, "service": 3,
          "unclassified": 3, "residential": 4, "living_street": 4, "tertiary": 4,
          "secondary": 5, "primary": 5, "trunk": 5}
    for r in sorted(Roads, key=lambda r: order.get(r["tags"].get("highway"), 0)):
        hw = r["tags"].get("highway", "unclassified")
        w = float(r["tags"].get("width", W.get(hw, 4.0)))
        m = G.raster_line(r["pts"], w, X0, Z0, NX, NZ)
        road_mask |= m
        road_kind[m] = rk.get(hw, 3)
    logf(f"  roads: {road_mask.sum()} cells")
    # --- smooth terrain toward a road-fitted profile
    Rt = np.where(road_mask, H, 0.0); Wt = road_mask.astype(np.float64)
    sig = 26.0
    Rs = gaussian_filter(Rt, sig); Ws = gaussian_filter(Wt, sig)
    tgt = np.where(Ws > 0.02, Rs / np.maximum(Ws, 1e-6), H)
    C = np.where(road_mask, tgt - H, 0.0)
    H2 = H + gaussian_filter(C, 5.0)
    H2[road_mask] = tgt[road_mask]
    # --- buildings
    bmask = np.zeros((NX, NZ), bool)
    bld_meta = []
    for b in Bld:
        m, bx0, bz0 = G.raster_poly_sub(b["pts"], X0, Z0, NX, NZ)
        for h in b.get("holes", []):
            hm, hx0, hz0 = G.raster_poly_sub(h, X0, Z0, NX, NZ)
            if hm.size > 1:
                m[max(0, hx0 - bx0):max(0, hx0 - bx0) + hm.shape[0],
                  max(0, hz0 - bz0):max(0, hz0 - bz0) + hm.shape[1]] &= ~hm
        if not m.any():
            continue
        sl = (slice(bx0 - X0, bx0 - X0 + m.shape[0]), slice(bz0 - Z0, bz0 - Z0 + m.shape[1]))
        bmask[sl] |= m
        bld_meta.append((b, sl, m))
    Cb = np.zeros_like(H2)
    for b, sl, m in bld_meta:
        sub = H2[sl][m]
        med = float(np.median(sub))
        Cb[sl][m] = med - H2[sl][m]
    H3 = H2 + gaussian_filter(Cb, 2.6)
    for b, sl, m in bld_meta:
        med = float(np.median(H2[sl][m]))
        H3[sl][m] = med
    logf(f"  buildings: {len(bld_meta)} footprints, {bmask.sum()} cells")
    H3 = np.maximum(H3, H.min())
    np.save("data/model/H.npy", H3.astype(np.float32))
    np.save("data/model/road_mask.npy", road_mask)
    np.save("data/model/road_kind.npy", road_kind)
    np.save("data/model/bmask.npy", bmask)
    return H3, road_mask, road_kind, bmask

if __name__ == "__main__":
    os.makedirs("data/model", exist_ok=True)
    t0 = time.time()
    H, road_mask, road_kind, bmask = build_terrain()
    log(f"terrain done {time.time()-t0:.0f}s  H {H.min():.1f}..{H.max():.1f}")

# ---------------------------------------------------------------- surface
def build_surface(meta=(197638, 113179, 18)):
    """Ground material per cell, derived from imagery hue; plus a forest mask."""
    from scipy.ndimage import uniform_filter as uf
    im = imagery_layers(meta)
    r, g, b = im["rgb"][..., 0], im["rgb"][..., 1], im["rgb"][..., 2]
    V, tex = im["V"], im["tex"]
    exg = 2 * g - r - b
    sat = np.where(V > 1e-3, (V - im["rgb"].min(-1)) / np.maximum(V, 1e-3), 0)
    veg = exg > 0.020
    dark = (V < 0.42) & (exg > 0.008)
    dens = uf(dark.astype(np.float32), 20)
    tree = (dark & (dens > 0.45)) | ((V < 0.20) & (exg > 0.0))
    grass = veg & ~tree & (g >= r * 1.045)
    brown = (~grass) & ~tree & (r >= g * 1.02)
    paved = (~veg) & (V > 0.30) & (sat < 0.26) & ~brown
    dirt = (~grass) & ~tree & ~paved
    np.save("data/model/tree_mask.npy", tree)
    return dict(tree=tree, grass=grass, paved=paved, dirt=dirt, brown=brown,
                V=V, rgb=im["rgb"], dens=dens)

def surface_block(surf, i, j):
    if surf["paved"][i, j]: return blocks.B["smooth_stone"]
    if surf["dirt"][i, j]:  return blocks.B["coarse"]
    return blocks.B["grass"]

def build_ground(model, H, surf, road_mask, road_kind, bmask):
    """Lay terrain columns and road surfaces into the volume."""
    gy = np.round(H - H.min()).astype(np.int32) + Y_BASE
    water = load_water()
    if water is not None and water.any():
        lab = label(water)[0]
        for wi in range(1, lab.max() + 1):
            m = lab == wi
            if m.sum() < 20:
                continue
            lvl = int(np.percentile(gy[m], 10)) - 1
            gy[m] = lvl
            gy[m] = lvl
        near = G.dilate(water, 2) & ~water
        gy[near] = np.minimum(gy[near], int(gy[water].mean()) + 1)
    yy = np.arange(Y_BASE, Y_BASE + NY)
    RC = np.array([blocks.B["concrete_g"], blocks.B["gravel"], blocks.B["coarse"],
                   blocks.B["concrete_lg"], blocks.B["concrete_g"]], dtype=np.uint16)
    for i in range(0, NX, 128):
        for j in range(0, NZ, 128):
            sl = np.s_[i:i + 128, j:j + 128]
            h = gy[sl][..., None]
            sub = model.vol[sl]
            below = yy[None, None, :] < h
            at = yy[None, None, :] == h
            sub[below] = blocks.B["stone"]
            sub[below & (yy[None, None, :] >= h - 3)] = blocks.B["dirt"]
            sub[at] = blocks.B["grass"]
            sub[surf["paved"][sl][..., None] & at] = blocks.B["smooth_stone"]
            sub[surf["brown"][sl][..., None] & at] = blocks.B["coarse"]
            sub[surf["tree"][sl][..., None] & at & (surf["dens"][sl][..., None] > 0.78)] = blocks.B["podzol"]
            sub[surf["dirt"][sl][..., None] & at] = blocks.B["podzol"]
            if water is not None:
                w = water[sl][..., None] & at
                sub[w] = blocks.B["water"]
                sub[water[sl][..., None] & (yy[None, None, :] < h)] = blocks.B["mud"]
            rm = road_mask[sl][..., None]
            sub[rm & at] = RC[0]
            for k in (1, 2, 3, 4):
                sub[rm & (road_kind[sl][..., None] == k) & at] = RC[min(k, 4)]
    return gy

def load_water():
    if not os.path.exists("data/model/water.npy"):
        return None
    return np.load("data/model/water.npy")

def build_water_mask():
    """Ponds digitised from Esri imagery (see out/refs/water_montage2.jpg)."""
    from scipy.ndimage import label, find_objects
    a = np.asarray(Image.open("data/raw/esri_z18_campus.jpg").convert("RGB"), dtype=np.float32) / 255.0
    V = a.max(-1)
    from scipy.ndimage import uniform_filter
    m = [uniform_filter(a[..., i], 5) for i in range(3)]
    tex = np.sqrt(sum(np.maximum(uniform_filter(a[..., i] ** 2, 5) - m[i] ** 2, 0) for i in range(3)))
    cand = (V < 0.26) & (tex < 0.020) & (a[..., 1] - a[..., 0] < 0.10)
    cand = binary_opening(cand, np.ones((3, 3)))
    lab, n = label(cand)
    objs = find_objects(lab)
    Bld = dataset.load()[0]
    bmask_img = np.zeros(V.shape, bool)
    from PIL import ImageDraw
    im = Image.fromarray((bmask_img * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    import overlay
    for b in Bld:
        d.polygon([overlay.world_to_mosaic_px((197638, 113179, 18), x, z) for x, z in b["pts"]], fill=255)
    bmask_img = np.asarray(im) > 0
    dist = distance_transform_edt(~bmask_img)
    keep = np.zeros(n + 1, bool)
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        mk = lab[sl] == i
        sz = mk.sum()
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if sz < 1200 or w < 16 or h < 16: continue
        fill = sz / max(1, h * w)
        if fill < 0.42 or fill > 0.92: continue
        if dist[sl][mk].min() < 2.5: continue
        if a[sl][..., 0][mk].mean() > 0.20: continue
        keep[i] = True
    wm = keep[lab]
    # to world grid
    X = X0 + np.arange(NX) + 0.5; Z = Z0 + np.arange(NZ) + 0.5
    XX, ZZ = np.meshgrid(X, Z, indexing="ij")
    px, py = world_to_px(XX, ZZ, (197638, 113179, 18))
    out = wm[np.clip(py.astype(int), 0, wm.shape[0] - 1), np.clip(px.astype(int), 0, wm.shape[1] - 1)]
    np.save("data/model/water.npy", out)
    log(f"  water: {out.sum()} cells, {keep.sum()} bodies")
    return out

# ---------------------------------------------------------------- buildings
ROOF_MAP = {"red": "concrete_r", "brown": "concrete_br", "orange": "concrete_o",
            "grey": "concrete_g", "white": "concrete_w", "blue": "concrete_bg",
            "green": "concrete_gr", "black": "concrete_b", "lightgrey": "concrete_lg",
            "yellow": "concrete_y", "pink": "concrete_p", "cyan": "concrete_c"}
ROOF_RGB = {"terracotta": (0.42, 0.29, 0.19), "concrete_br": (0.35, 0.26, 0.18),
            "concrete_r": (0.48, 0.20, 0.16), "concrete_o": (0.55, 0.30, 0.14),
            "concrete_g": (0.33, 0.34, 0.35), "concrete_w": (0.76, 0.77, 0.77),
            "concrete_lg": (0.58, 0.59, 0.60), "concrete_bg": (0.22, 0.28, 0.42)}
ROOF_KEY = {"terracotta": "terracotta", "concrete_br": "terracotta_br", "concrete_r": "terracotta_r",
            "concrete_o": "terracotta_o", "concrete_g": "concrete_g", "concrete_w": "concrete_w",
            "concrete_lg": "concrete_lg", "concrete_bg": "concrete_bg"}

def ROOF_MAP_KEY(k):
    return k

def sample_roof(mask, rgb):
    """Median roof colour inside the footprint (eroded to avoid walls/ground)."""
    m = mask
    inner = G.erode(m, 1)
    if inner.sum() >= max(4, 0.25 * m.sum()):
        m = inner
    r = rgb[m]
    if len(r) == 0: return None
    med = np.median(r, axis=0)
    best = None
    for k, c in ROOF_RGB.items():
        d = float((((med - np.array(c)) ** 2) * np.array([1.0, 1.0, 1.0])).sum())
        if best is None or d < best[0]: best = (d, k)
    return best[1], med

def inside_campus(x, z, campus):
    from matplotlib.path import Path
    return Path(campus).contains_point((x, z))

def relation_buildings():
    """Multipolygon building relations (holes) that Overpass 'out geom' omits."""
    import json
    try:
        j = json.load(open("data/osm/relations.json"))
    except Exception:
        return [], {}
    out, holes = [], {}
    for e in j.get("elements", []):
        outer = [m for m in e.get("members", []) if m.get("role") == "outer"]
        inner = [m for m in e.get("members", []) if m.get("role") == "inner"]
        if not outer:
            continue
        op = [tuple(geo.xy(p["lat"], p["lon"])) for p in outer[0]["geometry"]]
        nm = e.get("tags", {}).get("name", "")
        if e["id"] == 5385967:
            # same outer ring as way 361838658 "NIT Agartala": record the courtyard as a hole
            if inner:
                holes[361838658] = [[tuple(geo.xy(p["lat"], p["lon"])) for p in inner[0]["geometry"]]]
            continue
        out.append(dict(id="rel:" + str(e["id"]), type="relation",
                        tags=dict(e.get("tags", {})), pts=op, closed=True,
                        holes=[[tuple(geo.xy(p["lat"], p["lon"])) for p in m["geometry"]] for m in inner]))
    return out, holes

def load_all_buildings():
    """OSM footprints plus Microsoft footprints that OSM lacks."""
    Bld = dataset.load()[0]
    try:
        extra = json.load(open("data/model/ms_new.json"))
    except Exception:
        extra = []
    for k in extra:
        Bld.append(dict(id="ms:" + str(k["id"]), type="way",
                        tags={"building": "yes", "source": "microsoft_ml_footprints"},
                        pts=[(round(x, 2), round(z, 2)) for x, z in k["pts"]],
                        closed=True))
    rel, hooks = relation_buildings()
    Bld.extend(rel)
    for b in Bld:
        if b["id"] in hooks:
            b["holes"] = hooks[b["id"]]
    log(f"  footprints: {len(Bld)} ({len(extra)} from Microsoft ML, {len(rel)} relations)")
    return Bld

def build_buildings(model, gy, surf, campus):
    global ROADPTS, ROADTREE
    import builder as BD
    from scipy.spatial import cKDTree
    Roads = dataset.load()[1]
    pts = []
    for r in Roads:
        P = np.asarray(r["pts"], float)
        for a, b in zip(P[:-1], P[1:]):
            n = max(1, int(np.hypot(*(b - a)) / 3))
            for t in np.linspace(0, 1, n):
                pts.append(a + t * (b - a))
    ROADPTS = np.array(pts)
    ROADTREE = cKDTree(ROADPTS)
    Bld = load_all_buildings()
    named = {}
    for b in Bld:
        n = b["tags"].get("name")
        if n: named[n] = b
    rows = []
    for b in Bld:
        m, bx0, bz0 = G.raster_poly_sub(b["pts"], X0, Z0, NX, NZ)
        if m.sum() < 4:
            rows.append((b, None)); continue
        n = b["tags"].get("name", "")
        sp = dict(specs.SPECS.get(specs.ALIASES.get(n, n), specs.DEFAULT))
        cx, cz = dataset.centroid(b["pts"])
        inc = inside_campus(cx, cz, campus)
        area = float(m.sum())
        if n not in specs.SPECS:
            sl0 = np.s_[bx0 - X0:bx0 - X0 + m.shape[0], bz0 - Z0:bz0 - Z0 + m.shape[1]]
            rc = sample_roof(m, surf["rgb"][sl0])
            col, med = (rc if rc else ("lightgrey", np.array([0.6, 0.6, 0.6])))
            tile = bool(med[0] - med[2] > 0.055 and med[0] > 0.22 and med.mean() < 0.55)
            if inc:
                sp.update(floors=1 if area < 120 else (2 if area < 700 else 3),
                          storey=3.3, wall="concrete_w", wall2="concrete_lg",
                          win_period=3, win_width=2)
                sp["roof"] = ("gable" if area < 900 else "gable_low") if tile else "flat"
                sp["parapet"] = 0 if tile else 1
            else:
                sp.update(floors=1 if area < 90 else 2, storey=3.1, wall="concrete_w",
                          wall2=rng_wall, win_period=2, win_width=1)
                sp["roof"] = ("gable" if area < 400 else "gable_low") if tile else "flat"
                sp["parapet"] = 0 if tile else 1
            sp["roof_mat"] = ROOF_KEY.get(col, "concrete_lg")
        ground = int(round(np.median(gy[bx0 - X0:bx0 - X0 + m.shape[0], bz0 - Z0:bz0 - Z0 + m.shape[1]][m])))
        y0 = ground + int(sp.get("plinth", 1))
        # local model
        tmp = BD.Model(bx0, bz0, m.shape[0], m.shape[1], Y_BASE, NY)
        try:
            top = BD.build(tmp, m, y0, sp, seed=abs(hash(str(b["id"]))) % 100000)
        except Exception as e:
            log("    build failed", b["id"], e); rows.append((b, None)); continue
        # blit
        sl = np.s_[bx0 - X0:bx0 - X0 + m.shape[0], bz0 - Z0:bz0 - Z0 + m.shape[1]]
        g = model.vol[sl]
        nz_ = tmp.vol > 0
        g[nz_] = tmp.vol[nz_]
        # entrance facing the nearest road
        try:
            if ROADTREE is not None:
                c = np.array([cx, cz])
                dist, idx = ROADTREE.query(c, k=1)
                rp = ROADPTS[idx]
                d = rp - c; d /= max(1e-6, np.hypot(*d))
                # nearest wall cell toward the road
                cand = np.argwhere(m)
                rel = np.stack([cand[:, 0] + bx0 - cx, cand[:, 1] + bz0 - cz], 1)
                proj = rel @ d
                pick = rel[np.argmax(proj - 0.25 * np.hypot(rel[:, 0], rel[:, 1]))]
                wc = (cand[np.argmax(proj - 0.25 * np.hypot(rel[:, 0], rel[:, 1]))][0],
                      cand[np.argmax(proj - 0.25 * np.hypot(rel[:, 0], rel[:, 1]))][1])
                if 150 < area < 2600:
                    BD.entrance(tmp, m, y0, wc, (d[0], d[1]), sp, ground)
        except Exception as e:
            pass
        # relief colour for the aerial render
        rows.append((b, dict(spec=sp, y0=y0, top=top, inc=inc, area=area, ground=ground)))
    log(f"  built {sum(1 for r in rows if r[1])} buildings")
    return rows

rng_wall = "concrete_lg"
ROADPTS = None
ROADTREE = None

def campus_poly():
    import json
    d = json.load(open("data/osm/campus_outline.json"))
    return [tuple(geo.xy(p["lat"], p["lon"])) for p in d["elements"][0]["geometry"] if p]

# ---------------------------------------------------------------- trees
def build_trees(model, gy, surf, road_mask, bmask, water):
    tree = surf["tree"]
    cand = tree & ~road_mask & ~G.dilate(bmask, 4)
    if water is not None: cand &= ~water
    cand = G.erode(cand, 1) | cand
    log(f"  tree candidates {cand.sum()} cells")
    rng = np.random.default_rng(7)
    step = 5
    n = 0
    D = surf.get("dens")
    if D is None:
        D = np.ones_like(gy)
    yy0 = Y_BASE
    for gx in range(0, NX, step):
        for gz in range(0, NZ, step):
            i = gx + int(rng.integers(0, step)); j = gz + int(rng.integers(0, step))
            if i >= NX or j >= NZ or not cand[i, j]:
                continue
            if D[i, j] < 0.50 and rng.random() > 0.30:
                continue
            h = int(rng.integers(7, 13))
            r = int(rng.choice([2, 3, 3, 4]))
            base = int(gy[i, j])
            trunk = blocks.B["jungle_log"] if rng.random() < 0.7 else blocks.B["dark_log"]
            leaf = blocks.B["jungle_leaves"] if rng.random() < 0.65 else blocks.B["dark_leaves"]
            for k in range(h):
                if 0 <= base + k - Y_BASE < NY:
                    model.vol[i, j, base + k - Y_BASE] = trunk
            cy = base + h
            for dy in range(-r // 2, r + 1):
                rr = r * math.sqrt(max(0.0, 1 - ((dy) / (r * 1.1)) ** 2))
                ri = int(round(rr))
                if ri <= 0: continue
                ix0, ix1 = max(0, i - ri), min(NX, i + ri + 1)
                jz0, jz1 = max(0, j - ri), min(NZ, j + ri + 1)
                y = cy + dy
                if not (Y_BASE <= y < Y_BASE + NY): continue
                sub = model.vol[ix0:ix1, jz0:jz1, y - Y_BASE]
                xs = np.arange(ix0, ix1)[:, None] - i
                zs = np.arange(jz0, jz1)[None, :] - j
                m2 = (xs * xs + zs * zs) <= ri * ri
                sub[m2] = leaf
            n += 1
    log(f"  trees placed: {n}")


def build_all():
    t0 = time.time()
    os.makedirs("data/model", exist_ok=True)
    H = np.load("data/model/H.npy")
    road_mask = np.load("data/model/road_mask.npy")
    bmask = np.load("data/model/bmask.npy")
    road_kind = np.load("data/model/road_kind.npy")
    log("gathering imagery layers...")
    surf = build_surface()
    if not os.path.exists("data/model/water.npy"):
        log("digitising water...")
        build_water_mask()
    water = load_water()
    log("allocating volume...")
    model = builder.Model(X0, Z0, NX, NZ, Y_BASE, NY)
    log("ground...")
    gy = build_ground(model, H, surf, road_mask, road_kind, bmask)
    np.save("data/model/gy.npy", gy)
    log("buildings...")
    campus = campus_poly()
    rows = build_buildings(model, gy, surf, campus)
    log("extras...")
    apply_extras(model, gy, rows)
    log("trees...")
    build_trees(model, gy, surf, road_mask, bmask, water)
    log("saving volume...")
    np.save(VOL, model.vol)
    json.dump({"rows": [{"id": b["id"], "name": b["tags"].get("name", ""),
                         "tags": b["tags"], "meta": m} for b, m in rows]},
              open("data/model/buildings.json", "w"), indent=1, default=str)
    log(f"model built in {time.time()-t0:.0f}s  vol {model.vol.shape} {model.vol.nbytes/1e6:.0f} MB")



def apply_extras(model, gy, rows):
    """Digitised sports ground and two large unmapped halls."""
    import extras as EX
    import builder as BD
    # oval track + infield
    ring = EX.ellipse_ring_mask(NX, NZ, X0, Z0, EX.TRACK["cx"], EX.TRACK["cz"],
                                EX.TRACK["rx"], EX.TRACK["rz"], EX.TRACK["width"])
    inf = EX.ellipse_mask(NX, NZ, X0, Z0, EX.TRACK["cx"], EX.TRACK["cz"],
                          EX.TRACK["rx"] - EX.TRACK["width"], EX.TRACK["rz"] - EX.TRACK["width"])
    yy = np.arange(Y_BASE, Y_BASE + NY)
    at = yy[None, None, :] == gy[..., None]
    model.vol[ring[..., None] & at] = blocks.B["terracotta"]
    model.vol[inf[..., None] & at] = blocks.B["grass"]
    model.vol[ring[..., None] & (yy[None, None, :] < gy[..., None]) & (yy[None, None, :] >= gy[..., None] - 2)] = blocks.B["stone"]
    log(f"    oval track: {int(ring.sum())} cells")
    # two large halls
    halls = [dict(name=EX.RED_HALL["name"], pts=EX.RED_HALL["pts"],
                  spec=dict(floors=1, storey=11.0, wall="concrete_lg", wall2="brick",
                            roof="gable_low", roof_mat="terracotta_r", win="glass_g",
                            win_period=4, win_width=2, parapet=0, plinth=1, roof_kit=False)),
             dict(name=EX.ROUND_HALL["name"], pts=EX.circle_poly(EX.ROUND_HALL["cx"], EX.ROUND_HALL["cz"], EX.ROUND_HALL["r"], 48),
                  spec=dict(floors=1, storey=13.0, wall="concrete_lg", wall2="terracotta_w",
                            roof="radial", roof_mat="terracotta_r", win="glass_c",
                            win_period=4, win_width=2, parapet=0, plinth=1, roof_kit=False))]
    out = []
    for h in halls:
        m, bx0, bz0 = G.raster_poly_sub(h["pts"], X0, Z0, NX, NZ)
        if m.sum() < 10: continue
        ground = int(round(np.median(gy[bx0 - X0:bx0 - X0 + m.shape[0], bz0 - Z0:bz0 - Z0 + m.shape[1]][m])))
        ground = int(round(np.median(gy[bx0 - X0:bx0 - X0 + m.shape[0], bz0 - Z0:bz0 - Z0 + m.shape[1]][m])))
        y0 = ground + int(h["spec"].get("plinth", 1))
        tmp = BD.Model(bx0, bz0, m.shape[0], m.shape[1], Y_BASE, NY)
        top = BD.build(tmp, m, y0, h["spec"], seed=99)
        sl = np.s_[bx0 - X0:bx0 - X0 + m.shape[0], bz0 - Z0:bz0 - Z0 + m.shape[1]]
        g = model.vol[sl]; nzm = tmp.vol > 0; g[nzm] = tmp.vol[nzm]
        out.append(dict(name=h["name"], top=top, y0=y0))
        rows.append((dict(id="imagery:" + h["name"], tags={"name": h["name"], "building": "yes",
                      "source": "Esri World Imagery digitisation"}, pts=h["pts"]),
                     dict(spec=h["spec"], y0=y0, top=top, inc=True, area=float(m.sum()))))
    log(f"    halls: {[o['name'] for o in out]}")


if __name__ == "__main__" and os.environ.get("STAGE") == "all":
    build_all()


def write_minecraft(vol_path=VOL, outdir=".scratch/gen"):
    import anvil, blocks, shutil
    vol = np.load(vol_path, mmap_mode="r")
    wdir = anvil.write_world(np.ascontiguousarray(vol), blocks.PALETTE, outdir, "NITAgartala",
                             Y_BASE, X0, Z0, spawn=(X0 + 600, Y_BASE + 40, Z0 + 900),
                             levelname="NIT Agartala 1:1 (Barjala, Jirania)")
    return wdir


if __name__ == "__main__" and os.environ.get("STAGE") == "write":
    write_minecraft()
