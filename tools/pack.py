"""Pack the generated regions into a valid 26.3 world save using a server-made skeleton."""
import os, shutil, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import nbtparse, nbt as N

def pack(src_regions=".scratch/gen/NITAgartala/region", out="out/world/NITAgartala",
         skeleton="data/skeleton", spawn=(632, 96, 964), levelname="NIT Agartala 1:1 (Barjala, Jirania, Tripura)"):
    world = out
    if not os.path.isdir(src_regions):
        raise SystemExit(f"no regions at {src_regions}; run STAGE=write first")
    tmp = out + ".tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(skeleton, tmp)
    dim = os.path.join(tmp, "dimensions", "minecraft", "overworld")
    os.makedirs(os.path.join(dim, "region"), exist_ok=True)
    for f in os.listdir(src_regions):
        if f.endswith(".mca"):
            shutil.copy2(os.path.join(src_regions, f), os.path.join(dim, "region", f))
    # patch level.dat
    name, tree = nbtparse.load(os.path.join(tmp, "level.dat"))
    d = tree["Data"]
    d["LevelName"] = N.Str(levelname)
    if "spawn" in d:
        d["spawn"]["pos"] = N.IA([int(spawn[0]), int(spawn[1]), int(spawn[2])])
    d["GameType"] = N.I(1)
    d["allowCommands"] = N.B(1)
    if "difficulty_settings" in d:
        d["difficulty_settings"]["difficulty"] = N.Str("peaceful")
    nbtparse.save(os.path.join(tmp, "level.dat"), name, tree)
    for junk in ("session.lock", "level.dat_old"):
        p = os.path.join(tmp, junk)
        if os.path.exists(p): os.remove(p)
    if os.path.exists(world):
        shutil.rmtree(world)
    os.rename(tmp, world)
    dim = os.path.join(world, "dimensions", "minecraft", "overworld")
    n = sum(1 for f in os.listdir(os.path.join(dim, "region")) if f.endswith(".mca"))
    print(f"packed world -> {world}  regions={n}")
    return world

if __name__ == "__main__":
    pack()
