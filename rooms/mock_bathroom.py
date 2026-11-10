#!/usr/bin/env python3
"""Static isometric mock-up of The Bathroom for 'Hide and Seek'.

The 8'5 x 7'9 (2.6 m E-W x 2.4 m N-S) first-floor bathroom at the east
end of the upstairs corridor, reached through the lobby doorway. Pale
blue walls, white skirting, patterned encaustic floor (brown/terracotta,
blue-grey and cream, four-petal motif). North wall: white roll-top
clawfoot bath with metro tiles to the ceiling, a chrome rain shower and
hinged glass screen at the west end, a wooden ladder shelf at the east
end. East wall: tall sash with white plantation shutters, the close-
coupled loo beneath it and a small framed picture. West wall: open
doorway back to the corridor and a pedestal basin near the door.
South wall: open doorway into Holly's Room (the SE bedroom), near the basin.
Ceiling spots are left out (ceiling-light rule). No internal door leaf.
"""
import math
import random
import sys

import numpy as np

import house_common as hc
hc.init_room(4.6, 4.4)
from house_common import *  # noqa: E402,F401,F403
import iso_paint  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_bathroom_mock.png"

WALL = (168, 188, 202)          # pale blue
WHITE_ = (244, 242, 236)
CHROME = (196, 200, 206)
WOOD = (150, 108, 68)
CREAM = (222, 208, 184)

# west wall (x = RW) -> corridor lobby, same span as corridor BATH_DOOR
DOOR = (0.65, 2.15)
# east wall (x = 0): tall sash
WINDOW = (0.95, 2.75)
# south wall (y = 0) -> Holly's Room, east end next to the window/loo wall
HOLLY_DOOR = (0.22, 1.62)


def garden_east(side, rnd):
    """Garden beyond the east sash, a storey down."""
    ext_lawn(side, -10, 14, 0.2, 14, rnd, base=(86, 142, 60))
    ext_lawn(side, -10, 14, 3.8, 9.5, rnd, base=(108, 148, 66))
    ext_tree(side, 0.4, 4.2, trunk=90, canopy=132, r=1.15, col=(74, 120, 50), rnd=random.Random(11))
    ext_tree(side, 3.4, 6.0, trunk=102, canopy=146, r=1.3, col=(88, 130, 54), rnd=random.Random(12))
    ext_shrub(side, 1.6, 2.2, r=0.55, h=110, col=(76, 108, 60), rnd=random.Random(13))
    ext_shrub(side, 2.8, 1.6, r=0.4, h=96, col=(70, 118, 58), rnd=random.Random(14))
    ext_house_shadow(side, -10, 14, depth=0.9)


def encaustic_floor():
    """Square encaustic tiles: terracotta field, cream four-petal, blue-grey eye."""
    import paint
    ppm = 56
    tw, th = max(8, int(RW * ppm)), max(8, int(RD * ppm))
    ts = max(10, int(0.32 * ppm))
    grout = np.array((198, 180, 150), np.float32)
    img = np.empty((th, tw, 3), np.float32)
    img[:] = grout
    brown = np.array((150, 94, 58), np.float32)
    terracotta = np.array((168, 98, 62), np.float32)
    cream = np.array((224, 210, 186), np.float32)
    blueg = np.array((120, 132, 140), np.float32)
    rng = np.random.RandomState(21)
    for iy, y in enumerate(range(0, th, ts)):
        for ix, x in enumerate(range(0, tw, ts)):
            y1, x1 = min(y + ts - 2, th), min(x + ts - 2, tw)
            tile = img[y:y1, x:x1]
            if tile.shape[0] < 6 or tile.shape[1] < 6:
                continue
            field = terracotta if (ix + iy) % 2 == 0 else brown
            tile[:] = field * rng.uniform(0.93, 1.07)
            hh, ww = tile.shape[:2]
            cy, cx = hh / 2.0, ww / 2.0
            yy = np.arange(hh)[:, None]
            xx = np.arange(ww)[None, :]
            pr, pc = hh * 0.16, ww * 0.12
            petals = (
                ((yy - (cy - hh * 0.18)) / max(pr, 1)) ** 2 + ((xx - cx) / max(pc, 1)) ** 2 <= 1,
                ((yy - (cy + hh * 0.18)) / max(pr, 1)) ** 2 + ((xx - cx) / max(pc, 1)) ** 2 <= 1,
                ((yy - cy) / max(pc, 1)) ** 2 + ((xx - (cx - ww * 0.18)) / max(pr, 1)) ** 2 <= 1,
                ((yy - cy) / max(pc, 1)) ** 2 + ((xx - (cx + ww * 0.18)) / max(pr, 1)) ** 2 <= 1,
            )
            for mask in petals:
                tile[mask] = cream
            core = ((yy - cy) / max(hh * 0.10, 1)) ** 2 + ((xx - cx) / max(ww * 0.10, 1)) ** 2 <= 1
            tile[core] = blueg
    paint.stamp(np.clip(img, 0, 255).astype(np.uint8), 0, 0, RW, RD, 0)


def metro_tiles(side, u0, u1, z0=14, z1=None):
    """White metro (subway) tiles to the ceiling around the bath end."""
    z1 = WALL_H - 6 if z1 is None else z1
    k = wall_k(side)
    grout = shade((210, 214, 216), k * 0.85)
    tile = shade((246, 246, 244), k)
    wall_quad(side, u0, u1, z0, z1, grout)
    tw, th = 0.22, 8.5
    row = 0
    z = z0 + 1
    while z < z1 - 2:
        u = u0 + (0.11 if row % 2 else 0.0)
        while u < u1 - 0.04:
            b = min(u1 - 0.01, u + tw)
            wall_quad(side, u + 0.012, b - 0.012, z + 0.6, min(z1 - 1, z + th - 0.6), tile)
            u += tw
        z += th
        row += 1


def plantation_shutters(side, u0, u1, z0=70, z1=196):
    """White louvered plantation shutters folded back either side of the sash."""
    k = wall_k(side)
    w = 0.30
    for a, b in ((u0 - w - 0.05, u0 - 0.02), (u1 + 0.02, u1 + w + 0.05)):
        wall_quad(side, a, b, z0 - 6, z1 + 6, shade(WHITE_, k), 0.03)
        z = z0
        while z < z1:
            wall_quad(side, a + 0.04, b - 0.04, z, z + 3.2, shade((228, 226, 220), k * 0.9), 0.036)
            z += 6.2
        wall_quad(side, a, a + 0.035, z0 - 6, z1 + 6, shade(WHITE_, k * 1.02), 0.038)
        wall_quad(side, b - 0.035, b, z0 - 6, z1 + 6, shade(WHITE_, k * 1.02), 0.038)
        wall_quad(side, a, b, (z0 + z1) / 2 - 2, (z0 + z1) / 2 + 2, shade(WHITE_, k), 0.038)


def clawfoot_bath():
    """White roll-top clawfoot bath along the north wall."""
    x0, x1 = 0.88, RW - 0.82
    y0, y1 = RD - 1.18, RD - 0.16
    iron = (64, 56, 52)
    for fx, fy in ((x0 + 0.24, y0 + 0.20), (x1 - 0.28, y0 + 0.20),
                   (x0 + 0.24, y1 - 0.20), (x1 - 0.28, y1 - 0.20)):
        cyl(fx, fy, 0.065, 0, 14, iron)
        cyl(fx, fy, 0.12, 10, 24, shade(iron, 0.8))
        cyl(fx, fy, 0.07, 22, 30, WHITE_)
    # tub body with rounded ends
    iso_paint.paint_box(x0 + 0.10, y0 + 0.08, x1 - 0.10, y1 - 0.08, 22, 50, "bathroom_bath", front="S", col=WHITE_)
    cyl(x0 + 0.44, (y0 + y1) / 2, 0.46, 22, 50, WHITE_, top=shade(WHITE_, 1.04))
    cyl(x1 - 0.44, (y0 + y1) / 2, 0.46, 22, 50, WHITE_, top=shade(WHITE_, 1.04))
    # roll-top rim (fat white border) with the basin showing through
    iso_paint.paint_box(x0, y0, x1, y1, 48, 58, "wc_ceramic", front="S", col=WHITE_)
    cyl(x0 + 0.40, (y0 + y1) / 2, 0.52, 48, 58, WHITE_, top=shade(WHITE_, 1.12))
    cyl(x1 - 0.40, (y0 + y1) / 2, 0.52, 48, 58, WHITE_, top=shade(WHITE_, 1.12))
    qz(58.4, x0 + 0.16, y0 + 0.16, x1 - 0.16, y1 - 0.16, (168, 192, 206))
    # chrome taps at the east (window) end
    box(x1 - 0.42, (y0 + y1) / 2 - 0.08, x1 - 0.22, (y0 + y1) / 2 + 0.08, 58, 74, CHROME)
    cyl(x1 - 0.32, (y0 + y1) / 2, 0.045, 72, 84, CHROME)


def rain_shower():
    """Chrome rain head and a hinged glass screen at the west end of the bath."""
    cx, cy = RW - 0.95, RD - 0.67
    # riser and arm
    cyl(cx, cy, 0.035, 58, 220, CHROME)
    box(cx - 0.55, cy - 0.04, cx + 0.04, cy + 0.04, 214, 222, CHROME)
    # rain rose
    cyl(cx - 0.52, cy, 0.22, 208, 218, CHROME, top=shade(CHROME, 1.12))
    cyl(cx - 0.52, cy, 0.16, 204, 210, shade(CHROME, 0.85))
    # hinged glass screen (south side of the west end)
    gx0, gx1 = RW - 1.55, RW - 0.72
    gy = RD - 1.28
    box(gx0, gy, gx1, gy + 0.05, 20, 168, (186, 206, 214), top=(210, 224, 230))
    box(gx0, gy, gx0 + 0.04, gy + 0.05, 20, 168, CHROME)
    box(gx1 - 0.04, gy, gx1, gy + 0.05, 20, 168, CHROME)
    box(gx0, gy, gx1, gy + 0.05, 164, 170, CHROME)


def ladder_shelf():
    """Small wooden ladder shelf at the east end of the bath: plants, bottles, a basket."""
    x0, x1 = 0.16, 0.52
    y0, y1 = RD - 1.15, RD - 0.32
    for xx in (x0, x1 - 0.045):
        iso_paint.paint_box(xx, y0 + 0.04, xx + 0.045, y1 - 0.04, 0, 138, "up_oak", front="S", col=WOOD)
    for z in (38, 76, 114):
        iso_paint.paint_box(x0, y0 + 0.05, x1, y1 - 0.05, z, z + 5, "up_oak", front="S", col=shade(WOOD, 1.08))
    # bottles on the middle rung
    cyl(0.28, RD - 0.68, 0.045, 81, 110, (70, 110, 96))
    cyl(0.40, RD - 0.82, 0.04, 81, 106, (186, 92, 64))
    # basket on the top rung
    box(0.20, RD - 1.02, 0.46, RD - 0.78, 119, 130, (186, 150, 96), top=shade((186, 150, 96), 1.1))
    # plant pot on the floor beside the ladder
    cyl(0.34, RD - 0.48, 0.08, 0, 28, (176, 86, 58))
    cyl(0.34, RD - 0.48, 0.14, 26, 52, (62, 118, 58))
    cyl(0.28, RD - 0.44, 0.09, 44, 68, (56, 108, 52))


def pedestal_basin():
    """White pedestal basin on the west wall, just north of the corridor door."""
    x0, x1 = RW - 0.58, RW - 0.10
    y0, y1 = 2.30, 2.88
    # pedestal
    iso_paint.paint_box(x0 + 0.14, y0 + 0.16, x1 - 0.10, y1 - 0.16, 0, 52, "wc_ceramic", front="W", col=WHITE_)
    # bowl
    iso_paint.paint_box(x0, y0, x1, y1, 50, 64, "wc_ceramic", front="W", col=WHITE_)
    box(x0 + 0.08, y0 + 0.08, x1 - 0.06, y1 - 0.08, 58, 66, (214, 222, 226), top=(198, 210, 216))
    # taps and splash
    box(x1 - 0.12, (y0 + y1) / 2 - 0.06, x1 - 0.02, (y0 + y1) / 2 + 0.06, 64, 76, CHROME)
    cyl((x0 + x1) / 2, (y0 + y1) / 2, 0.035, 64, 78, CHROME)


def loo():
    """Close-coupled white loo on the east wall, under the sash."""
    x0, x1, y0, y1 = 0.08, 0.62, 1.22, 1.92
    # pan
    iso_paint.paint_box(x0 + 0.10, y0 + 0.06, x1 - 0.04, y1 - 0.06, 0, 40, "wc_ceramic", front="W", col=WHITE_)
    box(x0 + 0.16, y0 + 0.14, x1 - 0.10, y1 - 0.14, 38, 44, (230, 232, 234), top=(214, 218, 222))
    # cistern against the east wall
    iso_paint.paint_box(x0, y0 + 0.10, x0 + 0.28, y1 - 0.10, 40, 82, "wc_ceramic", front="W", col=WHITE_)
    box(x0 + 0.04, (y0 + y1) / 2 - 0.05, x0 + 0.16, (y0 + y1) / 2 + 0.05, 82, 88, CHROME)
    # small framed picture north of the cistern
    if not hc.FLIP:
        qx(0.035, 2.05, 2.42, 118, 152, shade((120, 88, 48), KX))
        qx(0.04, 2.09, 2.38, 122, 148, shade((186, 176, 150), KX))


def main():
    background()
    encaustic_floor()
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        metro_tiles("W", RD - 1.45, RD)          # east return around the bath
        ext = exterior_layer({"W": garden_east}, haze=(170, 188, 150))
        sash_window("W", *WINDOW, ext, z0=70, z1=198, curtains=None)
        plantation_shutters("W", *WINDOW, z0=70, z1=198)
        back_opening("N", *HOLLY_DOOR, glimpses.holly_from_bathroom)
    wall_trim()
    clawfoot_bath()
    rain_shower()
    ladder_shelf()
    pedestal_basin()
    loo()
    place_sprite("archie", 2.15, 2.20)
    ghost_near_walls(WALL, doors_E=[DOOR], doors_S=[])
    if hc.FLIP:
        # north wall is far here; paint the metro surround after the solid ghost fill
        metro_tiles("S", 0.0, RW)
        metro_tiles("E", RD - 1.45, RD)
    finish("Hide and Seek - The Bathroom (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_bathroom_mock.png",))


if __name__ == "__main__":
    main()
