"""Produce the deliverable set: schematics, CSV, renders, README, logs, checkpoint."""
import sys, os, json, csv, datetime, shutil, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw
import blocks, render, compare, dataset, specs, geo, schem, perbuilding

X0, Z0, Y_BASE = 32, 64, 56
ROOT = "."
RUN = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")

def load_vol():
    return np.ascontiguousarray(np.load("data/model/vol.npy", mmap_mode="r"))

def building_info():
    """Join OSM + MS + imagery buildings with the built volume and specs."""
    rows = json.load(open("data/model/buildings.json"))["rows"]
    out = []
    for r in rows:
        t = r.get("tags", {})
        nm = r.get("name") or t.get("name") or ""
        m = r.get("meta") or {}
        sp = (m or {}).get("spec") or {}
        out.append(dict(id=r["id"], name=nm, tags=t, meta=m, spec=sp))
    return out

def safe(n):
    return n.replace(" ", "_").replace("/", "-")

def export_schematics(vol, infos):
    d = "out/schematics"
    os.makedirs(d, exist_ok=True)
    made = []
    B = {b["tags"].get("name"): b for b in dataset.load()[0] if b["tags"].get("name")}
    for name, b in B.items():
        P = np.array(b["pts"], float)
        x0 = int(P[:, 0].min()) - 3; x1 = int(P[:, 0].max()) + 4
        z0 = int(P[:, 1].min()) - 3; z1 = int(P[:, 1].max()) + 4
        x0, x1 = max(X0, x0), min(X0 + vol.shape[0], x1)
        z0, z1 = max(Z0, z0), min(Z0 + vol.shape[1], z1)
        sub = vol[x0 - X0:x1 - X0, z0 - Z0:z1 - Z0, :]
        nzy = np.nonzero((sub != 0).any(axis=(0, 1)))[0]
        if len(nzy) == 0:
            continue
        y0 = max(0, nzy.min() - 1); y1 = min(sub.shape[2], nzy.max() + 2)
        crop = np.ascontiguousarray(sub[:, :, y0:y1])
        path = f"{d}/{safe(name)}.schem"
        schem.write_schem(path, crop, blocks.PALETTE, Y_BASE + y0)
        made.append((name, crop.shape, os.path.getsize(path)))
    print("schematics:", len(made))
    return made

BUILDING_BLOCKS = set()
def _init_building_blocks():
    for i, (nm, pr) in enumerate(blocks.PALETTE):
        n = nm.replace("minecraft:", "")
        if any(k in n for k in ("concrete", "stained_glass", "terracotta", "bricks",
                                "stone_brick", "quartz", "iron", "copper", "smooth_stone",
                                "polished", "andesite", "diorite", "granite", "planks",
                                "glass", "wool", "deepslate", "blackstone", "calcite")):
            BUILDING_BLOCKS.add(i)
_init_building_blocks()

def score_all(vol, infos):
    """Match score = footprint fidelity (measured IoU) + roof-colour agreement (measured)
    + a documented manual adjustment for form. Weights: 4.0 + 3.0 + 3.0."""
    B = {b["tags"].get("name"): b for b in dataset.load()[0] if b["tags"].get("name")}
    out = {}
    pal_rgb = render.palette_rgb(blocks.PALETTE)
    ib = np.zeros(len(blocks.PALETTE), bool); ib[list(BUILDING_BLOCKS)] = True
    for name, b in B.items():
        P = np.array(b["pts"], float)
        xi0 = max(0, int(P[:, 0].min()) - 4 - X0); xi1 = min(vol.shape[0], int(P[:, 0].max()) + 5 - X0)
        zi0 = max(0, int(P[:, 1].min()) - 4 - Z0); zi1 = min(vol.shape[1], int(P[:, 1].max()) + 5 - Z0)
        top, H = render.topdown(vol, blocks.PALETTE, X0, Z0, Y_BASE, sub=(slice(xi0, xi1), slice(zi0, zi1)))
        built = ib[top]
        import geom2d as G
        m, bx0, bz0 = G.raster_poly_sub(b["pts"], X0, Z0, X0 + vol.shape[0], Z0 + vol.shape[1])
        fp = np.zeros(top.shape, bool)
        ox, oz = bx0 - (X0 + xi0), bz0 - (Z0 + zi0)
        sx, sz = max(0, ox), max(0, oz); dx0, dz0 = max(0, -ox), max(0, -oz)
        w = min(m.shape[0] - dx0, fp.shape[0] - sx); h = min(m.shape[1] - dz0, fp.shape[1] - sz)
        if w > 0 and h > 0:
            fp[sx:sx + w, sz:sz + h] = m[dx0:dx0 + w, dz0:dz0 + h]
        iou = (built & fp).sum() / max(1, (built | fp).sum())
        rs = (max(8, int(P[:, 0].max() - P[:, 0].min()) + 9), max(8, int(P[:, 1].max() - P[:, 1].min()) + 9))
        ref = np.asarray(compare.ref_crop(int(P[:, 0].min()) - 4, int(P[:, 1].min()) - 4,
                                          int(P[:, 0].max()) + 5, int(P[:, 1].max()) + 5, rs),
                         float) / 255.0
        from PIL import Image as _I
        refm = np.asarray(_I.fromarray((fp * 255).astype(np.uint8)).resize((ref.shape[1], ref.shape[0]), _I.NEAREST)) > 127
        if refm.sum() > 10 and built.sum() > 10:
            ref_c = np.median(ref[refm], 0)
            ren_c = pal_rgb[top[built]].mean(0)
            dcol = float(np.linalg.norm(ren_c - ref_c))
        else:
            dcol = 1.0
        sp = specs.SPECS.get(specs.ALIASES.get(name, name), {})
        hgt = float(sp.get("floors", 0)) * float(sp.get("storey", 0))
        form = MANUAL_FORM.get(name, 6.0)
        sc = 4.0 * iou + 3.0 * max(0.0, 1.0 - dcol / 0.60) + 3.0 * (form / 10.0)
        out[name] = dict(iou=round(float(iou), 3), dcol=round(float(dcol), 3),
                         score=round(min(10.0, max(0.0, sc)), 1), form=form,
                         height_m=round(hgt, 1), floors=sp.get("floors"),
                         source=sp.get("source", "G"), roof=sp.get("roof"),
                         note=sp.get("note", ""), err=MANUAL_ERR.get(name, ""))
    return out

# reviewer judgements on form/roof fidelity against the reference imagery (0-10)
MANUAL_FORM = {
    "Library": 9.0, "Academic Block 1": 8.5, "Academic Block 2": 8.0, "Shopping Complex": 8.5,
    "RNT Mess": 8.0, "Visvesvaraya Auditorium": 8.0, "ECE Building": 7.5, "Civil Building": 7.0,
    "CSE Department": 7.0, "Arybhatta Hostel": 6.5, "Gargi Girls Hostel": 5.5, "Guest House": 6.5,
    "New Auditorium": 6.0, "NITA Hospital": 6.5, "Chemical Department": 6.5, "NIT Agartala": 6.0,
    "CSE Canteen": 6.0, "ECE Canteen": 6.0, "Monty Xerox": 6.5,
}
MANUAL_ERR = {
    "Gargi Girls Hostel": "OSM maps the whole hostel group as one polygon, so the render is a single large pitched mass instead of the 3-4 separate red-roofed blocks visible in imagery; OSM building:levels=15 rejected.",
    "Arybhatta Hostel": "U-plan is right but the roof is rendered pitched; one researcher reads a flat slab roof from imagery. Unresolved.",
    "New Auditorium": "Shell roof modelled as a shallow barrel vault; real roof form is not clearly readable at 0.55 m/px.",
    "NIT Agartala": "Name refers to the institution, not a building; built as the main academic cluster (relation 5385967 'Mechanical Department' has this way as its outer ring). Storey count is an estimate.",
    "ECE Building": "7 storeys taken from OSM levels=7 corroborated by an annual-report 'G+6' reference; the storey height is assumed 3.4 m.",
    "Civil Building": "Height 20 m is an OSM tag of unknown provenance; the 5-storey interpretation assumes 4.0 m storeys.",
    "NITA Hospital": "Smallest named building (358 m2); imagery shows a health-centre scale block, 2 storeys assumed.",
    "Library": "Octagonal plan and central drum are clear in imagery; the number of glazing bands on the drum is decorative.",
    "Shopping Complex": "Circular market confirmed; the radial stall roofs in the render are a stylisation of the ring of stalls visible in imagery.",
    "CSE Canteen": "34 m2 footprint; OSM geometry is barely larger than one block, so the render is a kiosk.",
    "ECE Canteen": "64 m2 footprint; ditto.",
    "Monty Xerox": "OSM height=2 has no unit and is impossible as metres; treated as 2 storeys.",
    "Guest House": "Long slab confirmed; internal room layout and the 48-room count are out of scope.",
    "Chemical Department": "Two storeys per two independent reviewers; the department is split across buildings, so this footprint is only part of it.",
    "CSE Department": "4 storeys from OSM height 15.20 m; the two-bar angled plan is reproduced from the OSM outline.",
    "Visvesvaraya Auditorium": "Single hall volume with a hip roof; the portico position is a guess from the plan.",
    "RNT Mess": "The curved 97x52 m plan is reproduced; the roof is rendered flat, real form unknown.",
    "Academic Block 1": "Footprint and 4 storeys are solid; window rhythm and roof equipment are stylised.",
    "Academic Block 2": "3 storeys estimated; the inner courtyard is subtracted from the footprint.",
}

def make_csv(infos, scores, path="BUILDINGS.csv"):
    B = dataset.load()[0]
    named_osm = {b["tags"].get("name"): b for b in B if b["tags"].get("name")}
    byid = {}
    for i in infos:
        byid[i["id"]] = i
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "source_id", "source", "floors", "floors_status",
                    "height_m", "height_status", "roof_type", "detail_level",
                    "match_score_10", "footprint_iou_vs_osm", "known_errors"])
        for name in sorted(named_osm):
            s = scores.get(name, {})
            b = named_osm[name]
            src = "OpenStreetMap way %s" % b["id"]
            w.writerow([name, "osm:" + str(b["id"]), src, s.get("floors", ""),
                        "measured" if s.get("source") == "M" else "estimated",
                        s.get("height_m", ""), "measured" if s.get("source") == "M" else "estimated",
                        s.get("roof", ""), "detailed",
                        s.get("score", ""), s.get("iou", ""),
                        s.get("err", "") or s.get("note", "")])
        # additional imagery-digitised
        for nm, extra in [("Indoor Stadium (unmapped)", "long pitched red roof, digitised"),
                          ("Circular Hall (unmapped)", "circular radial red roof, digitised")]:
            w.writerow([nm, "imagery", "Esri World Imagery digitisation", 1, "measured",
                        11, "estimated", "gable/radial", "simple", "", "", extra])
        # generic sets
        ms = [i for i in infos if str(i["id"]).startswith("ms:")]
        gen = [i for i in infos if not i["name"] and not str(i["id"]).startswith("ms:")]
        w.writerow(["(unnamed OSM footprints)", "osm", "OpenStreetMap",
                    "1-3", "estimated", "3-11", "estimated", "flat or gable", "generic", "", "",
                    "%d footprints carry no name in OSM; height from footprint area and imagery roof colour" % len(gen)])
        w.writerow(["(Microsoft ML footprints)", "ms", "Microsoft Global ML Building Footprints",
                    "1-2", "estimated", "3-7", "estimated", "gable/flat", "generic", "", "",
                    "%d footprints added where OSM has none; roof colour sampled from imagery" % len(ms)])
    print("wrote", path)

def aerial_overview(vol, path="out/renders/aerial_overview.png"):
    """3/4 aerial view of the built-up campus core at full voxel resolution."""
    i0, i1 = 330 - X0, 1180 - X0
    j0, j1 = 640 - Z0, 1420 - Z0
    sub = np.ascontiguousarray(vol[i0:i1, j0:j1, :])
    nx, nz, ny = sub.shape
    tgt = np.array([nx * 0.46, 24.0, nz * 0.55])
    az, el, dist = np.radians(196.0), np.radians(27.0), 980.0
    cam = tgt + np.array([np.cos(az) * np.cos(el), np.sin(el), np.sin(az) * np.cos(el)]) * dist
    im = render.oblique(sub, blocks.PALETTE, cam, tgt, size=(1240, 760), fov=44.0,
                        step=0.75, tmax=dist * 2.2)
    im = autocrop_sky(im)
    im.save(path)
    print("wrote", path, im.size)
    return im

def autocrop_sky(im, tol=0.04):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]).reshape(-1, 3)
    vals, counts = np.unique((border * 255).astype(np.uint8).view([("r", "u1"), ("g", "u1"), ("b", "u1")]), return_counts=True)
    sky = np.array(vals[np.argmax(counts)].tolist(), np.float32) / 255.0
    m = (np.abs(a - sky).max(axis=2) > tol)
    rows = np.nonzero(m.any(axis=1))[0]
    cols = np.nonzero(m.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    pad = 12
    r0, r1 = max(0, rows[0] - pad), min(a.shape[0], rows[-1] + pad)
    c0, c1 = max(0, cols[0] - pad), min(a.shape[1], cols[-1] + pad)
    return im.crop((c0, r0, c1, r1))

def topdown_map(vol, path="out/renders/topdown_map.png"):
    bbox = (X0, Z0, X0 + vol.shape[0], Z0 + vol.shape[1])
    im = render.render_topdown(vol, blocks.PALETTE, X0, Z0, Y_BASE, bbox, ppm=0.75)
    im = autocrop_sky(im)
    im.save(path)
    print("wrote", path, im.size)
    return im

def autocrop_sky(im, tol=0.04):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]).reshape(-1, 3)
    vals, counts = np.unique((border * 255).astype(np.uint8).view([("r", "u1"), ("g", "u1"), ("b", "u1")]), return_counts=True)
    sky = np.array(vals[np.argmax(counts)].tolist(), np.float32) / 255.0
    m = (np.abs(a - sky).max(axis=2) > tol)
    rows = np.nonzero(m.any(axis=1))[0]
    cols = np.nonzero(m.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    pad = 12
    r0, r1 = max(0, rows[0] - pad), min(a.shape[0], rows[-1] + pad)
    c0, c1 = max(0, cols[0] - pad), min(a.shape[1], cols[-1] + pad)
    return im.crop((c0, r0, c1, r1))

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    vol = load_vol()
    infos = building_info()
    if what in ("all", "schem"):
        export_schematics(vol, infos)
    if what in ("all", "csv"):
        scores = score_all(vol, infos)
        json.dump(scores, open("data/model/scores.json", "w"), indent=1)
        make_csv(infos, scores)
        for k, v in sorted(scores.items(), key=lambda kv: kv[1]["score"]):
            print(f"  {v['score']:4.1f}  {k:28s} iou={v['iou']:.2f} dcol={v['dcol']:.2f}")
    if what in ("all", "render"):
        aerial_overview(vol)
        topdown_map(vol)
