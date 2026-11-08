# Contributing

Thank you for helping to build the campus. This page explains how to change one building and check the result before you open a pull request.

## Setting up

1. Install Minecraft Java Edition 26.3 and Python 3 with `numpy`, `scipy` and `Pillow`.
2. Download the world from the latest release and unzip it to `work/world_edit/`, so that `work/world_edit/level.dat` exists.
3. Make sure Java 25 or newer is on your PATH, or set `NITA_JAVA` to the Java binary. The Minecraft launcher on macOS already ships one, and the scripts find it.

## Changing a building

Each named building has its own script in `tools/hand/`, listed in [docs/BUILDINGS.md](docs/BUILDINGS.md). Edit the script, then place it.

```bash
cd tools/hand
python3 place.py library
```

The first run downloads the official server jar. The script prints any command the server rejects, so read the last lines of its output.

A new building needs a new script. Copy a similar one: a voxel module such as `ece.py` for a building drawn by hand, or a footprint module such as `civil.py` for a building raised from its real outline. Set `CLEAR` to the box the building may clear, and give the source of every detail in the docstring, such as a video timestamp or a map label.

## Checking your change

Run the audit after every change. It must report zero problems.

```bash
python3 audit.py report
```

If it finds floating or unsupported blocks, `python3 audit.py fix` removes them. Then render your area to look at it from above, for example with `python3 render_readme.py ../../work/world_edit /tmp/look iso library`, and walk round it in the game.

## Pull requests

Keep one building or one fix in each pull request. Say what changed, which source you used, and include a screenshot from the game. Do not commit world files, renders or reference videos. The `.gitignore` already keeps them out.
