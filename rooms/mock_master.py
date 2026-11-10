#!/usr/bin/env python3
"""Static isometric mock-up of the Master Bedroom for 'Hide and Seek'.

The 14'1 x 13' (4.3 m N-S x 4.0 m E-W) bedroom west of the landing,
above the Drawing Room. Pale grey walls, white skirting, light oak
laminate. East wall: open doorway to the landing at the south end.
South wall (front): sash with pale blue floral curtains and rooftops
beyond, a pine chest of drawers with a television. West wall: sash
with the same curtains, a pine desk and white chair, radiator under
each window. North wall: chimney breast with a white fireplace and
black insert, an open doorway to the Dressing Room, a white bookcase
with a globe; a wooden double bed with a cane headboard and pink
bedding runs along this wall, head to the west. Ceiling pendant
left out. No internal door leaf; no registration-plate lettering.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(7.3, 7.8)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_master_mock.png"

WALL = (176, 178, 176)          # pale grey
OAK1, OAK2 = (214, 186, 148), (196, 166, 126)
WHITE_ = (244, 242, 236)
FLORAL = (176, 192, 186)        # pale blue-green floral curtains
PINE = (198, 158, 98)
PINK = (224, 176, 186)
CANE = (186, 150, 96)

LANDING_DOOR = (0.50, 1.75)     # east wall, south end -> landing
DRESSING_DOOR = (4.40, 5.75)    # north wall, east of the chimney -> dressing room
WIN_S = (1.45, 3.20)            # south wall (front)
WIN_W = (2.55, 4.30)            # west wall
BREAST = (5.95, 7.18, 0.72)     # chimney on the north wall: x0, x1, depth


def front_garden(side, rnd):
    """Front of the house, a step below: lawn, hedge, a neighbour's roofs."""
    ext_lawn(side, -8, RW + 8, 0.2, 12, rnd, base=(86, 142, 60))
    ext_hedge(side, -8, RW + 8, 4.4, 5.1, h=86, rnd=rnd)
    ext_tree(side, 2.2, 3.2, trunk=120, canopy=158, r=1.25, col=(96, 140, 64), rnd=random.Random(31))
    ext_house_shadow(side, -8, RW + 8, depth=0.9)


def side_garden(side, rnd):
    """West side: gardens and rooftops, as in the west window."""
    ext_lawn(side, -8, RD + 8, 0.2, 12, rnd, base=(90, 138, 62))
    ext_hedge(side, -8, RD + 8, 3.8, 4.5, h=92, rnd=rnd)
    ext_tree(side, 1.6, 2.8, trunk=100, canopy=140, r=1.1, col=(78, 122, 50), rnd=random.Random(32))
    ext_tree(side, 4.4, 3.6, trunk=88, canopy=128, r=1.0, col=(88, 130, 54), rnd=random.Random(33))
    ext_house_shadow(side, -8, RD + 8, depth=0.9)


def oak_floor():
    import paint
    paint.stamp(paint.timber(RW, RD, 14, OAK1, OAK2, along="x", plank=0.24), 0, 0, RW, RD, 0)


def pale_rug():
    box(2.05, 2.15, 5.35, 5.15, 0.4, 1.2, (214, 216, 218), top=shade((220, 222, 224), 1.04))


def hearth():
    x0, x1, d = BREAST
    y = RD - d
    box(x0 - 0.12, y - 0.40, x1 + 0.10, y, 0, 4, (48, 46, 46), top=(58, 56, 56))


def chimney_hung():
    if hc.FLIP:
        return
    x0, x1, d = BREAST
    with hung_layer(alpha=115):
        box(x0, RD - d, x1, RD, 0, WALL_H, shade(WALL, 0.95), faces="x")
        box(x0 - 0.10, RD - d - 0.14, x1 + 0.08, RD - d, 92, 104, WHITE_, faces="xz")


def fireplace_front():
    """White surround and black insert on the far north wall (V-view)."""
    if not hc.FLIP:
        return
    x0, x1, d = BREAST
    y = RD - 0.03
    qy(y, x0 - 0.04, x1 + 0.04, 0, WALL_H, shade(WALL, KY * 0.92))
    qy(y - 0.01, x0 + 0.18, x1 - 0.18, 8, 96, shade(WHITE_, KY))
    qy(y - 0.02, x0 + 0.42, x1 - 0.42, 16, 82, (32, 30, 30))
    qy(y - 0.025, x0 + 0.54, x1 - 0.54, 28, 70, (22, 20, 20))
    qy(y - 0.01, x0 - 0.08, x1 + 0.08, 94, 110, shade(WHITE_, KY * 1.02))
    box(x0 - 0.10, RD - d - 0.10, x1 + 0.10, RD - d + 0.02, 94, 108, WHITE_, top=shade(WHITE_, 1.08))
    # round black-framed mirror above the mantel
    mid = (x0 + x1) / 2
    qy(y - 0.02, mid - 0.30, mid + 0.30, 126, 178, shade((36, 36, 38), KY))
    qy(y - 0.025, mid - 0.22, mid + 0.22, 134, 170, shade((198, 202, 206), KY))
    # a tiny framed photo on the mantel
    qy(y - 0.02, x0 + 0.28, x0 + 0.50, 112, 130, shade((120, 88, 48), KY))
    qy(y - 0.025, x0 + 0.32, x0 + 0.46, 116, 126, shade((186, 176, 150), KY))


def wooden_bed():
    """Double bed along the north wall, head to the west by the fireplace."""
    x0, x1 = 3.05, 6.52
    y0, y1 = 4.48, 6.42
    # frame
    box(x0, y0, x1, y1, 0, 28, PINE, top=shade(PINE, 1.05))
    # mattress and pink bedding
    box(x0 + 0.10, y0 + 0.08, x1 - 0.10, y1 - 0.10, 28, 48, PINK, top=shade(PINK, 1.06))
    box(x0 + 0.12, y0 + 0.10, x1 - 0.12, y1 - 0.12, 48, 54, shade(PINK, 1.04), top=shade(PINK, 1.08))
    # pillows at the west (head)
    box(x1 - 0.85, y0 + 0.18, x1 - 0.18, (y0 + y1) / 2 - 0.06, 54, 68, (244, 236, 232), top=shade((244, 236, 232), 1.05))
    box(x1 - 0.85, (y0 + y1) / 2 + 0.06, x1 - 0.18, y1 - 0.18, 54, 68, (244, 236, 232), top=shade((244, 236, 232), 1.05))
    # floral cushion
    box(x1 - 1.15, y0 + 0.55, x1 - 0.55, y1 - 0.55, 68, 78, (186, 204, 196), top=shade((186, 204, 196), 1.08))
    # cane headboard at the west end
    box(x1 - 0.10, y0 - 0.04, x1 + 0.08, y1 + 0.04, 28, 110, CANE, top=shade(CANE, 1.08))
    for i in range(6):
        yy = y0 + 0.10 + i * (y1 - y0 - 0.20) / 5
        box(x1 - 0.08, yy - 0.02, x1 + 0.06, yy + 0.02, 34, 104, shade(CANE, 0.85), ol=False)
    for j in range(5):
        zz = 40 + j * 12
        box(x1 - 0.08, y0 + 0.08, x1 + 0.06, y1 - 0.08, zz, zz + 3, shade(CANE, 0.9), ol=False)
    # foot rail (east)
    box(x0 - 0.04, y0, x0 + 0.08, y1, 20, 52, PINE, top=shade(PINE, 1.06))
    # nightstand at the head, south of the bed a little
    box(x1 - 0.08, y0 - 0.52, x1 + 0.42, y0 - 0.08, 0, 48, PINE, top=shade(PINE, 1.1))
    cyl(x1 + 0.16, y0 - 0.30, 0.05, 48, 72, WHITE_)
    cyl(x1 + 0.16, y0 - 0.30, 0.14, 70, 88, (232, 228, 220), top=shade((232, 228, 220), 1.08))


def pine_chest():
    """Pine chest of drawers on the south wall, with a television on top."""
    if hc.FLIP:
        return  # south wall is near in the opposite view
    x0, x1, y0, y1 = 4.20, 5.90, 0.10, 0.72
    box(x0, y0, x1, y1, 0, 86, PINE, top=shade(PINE, 1.1))
    for z in (22, 44, 66):
        box(x0 + 0.10, y0 + 0.10, x1 - 0.10, y1 - 0.10, z, z + 5, shade(PINE, 1.14), ol=False)
        box((x0 + x1) / 2 - 0.08, (y0 + y1) / 2 - 0.03, (x0 + x1) / 2 + 0.08, (y0 + y1) / 2 + 0.03,
            z + 5, z + 8, shade((196, 176, 120), 1.0), ol=False)
    # TV facing into the room
    box(x0 + 0.35, y0 + 0.18, x0 + 0.55, y1 - 0.18, 86, 94, (28, 28, 32))
    box(x0 + 0.22, y0 + 0.16, x0 + 0.42, y1 - 0.16, 94, 142, (24, 26, 30), top=(36, 38, 42))
    # small pink bag
    box(x1 - 0.48, y0 + 0.18, x1 - 0.14, y1 - 0.18, 86, 102, (214, 120, 140), top=shade((214, 120, 140), 1.08))


def pine_desk():
    """Pine desk and white chair in front of the west window."""
    x0, x1, y0, y1 = RW - 1.28, RW - 0.10, 2.55, 4.15
    box(x0, y0, x1, y1, 48, 56, PINE, top=shade(PINE, 1.1))
    for xx, yy in ((x0 + 0.08, y0 + 0.08), (x1 - 0.16, y0 + 0.08),
                   (x0 + 0.08, y1 - 0.16), (x1 - 0.16, y1 - 0.16)):
        box(xx, yy, xx + 0.08, yy + 0.08, 0, 48, shade(PINE, 0.9))
    box(x0 + 0.22, y0 + 0.45, x0 + 0.55, y1 - 0.45, 56, 62, (40, 42, 46))   # laptop
    # white wooden chair
    box(x0 - 0.70, y0 + 0.45, x0 - 0.16, y1 - 0.45, 0, 42, WHITE_, top=shade(WHITE_, 1.04))
    box(x0 - 0.28, y0 + 0.50, x0 - 0.12, y1 - 0.50, 42, 78, shade(WHITE_, 0.92))


def white_bookcase():
    """White bookcase on the north wall, east of the dressing door, globe on top."""
    x0, x1, y0, y1 = 3.15, 4.25, RD - 0.55, RD - 0.08
    box(x0, y0, x1, y1, 0, 118, WHITE_, top=shade(WHITE_, 1.05))
    rnd = random.Random(8)
    for z in (28, 56, 84):
        box(x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, z, z + 4, shade(WHITE_, 0.9), ol=False)
        u = x0 + 0.10
        while u < x1 - 0.14:
            bw = rnd.uniform(0.06, 0.11)
            col = rnd.choice([(160, 50, 50), (40, 70, 130), (200, 180, 70), (50, 110, 70), (230, 220, 200), (90, 60, 40)])
            box(u, y0 + 0.10, u + bw, y1 - 0.10, z + 4, z + rnd.uniform(16, 24), col, ol=False)
            u += bw + 0.015
    cyl((x0 + x1) / 2, (y0 + y1) / 2, 0.14, 118, 142, (70, 120, 170), top=shade((90, 140, 120), 1.1))


def radiators():
    """White radiators under the south and west windows."""
    # south
    a, b = WIN_S
    box(a + 0.10, 0.04, b - 0.10, 0.18, 0, 38, WHITE_, top=shade(WHITE_, 1.04))
    # west — drawn solid only when that wall faces the camera
    if hc.FLIP:
        a, b = WIN_W
        box(RW - 0.16, a + 0.10, RW - 0.03, b - 0.10, 0, 38, WHITE_, top=shade(WHITE_, 1.04))


def wall_picture():
    """Landscape print above the bed, on the north wall (far in V)."""
    if not hc.FLIP:
        return
    qy(RD - 0.04, 3.55, 4.35, 132, 172, shade((120, 136, 148), KY))
    qy(RD - 0.045, 3.62, 4.28, 138, 166, shade((186, 196, 176), KY))


def floral_drapes_south():
    if hc.FLIP:
        return
    u0, u1 = WIN_S
    W = lambda u, z, n=0.0: wall_pt("N", u, z, n)

    def quad(a, b, za, zb, col, n=0.07):
        poly([W(a, za, n), W(b, za, n), W(b, zb, n), W(a, zb, n)], col)

    z1 = 198
    aa, bb = W(u0 - 0.58, z1 + 16, 0.08), W(u1 + 0.58, z1 + 16, 0.08)
    pygame.draw.line(screen, (200, 200, 196), aa, bb, max(2, int(3 * S)))
    rnd = random.Random(27)
    for ca, cb in ((u0 - 0.52, u0 + 0.06), (u1 - 0.06, u1 + 0.52)):
        for f in range(6):
            fa = ca + (cb - ca) * f / 6
            fb = ca + (cb - ca) * (f + 1) / 6
            quad(fa, fb, 10, z1 + 12, shade(FLORAL, 0.78 + 0.2 * (f % 2)), n=0.08)
            for _ in range(2):
                uu = fa + (fb - fa) * rnd.random()
                zz = 28 + rnd.random() * 140
                quad(uu, uu + 0.035, zz, zz + 7, shade((220, 228, 220), 0.95), n=0.085)


def main():
    background()
    oak_floor()
    pale_rug()
    hearth()
    wall_shell(WALL)
    import glimpses
    ext = exterior_layer({"N": front_garden, "E": side_garden}, haze=(170, 188, 150))
    sash_window("N", *WIN_S, ext, z0=70, z1=198, curtains=FLORAL)
    if not hc.FLIP:
        floral_drapes_south()
        back_opening("W", *LANDING_DOOR, glimpses.landing_from_master)
    wall_trim()
    wooden_bed()
    pine_chest()
    pine_desk()
    white_bookcase()
    radiators()
    chimney_hung()
    wall_picture()
    place_sprite("archie", 3.45, 3.15)
    ghost_near_walls(WALL,
                     doors_S=[DRESSING_DOOR],
                     windows_E=() if hc.FLIP else [WIN_W],
                     window_z=(70, 198), window_cols=2, curtains=FLORAL)
    if hc.FLIP:
        ext_w = exterior_layer({"E": side_garden}, haze=(170, 188, 150))
        sash_on_far("E", *WIN_W, ext_w, z0=70, z1=198, curtains=FLORAL, cols=2)
        x0, x1, d = BREAST
        box(x0, RD - d, x1, RD, 0, WALL_H, shade(WALL, 0.96), faces="x")
        fireplace_front()
        radiators()
    finish("Hide and Seek - Master Bedroom (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_master_mock.png",))


if __name__ == "__main__":
    main()
