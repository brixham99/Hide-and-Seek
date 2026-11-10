#!/usr/bin/env python3
"""Static isometric mock-up of Holly's Room for 'Hide and Seek'.

The 12'11 x 11'5 (3.9 m E-W x 3.5 m N-S) south-east bedroom, east of
the landing and south of the bathroom. Pale pink walls, light oak
laminate, white skirting. East and south walls (the outside corner):
tall white sashes with cream curtains. North wall: chimney breast
(pink-and-white striped alcove, white fireplace, black cast-iron
insert) and an open doorway to the bathroom. West wall: open doorway
to the landing at the south end, a tall white wardrobe beside it.
A single white metal-framed bed runs along the west side, head by
the chimney alcove. Ceiling lampshade left out. No internal door leaf.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(6.9, 6.4)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_holly_mock.png"

WALL = (226, 188, 192)          # pale pink
OAK1, OAK2 = (214, 186, 148), (196, 166, 126)
WHITE_ = (244, 242, 236)
CREAM_C = (232, 222, 200)
OAK = (168, 118, 72)
PINE = (196, 150, 92)
LILAC = (176, 158, 198)
IRON = (232, 232, 228)          # white-painted metal
TEDDY = (176, 124, 78)

BATH_DOOR = (2.90, 4.30)        # north wall -> bathroom
LANDING_DOOR = (0.45, 1.70)     # west wall -> landing (south end)
WIN_E = (2.15, 3.85)            # east wall
WIN_S = (2.85, 4.65)            # south wall
BREAST = (0.55, 2.50, 0.72)     # chimney on north wall: x0, x1, depth


def east_garden(side, rnd):
    ext_lawn(side, -8, 14, 0.2, 14, rnd, base=(86, 142, 60))
    ext_lawn(side, -8, 14, 3.6, 9.5, rnd, base=(108, 148, 66))
    ext_hedge(side, -8, 14, 3.2, 3.9, h=96, rnd=rnd)
    ext_tree(side, 1.2, 5.0, trunk=92, canopy=136, r=1.15, col=(74, 120, 50), rnd=random.Random(21))
    ext_house_shadow(side, -8, 14, depth=0.9)


def south_garden(side, rnd):
    ext_lawn(side, -8, 16, 0.2, 14, rnd, base=(86, 142, 60))
    ext_hedge(side, -8, 16, 4.2, 4.8, h=88, rnd=rnd)
    ext_tree(side, 2.4, 2.8, trunk=118, canopy=168, r=1.15, col=(70, 118, 48), rnd=random.Random(22))
    ext_shrub(side, 4.8, 2.0, r=0.5, h=108, col=(76, 108, 60), rnd=random.Random(23))
    ext_house_shadow(side, -8, 16, depth=0.9)


def oak_floor():
    import paint
    paint.stamp(paint.timber(RW, RD, 13, OAK1, OAK2, along="x", plank=0.24), 0, 0, RW, RD, 0)


def striped_alcove(x0, x1):
    """Pink-and-white vertical stripes on a north-wall alcove, plus a picture rail."""
    y = RD - 0.03
    n = 7
    w = (x1 - x0) / n
    for i in range(n):
        col = WHITE_ if i % 2 == 0 else shade(WALL, 0.92)
        qy(y, x0 + i * w, x0 + (i + 1) * w, 14, WALL_H - 8, shade(col, KY))
    qy(y - 0.01, x0, x1, 168, 174, shade(WHITE_, KY))   # picture rail


def hearth():
    x0, x1, d = BREAST
    y = RD - d
    box(x0 - 0.12, y - 0.42, x1 + 0.12, y, 0, 4, (48, 46, 46), top=(58, 56, 56))


def chimney_hung():
    """Faint breast on the near north wall (SE view); the fire face stays unseen."""
    if hc.FLIP:
        return
    x0, x1, d = BREAST
    with hung_layer(alpha=115):
        box(x0, RD - d, x1, RD, 0, WALL_H, shade(WALL, 0.95), faces="x")
        box(x0 - 0.10, RD - d - 0.14, x1 + 0.10, RD - d, 96, 108, WHITE_, faces="xz")


def fireplace_front():
    """White surround and black insert, painted on the far north wall plane
    (the inset breast face loses the flipped depth test against that wall)."""
    if not hc.FLIP:
        return
    x0, x1, d = BREAST
    y = RD - 0.03
    qy(y, x0 - 0.04, x1 + 0.04, 0, WALL_H, shade(WALL, KY * 0.9))
    # white surround
    qy(y - 0.01, x0 + 0.18, x1 - 0.18, 8, 96, shade(WHITE_, KY))
    qy(y - 0.02, x0 + 0.42, x1 - 0.42, 16, 82, (32, 30, 30))     # cast-iron insert
    qy(y - 0.025, x0 + 0.54, x1 - 0.54, 28, 70, (22, 20, 20))
    # mantel shelf (a flat band on the wall plus a shallow box)
    qy(y - 0.01, x0 - 0.06, x1 + 0.06, 96, 110, shade(WHITE_, KY * 1.02))
    box(x0 - 0.10, RD - d - 0.10, x1 + 0.10, RD - d + 0.02, 96, 108, WHITE_, top=shade(WHITE_, 1.08))
    hy = RD - d - 0.08
    for xx, col in ((x0 + 0.35, TEDDY), (x0 + 0.85, (220, 92, 96)), (x1 - 0.90, TEDDY), (x1 - 0.40, (80, 140, 170))):
        cyl(xx, hy, 0.08, 108, 128, col, top=shade(col, 1.1))
        cyl(xx, hy, 0.06, 126, 140, col)
    # small framed picture above
    qy(y - 0.02, x0 + 0.55, x1 - 0.55, 130, 178, shade((120, 88, 48), KY))
    qy(y - 0.025, x0 + 0.62, x1 - 0.62, 136, 172, shade((196, 186, 160), KY))
    striped_alcove(x1 + 0.04, BATH_DOOR[0] - 0.04)
    striped_alcove(0.08, x0 - 0.04)


def white_bed():
    """Single white metal-framed bed along the west wall, head toward the north alcove."""
    x0, x1 = RW - 1.72, RW - 0.12
    y0, y1 = 2.55, 5.95
    # mattress and pale pink/white bedding
    box(x0 + 0.06, y0 + 0.08, x1 - 0.06, y1 - 0.08, 28, 46, (244, 236, 232), top=shade((244, 236, 232), 1.04))
    box(x0 + 0.08, y1 - 1.35, x1 - 0.08, y1 - 0.12, 46, 54, (236, 214, 216), top=shade((236, 214, 216), 1.05))
    # pillow
    box(x0 + 0.18, y1 - 0.55, x1 - 0.16, y1 - 0.14, 54, 66, (248, 246, 242), top=shade((248, 246, 242), 1.06))
    # white metal foot (south) and head (north) rails
    for y, h1 in ((y0, 78), (y1, 96)):
        box(x0, y - 0.04, x0 + 0.07, y + 0.04, 0, h1, IRON)
        box(x1 - 0.07, y - 0.04, x1, y + 0.04, 0, h1, IRON)
        box(x0, y - 0.05, x1, y + 0.05, h1 - 6, h1, IRON, top=shade(IRON, 1.08))
        for i in range(7):
            xx = x0 + 0.14 + i * (x1 - x0 - 0.28) / 6
            box(xx - 0.02, y - 0.03, xx + 0.02, y + 0.03, 12, h1 - 6, shade(IRON, 0.92), ol=False)


def oak_chest():
    """Tall oak chest of drawers on the east wall, left (north) of the window."""
    x0, x1, y0, y1 = 0.08, 0.72, 4.05, 5.55
    box(x0, y0, x1, y1, 0, 132, OAK, top=shade(OAK, 1.1))
    for z in (36, 68, 100):
        box(x0 + 0.06, y0 + 0.08, x1 - 0.06, y1 - 0.08, z, z + 5, shade(OAK, 1.14), ol=False)
        box(x0 + 0.28, (y0 + y1) / 2 - 0.04, x0 + 0.42, (y0 + y1) / 2 + 0.04, z + 5, z + 9, shade((196, 176, 120), 1.0), ol=False)


def pine_desk():
    """Pine desk with a monitor, in front of the east window, and a wooden chair."""
    x0, x1, y0, y1 = 0.12, 1.28, 2.30, 3.70
    box(x0, y0, x1, y1, 48, 56, PINE, top=shade(PINE, 1.1))
    for xx, yy in ((x0 + 0.08, y0 + 0.08), (x1 - 0.16, y0 + 0.08), (x0 + 0.08, y1 - 0.16), (x1 - 0.16, y1 - 0.16)):
        box(xx, yy, xx + 0.08, yy + 0.08, 0, 48, shade(PINE, 0.9))
    # monitor
    box(x0 + 0.28, y0 + 0.35, x0 + 0.42, y1 - 0.35, 56, 64, (40, 40, 44))
    box(x0 + 0.18, y0 + 0.30, x0 + 0.32, y1 - 0.30, 64, 112, (28, 30, 34), top=(36, 38, 42))
    # wooden chair in front (west) of the desk
    box(1.35, 2.70, 1.95, 3.30, 0, 42, PINE, top=shade(PINE, 1.08))
    box(1.82, 2.74, 1.98, 3.26, 42, 78, shade(PINE, 0.95))


def oak_wardrobe_se():
    """Tall oak double wardrobe with a drawer base, between the two windows."""
    x0, x1, y0, y1 = 0.10, 1.18, 0.08, 1.15
    box(x0, y0, x1, y1, 0, 36, OAK, top=shade(OAK, 1.08))            # drawer base
    box(x0 + 0.10, y0 + 0.12, x1 - 0.10, y1 - 0.12, 14, 22, shade(OAK, 1.12), ol=False)
    box(x0, y0, x1, y1, 36, 168, OAK, top=shade(OAK, 1.12))
    mid = (x0 + x1) / 2
    box(mid - 0.02, y0 + 0.04, mid + 0.02, y1 - 0.04, 40, 164, shade(OAK, 0.85), ol=False)
    for xx in (x0 + 0.22, x1 - 0.30):
        box(xx, y0 + 0.18, xx + 0.08, y0 + 0.28, 96, 104, shade((196, 176, 120), 1.0), ol=False)
    # small white wooden house on top
    box(x0 + 0.28, y0 + 0.22, x0 + 0.72, y1 - 0.22, 168, 188, WHITE_, top=shade(WHITE_, 1.06))
    box(x0 + 0.24, y0 + 0.18, x0 + 0.76, y1 - 0.18, 186, 198, (220, 96, 92))
    # fabric toy basket beside it
    box(1.24, 0.18, 1.72, 0.70, 0, 28, (196, 150, 120), top=shade((196, 150, 120), 1.1))
    qz(28.4, 1.30, 0.24, 1.66, 0.64, shade((196, 150, 120), 0.7))
    cyl(1.40, 0.40, 0.08, 22, 42, (220, 92, 96))
    cyl(1.56, 0.48, 0.07, 22, 38, (80, 140, 170))


def south_window_toys():
    """Doll's house, beanbag and low lilac metal cabinet by the south window."""
    # white doll's house
    box(2.90, 0.12, 3.60, 0.62, 0, 52, WHITE_, top=shade(WHITE_, 1.05))
    box(2.85, 0.10, 3.65, 0.64, 50, 68, (214, 96, 96))
    box(3.12, 0.22, 3.38, 0.40, 8, 36, shade((160, 200, 220), 1.0), ol=False)
    # beanbag cushion
    cyl(3.88, 0.78, 0.38, 0, 28, (186, 120, 160), top=shade((186, 120, 160), 1.12))
    cyl(3.88, 0.78, 0.30, 24, 42, shade((186, 120, 160), 1.08))
    # low lilac metal two-door cabinet (also reads as the lilac desk from the other view)
    box(4.15, 0.10, 5.55, 0.58, 0, 52, LILAC, top=shade(LILAC, 1.1))
    mid = 4.85
    box(mid - 0.02, 0.14, mid + 0.02, 0.54, 8, 48, shade(LILAC, 0.82), ol=False)
    for xx in (4.40, 5.15):
        box(xx, 0.28, xx + 0.08, 0.38, 24, 30, shade((196, 176, 120), 1.0), ol=False)
    # wastepaper bin near the cabinet
    cyl(5.80, 0.85, 0.14, 0, 26, (80, 82, 86), top=shade((80, 82, 86), 1.1))


def white_wardrobe():
    """Tall white cupboard on the west wall, just north of the landing door."""
    x0, x1 = RW - 0.58, RW - 0.08
    y0, y1 = 1.78, 2.48
    box(x0, y0, x1, y1, 0, 156, WHITE_, top=shade(WHITE_, 1.06))
    box(x0 + 0.08, y0 + 0.10, x1 - 0.08, y1 - 0.10, 12, 20, shade(WHITE_, 0.92), ol=False)
    box((x0 + x1) / 2 - 0.03, y0 + 0.16, (x0 + x1) / 2 + 0.03, y1 - 0.16, 70, 80, shade((196, 176, 120), 1.0), ol=False)


def dressing_gown():
    """A dressing gown hanging on the landing doorway (no door leaf)."""
    if not hc.FLIP:
        return
    a, b = LANDING_DOOR
    mid = (a + b) / 2
    qx(RW - 0.06, mid - 0.16, mid + 0.22, 48, 150, shade((186, 92, 118), KX))
    qx(RW - 0.07, mid - 0.10, mid + 0.16, 70, 148, shade((168, 78, 104), KX))
    qx(RW - 0.05, mid + 0.02, mid + 0.10, 40, 58, shade((148, 64, 88), KX))



def cream_drapes(side, u0, u1, z1=198):
    """Floor-length cream curtains on a pole, drawn after the trim so they read."""
    k = KY if side == "N" else KX
    W = lambda u, z, n=0.0: wall_pt(side, u, z, n)

    def quad(a, b, za, zb, col, n=0.07):
        poly([W(a, za, n), W(b, za, n), W(b, zb, n), W(a, zb, n)], col)

    a, b = W(u0 - 0.68, z1 + 20, 0.09), W(u1 + 0.68, z1 + 20, 0.09)
    pygame.draw.line(screen, (164, 146, 118), a, b, max(2, int(3 * S)))
    for ca, cb in ((u0 - 0.64, u0 + 0.08), (u1 - 0.08, u1 + 0.64)):
        for f in range(6):
            fa = ca + (cb - ca) * f / 6
            fb = ca + (cb - ca) * (f + 1) / 6
            tone = shade(CREAM_C, (0.72 + 0.26 * (f % 2)) * k / KY)
            quad(fa + 0.005, fb - 0.005, 8, z1 + 16, tone, n=0.08)


def wall_pictures():
    """A few small pictures on the far walls."""
    if not hc.FLIP:
        qx(0.04, 5.70, 6.10, 128, 158, shade((120, 88, 48), KX))
        qx(0.045, 5.74, 6.06, 132, 154, shade((186, 170, 140), KX))
        qy(0.04, 5.30, 5.72, 122, 154, shade((120, 88, 48), KY))
        qy(0.045, 5.34, 5.68, 126, 150, shade((160, 176, 150), KY))
    else:
        qx(RW - 0.04, 3.15, 3.55, 124, 156, shade((120, 88, 48), KX))
        qx(RW - 0.045, 3.19, 3.51, 128, 152, shade((190, 176, 150), KX))


def main():
    background()
    oak_floor()
    hearth()
    wall_shell(WALL)
    import glimpses
    ext = exterior_layer({"W": east_garden, "N": south_garden}, haze=(170, 188, 150))
    sash_window("W", *WIN_E, ext, z0=70, z1=198, curtains=CREAM_C)
    sash_window("N", *WIN_S, ext, z0=70, z1=198, curtains=CREAM_C)
    wall_trim()
    white_bed()
    oak_chest()
    pine_desk()
    oak_wardrobe_se()
    south_window_toys()
    white_wardrobe()
    chimney_hung()
    wall_pictures()
    dressing_gown()
    place_sprite("archie", 3.40, 3.15)
    cream_drapes("W", *WIN_E)
    cream_drapes("N", *WIN_S)
    ghost_near_walls(WALL,
                     doors_S=[BATH_DOOR],
                     doors_E=[LANDING_DOOR],
                     curtains=CREAM_C)
    if hc.FLIP:
        # north wall is far here; paint the breast after the solid ghost fill
        x0, x1, d = BREAST
        box(x0, RD - d, x1, RD, 0, WALL_H, shade(WALL, 0.96), faces="x")
        fireplace_front()
    finish("Hide and Seek - Holly's Room (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_holly_mock.png",))


if __name__ == "__main__":
    main()
