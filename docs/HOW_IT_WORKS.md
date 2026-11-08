# How the world is made

The world is built in two layers. The base layer turns map data into a 1:1 terrain and a first set of buildings. The hand layer replaces the important buildings with designed ones, styles the rest, and adds roads, trees, interiors, lights and people. Every step is a Python script, so the whole world can be rebuilt from the data in this repository.

## Coordinates

One block is one metre, both across and up. The model covers x 32 to 1887 and z 64 to 2047, which is about 1.9 by 2.0 km round the campus at Barjala, Jirania. North is towards negative z. The ground sits between y 56 and y 81, following the real terrain.

## Base layer (`tools/`)

`tools/main.py` runs the base layer. Set `STAGE=all` to build the voxel model and `STAGE=write` to write it as a world.

- `osm_fetch.py` and `dataset.py` download the campus from OpenStreetMap with Overpass and turn it into world coordinates (`data/osm/`).
- `terrain.py` turns a public elevation model into a smoothed 1 m height field (`data/model/gy.npy`).
- `msfoot.py` adds Microsoft building footprints where OpenStreetMap has none (`data/model/ms_new.json`).
- `builder.py` and `specs.py` raise the first buildings from their outlines.
- `anvil.py`, `nbt.py` and `pack.py` write the regions as a Minecraft 26.3 save, using the server-made template in `data/skeleton/`.

## Hand layer (`tools/hand/`)

The hand layer edits the world through the official 26.3 server, run headless. Each script produces commands. `mcserver.py` writes them into a datapack as functions of at most 20,000 commands, loads the area with `forceload`, runs the functions and saves. Long jobs are split into sessions of about ten 256 by 256 tiles so the server does not run out of memory.

`place.py <name> ...` places one or more buildings. A building module is one of two kinds.

- **Voxel modules** draw the building in a small grid with `vox.py` and are placed square to the world grid. The Administrative Block, SAC, Library, CSE, ECE, both auditoriums and the gates are made this way.
- **Footprint modules** use `extrude.py`, which raises a building from its real outline with storeys, bands, pilasters, windows with sunshades, an entrance, a roof kit and ceiling lights. The hostels, the Science Block, Civil, Mechanical, Chemical, the hospital and others are made this way. `interiors.py` adds hostel rooms, mess halls and labs to them.

The rest of the world comes from scripts that work over the whole map.

| Script | What it does |
| --- | --- |
| `generic.py`, `genbatch.py` | Restyle about 970 unnamed buildings from their outlines, with seeded looks |
| `env.py`, `liveworld.py`, `life2.py` | Roads with kerbs and footpaths, lamps, benches, bins, parked cars, trees, grass and flowers |
| `grounds.py`, `lake.py` | The RNT Ground, the stadium oval and the campus lake |
| `furnish_all.py` | Finds every room in every building and furnishes it as a home, classroom, office, open-plan floor or hall. It also cuts doors into closed ground floors and adds ladders between floors |
| `lightlife.py` | Hidden light blocks in every room and along paths and roads, and dressed armour stands as students |
| `leaves.py` | Makes every leaf block persistent so trees never decay |
| `worldedge.py` | Turns land past the model into flat grass and sets the world border |
| `audit.py` | Scans every block for floating parts and anything that would pop off, and fixes them |
| `entclean.py` | Removes dropped items and animals, one tile per server session |
| `render_readme.py` | Draws the maps and views in `docs/images/` straight from the save |

## Checks

`audit.py report` loads the world with `fastworld.py`, a numpy reader for 26.3 region files, and checks every block from y 56 to y 140. It looks for these problems.

- Parts that do not touch the ground through other blocks (floating).
- Plants without soil, sugar cane without water and lily pads without water.
- Carpets, pots, cakes and standing lanterns with nothing under them.
- Hanging lanterns with nothing above them.
- Sand, gravel and concrete powder over air.
- Beds with only one half.

`audit.py fix` replaces or removes each problem block. The world ships with an audit count of zero.

## Game rules in the save

Random ticks are off and block and entity drops are off, so nothing grows, decays or drops. Mob spawning, patrols, traders and phantoms are off. The world border is 1984 blocks wide, centred on 960 1056.

## Reproducing the hand layer

1. Install Minecraft Java 26.3 and Python 3 with `numpy`, `scipy` and `Pillow`.
2. Copy a world save to `work/world_edit/`. The released world is the easiest start.
3. Run any hand script from `tools/hand/`, for example `python3 place.py library`. The server jar is downloaded on the first run. Set `NITA_JAVA` if Java 25 or newer is not on the PATH.
4. Run `python3 audit.py report` to check the result.
