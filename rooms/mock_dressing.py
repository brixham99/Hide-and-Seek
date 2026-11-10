#!/usr/bin/env python3
"""Static isometric mock-up of the Dressing Room for 'Hide and Seek'.

The 10' x 7'2 (3.0 m E-W x 2.2 m N-S) room north of the Master Bedroom,
west-aligned with it. Pale grey walls, white skirting, light oak laminate.
South wall: open doorway from the master, west of centre; floor-to-ceiling
grey-blue shaker wardrobes from the east corner up to that door. East wall:
a full run of the same built-in wardrobes, a pair of doors in the middle
and overhead cupboards across the top. North wall: matching wardrobes from
the east corner up to an open doorway into the En-suite at the west end;
a wicker basket on the floor by that door. West wall: a sash with pale
blue-green floral curtains, rooftops beyond, and a white radiator under
it. A sage runner with a branch pattern lies in the aisle between the
north and south wardrobe runs, pointing at the east wall. No internal
door leaf; ceiling light left out; no registration-plate lettering.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(5.3, 4.0)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_dressing_mock.png"

WALL = (176, 178, 176)          # pale grey, as the master
OAK1, OAK2 = (214, 186, 148), (196, 166, 126)
WHITE_ = (244, 242, 236)
FLORAL = (176, 192, 186)        # same pale blue-green floral as the master
WARD = (110, 114, 118)          # painted grey-blue shaker
WARD_IN = (96, 100, 104)
SAGE = (186, 192, 176)
BRANCH = (124, 132, 114)
WICKER = (148, 112, 72)

MASTER_DOOR = (3.10, 4.45)      # south wall, west of centre -> master
ENSUITE_DOOR = (3.75, 5.10)     # north wall, west end -> en-suite
WIN_W = (1.20, 2.80)            # west wall, over the radiator
WD = 0.88                       # wardrobe depth


def side_garden(side, rnd):
    """West side: gardens and rooftops, a step below, as in the sash."""
    ext_lawn(side, -8, RD + 8, 0.2, 12, rnd, base=(90, 138, 62))
    ext_hedge(side, -8, RD + 8, 3.8, 4.5, h=92, rnd=rnd)
    ext_tree(side, 1.4, 2.6, trunk=100, canopy=140, r=1.1, col=(78, 122, 50), rnd=random.Random(41))
    ext_tree(side, 3.6, 3.4, trunk=88, canopy=128, r=1.0, col=(88, 130, 54), rnd=random.Random(42))
    ext_house_shadow(side, -8, RD + 8, depth=0.9)


def oak_floor():
    import paint
    paint.stamp(paint.timber(RW, RD, 11, OAK1, OAK2, along="x", plank=0.24), 0, 0, RW, RD, 0)


def sage_runner():
    """Sage runner with a simple branch pattern, down the aisle toward the east wall."""
    x0, x1, y0, y1 = 1.10, 3.40, 1.28, 2.72
    box(x0, y0, x1, y1, 0.4, 1.2, SAGE, top=shade(SAGE, 1.04))
    rnd = random.Random(9)
    for i in range(7):
        xa = x0 + 0.18 + i * 0.42
        ya = y0 + 0.22 + (i % 3) * 0.28
        box(xa, ya, xa + 0.55, ya + 0.07, 1.2, 1.6, BRANCH, ol=False)
        box(xa + 0.12, ya - 0.10, xa + 0.18, ya + 0.22, 1.2, 1.6, shade(BRANCH, 0.92), ol=False)


def _knob(x, y, z):
    cyl(x, y, 0.035, z - 4, z + 4, WHITE_, top=shade(WHITE_, 1.06))


def wardrobe_east():
    """Floor-to-ceiling run on the east wall, doors facing west into the aisle."""
    x0, x1, y0, y1 = 0.0, WD, 0.0, RD
    box(x0, y0, x1, y1, 0, WALL_H, WARD, top=shade(WARD, 1.04))
    z_split = 198
    qx(x1 + 0.01, y0 + 0.05, y1 - 0.05, z_split - 4, z_split + 3, shade(WARD, 0.82))
    n = 4
    span = y1 - y0 - 0.12
    for i in range(n):
        a = y0 + 0.06 + i * span / n
        b = y0 + 0.06 + (i + 1) * span / n - 0.05
        qx(x1 + 0.015, a + 0.07, b - 0.07, 16, z_split - 14, shade(WARD_IN, KX))
        qx(x1 + 0.015, a + 0.07, b - 0.07, z_split + 10, WALL_H - 14, shade(WARD_IN, KX))
        mid = (a + b) / 2
        _knob(x1 + 0.05, mid, 112)
        _knob(x1 + 0.05, mid, z_split + 32)


def wardrobe_south():
    """Built-ins along the south wall, east of the master door, doors facing north."""
    x0, x1, y0, y1 = WD, 3.02, 0.0, WD
    box(x0, y0, x1, y1, 0, WALL_H, WARD, top=shade(WARD, 1.04))
    z_split = 198
    qy(y1 + 0.01, x0 + 0.04, x1 - 0.04, z_split - 4, z_split + 3, shade(WARD, 0.88))
    n = 3
    span = x1 - x0 - 0.10
    for i in range(n):
        a = x0 + 0.05 + i * span / n
        b = x0 + 0.05 + (i + 1) * span / n - 0.05
        qy(y1 + 0.015, a + 0.07, b - 0.07, 16, z_split - 14, shade(WARD_IN, KY))
        qy(y1 + 0.015, a + 0.07, b - 0.07, z_split + 10, WALL_H - 14, shade(WARD_IN, KY))
        mid = (a + b) / 2
        _knob(mid, y1 + 0.05, 112)
        _knob(mid, y1 + 0.05, z_split + 32)


def wardrobe_north():
    """Built-ins along the north wall, east of the ensuite door, doors facing south."""
    x0, x1, y0, y1 = WD, 3.62, RD - WD, RD
    box(x0, y0, x1, y1, 0, WALL_H, WARD, top=shade(WARD, 1.04))
    z_split = 198
    qy(y0 - 0.01, x0 + 0.04, x1 - 0.04, z_split - 4, z_split + 3, shade(WARD, 0.88))
    n = 3
    span = x1 - x0 - 0.10
    for i in range(n):
        a = x0 + 0.05 + i * span / n
        b = x0 + 0.05 + (i + 1) * span / n - 0.05
        qy(y0 - 0.015, a + 0.07, b - 0.07, 16, z_split - 14, shade(WARD_IN, KY))
        qy(y0 - 0.015, a + 0.07, b - 0.07, z_split + 10, WALL_H - 14, shade(WARD_IN, KY))
        mid = (a + b) / 2
        _knob(mid, y0 - 0.05, 112)
        _knob(mid, y0 - 0.05, z_split + 32)


def wicker_basket():
    """Wicker basket on the floor by the ensuite doorway."""
    x0, x1, y0, y1 = 3.78, 4.20, 2.88, 3.28
    box(x0, y0, x1, y1, 0, 28, WICKER, top=shade(WICKER, 0.85))
    box(x0 + 0.04, y0 + 0.04, x1 - 0.04, y1 - 0.04, 28, 36, shade(WICKER, 1.08), top=shade(WICKER, 0.7))
    # a hint of white linen peeking out
    box(x0 + 0.12, y0 + 0.14, x0 + 0.28, y1 - 0.14, 36, 48, (232, 228, 220), ol=False)


def radiator():
    """White radiator under the west sash; solid when that wall faces the camera."""
    if not hc.FLIP:
        return
    a, b = WIN_W
    box(RW - 0.16, a + 0.10, RW - 0.03, b - 0.10, 0, 38, WHITE_, top=shade(WHITE_, 1.04))


def floral_drapes_west():
    if not hc.FLIP:
        return
    u0, u1 = WIN_W
    W = lambda u, z, n=0.0: wall_pt("E", u, z, n)

    def quad(a, b, za, zb, col, n=0.07):
        poly([W(a, za, n), W(b, za, n), W(b, zb, n), W(a, zb, n)], col)

    z1 = 198
    aa, bb = W(u0 - 0.52, z1 + 16, 0.08), W(u1 + 0.52, z1 + 16, 0.08)
    pygame.draw.line(screen, (200, 200, 196), aa, bb, max(2, int(3 * S)))
    rnd = random.Random(29)
    for ca, cb in ((u0 - 0.50, u0 + 0.04), (u1 - 0.04, u1 + 0.50)):
        for f in range(5):
            fa = ca + (cb - ca) * f / 5
            fb = ca + (cb - ca) * (f + 1) / 5
            quad(fa, fb, 10, z1 + 12, shade(FLORAL, 0.78 + 0.2 * (f % 2)), n=0.08)
            for _ in range(2):
                uu = fa + (fb - fa) * rnd.random()
                zz = 28 + rnd.random() * 140
                quad(uu, uu + 0.035, zz, zz + 7, shade((220, 228, 220), 0.95), n=0.085)


def main():
    background()
    oak_floor()
    sage_runner()
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        back_opening("N", *MASTER_DOOR, glimpses.master_from_dressing)
    wall_trim()
    # Far-to-near: east and south are farther in SE; north is farther in V.
    if hc.FLIP:
        wardrobe_north()
        wardrobe_east()
        wardrobe_south()
    else:
        wardrobe_east()
        wardrobe_south()
        wardrobe_north()
    wicker_basket()
    place_sprite("archie", 2.65, 2.00)
    ghost_near_walls(WALL,
                     doors_S=[ENSUITE_DOOR],
                     windows_E=() if hc.FLIP else [WIN_W],
                     window_z=(70, 198), window_cols=2, curtains=FLORAL)
    if hc.FLIP:
        ext_w = exterior_layer({"E": side_garden}, haze=(170, 188, 150))
        sash_on_far("E", *WIN_W, ext_w, z0=70, z1=198, curtains=FLORAL, cols=2)
        floral_drapes_west()
        radiator()
    finish("Hide and Seek - Dressing Room (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_dressing_mock.png",))


if __name__ == "__main__":
    main()
