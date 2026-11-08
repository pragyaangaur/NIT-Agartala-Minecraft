![NIT Agartala in Minecraft](docs/images/banner.jpg)

# NIT Agartala in Minecraft

This is the campus of the National Institute of Technology Agartala, rebuilt block by block in Minecraft Java Edition 26.3. One block is one metre, both across and up, so every road, hostel and hill is where it is on the ground at Barjala, Jirania. You can walk in through the main gate, find your hostel room and sit in the Library reading hall.

**Keywords:** minecraft, nit-agartala, campus-map, openstreetmap, voxel, python

## Play it

1. Download `NIT_Agartala_world_26.3.zip` from the [latest release](../../releases/latest).
2. Unzip it into your Minecraft `saves` folder. On Windows this is `%appdata%\.minecraft\saves`, and on macOS it is `~/Library/Application Support/minecraft/saves`.
3. Open Minecraft Java Edition 26.3 or newer and pick **NIT Agartala** from the world list.

The world opens in creative mode with cheats on, and you start in Knowledge Park. [docs/BUILDINGS.md](docs/BUILDINGS.md) has a teleport command for every named building, for example `/tp @s 872 76 1245` for the Library.

## The campus

| Day | Night |
| --- | --- |
| ![Top view of the model by day](docs/images/map_day.jpg) | ![Top view of the model at night](docs/images/map_night.jpg) |

The model covers about 1.9 by 2.0 km. It holds the campus and the villages round it, the real terrain, every road and footpath, the lake and the playing fields.

![Administrative Block, SAC, Knowledge Park and both auditoriums](docs/images/iso_core.png)

The academic core is in the picture above. The SAC and the Administrative Block face each other across Knowledge Park and the Swami Vivekananda statue. The Swami Vivekananda Seminar Hall stands with its green curved roof, and the Visvesvaraya Auditorium sits with its fountain forecourt.

| | |
| --- | --- |
| ![Central Library](docs/images/iso_library.png) | ![Main gate](docs/images/iso_maingate.png) |
| Central Library (Knowledge Centre) | Main gate, Gate No. 1 at Jirania |
| ![RNT Hostel and Dining Hall](docs/images/iso_rnt.png) | ![Aryabhatta Hostel](docs/images/iso_aryabhatta.png) |
| RNT Hostel towers and the Dining Hall | Aryabhatta Hostel round its oval garden |
| ![ABV Sports Complex](docs/images/iso_sports.png) | ![Village houses](docs/images/inside_village.png) |
| ABV Sports Complex | Village houses outside the wall, roofs cut away |

## Inside

Almost every building has a way in, and most have furniture. The pictures below slice the roof off just above one floor.

| | |
| --- | --- |
| ![Hostel rooms](docs/images/inside_hostel.png) | ![Classrooms](docs/images/inside_classrooms.png) |
| RNT hostel rooms, each with a bed, desk, chest and rug | Classrooms with a dark board and rows of desks |
| ![Library ground floor](docs/images/inside_library.png) | ![Seminar hall](docs/images/inside_seminar_hall.png) |
| Library stacks, reading tables and lecterns | Seminar hall seating, stage and screen |

- The Library has bookshelves on three floors, reading tables, lecterns holding a Knowledge Centre book and a circulation desk.
- Both auditoriums have a stage, a screen, curtains, raked seating and paintings on the walls.
- The RNT Dining Hall and the Aryabhatta mess have long tables and benches, and counters with chests of food.
- The Science Block has lab benches with brewing stands.
- The other buildings are furnished by type as homes, classrooms, offices or open-plan floors. Ladders join the floors.

## By the numbers

| | |
| --- | --- |
| Named buildings designed by hand | 30 |
| Other buildings, styled from their real outlines | about 970 |
| Rooms furnished | about 1,000 |
| Students standing about campus | 87 |
| Students sitting at desks | about 1,100 |
| Scale | 1 block = 1 m |
| Area | x 32 to 1887, z 64 to 2047 |

## How it was made

The base terrain and building outlines come from OpenStreetMap, Microsoft building footprints and a public elevation model. The named buildings were then designed by hand from three campus tour videos, the official campus map and the satellite view. Every step is a Python script that edits the world through the official Minecraft server, and a whole-world check makes sure nothing floats or breaks. [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) explains the pipeline, and [docs/BUILDINGS.md](docs/BUILDINGS.md) lists every building with its sources.

```
tools/          base layer: map data to terrain and first buildings
tools/hand/     hand layer: designed buildings, interiors, roads, lights, people, checks
data/osm/       OpenStreetMap extract of the campus
data/model/     height field, masks and footprints in world coordinates
docs/           guides and the pictures in this README
```

## Contributing

Classmates are welcome to help. Good first jobs are the buildings in [docs/BUILDINGS.md](docs/BUILDINGS.md) that are not tied to a name yet, and interiors for buildings you know from the inside. Each building lives in its own script in `tools/hand/`, so a change to one building does not touch the others. [CONTRIBUTING.md](CONTRIBUTING.md) explains how to place a building and check it.

## Credits

Map data is © OpenStreetMap contributors and available under the Open Database License. Building footprints come from Microsoft's Global ML Building Footprints, also under the ODbL. The tour videos used as reference belong to their creators and are not included here. Minecraft is a trademark of Mojang Studios, and this project is not affiliated with Mojang or with NIT Agartala.
