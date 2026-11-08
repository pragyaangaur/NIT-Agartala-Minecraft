import sys; sys.path.insert(0,'tools')
import json, numpy as np
from PIL import Image, ImageDraw
import geo, dataset

def world_to_mosaic_px(meta, x, z):
    tx0, ty0, zz = meta
    n = 1 << zz
    lat, lon = geo.lonlat(x, z)
    gx = (lon + 180.0) / 360.0 * (n * 256.0)
    gy = (1.0 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2.0 * (n * 256.0)
    return gx - tx0 * 256, gy - ty0 * 256

def main(out="out/refs/overlay_osm.png", named=True):
    meta = eval(open('data/raw/esri_z18_meta.json').read()) if False else (197638, 113179, 18)
    img = Image.open('data/raw/esri_z18_campus.jpg').convert('RGB')
    d = ImageDraw.Draw(img)
    B, R, N, O = dataset.load()
    for r in R:
        pts = [world_to_mosaic_px(meta, x, z) for x, z in r['pts']]
        w = {'primary':4,'secondary':3,'tertiary':3,'residential':2,'unclassified':2,'service':2,'track':1,'footway':1,'path':1,'cycleway':1}.get(r['tags'].get('highway'), 1)
        d.line(pts, fill=(255,220,0), width=w)
    for b in B:
        pts = [world_to_mosaic_px(meta, x, z) for x, z in b['pts']]
        nm = b['tags'].get('name')
        d.polygon(pts, outline=(0,255,255) if nm else (255,0,255))
        if nm and named:
            cx, cz = dataset.centroid(b['pts'])
            px, py = world_to_mosaic_px(meta, cx, cz)
            d.text((px-30, py-5), nm[:22], fill=(255,255,255))
    img.save(out)
    img.resize((img.size[0]//3, img.size[1]//3)).save(out.replace('.png','_small.jpg'), quality=85)
    print('wrote', out, img.size)

if __name__ == '__main__':
    main()
