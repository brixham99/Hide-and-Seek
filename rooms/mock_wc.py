#!/usr/bin/env python3
"""Static isometric mock-up of the downstairs WC (the 'Dragon Toilet') for
'Hide and Seek', in the house camera convention (looking plan-south-east).

On the plan it is the small room at the west end of the Boot Room (between the
Boot Room and the Garage), under the Study; it has the same south outside wall
and the same depth as the Boot Room. Room about 0.9 m E-W x 1.7 m N-S =
1.65 x 3.1 tiles (x west from the east wall, y north from the south wall):
  back-left  (x = 0)  = east wall (to the Boot Room): the sage ledged door
                        (closed), at the same y as the Boot Room's WC door.
  back-right (y = 0)  = south wall (outside, onto the drive): tall narrow
                        casement in a deep reveal with a tiled sill (soap dish
                        and soap) at the east end; the small white wall-hung
                        basin with a chrome mixer in the south-west corner, grey
                        hand towel below it.
  near-right (y = RD) = north wall, ghost: the close-coupled toilet with its
                        cistern against it, facing south; the tiled ledge with
                        the toilet brush east of the cistern; the loo-roll holder
                        and the dark-wood two-tier towel shelf high up (faint).
  near-left  (x = RW) = west wall (to the garage), ghost: the slim white column
                        radiator just north of the basin and the chrome mirror
                        on a chain above it (faint backs; they face east).
Deep teal paint above white embossed tiles to ~1.1 m with a rounded dado
capping tile; grey stone floor; cream shaggy mat in front of the toilet,
pink/grey patterned mat under the basin.

    python mock_wc.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(1.65, 3.1)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_wc_mock.png"

DOOR = (0.9, 2.3)             # east wall: the Boot Room's WC_DOOR (same y, both rooms share the south wall)
WINDOW = (0.18, 0.6, 96, 206)  # south wall, east end, deep reveal
REVEAL = 0.2
BASIN = (0.92, 1.6)           # south wall, west end
DEEP_TEAL = (22, 88, 98)
TILE_WHITE = (240, 240, 236)
SAGE_DOOR = (138, 158, 150)
DADO = 100
CHROME = (196, 200, 206)
WOOD_DARK = (88, 60, 40)
BOOT_SHIFT = 6.6              # WC u + this = Boot Room u along the same south wall


def drive_side(side, rnd):
    """Out of the window: the same gravel drive and shrubs as the Boot Room's view,
    shifted to this window's place along the south wall."""
    s = BOOT_SHIFT
    ext_gravel(side, -18, 8, 0, 14, rnd)
    ext_barn(side, -9 - s, 1.2 - s, 2.0, 5.0, h=62, roof=56)
    ext_car(side, 1.6 - s, 9.5 - s, 1.25, 4.3, col=(58, 78, 112), h=92, cabin=56)
    ext_paving(side, -18, 8, 0.0, 0.55, rnd, col=(150, 142, 130), slab=0.45)
    for u, t in ((-2.2, 1.1), (-1.2, 0.9), (0.2, 1.0)):
        ext_shrub(side, u, t, r=0.45, h=120, col=(76, 108, 60), rnd=random.Random(int(u * 10 + 70)))
    ext_house_shadow(side, -18, 8, depth=0.9)


def embossed_tiles(side, u0, u1, z0=0, z1=DADO, size=.26, zs=14):
    """White pressed-tin-pattern tiles: grout grid, each tile with a raised square and boss."""
    k = wall_k(side)
    wall_quad(side, u0, u1, z0, z1, shade(TILE_WHITE, k * .8))
    z = z0
    while z < z1 - 1e-6:
        zt = min(z1, z + zs)
        u = u0
        while u < u1 - 1e-6:
            b = min(u1, u + size)
            wall_quad(side, u + .01, b - .01, z + .7, zt - .7, shade(TILE_WHITE, k))
            if b - u > size * .8 and zt - z > zs * .8:
                wall_quad(side, u + .05, b - .05, z + 3, zt - 3, shade(TILE_WHITE, k * .9))
                wall_quad(side, u + .07, b - .07, z + 4, zt - 4, shade(TILE_WHITE, k * 1.02))
                c = (u + b) / 2
                wall_quad(side, c - .025, c + .025, (z + zt) / 2 - 1.5, (z + zt) / 2 + 1.5, shade(TILE_WHITE, k * .86))
            u += size
        z = zt
    # rounded capping tile
    wall_quad(side, u0, u1, z1, z1 + 4, shade(TILE_WHITE, k * 1.08), .03)
    wall_quad(side, u0, u1, z1 + 4, z1 + 6, shade(TILE_WHITE, k * .92), .02)
    wall_quad(side, u0, u1, z1 - 2, z1, shade(TILE_WHITE, k * .7), .03)


def walls():
    wall_shell(DEEP_TEAL)
    a, b = DOOR
    embossed_tiles("W", 0, a - .1)
    embossed_tiles("W", b + .1, RD)
    w0, w1 = WINDOW[:2]
    embossed_tiles("N", 0, w0 - .05)
    embossed_tiles("N", w1 + .05, RW)
    embossed_tiles("N", w0 - .05, w1 + .05, z0=0, z1=WINDOW[2] - 4)


def window(ext):
    """Tall narrow white casement set back in a deep reveal; tiled sill with the soap dish."""
    u0, u1, z0, z1 = WINDOW
    n = -REVEAL
    show_through(ext, [wall_pt("N", u0, z0, n), wall_pt("N", u1, z0, n), wall_pt("N", u1, z1, n), wall_pt("N", u0, z1, n)])
    fc = shade(WHITE, KY * 1.03)
    for zz in (z0, z1 - 5):
        wall_quad("N", u0, u1, zz, zz + 5, fc, n + .005)
    for u in (u0, (u0 + u1) / 2, u1):
        wall_quad("N", u - .03, u + .03, z0, z1, fc, n + .006)
    wall_quad("N", u0, u1, z0 + (z1 - z0) * .7 - 2, z0 + (z1 - z0) * .7 + 2, fc, n + .006)   # transom
    # reveal: the east jamb (faces west, +x) and the tiled sill
    qx(u0, n, 0, z0 - 4, z1 + 6, shade(DEEP_TEAL, KX * 1.1))
    poly([P(u0, n, z0 - 4), P(u1, n, z0 - 4), P(u1, 0, z0 - 4), P(u0, 0, z0 - 4)], shade(TILE_WHITE, KT))
    for t in (.33, .66):
        line((u0 + (u1 - u0) * t, n, z0 - 4), (u0 + (u1 - u0) * t, 0, z0 - 4), shade(TILE_WHITE, .8), 1)
    qy(0.001, u0, u1, z0 - 10, z0 - 4, shade(TILE_WHITE, KY * 1.06))
    # head
    wall_quad("N", u0 - .03, u1 + .03, z1 + 6, z1 + 10, shade(DEEP_TEAL, KY * .8), .001)
    # soap dish and soap
    cx, cy = (u0 + u1) / 2 + .05, -.08
    box(cx - .09, cy - .05, cx + .09, cy + .05, z0 - 4, z0, (232, 232, 228))
    box(cx - .06, cy - .035, cx + .06, cy + .035, z0, z0 + 4, (236, 214, 170), top=(246, 228, 190))


def door():
    """The sage ledged door to the Boot Room, closed, seen from inside."""
    a, b = DOOR
    architrave("W", a, b, DOOR_H, WHITE)
    Wf = lambda u, z: P(.01, u, z)
    draw_polys(plank_door_face(Wf, a, b, DOOR_H, SAGE_DOOR, KX, hinge="right", strap=True, latch=True))


def mats():
    # pink/grey patterned mat under the basin
    x0, x1, y0, y1 = .9, 1.58, .14, .78
    qz(.5, x0, y0, x1, y1, (196, 160, 168))
    qz(.6, x0 + .05, y0 + .05, x1 - .05, y1 - .05, (170, 170, 176))
    for i in range(3):
        for j in range(4):
            cx, cy = x0 + .14 + i * .2, y0 + .12 + j * .14
            poly([P(cx, cy - .05, .7), P(cx + .06, cy, .7), P(cx, cy + .05, .7), P(cx - .06, cy, .7)], (214, 150, 166))
    # cream shaggy mat in front of the toilet
    rnd = random.Random(3)
    x0, x1, y0, y1 = .38, 1.28, 1.05, 1.78
    qz(.8, x0, y0, x1, y1, (226, 216, 190))
    for _ in range(140):
        fx, fy = rnd.uniform(x0 + .03, x1 - .03), rnd.uniform(y0 + .03, y1 - .03)
        fl_ellipse(fx, fy, .03, .02, shade((232, 222, 196), rnd.uniform(.9, 1.06)), 1.2, n=8)
    qy(y1, x0, x1, 0, 1.6, (200, 190, 166))
    qx(x1, y0, y1, 0, 1.6, (188, 178, 156))


def basin():
    """Small white rectangular wall-hung basin, single chrome mixer, grey towel below."""
    x0, x1 = BASIN
    d = .62
    top = 80
    # towel on a little rail under the front
    box(x0 + .1, d - .02, x1 - .1, d + .02, top - 22, top - 19, CHROME, ol=False)
    box(x0 + .14, d - .03, x1 - .14, d + .01, top - 64, top - 20, (120, 124, 128), top=(140, 144, 148))
    box(x0, 0, x1, d - .04, top - 18, top, (246, 246, 244), top=(250, 250, 248))
    qz(top + .3, x0 + .07, .14, x1 - .07, d - .12, (210, 214, 216))
    qz(top + .4, x0 + .1, .17, x1 - .1, d - .15, (188, 194, 198))
    cx = (x0 + x1) / 2
    cyl(cx, .08, .03, top, top + 18, CHROME)
    box(cx - .02, .08, cx + .02, .22, top + 14, top + 18, CHROME, ol=False)
    box(cx - .015, .02, cx + .015, .1, top + 18, top + 26, CHROME, ol=False)     # lever


def ledge():
    """Small tiled ledge east of the cistern (boxed pipework), toilet brush on it."""
    x0, x1, y0 = 0, .36, RD - .34
    box(x0, y0, x1, RD, 0, 58, TILE_WHITE, top=shade(TILE_WHITE, 1.02))
    for zz in (14, 28, 42):
        line((x1, y0, zz), (x1, RD, zz), shade(TILE_WHITE, .7), 1)
        line((x0, y0, zz), (x1, y0, zz), shade(TILE_WHITE, .72), 1)
    cyl(.18, RD - .17, .07, 58, 80, (244, 244, 242), top=(220, 220, 220))
    cyl(.18, RD - .17, .012, 80, 102, CHROME)


def toilet():
    """White close-coupled toilet, cistern against the north wall, facing south."""
    w = (248, 248, 246)
    cx = .84
    cy0 = RD - .34
    # pan: pedestal, then bowl rim and seat/lid
    box(cx - .17, cy0 - .7, cx + .17, cy0, 0, 30, shade(w, .96))
    fl_ellipse(cx, cy0 - .48, .3, .42, shade(w, .9), 30)
    box(cx - .3, cy0 - .5, cx + .3, cy0, 30, 40, w, ol=False)
    poly([P(cx + .3 * math.cos(t), cy0 - .5 + .44 * math.sin(t), 40) for t in [math.pi + i * math.pi / 12 for i in range(13)]] +
         [P(cx + .3, cy0, 40), P(cx - .3, cy0, 40)], shade(w, KT))
    poly([P(cx + .3 * math.cos(t), cy0 - .5 + .44 * math.sin(t), 40) for t in [math.pi + i * math.pi / 12 for i in range(13)]],
         shade(w, KT), outline=(170, 170, 172))
    # cistern
    box(cx - .32, cy0, cx + .32, RD - .01, 40, 96, w, top=(238, 238, 236))
    box(cx - .06, RD - .2, cx + .06, RD - .14, 96, 99, CHROME, ol=False)            # flush button


def west_wall_hung():
    """West (ghost) wall, faint: column radiator just north of the basin, chain-hung
    chrome mirror with a little shelf above it (both face east, away from us)."""
    with hung_layer():
        y0, y1 = .74, 1.24
        for i in range(5):
            yy = y0 + i * (y1 - y0) / 5
            box(RW - .12, yy + .01, RW - .03, yy + .085, 14, 70, (240, 240, 238), ol=False)
        box(RW - .1, y0, RW - .04, y1, 22, 26, (220, 220, 218), ol=False)
        box(RW - .1, y0, RW - .04, y1, 60, 64, (220, 220, 218), ol=False)
        my0, my1 = .78, 1.2
        box(RW - .05, my0, RW - .02, my1, 124, 174, CHROME, ol=False)
        box(RW - .14, my0, RW - .02, my1, 120, 123, CHROME, ol=False)              # little shelf
        cm = (my0 + my1) / 2
        line((RW - .03, my0 + .04, 174), (RW - .03, cm, 204), CHROME, 1)
        line((RW - .03, my1 - .04, 174), (RW - .03, cm, 204), CHROME, 1)


def north_wall_hung():
    """North (ghost) wall, faint: loo-roll holder by the ledge and the two-tier
    dark-wood towel shelf on a black frame, high up, with rolled towels."""
    with hung_layer(alpha=120):
        box(.42, RD - .1, .46, RD - .01, 76, 80, CHROME, ol=False)
        box(.38, RD - .2, .5, RD - .06, 66, 88, (246, 246, 244))
        x0, x1, d = .2, 1.45, .44
        for zz in (168, 206):
            box(x0, RD - d, x1, RD - .01, zz - 5, zz, WOOD_DARK, top=shade(WOOD_DARK, 1.15))
        for xx in (x0 + .02, x1 - .04):
            box(xx, RD - d, xx + .02, RD - d + .02, 150, 210, IRON, ol=False)
            box(xx, RD - d, xx + .02, RD - .01, 150, 153, IRON, ol=False)
        rnd = random.Random(8)
        for zz in (168, 206):
            xx = x0 + .1
            while xx < x1 - .25:
                col = rnd.choice([(244, 244, 240), (150, 152, 156), (236, 236, 232), (120, 124, 130)])
                r = .1
                box(xx, RD - d + .04, xx + 2 * r, RD - .05, zz, zz + 15, col, top=shade(col, 1.04), ol=False)
                fl_ellipse(xx + r, RD - .049, r, .001, col, zz + 7)
                ring = [P(xx + r + r * math.cos(t), RD - .048, zz + 7.5 + 7.5 * math.sin(t)) for t in [i * math.pi / 8 for i in range(16)]]
                poly(ring, shade(col, KY * 1.02), outline=shade(col, .7))
                xx += 2 * r + .04


def main():
    background()
    floor_flagstones(cols=((150, 150, 146), (136, 138, 136), (160, 158, 152), (128, 130, 130)), seed=21, row=0.6)
    floor_slab((136, 138, 136))
    ext = exterior_layer({"N": drive_side})
    walls()
    window(ext)
    door()
    wall_trim(cornice=False, skirting=False)
    mats()
    basin()
    ledge()
    place_sprite("archie", 0.62, 1.05)
    toilet()
    west_wall_hung()
    north_wall_hung()
    ghost_near_walls(DEEP_TEAL, cornice=False)
    finish("Hide and Seek - Dragon Toilet (mock-up)", OUT)


if __name__ == "__main__":
    main()
