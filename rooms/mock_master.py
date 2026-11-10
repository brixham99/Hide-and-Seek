#!/usr/bin/env python3
"""Static isometric mock-up of the Master Bedroom for 'Hide and Seek'.

The 14'1 x 13' (4.3 m N-S x 4.0 m E-W) bedroom west of the landing,
above the Drawing Room. Pale grey walls, white skirting, light oak
laminate. East wall: landing door at the south end; a chimney breast
with a small fireplace north of that door (the wall juts out);
through the landing door the Landing's oak floor and south sash are
visible. South wall: a wide low white bookcase with a globe (between
the landing-door corner and the sash), then a more centred sash with
floral curtains and a radiator, then a pine chest with a television
in the south-west corner. West wall: sash with the same curtains, a
pine desk and white chair, radiator under the window. North wall: an
open doorway to the Dressing Room toward the west (wall on both
sides, the dressing room sitting fully behind it), a king-size bed
with a cane headboard against this wall projecting south onto a large
pale blue-grey rug, and a bedside table with a lamp on each side of
the head (the west one next to the dressing doorway).
Ceiling pendant left out. No internal door leaf; no registration-plate
lettering.
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
SHEET = (248, 246, 242)
CUSHION = (176, 186, 196)     # blue-grey
CANE = (186, 150, 96)

LANDING_DOOR = (0.50, 1.75)     # east wall, south end -> landing
DRESSING_DOOR = (5.10, 6.45)    # north wall, west of centre -> dressing room
WIN_S = (2.55, 4.35)            # south wall, more centred (bookcase takes the east end)
WIN_W = (2.55, 4.30)            # west wall
BREAST = (2.15, 3.85, 0.62)     # chimney on the east wall, north of the landing door: y0, y1, depth


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
    """Large pale blue-grey rug under the bed, spreading into the room."""
    box(1.20, 3.20, 5.20, 7.45, 0.4, 1.2, (196, 202, 208), top=shade((206, 210, 214), 1.04))


def hearth():
    """Slate hearth in front of the east-wall chimney breast."""
    y0, y1, d = BREAST
    box(d, y0 - 0.10, d + 0.40, y1 + 0.10, 0, 4, (48, 46, 46), top=(58, 56, 56))


def east_fireplace():
    """Small white fireplace on the east wall, north of the landing door.
    That wall faces the camera in the SE view."""
    if hc.FLIP:
        return
    y0, y1, d = BREAST
    box(0, y0, d, y1, 0, WALL_H, shade(WALL, 0.96), faces="y")
    # white surround and black insert on the breast's west face
    qx(d + 0.01, y0 + 0.18, y1 - 0.18, 8, 96, shade(WHITE_, KX))
    qx(d + 0.02, y0 + 0.40, y1 - 0.40, 16, 82, (32, 30, 30))
    qx(d + 0.025, y0 + 0.50, y1 - 0.50, 28, 70, (22, 20, 20))
    box(d - 0.02, y0 - 0.08, d + 0.14, y1 + 0.08, 94, 108, WHITE_, top=shade(WHITE_, 1.08))
    mid = (y0 + y1) / 2
    qx(d + 0.02, mid - 0.28, mid + 0.28, 126, 176, shade((36, 36, 38), KX))
    qx(d + 0.025, mid - 0.20, mid + 0.20, 134, 168, shade((198, 202, 206), KX))
    qx(d + 0.02, y0 + 0.22, y0 + 0.42, 112, 128, shade((120, 88, 48), KX))
    qx(d + 0.025, y0 + 0.26, y0 + 0.38, 116, 124, shade((186, 176, 150), KX))


def wooden_bed():
    """King-size bed: cane headboard against the north wall, just east of
    the dressing doorway, projecting south into the middle of the room."""
    x0, x1 = 1.70, 4.44          # east ... west (width)
    y0, y1 = 4.18, 7.62          # foot (south) ... head (north)
    # frame
    box(x0, y0, x1, y1, 0, 28, PINE, top=shade(PINE, 1.05))
    # white mattress and duvet
    box(x0 + 0.08, y0 + 0.10, x1 - 0.08, y1 - 0.10, 28, 48, SHEET, top=shade(SHEET, 1.04))
    box(x0 + 0.10, y0 + 0.12, x1 - 0.10, y1 - 0.12, 48, 54, shade(SHEET, 1.02), top=shade(SHEET, 1.06))
    # pillows at the north (head)
    mid = (x0 + x1) / 2
    box(x0 + 0.18, y1 - 0.88, mid - 0.06, y1 - 0.18, 54, 70, SHEET, top=shade(SHEET, 1.05))
    box(mid + 0.06, y1 - 0.88, x1 - 0.18, y1 - 0.18, 54, 70, SHEET, top=shade(SHEET, 1.05))
    # blue-grey cushion
    box(mid - 0.38, y1 - 1.12, mid + 0.38, y1 - 0.48, 68, 80, CUSHION, top=shade(CUSHION, 1.08))
    # cane headboard at the north
    box(x0, y1 - 0.12, x1, y1 + 0.06, 28, 112, CANE, top=shade(CANE, 1.08))
    for i in range(7):
        xx = x0 + 0.10 + i * (x1 - x0 - 0.20) / 6
        box(xx - 0.02, y1 - 0.10, xx + 0.02, y1 + 0.04, 34, 106, shade(CANE, 0.85), ol=False)
    for j in range(5):
        zz = 40 + j * 12
        box(x0 + 0.08, y1 - 0.10, x1 - 0.08, y1 + 0.04, zz, zz + 3, shade(CANE, 0.9), ol=False)
    # foot rail (south)
    box(x0, y0 - 0.04, x1, y0 + 0.08, 20, 52, PINE, top=shade(PINE, 1.06))


# Just outside the bed's width (1.70–4.44), clear of the headboard too.
# West table stays next to the dressing doorway at (5.10, 6.45).
EAST_NS = (1.08, 7.18, 1.54, 7.70)
WEST_NS = (4.58, 7.18, 5.04, 7.70)


def bedside_table(x0, y0, x1, y1):
    """A pine bedside table and lamp against the north wall."""
    box(x0, y0, x1, y1, 0, 48, PINE, top=shade(PINE, 1.1))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cyl(cx, cy, 0.05, 48, 74, WHITE_)
    cyl(cx, cy, 0.14, 72, 90, (232, 228, 220), top=shade((232, 228, 220), 1.08))


def bedside_east():
    bedside_table(*EAST_NS)


def bedside_west():
    bedside_table(*WEST_NS)


def pine_chest():
    """Pine chest of drawers in the south-west corner, between the two
    sash windows, with a television standing on top."""
    x0, x1, y0, y1 = 5.40, 7.15, 0.10, 0.78
    box(x0, y0, x1, y1, 0, 86, PINE, top=shade(PINE, 1.1))
    for z in (22, 44, 66):
        box(x0 + 0.10, y0 + 0.10, x1 - 0.10, y1 - 0.10, z, z + 5, shade(PINE, 1.14), ol=False)
        box((x0 + x1) / 2 - 0.08, (y0 + y1) / 2 - 0.03, (x0 + x1) / 2 + 0.08, (y0 + y1) / 2 + 0.03,
            z + 5, z + 8, shade((196, 176, 120), 1.0), ol=False)
    # TV standing on the chest, screen facing north into the room
    box(x0 + 0.28, y1 - 0.24, x1 - 0.28, y1 - 0.08, 86, 94, (28, 28, 32))
    box(x0 + 0.20, y1 - 0.22, x1 - 0.20, y1 - 0.06, 94, 148, (24, 26, 30), top=(36, 38, 42))
    qy(y1 - 0.055, x0 + 0.28, x1 - 0.28, 100, 142, (20, 22, 26))
    # small pink bag
    box(x0 + 0.12, y0 + 0.18, x0 + 0.46, y1 - 0.22, 86, 102, (214, 120, 140), top=shade((214, 120, 140), 1.08))


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
    """Low wide white bookcase (~2.8 ft by 3 ft) on the south wall, between
    the landing-door corner and the south sash, with a globe on top."""
    x0, x1, y0, y1 = 0.18, 1.70, 0.08, 0.50
    box(x0, y0, x1, y1, 0, 86, WHITE_, top=shade(WHITE_, 1.05))
    rnd = random.Random(8)
    for z in (28, 56):
        box(x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, z, z + 4, shade(WHITE_, 0.9), ol=False)
        u = x0 + 0.10
        while u < x1 - 0.14:
            bw = rnd.uniform(0.07, 0.12)
            col = rnd.choice([(160, 50, 50), (40, 70, 130), (200, 180, 70), (50, 110, 70), (230, 220, 200), (90, 60, 40)])
            box(u, y0 + 0.10, u + bw, y1 - 0.10, z + 4, z + rnd.uniform(16, 24), col, ol=False)
            u += bw + 0.015
    cyl((x0 + x1) / 2, (y0 + y1) / 2, 0.16, 86, 112, (70, 120, 170), top=shade((90, 140, 120), 1.1))


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
    qy(RD - 0.04, 2.15, 4.00, 128, 176, shade((120, 88, 48), KY))
    qy(RD - 0.045, 2.25, 3.90, 134, 170, shade((186, 196, 176), KY))


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
    # Far-to-near: the east nightstand is farther in SE, the west one farther in V.
    if hc.FLIP:
        bedside_west()
        wooden_bed()
        bedside_east()
    else:
        bedside_east()
        wooden_bed()
        bedside_west()
    pine_chest()
    pine_desk()
    white_bookcase()
    radiators()
    east_fireplace()
    wall_picture()
    place_sprite("archie", 3.50, 3.15)
    ghost_near_walls(WALL,
                     doors_S=[DRESSING_DOOR],
                     windows_E=() if hc.FLIP else [WIN_W],
                     window_z=(70, 198), window_cols=2, curtains=FLORAL)
    if hc.FLIP:
        ext_w = exterior_layer({"E": side_garden}, haze=(170, 188, 150))
        sash_on_far("E", *WIN_W, ext_w, z0=70, z1=198, curtains=FLORAL, cols=2)
        y0, y1, d = BREAST
        box(0, y0, d, y1, 0, WALL_H, shade(WALL, 0.96), faces="y")
        radiators()
    finish("Hide and Seek - Master Bedroom (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_master_mock.png",))


if __name__ == "__main__":
    main()
