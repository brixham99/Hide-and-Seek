#!/usr/bin/env python3
"""Static isometric mock-up of the Upstairs Office for 'Hide and Seek'.

The 11'6 x 11'4 (3.5 m E-W x 3.5 m N-S) room north of the upstairs
corridor lobby, between Archie's Room (west) and the house's east wall
(the bathroom sits south-east of it). Pale blue-grey walls, white
skirting, light oak laminate. South wall: open doorway to the corridor
at the west end (the lobby's NE door) and an oak chest with a printer.
North wall: white casement with pink floral curtains on a brass pole
and a white radiator under it. West: black desk, monitor and office
chair by the window. East: cream three-seater sofa, purple check throw,
five framed prints and a side table with a brass lamp. Birdcage ceiling
light left out. No internal door leaf.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(6.2, 6.4)
from house_common import *  # noqa: E402,F401,F403
import iso_paint  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_upoffice_mock.png"

WALL = (176, 188, 196)          # pale blue-grey
OAK1, OAK2 = (214, 186, 148), (196, 166, 126)
WHITE_ = (244, 242, 236)
CREAM = (236, 232, 224)
PINK_C = (232, 186, 196)
OAK = (168, 118, 72)
BLACK = (36, 38, 42)
PURPLE = (118, 88, 128)

DOOR = (4.88, 6.20)             # south wall, west end -> corridor
WINDOW = (2.45, 4.15)           # north wall, opposite the door


def north_garden(side, rnd):
    """Trees close to the north window, a step below the floor."""
    ext_lawn(side, -8, RW + 8, 0.2, 12, rnd, base=(86, 142, 60))
    ext_lawn(side, -8, RW + 8, 3.4, 8.8, rnd, base=(118, 148, 70))
    ext_tree(side, 1.4, 2.6, trunk=90, canopy=136, r=1.15, col=(92, 128, 52), rnd=random.Random(17))
    ext_tree(side, 3.3, 3.4, trunk=108, canopy=156, r=1.35, col=(74, 118, 48), rnd=random.Random(18))
    ext_tree(side, 5.2, 2.4, trunk=84, canopy=124, r=1.0, col=(88, 130, 54), rnd=random.Random(19))
    ext_hedge(side, -4, RW + 4, 4.6, 5.2, h=80, rnd=rnd)
    ext_house_shadow(side, -8, RW + 8, depth=0.9)


def oak_floor():
    import paint
    paint.stamp(paint.timber(RW, RD, 12, OAK1, OAK2, along="x", plank=0.24), 0, 0, RW, RD, 0)


def cream_sofa():
    """Three-seater along the east wall, purple check throw toward the window end."""
    x0, x1, y0, y1 = 0.08, 0.80, 1.55, 5.05
    iso_paint.paint_box(x0 + 0.20, y0 + 0.16, x1, y1 - 0.16, 0, 46, "sofa_cream", front="W", col=CREAM)
    iso_paint.paint_box(x0, y0, x0 + 0.26, y1, 0, 80, "sofa_cream", front="W", col=CREAM)
    iso_paint.paint_box(x0, y0, x1, y0 + 0.20, 0, 64, "sofa_cream", front="S", col=CREAM)
    iso_paint.paint_box(x0, y1 - 0.20, x1, y1, 0, 64, "sofa_cream", front="N", col=CREAM)
    for ya, yb in ((y0 + 0.24, 2.65), (2.70, 3.80), (3.85, y1 - 0.24)):
        iso_paint.paint_box(x0 + 0.24, ya, x1 - 0.04, yb, 46, 54, "sofa_cream", front="W", col=shade(CREAM, 1.06))
    iso_paint.paint_box(x0 + 0.28, 3.95, x1 - 0.06, y1 - 0.28, 54, 58, "sofa_check", front="W", col=PURPLE)


def sofa_table():
    """Small wooden side table and brass lamp at the sofa's window end."""
    x0, x1, y0, y1 = 0.12, 0.58, 5.12, 5.62
    iso_paint.paint_box(x0, y0, x1, y1, 42, 50, "up_oak", front="W", col=OAK)
    for xx, yy in ((x0 + 0.04, y0 + 0.04), (x1 - 0.12, y0 + 0.04),
                   (x0 + 0.04, y1 - 0.12), (x1 - 0.12, y1 - 0.12)):
        box(xx, yy, xx + 0.08, yy + 0.08, 0, 42, shade(OAK, 0.9))
    # brass lamp
    cyl((x0 + x1) / 2, (y0 + y1) / 2, 0.04, 50, 78, (196, 152, 72))
    cyl((x0 + x1) / 2, (y0 + y1) / 2, 0.16, 76, 92, (232, 198, 120), top=shade((232, 198, 120), 1.1))


def print_gallery():
    """Five framed prints above the sofa on the east wall (far in SE)."""
    if hc.FLIP:
        return
    frames = [
        (1.70, 2.12, 128, 162, (120, 88, 48), (196, 186, 150)),
        (2.22, 2.62, 132, 168, (236, 232, 226), (220, 96, 140)),
        (2.78, 3.28, 124, 176, (32, 30, 28), (210, 196, 160)),
        (3.40, 3.92, 126, 172, (120, 88, 48), (186, 92, 86)),
        (4.10, 4.62, 130, 170, (236, 232, 226), (150, 176, 150)),
    ]
    for y0, y1, z0, z1, fr, inner in frames:
        qx(0.035, y0, y1, z0, z1, shade(fr, KX))
        qx(0.04, y0 + 0.04, y1 - 0.04, z0 + 4, z1 - 4, shade(inner, KX))


def oak_chest():
    """Oak three-drawer chest on the south wall, east of the door, printer on top."""
    x0, x1, y0, y1 = 3.22, 4.72, 0.08, 0.68
    iso_paint.paint_box(x0, y0, x1, y1, 0, 78, "up_oak_chest", front="N", col=OAK)
    for z in (18, 38, 58):
        box(x0 + 0.10, y0 + 0.10, x1 - 0.10, y1 - 0.10, z, z + 5, shade(OAK, 1.14), ol=False)
        box((x0 + x1) / 2 - 0.10, (y0 + y1) / 2 - 0.03, (x0 + x1) / 2 + 0.10, (y0 + y1) / 2 + 0.03,
            z + 5, z + 8, shade((196, 176, 120), 1.0), ol=False)
    # white printer
    box(x0 + 0.22, y0 + 0.14, x0 + 0.95, y1 - 0.14, 78, 96, WHITE_, top=shade(WHITE_, 1.04))
    box(x0 + 0.30, y0 + 0.20, x0 + 0.72, y1 - 0.20, 96, 100, (40, 40, 44), ol=False)
    # framed print above, on the south wall (far in SE)
    if not hc.FLIP:
        qy(0.035, x0 + 0.35, x1 - 0.35, 128, 172, shade((120, 88, 48), KY))
        qy(0.04, x0 + 0.42, x1 - 0.42, 134, 166, shade((214, 206, 186), KY))


def black_desk():
    """Black desk against the west wall by the window, with a monitor and chair."""
    x0, x1, y0, y1 = RW - 1.32, RW - 0.10, 4.00, 5.80
    iso_paint.paint_box(x0, y0, x1, y1, 48, 56, "up_black", front="E", col=BLACK)
    for xx, yy in ((x0 + 0.08, y0 + 0.08), (x1 - 0.16, y0 + 0.08),
                   (x0 + 0.08, y1 - 0.16), (x1 - 0.16, y1 - 0.16)):
        box(xx, yy, xx + 0.08, yy + 0.08, 0, 48, WHITE_)
    # monitor
    box(x0 + 0.18, y0 + 0.45, x0 + 0.32, y1 - 0.45, 56, 64, (28, 28, 32))
    box(x0 + 0.10, y0 + 0.38, x0 + 0.24, y1 - 0.38, 64, 112, (24, 26, 30), top=(36, 38, 42))
    box(x0 + 0.24, y0 + 0.70, x0 + 0.55, y1 - 0.70, 56, 60, (48, 48, 52))   # keyboard
    # wire bin and cardboard box under the desk
    cyl(x0 + 0.28, y0 + 0.35, 0.14, 0, 24, (140, 144, 148), top=shade((140, 144, 148), 1.1))
    box(x0 + 0.48, y0 + 0.22, x0 + 0.88, y0 + 0.58, 0, 22, (186, 142, 86), top=shade((186, 142, 86), 1.08))
    # black office chair in front (east) of the desk
    iso_paint.paint_box(x0 - 0.72, y0 + 0.45, x0 - 0.18, y1 - 0.45, 0, 44, "up_black", front="E", col=BLACK)
    box(x0 - 0.28, y0 + 0.50, x0 - 0.12, y1 - 0.50, 44, 86, shade(BLACK, 0.9))


def radiator():
    """White radiator under the north window."""
    a, b = WINDOW
    y0, y1 = RD - 0.16, RD - 0.02
    iso_paint.paint_box(a + 0.08, y0, b - 0.08, y1, 0, 40, "hall_radiator", front="S", col=WHITE_)
    n = 7
    for i in range(n):
        xx = a + 0.16 + i * (b - a - 0.32) / (n - 1)
        box(xx - 0.03, y0 + 0.02, xx + 0.03, y1 - 0.02, 4, 38, shade(WHITE_, 0.92), ol=False)


def pink_drapes(z1=196):
    """Pink floral curtains on a brass pole, on the far north window."""
    if not hc.FLIP:
        return
    u0, u1 = WINDOW
    W = lambda u, z, n=0.0: wall_pt("S", u, z, n)

    def quad(a, b, za, zb, col, n=0.07):
        poly([W(a, za, n), W(b, za, n), W(b, zb, n), W(a, zb, n)], col)

    a, b = W(u0 - 0.62, z1 + 18, 0.09), W(u1 + 0.62, z1 + 18, 0.09)
    pygame.draw.line(screen, (184, 148, 72), a, b, max(2, int(3 * S)))
    rnd = random.Random(21)
    for ca, cb in ((u0 - 0.58, u0 + 0.06), (u1 - 0.06, u1 + 0.58)):
        for f in range(6):
            fa = ca + (cb - ca) * f / 6
            fb = ca + (cb - ca) * (f + 1) / 6
            tone = shade(PINK_C, (0.78 + 0.22 * (f % 2)))
            quad(fa + 0.004, fb - 0.004, 10, z1 + 14, tone, n=0.08)
            for _ in range(3):
                uu = fa + (fb - fa) * rnd.random()
                zz = 24 + rnd.random() * (z1 - 40)
                quad(uu, uu + 0.04, zz, zz + 8, shade((214, 92, 118), 0.95), n=0.085)


def main():
    background()
    oak_floor()
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        back_opening("N", *DOOR, glimpses.corridor_from_upoffice)
        print_gallery()
    wall_trim()
    cream_sofa()
    sofa_table()
    oak_chest()
    black_desk()
    if not hc.FLIP:
        with hung_layer(alpha=110):
            radiator()
    place_sprite("archie", 3.05, 3.10)
    ghost_near_walls(WALL,
                     doors_S=[],
                     windows_S=() if hc.FLIP else [WINDOW],
                     window_z=(70, 196), window_cols=2, curtains=PINK_C)
    if hc.FLIP:
        ext = exterior_layer({"S": north_garden}, haze=(170, 188, 150))
        sash_on_far("S", *WINDOW, ext, z0=70, z1=196, curtains=PINK_C, cols=2)
        pink_drapes()
        radiator()
    finish("Hide and Seek - Upstairs Office (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_upoffice_mock.png",))


if __name__ == "__main__":
    main()
