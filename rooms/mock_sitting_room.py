#!/usr/bin/env python3
"""Static isometric mock-up of the Sitting Room for 'Hide and Seek', in the
house camera convention (looking plan-south-east; photo 1 is taken this way).

On the plan it is the front room at the east end of the house (south-east
corner), east of the hall/stairs, below the Dining Room: 3.9 m E-W x 3.6 m N-S
= 7.1 x 6.6 tiles (x west from the east wall, y north from the south wall).
Windows on the two outside walls (east and south), chimney breast on the north
wall (left of centre on the plan), hall door at the south end of the west wall.
  back-left  (x = 0)  = east wall: sash window with cream floral curtains over a
                        radiator, the dark side table with the drum-shade lamp
                        and smart speaker in front of it; small dark ornate print
                        towards the SE corner; cream boucle armchair (bee
                        cushion) and a small white box in the north-east corner.
  back-right (y = 0)  = south wall: second sash with curtains over a radiator;
                        small photo high by the SE corner; navy L-shaped corner
                        sofa along it (chaise running north up the east side);
                        low dark bookcase with plant and glass ornaments and two
                        butterfly pictures at the west end.
  near-right (y = RD) = north wall, ghost: chimney breast (fire surround, insert,
                        mantel, sepia picture and 'Married' sign all face away,
                        unseen); the black slate hearth with its plants shows on
                        the floor; TV (back view) on the sage cabinet in the west
                        alcove, white floating shelves in the east alcove (faint).
  near-left  (x = RW) = west wall, ghost: hall door frame at the south end; the
                        dusty-pink velvet sofa in front of it, facing east.
Centre: round marble coffee table on oak legs over a faded cream/blue rug;
the dark drum pendant is left out (from this
angle it would read as sitting on the sofa). Honey pine boards, soft blue-grey walls.

    python mock_sitting_room.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(7.1, 6.6)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_sitting_room_mock.png"

WALL = (170, 184, 194)        # soft blue-grey
CURTAIN = (232, 222, 200)     # cream floral
SLATE_BLUE = (52, 64, 88)
VELVET = (204, 150, 152)
DARK_WOOD = (84, 56, 38)
LIGHT_OAK = (200, 160, 110)
SAGE_CAB = (140, 160, 138)
WIN_E = (2.3, 4.0)            # east wall (x = 0), plan ~1.2-2.4 m from the south wall
WIN_S = (3.2, 5.1)            # south wall (y = 0), plan ~1.6-3.0 m from the east wall
HALL_DOOR = (0.75, 1.8)       # west wall (x = RW), south end
BREAST = (1.88, 4.67, 0.88)   # chimney breast on the north wall: x0, x1, depth
TABLE = (3.1, 3.3, .55)       # coffee table centre, radius


# ------------------------------------------------------------- outside
def east_side(side, rnd):
    """East: lawn, a tall hedge close by."""
    ext_lawn(side, -6, 12, 0, 12, rnd)
    ext_hedge(side, -6, 12, 3.2, 3.9, h=96, rnd=rnd)
    ext_picket_fence(side, -6, 12, 2.5)
    ext_border(side, -6, 12, 1.35, 1.75, rnd)
    ext_paving(side, -6, 12, 0.15, 1.25, rnd)
    ext_house_shadow(side, -6, 12)


def south_side(side, rnd):
    """South (front): lawn, a tree, shrubs, hedge further out."""
    ext_lawn(side, -6, 14, 0, 12, rnd)
    ext_hedge(side, -6, 14, 4.2, 4.8, h=88, rnd=rnd)
    ext_picket_fence(side, -6, 14, 3.35)
    ext_tree(side, 1.8, 2.6, trunk=120, canopy=170, r=1.1, rnd=random.Random(11))
    ext_shrub(side, 4.6, 2.0, rnd=random.Random(12))
    ext_border(side, -6, 14, 1.55, 1.95, rnd)
    ext_paving(side, -6, 14, 0.2, 1.45, rnd)
    ext_house_shadow(side, -6, 14)


# ------------------------------------------------------------- helpers
def _puff(pts_fn, col):
    n = 28
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        cu, cv = math.cos(a), math.sin(a)
        pts.append(pts_fn(.5 + .5 * math.copysign(abs(cu) ** .45, cu), .5 + .5 * math.copysign(abs(cv) ** .45, cv)))
    poly(pts, col, shade(col, .55), 1)
    inner = [pts_fn(.5 + .3 * math.copysign(abs(math.cos(a)) ** .6, math.cos(a)), .55 + .28 * math.copysign(abs(math.sin(a)) ** .6, math.sin(a)))
             for a in (2 * math.pi * i / n for i in range(n))]
    poly(inner, shade(col, 1.1))


def cushion_y(xa, xb, y, z0, z1, col):
    _puff(lambda u, v: P(xa + (xb - xa) * u, y - .12 * v, z0 + (z1 - z0) * v), shade(col, KY))


def cushion_x(x, ya, yb, z0, z1, col):
    _puff(lambda u, v: P(x - .12 * v, yb - (yb - ya) * u, z0 + (z1 - z0) * v), shade(col, KX))


def floral_curtains(side, u0, u1, z1):
    """Little pink/green sprigs over the cream curtains sash_window drew."""
    rnd = random.Random(int(u0 * 10))
    for ca, cb in ((u0 - .55, u0 + .02), (u1 - .02, u1 + .55)):
        for _ in range(26):
            u, z = rnd.uniform(ca + .04, cb - .04), rnd.uniform(18, z1 + 8)
            x, y = wall_pt(side, u, z, .075)
            pygame.draw.circle(screen, rnd.choice([(196, 120, 130), (176, 96, 110), (214, 160, 150)]), (x, y), 2.2 * S)
            pygame.draw.circle(screen, (120, 146, 100), (x + 3 * S, y + 2 * S), 1.4 * S)


def radiator(side, u0, u1, z0=14, z1=44):
    k = wall_k(side)
    wall_quad(side, u0, u1, z0, z1, shade((240, 240, 236), k), .06)
    u = u0 + .06
    while u < u1 - .03:
        wall_quad(side, u, u + .015, z0 + 2, z1 - 2, shade((240, 240, 236), k * .82), .062)
        u += .08


# ------------------------------------------------------------- east wall
def east_wall():
    a, b = WIN_E
    radiator("W", a + .1, b - .1)
    plane = lambda u0, u1, za, zb, c: qx(0.021, u0, u1, za, zb, shade(c, KX))
    def ornate(u0, u1, za, zb):
        plane(u0, u1, za, zb, (40, 36, 44))
        cu, cz = (u0 + u1) / 2, (za + zb) / 2
        for i in range(8):
            t = i * math.pi / 4
            x, y = P(.022, cu + (u1 - u0) * .28 * math.cos(t), cz + (zb - za) * .28 * math.sin(t))
            pygame.draw.circle(screen, (170, 140, 90), (x, y), 2 * S)
        x, y = P(.022, cu, cz)
        pygame.draw.circle(screen, (190, 150, 96), (x, y), 3.5 * S)
    frame_W(0.95, 1.45, 128, 170, ornate, mount=(30, 28, 26), fr=(30, 28, 26))


def side_table(y0, y1, x1=.66, h=58):
    box(.08, y0, x1, y1, h - 5, h, DARK_WOOD, top=shade(DARK_WOOD, 1.2))
    for lx, ly in ((.1, y0 + .02), (x1 - .07, y0 + .02), (.1, y1 - .07), (x1 - .07, y1 - .07)):
        box(lx, ly, lx + .05, ly + .05, 0, h - 5, DARK_WOOD, ol=False)
    box(.12, y0 + .04, x1 - .04, y1 - .04, 16, 19, DARK_WOOD, ol=False)
    cx, cy = .34, (y0 + y1) / 2 + .06
    cyl(cx, cy, .1, h, h + 30, (200, 220, 218), top=(220, 236, 236))           # glass base
    pygame.draw.line(screen, (160, 150, 120), P(cx, cy, h + 30), P(cx, cy, h + 48), 2 * S)
    cyl(cx, cy, .3, h + 46, h + 82, (124, 146, 128), top=(150, 168, 150))       # grey-green drum shade
    cyl(x1 - .14, y0 + .12, .06, h, h + 12, (24, 24, 26))                       # smart speaker


def armchair(x0, y0, x1, y1):
    """Cream boucle armchair, back to the east wall, facing west; light wood arms; bee cushion."""
    boucle = (234, 226, 210)
    aw = .2
    box(x0 + .05, y0 + .05, x1 - .05, y1 - .05, 0, 12, shade(LIGHT_OAK, .8), ol=False)
    box(x0, y0, x0 + .3, y1, 12, 92, boucle)                                    # back
    box(x0 + .3, y0 + aw, x1, y1 - aw, 12, 42, boucle)                          # seat
    cushion_x(x0 + .42, y0 + aw + .1, y1 - aw - .1, 42, 82, (28, 28, 30))
    # gold bee on the cushion
    cy = (y0 + y1) / 2
    bx, by = P(x0 + .38, cy, 64)
    pygame.draw.ellipse(screen, (206, 168, 70), (bx - 5 * S, by - 3.5 * S, 10 * S, 7 * S))
    for dx in (-1.5, 1.5):
        pygame.draw.line(screen, (28, 28, 30), (bx + dx * S, by - 3 * S), (bx + dx * S, by + 3 * S), S)
    pygame.draw.ellipse(screen, (226, 210, 160), (bx - 6 * S, by - 9 * S, 6 * S, 6 * S), S)
    pygame.draw.ellipse(screen, (226, 210, 160), (bx, by - 9 * S, 6 * S, 6 * S), S)
    for ya, yb in ((y0, y0 + aw), (y1 - aw, y1)):                               # arms: wood frame, boucle pad
        box(x0 + .3, ya, x1, yb, 12, 56, boucle)
        box(x0 + .3, ya, x1 + .03, yb, 56, 62, LIGHT_OAK, top=shade(LIGHT_OAK, 1.12))
        box(x1 - .06, ya + .04, x1, yb - .04, 0, 56, LIGHT_OAK, ol=False)


def white_box(x0, y0, s=.3, h=22):
    box(x0, y0, x0 + s, y0 + s, 0, h, (242, 242, 238), top=(250, 250, 248))


# ------------------------------------------------------------- south wall
def south_wall():
    a, b = WIN_S
    radiator("N", a + .1, b - .1)
    plane = lambda u0, u1, za, zb, c: qy(0.021, u0, u1, za, zb, shade(c, KY))
    frame_N(.45, .8, 176, 204, colour_photo(random.Random(3))(plane), fr=(30, 28, 26))
    for u0 in (5.62, 6.28):                                                     # butterflies over the bookcase
        def butterfly(p, q, za, zb, u0=u0):
            plane(p, q, za, zb, (236, 232, 222))
            cu, cz = (p + q) / 2, (za + zb) / 2
            for s in (-1, 1):
                for dz, r, col in ((5, 7, (60, 110, 170)), (-4, 5, (214, 120, 50))):
                    x, y = P(cu + s * (q - p) * .17, .023, cz + dz)
                    pygame.draw.circle(screen, shade(col, KY), (x, y), r * S)
            pygame.draw.line(screen, (30, 30, 30), P(cu, .024, cz - 9), P(cu, .024, cz + 9), S)
        frame_N(u0, u0 + .5, 126, 170, butterfly, mount=(236, 232, 222), fr=(26, 26, 28))


def bookcase(x0, x1, d=.55, h=92):
    box(x0, 0, x1, d, 0, h, DARK_WOOD, top=shade(DARK_WOOD, 1.18))
    rnd = random.Random(14)
    spines = [(160, 40, 40), (40, 70, 120), (220, 190, 70), (60, 110, 70), (200, 120, 60), (230, 220, 200), (110, 40, 60), (30, 30, 30)]
    qy(d + .002, x0 + .05, x1 - .05, 6, h - 6, (40, 28, 20))
    for za, zb in ((8, 40), (46, 84)):
        u = x0 + .06
        while u < x1 - .08:
            bw = rnd.uniform(.035, .07)
            qy(d + .004, u, min(x1 - .06, u + bw), za, zb - rnd.uniform(0, 8), shade(rnd.choice(spines), KY * rnd.uniform(.85, 1.0)))
            u += bw + .004
        qy(d + .005, x0 + .05, x1 - .05, za - 3, za, shade(DARK_WOOD, KY * 1.1))
    # plant and glass ornaments on top
    cyl(x0 + .35, .28, .1, h, h + 16, (220, 214, 200))
    bx, by = P(x0 + .35, .28, h + 16)
    for i in range(12):
        t = -math.pi * (.15 + .7 * i / 11)
        pygame.draw.line(screen, (70, 130, 70), (bx, by), (bx + math.cos(t) * 22 * S, by + math.sin(t) * 26 * S), 2 * S)
    for j, (u, col) in enumerate(((x0 + .8, (120, 180, 200)), (x0 + 1.05, (200, 140, 180)), (x0 + 1.25, (160, 200, 150)))):
        cyl(u, .28, .05, h, h + 14 + 6 * j, col, top=shade(col, 1.2))


def corner_sofa():
    """Navy/slate L-shaped corner sofa: main run along the south wall under the window,
    chaise pointing north up the east side."""
    c = SLATE_BLUE
    x_end, dep, ch_y = 4.9, 1.6, 3.0
    bh, sh, ah = 88, 42, 60
    box(0, 0, x_end, .45, 0, bh, c)                                 # back along the south wall
    box(.3, .45, 1.6, ch_y, 0, sh, c)                               # chaise seat
    box(0, .45, .3, ch_y, 0, ah - 6, c)                             # chaise's low outer arm (east side)
    box(1.6, .45, x_end - .35, dep, 0, sh, c)                       # main seat
    for xx in (2.6, 3.6):
        line((xx, .45, sh), (xx, dep, sh), shade(c, .7), 1)
        line((xx, dep, 4), (xx, dep, sh), shade(c, .7), 1)
    line((.3, 1.7, sh), (1.6, 1.7, sh), shade(c, .7), 1)
    box(x_end - .35, 0, x_end, dep, 0, ah, c)                       # west arm
    for x, col in ((.45, (226, 184, 180)), (1.05, (232, 224, 206)), (1.8, (70, 60, 70)),
                   (2.5, (226, 184, 180)), (3.25, (232, 224, 206)), (3.9, (226, 184, 180))):
        cushion_y(x, x + .55, .66, sh, sh + 38, col)
    # the dark floral one gets a few flowers
    for i in range(5):
        px, py = P(1.9 + i * .08, .6, sh + 12 + (i % 3) * 7)
        pygame.draw.circle(screen, (200, 110, 120), (px, py), 2 * S)


# ------------------------------------------------------------- centre
def rug(x0, y0, x1, y1):
    """Faded cream and blue rug under the marble table (photo 1)."""
    import paint
    paint.stamp(paint.rug(x1 - x0, y1 - y0, "sitting", seed=31), x0, y0, x1, y1, 0.6)


def coffee_table():
    cx, cy, r = TABLE
    h = 44
    for a in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4):
        lx, ly = cx + r * .68 * math.cos(a), cy + r * .68 * math.sin(a)
        box(lx - .03, ly - .03, lx + .03, ly + .03, 0, h - 6, LIGHT_OAK, ol=False)
    fl_ellipse(cx, cy, r * .72, r * .72, shade(LIGHT_OAK, .9), 12)              # slatted shelf
    for i in range(-3, 4):
        line((cx + i * .1, cy - r * .6, 12.5), (cx + i * .1, cy + r * .6, 12.5), shade(LIGHT_OAK, .65), 1)
    cyl(cx, cy, r, h - 6, h, (226, 226, 222), top=(240, 240, 238))              # marble top
    import paint
    paint.stamp(paint.marble(180, seed=2), cx - r, cy - r, cx + r, cy + r, h, mask="ellipse")
    box(cx - .22, cy - .06, cx - .02, cy + .06, h, h + 4, (30, 30, 32), ol=False)    # game controller
    fl_ellipse(cx + .2, cy + .05, .15, .15, (200, 220, 226), h + 1)                 # bowl of glass paperweights
    for dx, dy, col in ((.16, .02, (60, 120, 200)), (.24, .08, (200, 80, 90)), (.2, .12, (90, 180, 120))):
        px, py = P(cx + dx, cy + dy, h + 8)
        pygame.draw.circle(screen, col, (px, py), 3.5 * S)


# ------------------------------------------------------------- north wall
def hearth():
    x0, x1, d = BREAST
    y = RD - d
    box(x0 - .15, y - .55, x1 + .15, y, 0, 3, (40, 42, 46), top=(52, 54, 58))       # black slate hearth
    for px, h in ((x0 + .25, 40), (x1 - .3, 56)):
        cyl(px, y - .25, .12, 3, 18, (176, 110, 80))
        bx, by = P(px, y - .25, 18)
        for i in range(10):
            t = -math.pi * (.1 + .8 * i / 9)
            pygame.draw.line(screen, (60, 120, 64), (bx, by), (bx + math.cos(t) * 18 * S, by + math.sin(t) * h * .6 * S), 2 * S)


def tv_cabinet(x0, x1, d=.55, h=50):
    """Teal cabinet in the west alcove (left of the fireplace when you face it),
    with the television standing on it, clear of the chimney breast."""
    y0 = RD - d
    box(x0, y0, x1, RD - .02, 0, h, SAGE_CAB, top=shade(SAGE_CAB, 1.1))
    tx0, tx1 = x0 + .18, x1 - .18
    ty = y0 + .12
    box(tx0, ty, tx1, ty + .1, h, h + 8, BLACK)
    box(tx0 + .15, ty + .02, tx1 - .15, ty + .08, h + 8, h + 62, BLACK, top=(28, 30, 32))
    qy(ty + .02, tx0 + .28, tx1 - .28, h + 16, h + 54, (18, 22, 26))


def fireplace_front():
    """The south face of the chimney: dark painted breast, brick opening, mantel,
    candles and the print. The usual view looks at the back of this wall."""
    if not hc.FLIP:
        return
    x0, x1, d = BREAST
    y = RD - d
    grey = (96, 98, 102)
    qy(y, x0 - 0.05, x1 + 0.05, 0, WALL_H, shade(grey, KY))
    qy(y - 0.01, x0 + 0.35, x1 - 0.35, 6, 86, (150, 78, 62))          # exposed brick
    qy(y - 0.02, x0 + 0.55, x1 - 0.55, 10, 70, (36, 34, 32))           # the opening
    box(x0 - 0.12, y - 0.18, x1 + 0.12, y + 0.02, 92, 106, (236, 232, 224))
    for xx, col in ((x0 + 0.25, (40, 36, 34)), (x0 + 0.55, (230, 220, 190)),
                    (x1 - 0.7, (190, 150, 80)), (x1 - 0.35, (230, 220, 190))):
        cyl(xx, y - 0.08, 0.045, 106, 128, col)
    # framed print (the photo's picture over the mantel, not a mirror or a screen)
    qy(y - 0.02, x0 + 0.48, x1 - 0.48, 126, 200, (36, 32, 30))
    qy(y - 0.025, x0 + 0.60, x1 - 0.60, 132, 194, (232, 224, 206))
    qy(y - 0.03, x0 + 0.70, x1 - 0.70, 140, 188, (196, 176, 142))       # sepia sky
    qy(y - 0.032, x0 + 0.70, x1 - 0.70, 140, 162, (118, 100, 72))       # ground
    qy(y - 0.034, x0 + 0.88, x0 + 1.25, 148, 176, (72, 60, 44))         # a tree
    qy(y - 0.034, x1 - 1.35, x1 - 1.05, 150, 168, (86, 74, 52))


def north_wall_hung():
    """Faint (the ghost wall's room-facing side faces away): chimney breast, mantel,
    alcove shelves with books. The fire, surround, sepia picture and sign are on its
    south face and stay unseen."""
    x0, x1, d = BREAST
    with hung_layer(alpha=115):
        box(x0, RD - d, x1, RD, 0, WALL_H, shade(WALL, .95), faces="x")
        box(x0 - .1, RD - d - .14, x1 + .1, RD - d, 112, 120, (30, 30, 32), faces="xz")    # mantel shelf
        rnd = random.Random(19)
        for (a, b), col, levels in (((.1, x0 - .05), WHITE, (120, 160, 200)), ((x1 + .05, RW - .1), DARK_WOOD, (140, 180))):
            for zz in levels:
                box(a, RD - .32, b, RD - .02, zz - 4, zz, col, top=shade(col, 1.1))
                u = a + .05
                while u < b - .1:
                    bw = rnd.uniform(.04, .08)
                    bc = rnd.choice([(160, 40, 40), (40, 70, 120), (220, 190, 70), (60, 110, 70), (230, 220, 200)])
                    box(u, RD - .28, u + bw, RD - .06, zz, zz + rnd.uniform(22, 30), bc, ol=False)
                    u += bw + .01


# ------------------------------------------------------------- west side
def pink_sofa(y0, y1):
    """Large dusty-pink velvet sofa by the west wall, facing east across the room."""
    c = VELVET
    x0, x1 = RW - 1.55, RW - .1
    bh, sh, ah = 86, 42, 60
    box(x0, y0 + .3, x1 - .45, y1 - .3, 0, sh, c)                   # seat
    for yy in ((y0 + y1) / 2,):
        line((x0, yy, sh), (x1 - .45, yy, sh), shade(c, .7), 1)
    for ya, yb in ((y0, y0 + .3),):
        box(x0, ya, x1, yb, 0, ah, c)                               # south arm
    for yy, col in ((y0 + .4, (236, 228, 210)), (y1 - .95, (236, 228, 210))):
        cushion_x(x1 - .5, yy, yy + .55, sh, sh + 36, col)
    box(x1 - .45, y0, x1, y1, 0, bh, c)                             # back (nearest us)
    box(x0, y1 - .3, x1, y1, 0, ah, c)                              # north arm
    for k in range(3):                                              # velvet sheen on the back
        yy = y0 + .4 + k * (y1 - y0 - .8) / 2
        line((x1 + .001, yy, 12), (x1 + .001, yy + .25, bh - 10), shade(c, 1.12), 1)


def main():
    background()
    floor_boards()
    rug(1.7, 1.5, 5.5, 5.0)
    hearth()
    wall_shell(WALL)
    ext = exterior_layer({"W": east_side, "N": south_side})
    sash_window("W", *WIN_E, ext, curtains=CURTAIN)
    floral_curtains("W", *WIN_E, 206)
    sash_window("N", *WIN_S, ext, curtains=CURTAIN)
    floral_curtains("N", *WIN_S, 206)
    east_wall()
    south_wall()
    wall_trim()
    corner_sofa()
    bookcase(5.4, 6.95)
    side_table(3.25, 3.85)
    white_box(.2, 4.3)
    armchair(.08, 4.75, 1.3, 5.95)
    coffee_table()
    place_sprite("archie", 2.4, 4.55)
    pink_sofa(2.05, 5.35)
    tv_cabinet(5.3, 6.85)
    north_wall_hung()
    fireplace_front()
    ghost_near_walls(WALL, doors_E=[HALL_DOOR], curtains=None)
    finish("Hide and Seek - Sitting Room (mock-up)", OUT)


if __name__ == "__main__":
    main()
