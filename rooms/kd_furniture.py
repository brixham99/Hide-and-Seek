"""Furniture of the Kitchen + Dining Room in WORLD coordinates (house_common
KD_*: x = tiles west from the dining room's east wall, y = tiles north from
the south wall, y = KD_DEP the garden wall). Both views draw from here, so
the kitchen view's glimpse of the dining half and the dining view's glimpse
of the kitchen are the same objects. Call inside `with hc.world(view_x0):`.
"""
import math
import random

import house_common as hc
from house_common import (P, poly, line, qx, qy, qz, box, cyl, cone, fl_ellipse, shade, art,  # noqa: F401
                          KX, KY, KT, WALL_H, DOOR_H, BRASS, OAK, WHITE, CREAM, GRANITE, STEEL,
                          PINE_TOP, BURGUNDY, PALE_GREY, OFF_WHITE, turned_leg, bar_stool,
                          farmhouse_table, ladder_chair, KD_LEN, KD_DEP, KD_SPLIT)

RD = KD_DEP
CD, CH = 1.02, 92                      # counter depth (tiles), worktop height
CAB = (240, 238, 232)                  # painted white kitchen cupboards
RUN = RD - CD                          # front edge of the garden-wall run (y)

# ----------------------------------------------------------------- positions (world x)
# kitchen half (x 8.2 .. 16.4)
K_HALL_DOOR = (8.45, 9.7)              # south wall
K_DRAWING_DOOR = (14.9, 16.15)         # south wall, the Drawing Room's door
K_BOOT_DOOR = (0.2, 1.5)               # y range on the west wall (x = KD_LEN)
K_WIN2 = (8.3, 9.35)                   # garden wall, over the bins
K_WIN1 = (13.5, 14.7)                  # garden wall, over the sink
K_SAGE = (3.3, 4.6)                    # y range on the west wall
K_ISLAND = (10.1, 3.8, 13.5, 5.4)
# dining half (x 0 .. 8.2)
D_FRENCH = (2.8, 4.4)                  # garden wall
D_SASH = (1.6, 3.2)                    # y range on the east wall (x = 0)
D_CHEST = (4.8, 6.5)                   # y range on the east wall
D_TABLE = (2.3, 1.5, 3.8, 5.9)         # long axis north-south
PENINSULA = (7.15, 4.2, 8.17, RD)      # from the garden-wall run south into the room, at the split
D_DRESSER = (2.4, 5.5)                 # south wall
D_PIER = (6.2, 6.7)                    # south wall (poster + radiator on its east face)


# ================================================================= kitchen
def worktop(x0, x1, y0=RUN, y1=RD, z=CH):
    box(x0, y0 - .03, x1, y1, z - 5, z, GRANITE, top=shade(GRANITE, 1.15))
    rnd = random.Random(int(x0 * 10) + 3)
    for _ in range(int((x1 - x0) * (y1 - y0) * 14)):
        fl_ellipse(rnd.uniform(x0 + .02, x1 - .02), rnd.uniform(y0, y1 - .02), .02, .012, shade(GRANITE, rnd.choice((1.4, .8))), z, n=6)


def run_units(x0, x1):
    box(x0, RUN, x1, RD, 6, CH - 5, CAB)


def sink_top(x0, x1):
    qz(CH + .2, x0, RUN - .06, x1, RD - .06, (246, 246, 244))
    qz(CH + .4, x0 + .08, RUN + .04, x1 - .08, RD - .2, (176, 182, 186))
    cyl((x0 + x1) / 2, RD - .12, .035, CH, CH + 30, (200, 202, 206))
    line(((x0 + x1) / 2, RD - .12, CH + 30), ((x0 + x1) / 2, RD - .4, CH + 26), (200, 202, 206), 3)


def range_cooker(x0, x1):
    box(x0, RUN - .02, x1, RD, 0, CH, BURGUNDY, top=(30, 28, 30))
    for i in range(5):
        fl_ellipse(x0 + .3 + i * (x1 - x0 - .6) / 4, RD - CD * .5, .11, .09, (62, 60, 62), CH + .5)


def hood_and_cabinets(x0, x1, cl, cr):
    box(cl, RD - .6, x0 - .02, RD, 142, WALL_H, CAB)
    box(x1 + .02, RD - .6, cr, RD, 142, WALL_H, CAB)
    box(x0, RD - .78, x1, RD, 168, 198, CAB)
    box(x0 + .25, RD - .55, x1 - .25, RD, 198, WALL_H, CAB)


def drawer_unit(x0, x1):
    for lx in (x0 + .07, x1 - .07):
        turned_leg(lx, RUN + .08, 0, 56, CAB, .06)
    box(x0 + .05, RUN + .1, x1 - .05, RD, 10, 14, CAB, ol=False)
    box(x0 + .45, RUN + .3, x0 + .85, RUN + .7, 14, 42, (244, 244, 240))
    box(x0, RUN, x1, RD, 50, CH - 5, CAB)
    worktop(x0 - .02, x1 + .02)
    box(x1 - .55, RUN + .25, x1 - .1, RUN + .7, CH, CH + 30, (30, 30, 32))     # air fryer
    cyl(x0 + .3, RUN + .45, .14, CH, CH + 14, (200, 200, 204))                 # stand mixer
    box(x0 + .22, RUN + .55, x0 + .38, RUN + .75, CH + 14, CH + 40, (200, 200, 204), ol=False)
    cyl(x0 + .3, RUN + .4, .1, CH + 32, CH + 42, (210, 210, 214))


def plate_rack(x0, x1, z0=124, z1=222, d=.42):
    y0 = RD - d
    rnd = random.Random(2)
    for zz in (z0, z0 + 40):
        box(x0, y0, x1, RD, zz, zz + 5, CAB)
    u = x0 + .1
    while u < x1 - .1:
        c = (250, 250, 248) if rnd.random() < .8 else (210, 220, 228)
        qy(RD - d * .5, u, u + .045, z0 + 46, z1 - 14, shade(c, KY))
        u += .085
    for i in range(int((x1 - x0) / .2)):
        cyl(x0 + .14 + i * .2, RD - d * .5, .06, z0 + 5, z0 + 22, random.Random(i).choice([(240, 240, 238), (60, 70, 110), (200, 200, 196)]))
    box(x0, y0, x1, RD, z1 - 6, z1, CAB)
    box(x0, y0, x0 + .06, RD, z0, z1, CAB)
    box(x1 - .06, y0, x1, RD, z0, z1, CAB)


def larder(x0, x1, hinge="left", d=1.1, h=192):
    """A tall single-door larder-style stainless fridge or freezer, door facing north into the room."""
    box(x0, 0, x1, d, 0, h, STEEL, top=shade(STEEL, 1.05))
    qy(d + .001, x0 + .03, x1 - .03, 4, h - 4, shade(STEEL, KY * 1.02))
    hx = x1 - .14 if hinge == "left" else x0 + .11
    qy(d + .02, hx, hx + .03, 80, 150, (205, 207, 210))
    qy(d + .002, x0 + .18, x0 + .28, 10, h - 10, shade(STEEL, KY * 1.15))


def wine_corner(x0, x1, d=1.0):
    box(x0, 0, x1, d - .04, 4, CH - 6, (50, 50, 54))
    qy(d - .039, x0 + .06, x1 - .06, 12, CH - 14, (34, 40, 46))
    for zz in range(20, CH - 16, 12):
        qy(d - .038, x0 + .1, x1 - .1, zz, zz + 2, (140, 110, 70))
    qy(d - .037, x0 + .1, x1 - .1, 60, 66, (60, 150, 90))
    box(x0 - .02, 0, x1 + .02, d, CH - 6, CH, OAK, top=shade(OAK, 1.15))
    rnd = random.Random(9)
    for zz in (132, 176):
        box(x0 + .05, 0, x1 - .05, .42, zz, zz + 5, OAK)
        for i in range(4):
            xx = x0 + .2 + i * .22
            if zz == 132:
                cyl(xx, .2, .05, 137, 172 if i % 2 else 160, rnd.choice([(30, 70, 40), (90, 20, 30), (40, 40, 40)]))
            else:
                cyl(xx, .2, .04, 181, 200, (214, 222, 226))
    cyl(x0 + .3, .6, .05, CH, CH + 34, (30, 80, 40))


def island(x0, y0, x1, y1, h=96):
    """Pale grey T&G island, chunky pine top; drawers over open slatted shelves
    of bowls on the north (sink-side, +y) face; plain T&G end facing west (+x)."""
    box(x0 + .08, y0 + .08, x1 - .08, y1 - .08, 0, 8, (110, 112, 110), ol=False)
    box(x0 + .05, y0 + .05, x1 - .05, y1 - .05, 8, h - 12, PALE_GREY)
    Y = y1 - .049
    v = y0 + .05
    while v < y1 - .05:
        line((x1 - .049, v, 10), (x1 - .049, v, h - 14), shade(PALE_GREY, KX * .8), 1)
        v += .17
    n = 4
    w = (x1 - x0 - .3) / n
    qy(Y, x0 + .15, x1 - .15, 12, h - 38, shade((96, 98, 96), KY))
    for i in range(n):
        a, b = x0 + .15 + i * w + .02, x0 + .15 + (i + 1) * w - .02
        qy(Y, a, b, h - 34, h - 15, shade(PALE_GREY, KY * 1.04))
        qy(Y + .002, (a + b) / 2 - .05, (a + b) / 2 + .05, h - 27, h - 23, BRASS)
    for xx in (x0 + .05, x1 - .15):
        qy(Y + .001, xx, xx + .1, 8, h - 12, shade(PALE_GREY, KY * 1.05))
    rnd = random.Random(3)
    for zz in (14, 40):
        for i in range(5):
            qy(Y + .001, x0 + .15, x1 - .15, zz + i * 2, zz + i * 2 + 1, shade(PALE_GREY, KY * .95))
        xx = x0 + .3
        while xx < x1 - .5:
            c = rnd.choice([(240, 240, 236), (90, 150, 140), (200, 170, 120), (180, 190, 200)])
            poly([P(xx, Y + .01, zz + 12), P(xx + .32, Y + .01, zz + 12), P(xx + .28, Y + .01, zz + 22), P(xx + .04, Y + .01, zz + 22)], shade(c, KY * 1.1))
            xx += .42
    box(x0 - .08, y0 - .08, x1 + .08, y1 + .08, h - 12, h, PINE_TOP, top=shade(PINE_TOP, 1.06))
    import paint
    paint.stamp(paint.pine_top(x1 - x0 + .16, y1 - y0 + .16, seed=12), x0 - .08, y0 - .08, x1 + .08, y1 + .08, h)
    cyl(x0 + (x1 - x0) * .45, (y0 + y1) / 2, .26, h, h + 10, (196, 150, 90), top=(214, 170, 100))


def kitchen_south_wall():
    """Facing into the room from the south wall: pier, wine corner, fridge + freezer."""
    box(10.75, 0, 11.35, .45, 0, WALL_H, OFF_WHITE, ol=False)
    wine_corner(11.4, 12.45)
    larder(12.55, 13.53, hinge="right")        # fridge
    larder(13.57, 14.55, hinge="left")         # freezer


def kitchen_island_and_stools():
    for sx in (10.8, 11.8, 12.8):
        bar_stool(sx, 3.25)
    island(*K_ISLAND)


def kitchen_run_floor():
    """The garden-wall run's floor-standing pieces (their fronts face south, away from the camera)."""
    cyl(8.55, RD - .5, .27, 0, 70, STEEL, top=shade(STEEL, 1.1))       # pedal bins
    cyl(9.15, RD - .5, .29, 0, 76, (60, 60, 62), top=(80, 80, 82))
    drawer_unit(9.5, 10.3)
    run_units(12.6, 13.65)
    worktop(12.6, 13.65)
    range_cooker(10.95, 12.55)
    run_units(13.65, KD_LEN)
    worktop(13.65, KD_LEN)
    sink_top(13.7, 14.6)


def kitchen_run_hung():
    """Wall-hung on the garden wall: hood, wall cabinets, plate rack."""
    hood_and_cabinets(10.95, 12.55, 10.3, 13.2)
    plate_rack(14.8, 16.3)


# ================================================================= dining
def folding_chair(x, y, facing="E", col=(240, 240, 238), metal=(170, 172, 176)):
    """White folding chair (slatted seat, flat back) on thin metal legs; `facing` as ladder_chair."""
    s = .19
    bx = x - s if facing == "E" else x + s
    for dy in (-s, s):
        line((x - s, y + dy, 0), (x + s, y + dy, 46), metal, 2)
        line((x + s, y + dy, 0), (x - s, y + dy, 46), metal, 2)
        line((bx, y + dy, 46), (bx, y + dy, 112), metal, 2)
    box(x - s, y - s, x + s, y + s, 44, 48, col)
    box(bx - .02, y - s, bx + .02, y + s, 80, 110, col)


def peninsula():
    """The perpendicular granite worktop on white kitchen cupboards (doors on its
    kitchen/west side), running south from the garden-wall run at the split."""
    x0, y0, x1, y1 = PENINSULA
    box(x0 + .06, y0 + .06, x1 - .06, y1, 0, 6, (90, 88, 84), ol=False)
    box(x0, y0, x1 - .04, y1, 6, CH - 5, CAB)
    n = 4
    for i in range(n):          # cupboard doors and drawers on the +x (kitchen) face
        a = y0 + .05 + i * (y1 - y0 - .1) / n + .02
        b = y0 + .05 + (i + 1) * (y1 - y0 - .1) / n - .02
        X = x1 - .039
        qx(X, a, b, 10, 62, shade(CAB, KX * .93))
        qx(X + .001, a + .05, b - .05, 14, 58, shade(CAB, KX * 1.02))
        qx(X, a, b, 66, 84, shade(CAB, KX * .93))
        fl_ellipse(X + .01, (a + b) / 2, .015, .03, (60, 60, 64), 75)
    qy(y0 + .001, x0, x1 - .04, 6, CH - 5, shade(CAB, KY))
    # end panel facing south
    worktop(x0 - .18, x1, y0=y0 - .02, y1=y1)
    # iMac at the garden-wall end, screen facing east (the chairs); keyboard in front of it
    ix = x0 + .25
    box(ix - .05, 7.45, ix + .05, 7.75, CH, CH + 24, (200, 202, 206), ol=False)
    box(ix - .03, 7.05, ix + .03, 8.15, CH + 22, CH + 70, (206, 208, 212))
    qx(ix + .031, 7.1, 8.1, CH + 26, CH + 66, (190, 192, 196))
    qz(CH + .5, x0 - .12, 7.35, x0 + .05, 7.85, (236, 236, 236))


def peninsula_chairs():
    for yy in (4.9, 5.75, 6.6, 7.45):
        folding_chair(PENINSULA[0] - .55, yy, "E")


def dining_table_set():
    """Long pine farmhouse table, north-south, with white ladder-back chairs and woven placemats."""
    x0, y0, x1, y1 = D_TABLE
    for yy in (2.2, 3.7, 5.2):                     # east side, sitters face west (+x)
        ladder_chair(x0 - .45, yy, "E")
    ladder_chair((x0 + x1) / 2, y0 - .45, "S")       # south end
    farmhouse_table(x0, y0, x1, y1)
    for k in range(5):                               # woven placemats, stacked at the north end
        fl_ellipse((x0 + x1) / 2 + .1, y1 - .9, .26, .26, shade((176, 146, 96), 1 - k * .03), 74.5 + k * 2, ol=(150, 120, 76))
    fl_ellipse(x1 - .36, 2.3, .26, .26, (176, 146, 96), 74.5, ol=(150, 120, 76))
    for yy in (2.2, 3.7, 5.2):                       # west side, sitters face east (-x)
        ladder_chair(x1 + .45, yy, "W")
    ladder_chair((x0 + x1) / 2, y1 + .45, "N")       # north end, by the rug


def round_rug(cx, cy, r=.62):
    fl_ellipse(cx, cy, r, r, (206, 196, 170), .5, ol=(170, 160, 136))
    for k in (.75, .5, .25):
        fl_ellipse(cx, cy, r * k, r * k, shade((206, 196, 170), .94 + .04 * (k * 4 % 2)), .5, ol=(180, 170, 146))


def dresser(x0, x1, col=(214, 216, 212)):
    """Big grey-white painted dresser on the south wall: cupboards and drawers below,
    open plate shelves above; faces north into the room."""
    d = .8
    box(x0, 0, x1, d, 0, 8, shade(col, .8), ol=False)
    box(x0, 0, x1, d, 8, 84, col)
    n = 4
    w = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * w + .04, x0 + (i + 1) * w - .04
        qy(d + .001, a, b, 60, 80, shade(col, KY * .94))
        fl_ellipse((a + b) / 2, d + .01, .025, .015, (240, 240, 236), 70)
        qy(d + .001, a, b, 14, 56, shade(col, KY * .94))
        qy(d + .002, a + .06, b - .06, 18, 52, shade(col, KY * 1.02))
    box(x0 - .04, 0, x1 + .04, d + .05, 84, 90, shade(col, 1.04))
    # upper: open shelves with plates, jugs and a picture propped up
    du = .42
    box(x0 + .05, 0, x1 - .05, .04, 90, 222, shade(col, .92), ol=False)
    rnd = random.Random(4)
    for zz in (128, 162, 194):
        box(x0 + .05, 0, x1 - .05, du, zz, zz + 4, col)
        u = x0 + .2
        while u < x1 - .3:
            if rnd.random() < .7:
                fl_ellipse(u, .18, .1, .03, (246, 246, 244), zz + 4)
                qy(.2, u - .1, u + .1, zz + 4, zz + 22, shade((246, 246, 244), KY))
            u += .3
    qy(.3, x0 + 1.4, x0 + 2.0, 92, 126, shade((90, 150, 80), KY))       # the tiger picture
    for xx in (x0 + .02, x1 - .07):
        box(xx, 0, xx + .05, du, 90, 222, col)
    box(x0 - .03, 0, x1 + .03, du + .04, 222, 230, col)


def dining_south_wall():
    dresser(*D_DRESSER)
    box(5.65, .12, 6.1, .58, 0, 40, (244, 244, 242))                    # bread maker
    qy(.581, 5.72, 6.02, 22, 34, (200, 204, 206))
    box(D_PIER[0], 0, D_PIER[1], .7, 0, WALL_H, OFF_WHITE, ol=False)     # pier (poster + radiator on its east face)


def dining_east_wall_items(ext):
    """On the east wall (back-left of the dining view): sash window with cream curtains
    over a radiator cover; chest of drawers with mirror, green lamp and plants."""
    hc.sash_window("W", *D_SASH, ext, curtains=(226, 218, 196))
    a, b = D_SASH
    box(0, a - .2, .38, b + .2, 0, 64, (240, 238, 232))
    for i in range(12):
        yy = a - .1 + i * (b - a + .2) / 12
        qx(.381, yy, yy + .05, 20, 54, shade((200, 200, 196), KX))
    # mirror on the wall over the chest
    c0, c1 = D_CHEST
    hc.wall_quad("W", c0 + .35, c1 - .35, 118, 214, shade((120, 116, 104), KX), .02)
    hc.wall_quad("W", c0 + .43, c1 - .43, 126, 206, shade((196, 206, 210), KX), .025)
    # chest of drawers
    wood = (132, 84, 48)
    box(0, c0, .8, c1, 0, 88, wood, top=shade(wood, 1.12))
    for r in range(3):
        for half in ((c0 + .06, (c0 + c1) / 2 - .02), ((c0 + c1) / 2 + .02, c1 - .06)):
            qx(.801, half[0], half[1], 12 + r * 24, 32 + r * 24, shade(wood, KX * .9))
            fl_ellipse(.81, (half[0] + half[1]) / 2, .01, .03, BRASS, 22 + r * 24)
    # green lamp, photo frames, plants
    cyl(.35, c1 - .35, .08, 88, 130, (70, 110, 90))
    cone(.35, c1 - .35, .25, .19, 130, 166, (110, 150, 130))
    box(.15, c0 + .5, .2, c0 + .75, 88, 112, (30, 30, 30), ol=False)
    box(.15, c0 + .8, .2, c0 + 1.0, 88, 106, (180, 150, 90), ol=False)
    for py, pr in ((c0 + .25, .17), (c0 + 1.2, .14)):
        cyl(.4, py, .1, 88, 102, (220, 220, 214))
        rnd = random.Random(int(py * 10))
        for _ in range(9):
            fl_ellipse(.4 + rnd.uniform(-pr, pr), py + rnd.uniform(-pr, pr), .07, .05, shade((70, 120, 60), rnd.uniform(.8, 1.15)), 104 + rnd.uniform(0, 16))
