#!/usr/bin/env python3
"""Static isometric mock-up of Archie's Room for 'Hide and Seek'.

The 11'8 x 11'4 (3.6 m E-W x 3.5 m N-S) bedroom north of the upstairs
corridor, opposite the landing arch — the bedroom whose door sits at the
east end of that south wall, nearest the arch. Sage / duck-egg walls,
pale oak laminate, white skirting. South wall: open doorway to the
corridor, navy metal cabinet and a flag-grid print, pine wardrobe in the
south-west corner, a crucifix above the door. North wall: white casement
with red/white gingham curtains, radiator, fields and trees beyond.
West: grey iron single bed, bedside table, pictures. East: tall bookcase
and a pine desk with mint-dipped legs. The ceiling pendant is left out
(ceiling-light rule). No internal door leaf; no car-registration lettering.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(6.4, 6.4)
from house_common import *  # noqa: E402,F401,F403
import iso_paint  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_archie_mock.png"

WALL = (148, 166, 160)
OAK1, OAK2 = (210, 186, 148), (192, 168, 128)
WHITE_ = (244, 242, 236)
IRON = (156, 160, 164)
PINE = (198, 150, 92)
MINT = (140, 188, 158)
NAVY = (36, 58, 118)
GINGHAM = (198, 88, 94)
WICKER = (186, 142, 86)
TEDDY = (168, 118, 70)

DOOR = (1.09, 2.51)             # south wall -> corridor (east end)
WINDOW = (2.35, 4.05)           # north wall, opposite the door wall


def fields(side, rnd):
    """Countryside beyond the north window: fields and trees."""
    ext_lawn(side, -8, RW + 8, 0.2, 12, rnd, base=(86, 142, 60))
    ext_lawn(side, -8, RW + 8, 3.6, 8.5, rnd, base=(112, 152, 68))
    ext_tree(side, 1.1, 3.4, trunk=88, canopy=128, r=1.05, col=(74, 120, 50), rnd=random.Random(7))
    ext_tree(side, 3.6, 5.0, trunk=104, canopy=148, r=1.35, col=(88, 130, 54), rnd=random.Random(8))
    ext_tree(side, 5.8, 3.0, trunk=80, canopy=118, r=0.9, col=(70, 116, 48), rnd=random.Random(9))


def oak_floor():
    import paint
    paint.stamp(paint.timber(RW, RD, 11, OAK1, OAK2, along="x", plank=0.24), 0, 0, RW, RD, 0)


def iron_bed():
    """Grey iron single bed along the west wall, head toward the window."""
    x0, x1 = RW - 1.72, RW - 0.10
    y0, y1 = 2.50, 5.50
    # mattress and white duvet
    iso_paint.paint_box(x0 + 0.06, y0 + 0.08, x1 - 0.06, y1 - 0.08, 30, 48, "bed_cream", front="E", col=(240, 238, 232))
    # grey/white patterned throw over the foot half
    iso_paint.paint_box(x0 + 0.08, y0 + 0.10, x1 - 0.08, y0 + 1.55, 48.2, 53, "bed_throw_grey", front="E", col=(176, 174, 178))
    # a slim under-bed drawer, set back so it does not read as a separate ottoman
    box(x0 + 0.45, y0 + 0.70, x1 - 0.12, y0 + 1.25, 18, 29, (90, 62, 40), ol=False)
    # foot rail (south) and head rail (north)
    for y, h0, h1 in ((y0, 8, 78), (y1, 8, 92)):
        box(x0, y - 0.04, x0 + 0.08, y + 0.04, 0, h1, IRON)
        box(x1 - 0.08, y - 0.04, x1, y + 0.04, 0, h1, IRON)
        box(x0, y - 0.05, x1, y + 0.05, h1 - 6, h1, IRON, top=shade(IRON, 1.12))
        n = 8
        for i in range(n):
            xx = x0 + 0.12 + i * (x1 - x0 - 0.24) / (n - 1)
            box(xx - 0.025, y - 0.03, xx + 0.025, y + 0.03, h0, h1 - 6, shade(IRON, 0.95), ol=False)
        # slight curve: taller middle uprights
        mid = (x0 + x1) / 2
        cyl(mid, y, 0.05, h1, h1 + 10, IRON, top=shade(IRON, 1.15))


def bedside():
    # just east of the bed-head, toward the window
    iso_paint.paint_box(RW - 2.15, 5.45, RW - 1.78, 6.15, 0, 54, "up_oak", front="S", col=(86, 52, 34))
    box(RW - 2.10, 5.52, RW - 1.83, 6.08, 54, 58, (72, 44, 28), ol=False)


def teddy_and_basket():
    """Wicker basket and a big teddy at the foot of the bed."""
    # open wicker basket
    bx0, bx1, by0, by1 = RW - 1.70, RW - 0.72, 1.72, 2.38
    iso_paint.paint_box(bx0, by0, bx1, by1, 0, 22, "wicker", front="S", col=WICKER)
    iso_paint.paint_box(bx0 + 0.04, by0 + 0.04, bx1 - 0.04, by1 - 0.04, 20, 30, "wicker", front="S", col=shade(WICKER, 1.05))
    qz(30.4, bx0 + 0.10, by0 + 0.08, bx1 - 0.10, by1 - 0.08, shade(WICKER, 0.62))
    # teddy sitting up beside the basket — round head, brown body
    cx, cy = RW - 0.95, 2.05
    cyl(cx, cy, 0.26, 8, 52, TEDDY, top=shade(TEDDY, 1.06))
    cyl(cx, cy, 0.22, 50, 84, TEDDY, top=shade(TEDDY, 1.12))
    cyl(cx - 0.15, cy, 0.08, 80, 94, shade(TEDDY, 0.9))
    cyl(cx + 0.15, cy, 0.08, 80, 94, shade(TEDDY, 0.9))
    cyl(cx, cy + 0.04, 0.09, 64, 74, (232, 214, 186))


def bookcase():
    """Tall dark-wood bookcase on the east wall, by the window."""
    x0, x1, y0, y1 = 0.06, 0.72, 4.05, 6.28
    iso_paint.paint_box(x0, y0, x1, y1, 0, 168, "up_bookcase", front="W", col=(92, 58, 34))
    qz(168.3, x0, y0, x1, y1, shade((92, 58, 34), 1.1))          # plain wood top, not the front sheet
    rnd = random.Random(21)
    for s, z in enumerate((18, 48, 80, 112, 144)):
        box(x0 + 0.04, y0 + 0.04, x1 - 0.04, y1 - 0.04, z - 4, z, shade((92, 58, 34), 1.12), ol=False)
        u = y0 + 0.08
        while u < y1 - 0.12:
            if rnd.random() < 0.78:
                w = rnd.uniform(0.055, 0.10)
                col = rnd.choice([(48, 72, 140), (160, 48, 48), (48, 96, 64), (200, 170, 70),
                                  (40, 40, 44), (180, 96, 48), (88, 56, 120), (200, 80, 80)])
                box(x0 + 0.08, u, x1 - 0.10, u + w, z, min(z + rnd.uniform(20, 30), 164), col, ol=False)
                u += w + 0.008
            else:
                w = rnd.uniform(0.14, 0.22)
                col = rnd.choice([(240, 238, 232), (80, 160, 200), (248, 244, 230), (120, 176, 96)])
                box(x0 + 0.10, u, x1 - 0.12, min(y1 - 0.08, u + w), z, z + rnd.uniform(14, 24), col, ol=False)
                u += w + 0.03


def desk_and_chair():
    """Pine desk with mint-dipped legs, mint chair, lamp and white purifier."""
    x0, x1, y0, y1 = 0.10, 0.88, 1.72, 3.72
    # top
    iso_paint.paint_box(x0, y0, x1, y1, 68, 74, "up_pine", front="E", col=PINE)
    # legs: pine above, mint dipped below
    for xx, yy in ((x0 + 0.06, y0 + 0.06), (x1 - 0.14, y0 + 0.06),
                   (x0 + 0.06, y1 - 0.14), (x1 - 0.14, y1 - 0.14)):
        box(xx, yy, xx + 0.08, yy + 0.08, 0, 34, MINT)
        box(xx, yy, xx + 0.08, yy + 0.08, 34, 68, shade(PINE, 0.92))
    # lamp
    cyl(x0 + 0.22, y1 - 0.35, 0.05, 74, 98, shade(WHITE_, 0.9))
    cyl(x0 + 0.22, y1 - 0.35, 0.12, 96, 108, (248, 246, 230), top=shade((248, 246, 230), 1.08))
    # white cylinder air purifier
    cyl(x0 + 0.42, y0 + 0.35, 0.16, 74, 112, WHITE_, top=shade(WHITE_, 1.06))
    # mint chair
    cx0, cx1, cy0, cy1 = 1.02, 1.55, 2.25, 2.95
    iso_paint.paint_box(cx0, cy0, cx1, cy1, 0, 42, "archie_mint", front="E", col=MINT)
    box(cx0, cy1 - 0.10, cx1, cy1, 42, 78, shade(MINT, 0.92))


def navy_cabinet():
    iso_paint.paint_box(2.70, 0.08, 4.55, 0.58, 0, 72, "archie_navy", front="S", col=NAVY)
    # two doors
    for xx in (3.18, 4.06):
        cyl(xx, 0.52, 0.03, 34, 40, (180, 184, 188))


def wardrobe():
    iso_paint.paint_box(RW - 1.18, 0.06, RW - 0.08, 0.92, 0, 176, "archie_wardrobe", front="S", col=PINE)
    line((RW - 0.63, 0.08, 12), (RW - 0.63, 0.08, 168), shade(PINE, 0.7), 1)
    cyl(RW - 0.70, 0.90, 0.03, 88, 96, (180, 184, 188))


def radiator():
    u0, u1 = WINDOW
    iso_paint.paint_box(u0 + 0.05, RD - 0.32, u1 - 0.05, RD - 0.10, 8, 48, "hall_radiator", front="S", col=WHITE_)
    for i in range(7):
        xx = u0 + 0.12 + i * (u1 - u0 - 0.24) / 6
        qy(RD - 0.10, xx, xx + 0.04, 12, 44, shade(WHITE_, KY * 0.9))


def flag_print():
    """A framed grid of coloured rectangles above the navy cabinet (far south wall)."""
    if hc.FLIP:
        return
    x0, x1, z0, z1 = 2.85, 4.40, 108, 178
    qy(0.03, x0 - 0.04, x1 + 0.04, z0 - 3, z1 + 3, shade((48, 42, 36), KY))
    cols, rows = 6, 5
    rnd = random.Random(9)
    palette = [(180, 40, 40), (40, 80, 160), (240, 220, 70), (36, 120, 64),
               (240, 240, 240), (32, 32, 36), (80, 160, 200), (160, 48, 96)]
    dw, dh = (x1 - x0) / cols, (z1 - z0) / rows
    for r in range(rows):
        for c in range(cols):
            qy(0.035, x0 + c * dw + 0.015, x0 + (c + 1) * dw - 0.015,
               z0 + r * dh + 1.5, z0 + (r + 1) * dh - 1.5,
               shade(rnd.choice(palette), KY))


def crucifix():
    if hc.FLIP:
        return
    mid = (DOOR[0] + DOOR[1]) / 2
    qy(0.03, mid - 0.03, mid + 0.03, 198, 228, shade((120, 88, 48), KY))
    qy(0.03, mid - 0.12, mid + 0.12, 214, 222, shade((120, 88, 48), KY))


def west_pictures():
    """Small framed pictures above the bed, on the west wall (far only in V-view)."""
    if not hc.FLIP:
        return
    rnd = random.Random(14)
    frames = [(3.15, 132, 0.42, 28), (3.70, 128, 0.36, 32),
              (4.85, 136, 0.30, 26), (5.30, 130, 0.38, 30)]
    for (ya, za, w, h) in frames:
        qx(RW - 0.04, ya, ya + w, za, za + h, shade((196, 158, 72), KX))
        tone = rnd.choice([(200, 196, 184), (90, 110, 130), (186, 160, 120), (120, 140, 100)])
        qx(RW - 0.045, ya + 0.03, ya + w - 0.03, za + 3, za + h - 3, shade(tone, KX * 0.95))


def east_screen():
    """Small black screen/frame on the east wall above the desk."""
    if hc.FLIP:
        return
    qx(0.04, 2.55, 3.05, 128, 158, shade((28, 28, 30), KX))


def main():
    background()
    oak_floor()
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        back_opening("N", *DOOR, glimpses.corridor_from_archie)
        crucifix()
        flag_print()
        east_screen()
    wall_trim()
    iron_bed()
    bedside()
    teddy_and_basket()
    bookcase()
    desk_and_chair()
    navy_cabinet()
    wardrobe()
    radiator()
    west_pictures()
    place_sprite("archie", 3.15, 3.25)
    ghost_near_walls(WALL,
                     doors_S=[],
                     windows_S=() if hc.FLIP else [WINDOW],
                     window_z=(70, 196), window_cols=2, curtains=GINGHAM)
    if hc.FLIP:
        ext = exterior_layer({"S": fields}, haze=(170, 188, 150))
        sash_on_far("S", *WINDOW, ext, z0=70, z1=196, curtains=GINGHAM, cols=2)
        radiator()
    finish("Hide and Seek - Archie's Room (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_archie_mock.png",))


if __name__ == "__main__":
    main()
