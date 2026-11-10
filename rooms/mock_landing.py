#!/usr/bin/env python3
"""Static isometric mock-up of the first-floor Landing for 'Hide and Seek'.

Above the Hall (same 3.2 x 8.05 tiles, same origin). Stairs against the east
wall rise north from the Hall and open here; the well occupies the east side
of the floor, with a white-spindle balustrade and mahogany handrail. South
wall: sash window over the front door (willow outside) and a radiator.
North wall: arched opening into the upstairs corridor. West wall: doorway
to the master bedroom and a gold-framed photo gallery (far only in the
opposite view). East wall: doorway to the south-east bedroom and a
parliament canvas (far in the usual view). Pale oak laminate, light grey
walls, white skirting, a scalloped jute rug.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(3.2, 8.05)
from house_common import *  # noqa: E402,F401,F403
import iso_paint  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_landing_mock.png"

WALL = (188, 190, 192)
OAK1, OAK2 = (198, 164, 104), (176, 140, 82)
JUTE = (186, 166, 122)
MAHOGANY = (112, 48, 32)
CARPET = (198, 188, 172)
GOLD = (196, 158, 72)
GREY_CURTAIN = (150, 152, 156)
WHITE_ = (244, 242, 236)

# openings
ARCH = (0.35, 2.85)             # north wall -> corridor
MASTER_DOOR = (0.50, 1.75)      # west wall -> master bedroom (south end, opposite the SE bedroom door)
SE_BED_DOOR = (0.45, 1.70)      # east wall -> SE bedroom
WINDOW = (0.85, 2.15)           # south wall
WELL_X0, WELL_X1 = 0.02, 1.62
WELL_Y0, WELL_Y1 = 3.18, 7.20


def front_garden(side, rnd):
    """Willow and front lawn, as seen from the landing window above the door."""
    ext_lawn(side, -6, 10, 0, 12, rnd)
    ext_hedge(side, -6, 10, 4.6, 5.3, h=88, rnd=rnd)
    ext_picket_fence(side, -6, 10, 3.55)
    ext_tree(side, 1.5, 3.4, trunk=130, canopy=160, r=1.35, col=(96, 140, 64), rnd=random.Random(4))
    ext_paving(side, -1.4, 1.4, 0.2, 5.5, rnd, col=(170, 160, 144), slab=0.5)
    ext_paving(side, -6, 10, 0.15, 1.15, rnd, col=(160, 152, 138))
    ext_house_shadow(side, -6, 10)


def oak_floor(x0, y0, x1, y1, seed=6):
    import paint
    w, h = max(0.3, x1 - x0), max(0.3, y1 - y0)
    paint.stamp(paint.timber(w, h, seed, OAK1, OAK2, along="y", plank=0.26), x0, y0, x1, y1, 0)


def floors():
    oak_floor(0, 0, RW, WELL_Y0, seed=6)
    oak_floor(WELL_X1, WELL_Y0, RW, WELL_Y1, seed=7)
    oak_floor(0, WELL_Y1, RW, RD, seed=8)


def well_stairs():
    """Carpeted flight dropping through the stairwell, matching the Hall stairs
    (rise north, so they go down toward the south). Treads stay inside the well
    so they do not project out of the cut-away."""
    SHAFT = shade(WALL, 0.42)
    qx(WELL_X0 + 0.02, WELL_Y0, WELL_Y1, -22, 2, SHAFT)
    qy(WELL_Y0 + 0.02, WELL_X0, WELL_X1, -22, 2, shade(WALL, 0.38))
    qz(-6, WELL_X0 + 0.06, WELL_Y0 + 0.06, WELL_X1 - 0.06, WELL_Y1 - 0.04, shade(CARPET, 0.5))
    n, run, rise = 6, 0.30, 9
    for i in range(n):
        y1 = WELL_Y1 - 0.04 - i * run
        y0 = y1 - run
        if y0 < WELL_Y0 + 0.08:
            break
        z = -3 - i * rise
        qz(z, WELL_X0 + 0.08, y0, WELL_X1 - 0.10, y1, shade(CARPET, KT * (1.0 if i % 2 else 0.92)))
        qy(y1, WELL_X0 + 0.08, WELL_X1 - 0.10, z - rise, z, shade(CARPET, KY * 0.82))
    # brass threshold at the top step
    box(WELL_X0 + 0.06, WELL_Y1 - 0.04, WELL_X1 - 0.06, WELL_Y1 + 0.03, 0, 3, GOLD, top=shade(GOLD, 1.15))


def balustrade():
    """White square spindles and a dark handrail around the well, open at the
    north (top-of-stairs) end so you can walk down."""
    hx = WELL_X1 - 0.06
    # west rail (along the well)
    y = WELL_Y0 + 0.12
    while y < WELL_Y1 - 0.08:
        box(hx - 0.03, y - 0.015, hx + 0.03, y + 0.015, 8, 92, WHITE_, ol=False)
        y += 0.16
    box(hx - 0.05, WELL_Y0 + 0.04, hx + 0.05, WELL_Y1 - 0.02, 90, 100, MAHOGANY, top=shade(MAHOGANY, 1.18))
    # south rail (across the foot of the well)
    x = WELL_X0 + 0.18
    while x < WELL_X1 - 0.08:
        box(x - 0.015, WELL_Y0 - 0.03, x + 0.015, WELL_Y0 + 0.03, 8, 92, WHITE_, ol=False)
        x += 0.16
    box(WELL_X0 + 0.1, WELL_Y0 - 0.05, WELL_X1 - 0.02, WELL_Y0 + 0.05, 90, 100, MAHOGANY, top=shade(MAHOGANY, 1.18))
    # newel at the south-west corner of the well
    nx, ny = WELL_X1 - 0.04, WELL_Y0
    box(nx - 0.07, ny - 0.07, nx + 0.07, ny + 0.07, 0, 36, MAHOGANY, top=shade(MAHOGANY, 1.2))
    cyl(nx, ny, 0.05, 36, 96, MAHOGANY)
    cyl(nx, ny, 0.075, 96, 108, MAHOGANY, top=shade(MAHOGANY, 1.28))


def jute_rug(cx, cy, r=0.95):
    """Scalloped round jute rug."""
    fl_ellipse(cx, cy, r + 0.04, r * 0.72 + 0.03, shade(JUTE, 0.72), z=0.4, n=36)
    fl_ellipse(cx, cy, r, r * 0.72, shade(JUTE, 0.95), z=0.6, n=36)
    # scallops around the rim
    for i in range(16):
        a = 2 * math.pi * i / 16
        fl_ellipse(cx + r * 0.92 * math.cos(a), cy + r * 0.66 * math.sin(a),
                   0.14, 0.1, shade(JUTE, 0.88 + 0.08 * (i % 2)), z=0.7, n=12)
    fl_ellipse(cx, cy, r * 0.55, r * 0.4, shade(JUTE, 1.08), z=0.8, n=28)


def radiator(u0, u1, side="N"):
    y = 0.12
    iso_paint.paint_box(u0, y, u1, y + 0.22, 8, 52, "hall_radiator", front="N", col=WHITE_)
    for i in range(8):
        xx = u0 + 0.06 + i * (u1 - u0 - 0.1) / 7
        qy(y + 0.22, xx, xx + 0.035, 12, 48, shade(WHITE_, KY * 0.9))


def photo_gallery():
    """About fourteen small gold frames and a brass picture light, on the west wall."""
    if not hc.FLIP:
        return
    x = RW - 0.04
    frames = []
    y0, z0 = 3.55, 118
    cols, rows = 7, 2
    for j in range(rows):
        for i in range(cols):
            frames.append((y0 + i * 0.38, z0 + j * 38, 0.28, 28))
    rnd = random.Random(11)
    for (ya, za, w, h) in frames:
        yb, zb = ya + w, za + h
        qx(x, ya - 0.015, yb + 0.015, za - 2, zb + 2, shade(GOLD, KX))
        tone = rnd.choice([(210, 200, 184), (80, 78, 74), (186, 176, 158), (120, 116, 108)])
        qx(x - 0.004, ya, yb, za, zb, shade(tone, KX * 0.95))
    # picture light
    mid = y0 + 3 * 0.38 + 0.14
    box(RW - 0.14, mid - 0.22, RW - 0.03, mid + 0.22, 198, 206, GOLD)
    cyl((RW - 0.08), mid, 0.04, 206, 214, GOLD)


def parliament_canvas():
    """A dusk sky and dark towers — a geometric stand-in, not anyone's artwork."""
    if hc.FLIP:
        return
    y0, y1, z0, z1 = 4.55, 6.35, 78, 188
    qx(0.03, y0 - 0.06, y1 + 0.06, z0 - 5, z1 + 5, shade((48, 42, 34), KX))
    qx(0.04, y0, y1, z0, z1, shade((72, 96, 124), KX))
    qx(0.041, y0, y1, z0, z0 + 36, shade((168, 150, 128), KX))   # pale band of sky
    # towers
    for ya, yb, top in ((4.7, 5.05, 168), (5.15, 5.55, 180), (5.7, 6.2, 160)):
        qx(0.045, ya, yb, z0, top, shade((32, 34, 40), KX))
        qx(0.046, (ya + yb) / 2 - 0.04, (ya + yb) / 2 + 0.04, top, top + 10, shade((28, 30, 34), KX))


def main():
    background()
    floors()
    well_stairs()
    jute_rug(2.15, 2.15, r=0.92)
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        ext = exterior_layer({"N": front_garden})
        sash_window("N", *WINDOW, ext, curtains=GREY_CURTAIN)
        radiator(*WINDOW)
        back_opening("W", *SE_BED_DOOR, glimpses.holly_from_landing)
    wall_trim()
    balustrade()
    parliament_canvas()
    place_sprite("archie", 2.15, 4.6)
    ghost_near_walls(WALL, doors_S=[ARCH], doors_E=[MASTER_DOOR],
                     windows_S=() if not hc.FLIP else [WINDOW],
                     window_z=(52, 206), curtains=GREY_CURTAIN)
    photo_gallery()
    finish("Hide and Seek - Landing (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_landing_mock.png",))


if __name__ == "__main__":
    main()
