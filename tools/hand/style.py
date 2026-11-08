"""Shared pieces for the red-and-white NIT Agartala campus style."""
import math
from vox import disk

WHITE = "smooth_quartz"
RED = "red_terracotta"
GLASS = "tinted_glass"
LGLASS = "light_gray_stained_glass"
GREY = "light_gray_concrete"
ROOF = "white_concrete"
FLOOR = "smooth_stone"
PAVE = "pink_terracotta"
PAVE_LINE = "white_terracotta"


class Face:
    """Maps facade coordinates (u along the face, y up) to grid cells for one side of a box.
    u runs left to right as seen from outside."""
    def __init__(self, v, side, x0, x1, z0, z1):
        self.v, self.side = v, side
        self.x0, self.x1, self.z0, self.z1 = x0, x1, z0, z1
        self.n = (x1 - x0 + 1) if side in ("north", "south") else (z1 - z0 + 1)

    def xz(self, u, out=0):
        """out > 0 moves outward from the wall plane, out < 0 inward."""
        s = self.side
        if s == "north": return self.x0 + u, self.z0 - out
        if s == "south": return self.x1 - u, self.z1 + out
        if s == "east":  return self.x1 + out, self.z0 + u
        return self.x0 - out, self.z1 - u            # west

    def set(self, u, y, b, out=0):
        if 0 <= u < self.n:
            x, z = self.xz(u, out)
            self.v.set(x, y, z, b)

    def rect(self, u0, u1, y0, y1, b, out=0):
        for u in range(u0, u1 + 1):
            for y in range(y0, y1 + 1):
                self.set(u, y, b, out)

    def ring_window(self, uc, yc, r_out=3.3, r_in=2.3, ring=WHITE, glass=GLASS, out=0):
        for (u, y) in disk(uc, yc, r_out):
            self.set(u, y, ring, out)
        for (u, y) in disk(uc, yc, r_in):
            self.set(u, y, glass, out)


def shell(v, x0, x1, z0, z1, floors=(1, 5, 9, 13), top=17, wall=WHITE):
    """Hollow box with floor slabs, flat roof and parapet."""
    v.box(x0, x1, 1, top, z0, z1, wall)
    v.box(x0 + 1, x1 - 1, 2, top - 1, z0 + 1, z1 - 1, None)
    for fy in floors:
        v.box(x0 + 1, x1 - 1, fy, fy, z0 + 1, z1 - 1, FLOOR)
    v.box(x0, x1, top, top, z0, z1, ROOF)
    v.box(x0, x1, 0, 0, z0, z1, FLOOR)
    for x in range(x0, x1 + 1):
        v.set(x, top + 1, z0, wall); v.set(x, top + 1, z1, wall)
    for z in range(z0, z1 + 1):
        v.set(x0, top + 1, z, wall); v.set(x1, top + 1, z, wall)


def bay_wall(f, u0, u1, floors=(1, 5, 9, 13), module=4, red_ground=True, red_spandrel=True):
    """White piers every `module`, two-wide windows, red spandrels between floors."""
    for u in range(u0, u1 + 1):
        m = (u - u0) % module
        for fy in floors:
            for dy in range(4):
                y = fy + dy
                if m == 0:
                    b = WHITE
                elif dy in (1, 2) and m in (1, 2):
                    b = GLASS
                elif fy == floors[0] and red_ground:
                    b = RED
                elif red_spandrel:
                    b = RED if dy in (0, 3) else WHITE
                else:
                    b = WHITE
                f.set(u, y, b)


def red_tower(f, u0, u1, top=19, bands=(3, 7, 11, 15), depth=4):
    """Red stair tower on the facade, rising above the roof, with white bands."""
    for u in range(u0, u1 + 1):
        for y in range(1, top + 1):
            f.set(u, y, RED)
        for y in bands:
            f.set(u, y, WHITE)
        for d in range(1, depth):
            for y in range(17, top + 1):
                f.set(u, y, RED, out=-d)


def roof_boxes(v, boxes, y=18, h=3):
    for (xa, za, xb, zb) in boxes:
        v.box(xa, xb, y, y + h - 1, za, zb, WHITE)
        v.box(xa, xb, y + h, y + h, za, zb, "smooth_quartz_slab")


def paving(x, z, gx0, gz0, step=5):
    return PAVE_LINE if (x - gx0) % step == 0 or (z - gz0) % step == 0 else PAVE
