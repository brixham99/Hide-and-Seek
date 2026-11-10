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
import iso_paint  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_dressing_mock.png"

WALL = (176, 178, 176)          # pale grey, as the master
OAK1, OAK2 = (214, 186, 148), (196, 166, 126)
WHITE_ = (244, 242, 236)
FLORAL = (176, 192, 186)        # same pale blue-green floral as the master
WARD = (162, 170, 176)          # light grey-blue shaker (photos, not charcoal)
WARD_IN = (130, 144, 154)       # cooler, darker recessed panel
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


Z_SPLIT = 198
PLINTH_H = 18


def _shaker_x(x, y0, y1, knobs=False):
    """Shaker leaves on an x=const face (inset panels darker and cooler)."""
    qx(x, y0 + 0.04, y1 - 0.04, Z_SPLIT - 4, Z_SPLIT + 3, shade(WARD, 0.88))
    n = 4
    span = y1 - y0 - 0.12
    for i in range(n):
        a = y0 + 0.06 + i * span / n
        b = y0 + 0.06 + (i + 1) * span / n - 0.05
        qx(x, a + 0.04, b - 0.04, 12, Z_SPLIT - 8, shade(WARD, 1.02))
        qx(x, a + 0.12, b - 0.12, 26, Z_SPLIT - 20, shade(WARD_IN, KX))
        qx(x, a + 0.04, b - 0.04, Z_SPLIT + 8, WALL_H - 12, shade(WARD, 1.02))
        qx(x, a + 0.12, b - 0.12, Z_SPLIT + 20, WALL_H - 24, shade(WARD_IN, KX))
        if knobs:
            mid = (a + b) / 2
            _knob(x + 0.04, mid, 112)
            _knob(x + 0.04, mid, Z_SPLIT + 32)


def _shaker_y(y, x0, x1, knobs=False):
    """Shaker leaves on a y=const face."""
    qy(y, x0 + 0.04, x1 - 0.04, Z_SPLIT - 4, Z_SPLIT + 3, shade(WARD, 0.92))
    n = 3
    span = x1 - x0 - 0.10
    for i in range(n):
        a = x0 + 0.05 + i * span / n
        b = x0 + 0.05 + (i + 1) * span / n - 0.05
        qy(y, a + 0.04, b - 0.04, 12, Z_SPLIT - 8, shade(WARD, 1.02))
        qy(y, a + 0.12, b - 0.12, 26, Z_SPLIT - 20, shade(WARD_IN, KY))
        qy(y, a + 0.04, b - 0.04, Z_SPLIT + 8, WALL_H - 12, shade(WARD, 1.02))
        qy(y, a + 0.12, b - 0.12, Z_SPLIT + 20, WALL_H - 24, shade(WARD_IN, KY))
        if knobs:
            mid = (a + b) / 2
            _knob(mid, y + 0.04, 112)
            _knob(mid, y + 0.04, Z_SPLIT + 32)


def wardrobe_east(full):
    """East-wall run. Full-height when that wall is far; a low plinth when near."""
    x0, x1, y0, y1 = 0.0, WD, 0.0, RD
    if full:
        iso_paint.paint_box(x0, y0, x1, y1, 0, WALL_H, "dressing_ward", front="W", col=WARD)
    else:
        iso_paint.paint_box(x0, y0, x1, y1, 0, PLINTH_H, "dressing_ward", front="W", col=WARD)


def wardrobe_south(full):
    """South-wall run, east of the master door."""
    x0, x1, y0, y1 = WD, 3.02, 0.0, WD
    if full:
        iso_paint.paint_box(x0, y0, x1, y1, 0, WALL_H, "dressing_ward", front="N", col=WARD)
    else:
        iso_paint.paint_box(x0, y0, x1, y1, 0, PLINTH_H, "dressing_ward", front="N", col=WARD)


def wardrobe_north(full):
    """North-wall run, east of the ensuite door."""
    x0, x1, y0, y1 = WD, 3.62, RD - WD, RD
    if full:
        iso_paint.paint_box(x0, y0, x1, y1, 0, WALL_H, "dressing_ward", front="S", col=WARD)
    else:
        iso_paint.paint_box(x0, y0, x1, y1, 0, PLINTH_H, "dressing_ward", front="S", col=WARD)


def near_wardrobe_ghosts():
    """Faint shaker faces on near-wall runs (no tall occluders)."""
    if hc.FLIP:
        # east (x~0) and south (y~0) sit on the flipped near plane and go to the ghost layer
        _shaker_x(0.05, 0.0, RD, knobs=False)
        _shaker_y(0.05, WD, 3.02, knobs=False)
    else:
        with hung_layer(alpha=118):
            _shaker_y(RD - 0.04, WD, 3.62, knobs=False)


def master_door_ghost():
    """White architrave on the near south doorway (V view)."""
    if not hc.FLIP:
        return
    a, b = MASTER_DOOR
    qy(0.03, a - 0.08, a + 0.06, 0, DOOR_H + 10, shade(WHITE_, KY))
    qy(0.03, b - 0.06, b + 0.08, 0, DOOR_H + 10, shade(WHITE_, KY))
    qy(0.03, a - 0.08, b + 0.08, DOOR_H - 2, DOOR_H + 10, shade(WHITE_, KY))


def wicker_basket():
    """Wicker basket on the floor by the ensuite doorway."""
    x0, x1, y0, y1 = 3.78, 4.20, 2.88, 3.28
    iso_paint.paint_box(x0, y0, x1, y1, 0, 28, "wicker", front="S", col=WICKER)
    box(x0 + 0.04, y0 + 0.04, x1 - 0.04, y1 - 0.04, 28, 36, shade(WICKER, 1.08), top=shade(WICKER, 0.7))
    # a hint of white linen peeking out
    box(x0 + 0.12, y0 + 0.14, x0 + 0.28, y1 - 0.14, 36, 48, (232, 228, 220), ol=False)


def radiator():
    """White radiator under the west sash; solid when that wall faces the camera."""
    if not hc.FLIP:
        return
    a, b = WIN_W
    iso_paint.paint_box(RW - 0.16, a + 0.10, RW - 0.03, b - 0.10, 0, 38, "hall_radiator", front="E", col=WHITE_)


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
    # Far-wall runs stay solid and full height; near-wall runs are a low plinth
    # plus a faint shaker hint, so the aisle and Archie stay visible.
    if hc.FLIP:
        wardrobe_north(full=True)
        wardrobe_east(full=False)
        wardrobe_south(full=False)
    else:
        wardrobe_east(full=True)
        wardrobe_south(full=True)
        wardrobe_north(full=False)
    near_wardrobe_ghosts()
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
        master_door_ghost()
    finish("Hide and Seek - Dressing Room (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_dressing_mock.png",))


if __name__ == "__main__":
    main()
