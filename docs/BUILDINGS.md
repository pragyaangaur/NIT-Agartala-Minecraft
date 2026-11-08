# Buildings

Every named building has its own script in `tools/hand/`. The teleport commands work in the world with cheats on. Sources are the three public campus tour videos on YouTube, cited by timestamp as W7D ([W7D6gLvjizM](https://www.youtube.com/watch?v=W7D6gLvjizM)), Jkb ([JkbNik31wDE](https://www.youtube.com/watch?v=JkbNik31wDE)) and SqZ ([SqZLoYQonbc](https://www.youtube.com/watch?v=SqZLoYQonbc)). Other sources are the official campus map in the UG reporting guide 2024, the October 2025 Wi-Fi EoI hotspot diagram, OpenStreetMap, Microsoft building footprints and the satellite view.

## Hand-built

| Building | Script | Teleport | Main evidence |
| --- | --- | --- | --- |
| Administrative Block (OSM "Academic Block 1") | `ab1.py` | `/tp @s 593 76 1250` | W7D 1:24, Jkb 2:28 caption |
| SAC Building, Student Activity Centre (OSM "Academic Block 2") | `ab2.py` | `/tp @s 560 78 1238` | Jkb 0:22 caption |
| Knowledge Park with the Swami Vivekananda statue | `plaza.py` | `/tp @s 571 76 1215` | Jkb 0:14 caption |
| Central Library, Knowledge Centre | `library.py` | `/tp @s 872 76 1245` | W7D 2:02 to 2:32 |
| CSE Department (sign moved to the Library side) | `cse.py` | `/tp @s 802 76 1275` | W7D 2:12 |
| Round garden by the Library and CSE | `circle.py` | `/tp @s 862 76 1330` | W7D 2:26 |
| ECE Building (ECE, EE, EIE) | `ece.py` | `/tp @s 772 72 1430` | Jkb 0:48, 2:06 |
| Aryabhatta Hostel (7 wing pairs round the oval garden) | `aryabhatta.py` | `/tp @s 540 90 870` | Jkb 6:52 caption; satellite |
| RNT (Rabindranath Tagore) Hostel and Dining Hall | `rnt.py` | `/tp @s 926 80 790` | W7D 5:12, 5:26 ("DINING HALL") |
| Gargi Girls Hostel | `gargi.py` | `/tp @s 1270 95 850` | official map label 14; satellite |
| International Guest House | `guesthouse.py` | `/tp @s 1233 80 1245` | Jkb 5:32 caption; W7D 2:42 |
| Visvesvaraya Auditorium | `visvesvaraya.py` | `/tp @s 631 78 1120` | Jkb 3:12 sign |
| New Auditorium (very likely the Swami Vivekananda Seminar Hall) | `newaud.py` | `/tp @s 565 78 1195` | W7D 0:16, 1:02; Wi-Fi diagram |
| Civil Engineering Department | `civil.py` | `/tp @s 652 76 1070` | Jkb 3:18 sign |
| Science Block (5 storeys round a courtyard) | `science.py` | `/tp @s 455 78 1295` | OSM relation 5385969; W7D 0:40 |
| Mechanical Department / Old Academic Building (sawtooth workshop roofs) | `mechanical.py` | `/tp @s 515 80 1365` | Jkb 5:02 caption; W7D 0:50 |
| Chemical Engineering Department | `chemical.py` | `/tp @s 475 76 1375` | Jkb 5:12 caption |
| Domed round building west of the SAC (name not known) | `dome.py` | `/tp @s 503 80 1222` | W7D 0:20 |
| NITA Hospital / Medical Centre | `hospital.py` | `/tp @s 900 76 1100` | Jkb 3:54 caption |
| Food court | `foodcourt.py` | `/tp @s 655 78 1210` | Jkb 3:08 caption |
| Main Gate (Gate No. 1, Jirania) | `maingate.py` | `/tp @s 656 66 1650` | Jkb 0:36, SqZ 0:02 |
| Gate No. 2 (Ranir Bazar), west edge | `gate2.py` | `/tp @s 170 77 1101` | official map; style from Jkb 8:06 |
| Gate No. 3, north-east (position inferred from BWC minutes) | `gate3.py` | `/tp @s 1478 74 350` | BWC50 item 47.9 |
| ABV Sports Complex (two halls, arena, entrance block) | `sports.py` | `/tp @s 1131 76 375` | SqZ 2:04 sign; W7D 5:42 |
| Kendriya Vidyalaya | `kv.py` | `/tp @s 350 78 1045` | Jkb 7:24 sign; matched by route |
| Market Complex (Maharaja Bir Bikram Amenity Centre) | `market.py` | `/tp @s 1555 76 340` | official map label 16; satellite |
| Director's Bungalow | `bungalow.py` | `/tp @s 1308 78 1250` | Jkb 5:26 sign |

## Small named buildings (creative, no photo)

| Building | Script | Teleport |
| --- | --- | --- |
| CSE Canteen (tea-stall kiosk, seating outside) | `smallnamed.py` | `/tp @s 795 76 1312` |
| ECE Canteen | `smallnamed.py` | `/tp @s 795 73 1377` |
| Monty Xerox (two-storey photocopy shop) | `smallnamed.py` | `/tp @s 452 74 1325` |

## Everything else

`generic.py` restyles about 970 unnamed buildings from their real outlines. About 150 on campus are huts, sheds, offices and two to five storey blocks with colour bands and water tanks. About 800 village houses outside the campus wall have assorted colours, tin or thatch roofs and verandas. The look of each building is seeded by its footprint id, so a rerun gives the same result.

`furnish_all.py` then furnishes every room it can find in those buildings. Homes get a bed, storage and a rug. Campus rooms become classrooms with a board and rows of desks, offices with desks and shelves, or open-plan floors with desk blocks and aisles.

## Not tied to a name yet

- **Faculty Quarters.** Jkb 5:40 and W7D 7:46 show four cream towers with red sunshades, but they have not been found on the satellite yet.
- **Dhalai, Gomati, Howrah and Saima hostels.** The Wi-Fi diagram gives only rough arrows.
- **The west academic cluster.** This covers the New Academic Building (NB), CDAC, Maths, Workshop-1 (Central Workshop), Workshop-2 (Old KV), New Admin-2, the Smart Lecture Halls, and the New ME & Civil Workshop opposite ECE. The official map numbers them, but the footprints are not tied to names yet.
- **Bio Engineering building next to the Library, and the New Canteen & VCR Building.**
- **Staff housing (H2 to H5 blocks, Type II to IV quarters)** in the north-east cluster.

## Notes

- Buildings at an angle are built from their real outlines with `extrude.py`. The Administrative Block, SAC, Library, CSE, ECE, Visvesvaraya and the main gate are hand-designed and kept square to the grid.
- Sign text uses text display entities.


