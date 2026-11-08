"""Three small named places with no usable photo: CSE Canteen, ECE Canteen and Monty Xerox.

Position and size come from their OSM outlines; the look is creative liberty in the style
of Indian campus canteens and photocopy shops (a serving counter with an awning, tin roofs,
plastic-chair seating, a painted name board, a shop shutter front with a water tank on top).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vox import Vox

NAME = "smallnamed"
CLEAR = (430, 1285, 805, 1375)


def sign(x, y, z, text, rot, colour="#ffffff", scale=0.8):
    return (f'summon text_display {x} {y} {z} {{Rotation:[{rot}f,0f],background:0,'
            f'text:{{text:"{text}",color:"{colour}"}},transformation:{{left_rotation:[0f,0f,0f,1f],'
            f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}}}}')


def clear(x0, z0, x1, z1, g, gy, top=14, ground="grass_block"):
    cmds = []
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            t = gy(x, z)
            cmds.append(f"fill {x} {min(t, g) + 1} {z} {x} {max(t, g) + top} {z} air")
            if t < g:
                cmds.append(f"fill {x} {t} {z} {x} {g - 1} {z} dirt")
            cmds.append(f"setblock {x} {g} {z} {ground}")
    return cmds


def table(v, x, z, y=1, umbrella=None):
    v.set(x, y, z, "oak_fence"); v.set(x, y + 1, z, "white_carpet")
    for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
        v.set(x + dx, y, z + dz, f"white_concrete" if False else f"quartz_stairs[facing={f}]")
    if umbrella:
        for k in range(2, 4):
            v.set(x, y + k, z, "oak_fence")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                v.set(x + dx, y + 4, z + dz, umbrella)


def canteen(colour, trim, awning, name):
    """9 x 7 kiosk with a tin lean-to roof, a serving hatch and seating in front (south)."""
    v = Vox(13, 9, 15)
    x0, x1, z0, z1 = 2, 10, 1, 7
    v.box(x0, x1, 0, 0, z0, z1, "smooth_stone")
    v.box(x0, x1, 1, 4, z0, z1, colour)
    v.box(x0 + 1, x1 - 1, 1, 4, z0 + 1, z1 - 1, None)
    v.box(x0, x1, 1, 1, z0, z1, trim)                        # painted plinth
    for x in range(x0 + 2, x1 - 1):                          # serving hatch and counter
        v.set(x, 2, z1, "smooth_quartz_slab[type=top]")
        v.set(x, 3, z1, None)
    v.set(x0 + 1, 2, z1, "spruce_door[half=lower,facing=south]"); v.set(x0 + 1, 3, z1, "spruce_door[half=upper,facing=south]")
    for x in range(x0 - 1, x1 + 2):                          # tin roof sloping to the back
        for z in range(z0 - 1, z1 + 2):
            v.set(x, 5 if z >= (z0 + z1) // 2 else 5, z, "light_gray_concrete" if z % 2 else "iron_block")
        v.set(x, 4, z1 + 1, awning); v.set(x, 4, z1 + 2, awning)
    for x in range(x0 + 1, x1):                              # inside: counter, urn, fridge
        v.set(x, 1, z1 - 1, "smooth_stone_slab")
    v.set(x0 + 2, 2, z1 - 1, "cauldron"); v.set(x1 - 1, 1, z0 + 1, "iron_block"); v.set(x1 - 1, 2, z0 + 1, "iron_trapdoor[facing=south,open=true]")
    v.set(x0 + 4, 2, z1 - 1, "brewing_stand")
    for x in range(x0 - 1, x1 + 2):                          # paved seating area
        for z in range(z1 + 1, 15):
            v.set(x, 0, z, "polished_andesite" if (x + z) % 2 else "andesite")
    table(v, 4, 11); table(v, 8, 11); table(v, 6, 13 if False else 13, umbrella=awning)
    for z in range(z1 + 3, 15):                              # bench along the side
        v.set(0, 1, z, "spruce_slab")
    return v, name


def monty():
    """Photocopy and stationery shop: two storeys, shutter front, blue awning, tank on top."""
    v = Vox(18, 14, 20)
    x0, x1, z0, z1 = 1, 16, 1, 15
    v.box(x0, x1, 0, 0, z0, z1, "smooth_stone")
    v.box(x0, x1, 1, 8, z0, z1, "white_terracotta")
    v.box(x0 + 1, x1 - 1, 2, 7, z0 + 1, z1 - 1, None)
    v.box(x0 + 1, x1 - 1, 4, 4, z0 + 1, z1 - 1, "smooth_stone")
    v.box(x0, x1, 8, 8, z0, z1, "light_gray_concrete")
    for x in range(x0, x1 + 1):
        v.set(x, 9, z0, "white_terracotta"); v.set(x, 9, z1, "white_terracotta")
    for z in range(z0, z1 + 1):
        v.set(x0, 9, z, "white_terracotta"); v.set(x1, 9, z, "white_terracotta")
    # shop front (south): two open shop bays, one rolled-down shutter
    for x in range(x0 + 1, x1):
        for y in (1, 2, 3):
            v.set(x, y, z1, None if x not in (x0 + 5, x0 + 10) else "white_terracotta")
        v.set(x, 3, z1, "iron_trapdoor[facing=south,half=top]" if x0 + 11 <= x else None)
    for x in range(x0 + 11, x1):
        for y in (1, 2):
            v.set(x, y, z1, "iron_block")                    # shutter down
    for x in range(x0, x1 + 1):                              # blue awning and name board
        v.set(x, 4, z1 + 1, "blue_concrete"); v.set(x, 4, z1 + 2, "blue_concrete")
        v.set(x, 5, z1, "yellow_concrete")
    # counters with copiers inside
    for x in range(x0 + 1, x0 + 5):
        v.set(x, 1, z1 - 2, "smooth_quartz_slab")
    for x in (x0 + 2, x0 + 7, x0 + 8):
        v.set(x, 1, z0 + 2, "white_concrete"); v.set(x, 2, z0 + 2, "light_gray_carpet")
    v.set(x0 + 9, 1, z1 - 2, "bookshelf"); v.set(x0 + 9, 2, z1 - 2, "bookshelf"); v.set(x0 + 8, 1, z1 - 2, "bookshelf")
    # upper floor windows and a small balcony
    for x in range(x0 + 2, x1 - 1, 3):
        v.set(x, 6, z1, "tinted_glass"); v.set(x + 1, 6, z1, "tinted_glass"); v.set(x, 7, z1, "tinted_glass"); v.set(x + 1, 7, z1, "tinted_glass")
    for z in range(z0 + 2, z1 - 1, 3):
        v.set(x0, 2, z, "tinted_glass"); v.set(x1, 2, z, "tinted_glass")
        v.set(x0, 6, z, "tinted_glass"); v.set(x1, 6, z, "tinted_glass")
    # outside stair to the roof on the east side
    for k in range(8):
        v.set(x1 + 1, 1 + k, z0 + 2 + k, "stone_brick_stairs[facing=south]")
    # black water tank and a dish
    v.box(x0 + 2, x0 + 4, 9, 11, z0 + 2, z0 + 4, "black_concrete")
    v.set(x1 - 2, 9, z0 + 2, "iron_bars"); v.set(x1 - 2, 10, z0 + 2, "white_concrete")
    return v


def commands(gy):
    cmds = []
    # CSE Canteen, outline centre (795, 1298), faces south
    v, _ = canteen("orange_terracotta", "white_concrete", "red_concrete", "CSE CANTEEN")
    ox, oz = 789, 1292
    g = gy(795, 1298)
    cmds += clear(ox, oz, ox + 12, oz + 14, g, gy, ground="grass_block")
    cmds += v.commands(ox, g, oz)
    cmds.append(sign(ox + 6.5, g + 3.75, oz + 8 + 2.03, "CSE CANTEEN", 0, "#ffffff", 0.9))
    # ECE Canteen, outline centre (795, 1364)
    v, _ = canteen("light_blue_terracotta", "white_concrete", "yellow_concrete", "ECE CANTEEN")
    ox, oz = 789, 1357
    g = gy(795, 1364)
    cmds += clear(ox, oz, ox + 12, oz + 14, g, gy)
    cmds += v.commands(ox, g, oz)
    cmds.append(sign(ox + 6.5, g + 3.75, oz + 8 + 2.03, "ECE CANTEEN", 0, "#202020", 0.9))
    # Monty Xerox, outline centre (452, 1310)
    v = monty()
    ox, oz = 443, 1300
    g = gy(452, 1310)
    cmds += clear(ox, oz, ox + 17, oz + 19, g, gy, top=20)
    cmds += v.commands(ox, g, oz)
    cmds.append(sign(ox + 9, g + 5.25, oz + 15 + 1.03, "MONTY XEROX", 0, "#c00000", 0.75))
    return cmds


CHECKS = []

if __name__ == "__main__":
    out = sys.argv[1]
    canteen("orange_terracotta", "white_concrete", "red_concrete", "x")[0].iso("se", 14).save(os.path.join(out, "canteen.png"))
    monty().iso("se", 12).save(os.path.join(out, "monty.png"))
