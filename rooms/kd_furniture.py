"""Furniture of the Kitchen + Dining Room in WORLD coordinates (house_common
KD_*: x = tiles west from the dining room's east wall, y = tiles north from
the south wall, y = KD_DEP the garden wall). Both views draw from here, so
the kitchen view's glimpse of the dining half and the dining view's glimpse
of the kitchen are the same objects. Call inside `with hc.world(view_x0):`.
"""
import math
import random

import pygame

import house_common as hc
import painted
import iso_paint
from house_common import (P, poly, line, qx, qy, qz, box, cyl, cone, fl_ellipse, shade, art,  # noqa: F401
                          KX, KY, KT, WALL_H, DOOR_H, BRASS, OAK, WHITE, CREAM, GRANITE, STEEL,
                          PINE_TOP, BURGUNDY, PALE_GREY, OFF_WHITE, turned_leg, bar_stool,
                          farmhouse_table, ladder_chair, KD_LEN, KD_DEP, KD_SPLIT, S)

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


def drawer_unit(x0, x1):
    for lx in (x0 + .07, x1 - .07):
        turned_leg(lx, RUN + .08, 0, 56, CAB, .06)
    box(x0 + .05, RUN + .1, x1 - .05, RD, 10, 14, CAB, ol=False)
    box(x0 + .45, RUN + .3, x0 + .85, RUN + .7, 14, 42, (244, 244, 240))
    box(x0, RUN, x1, RD, 50, CH - 5, CAB)
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
    iso_paint.paint_box(x0, 0, x1, d, 0, h, "kitchen_larder", front="N", col=STEEL)


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
    iso_paint.paint_box(x0 + .05, y0 + .05, x1 - .05, y1 - .05, 8, h - 12, "kitchen_island", front="N", col=PALE_GREY, faces="x")
    Y = y1 - .049
    if hc.FLIP:
        # tongue-and-groove on the south end, the face this camera sees
        yy = y0 + 0.06
        u = x0 + 0.2
        while u < x1 - 0.2:
            qy(yy, u, u + 0.05, 16, h - 20, shade(PALE_GREY, KY * 0.82))
            u += 0.16
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
    iso_paint.paint_box(x0 - .08, y0 - .08, x1 + .08, y1 + .08, h - 12, h, "dining_pine", front="N", col=PINE_TOP)
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
    """The garden-wall run's floor-standing pieces (their fronts face south, away from the camera).

    One unbroken granite slab and base along the garden wall, broken only
    for the range, then meeting the peninsula at a right-angle corner.
    """
    # bins stand on the floor in front of the run (photos), not on the worktop
    cyl(8.55, RUN - 0.38, .27, 0, 70, STEEL, top=shade(STEEL, 1.1))
    cyl(9.15, RUN - 0.38, .29, 0, 76, (60, 60, 62), top=(80, 80, 82))
    px1 = PENINSULA[2]                               # kitchen-side edge of the peninsula
    cx0, cx1 = 10.95, 12.55                          # range sits flush between the slabs
    run_units(px1, 9.5)
    drawer_unit(9.5, 10.3)
    run_units(10.3, cx0)
    worktop(px1 - 0.04, cx0)                         # overlaps the peninsula slightly to close the mitre
    range_cooker(cx0, cx1)
    run_units(cx1, 13.65)
    run_units(13.65, KD_LEN)
    worktop(cx1, KD_LEN)
    sink_top(13.7, 14.6)


def _shaker(x0, x1, y, z0, z1, n=None):
    """Door panels and a handle on a south-facing cabinet front."""
    span = x1 - x0
    count = n if n is not None else (1 if span < 1.15 else 2)
    w = span / count
    for i in range(count):
        a = x0 + i * w + 0.05
        b = x0 + (i + 1) * w - 0.05
        if b - a < 0.12:
            continue
        qy(y, a, b, z0, z1, shade(CAB, KY * 0.92))
        qy(y - 0.012, a + 0.06, b - 0.06, z0 + 5, z1 - 5, shade(CAB, KY * 1.05))
        fl_ellipse((a + b) / 2, y - 0.02, 0.018, 0.032, (64, 64, 68), (z0 + z1) / 2)


def kitchen_seen_from_south():
    """Fronts of the floor-standing run, which the usual camera sees from behind.
    Wall-hung pieces are drawn later, after the garden wall itself."""
    if not hc.FLIP:
        return
    y = RUN - 0.02
    # shaker doors on the base run, in the spans the units already occupy
    _shaker(8.22, 9.45, y, 12, 78)                # under the east window, up to the drawer unit
    _shaker(10.35, 10.90, y, 12, 78)              # between the drawer unit and the range
    _shaker(12.58, 13.6, y, 12, 78, n=1)          # the bay beside the sink: dishwasher
    qy(y - 0.015, 12.85, 13.4, 28, 62, shade((186, 190, 192), KY))
    _shaker(14.7, 16.25, y, 12, 78)
    # burgundy range: two oven doors and a handle, on its existing front
    rx0, rx1 = 10.95, 12.55
    mid = (rx0 + rx1) / 2
    for a, b in ((rx0 + 0.1, mid - 0.05), (mid + 0.05, rx1 - 0.1)):
        qy(y, a, b, 8, 72, shade((120, 28, 36), KY))
        qy(y - 0.012, a + 0.08, b - 0.08, 16, 64, shade((28, 26, 28), KY))
        fl_ellipse((a + b) / 2, y - 0.02, 0.04, 0.02, (190, 176, 140), 36)
    # sage cupboard on the west wall, doors facing into the room
    a, b, x = 3.3, 4.6, KD_LEN - 0.04
    qx(x, a, b, 4, 148, shade((148, 174, 162), KX))
    midy = (a + b) / 2
    qx(x - 0.012, a + 0.1, midy - 0.05, 16, 136, shade((176, 196, 184), KX))
    qx(x - 0.012, midy + 0.05, b - 0.1, 16, 136, shade((176, 196, 184), KX))
    fl_ellipse(x - 0.02, midy - 0.14, 0.02, 0.04, (60, 60, 64), 78)
    fl_ellipse(x - 0.02, midy + 0.14, 0.02, 0.04, (60, 60, 64), 78)
    # extinguisher by the boot door, and the white ledged door standing open
    cyl(KD_LEN - 0.16, 1.7, 0.07, 14, 70, (176, 36, 34))
    qx(KD_LEN - 0.55, 0.28, 1.42, 4, 172, shade((244, 242, 236), KX))
    for zz in (28, 78, 128):
        qx(KD_LEN - 0.57, 0.36, 1.34, zz, zz + 7, shade((228, 224, 214), KX))


def _metro(x0, x1, z0, z1, y):
    """Grey metro tiles and grout, one flat coat on the wall plane."""
    grout = shade((186, 188, 186), KY)
    tile = shade((146, 152, 150), KY)
    qy(y, x0, x1, z0, z1, grout)
    tw, th = 0.28, 9.0
    row = 0
    z = z0 + 1.1
    while z < z1 - 1.6:
        x = x0 - (tw * 0.5 if row % 2 else 0)
        zt = min(z1 - 1.0, z + th - 1.3)
        while x < x1:
            a, b = max(x0 + 0.012, x + 0.01), min(x1 - 0.012, x + tw - 0.01)
            if b - a > 0.05:
                qy(y - 0.003, a, b, z, zt, tile)
            x += tw
        z += th
        row += 1


def _wall_cab(x0, x1, z0=146, z1=214):
    y0 = RD - 0.40
    box(x0, y0, x1, RD - 0.012, z0, z1, CAB)
    _shaker(x0, x1, y0, z0 + 6, z1 - 6)


def _cubby(x0, x1, z0=146, z1=214):
    """Open shelf beside the hood, books facing the room."""
    y0 = RD - 0.34
    box(x0, y0, x0 + 0.045, RD - 0.012, z0, z1, CAB)
    box(x1 - 0.045, y0, x1, RD - 0.012, z0, z1, CAB)
    qy(RD - 0.014, x0, x1, z0, z1, shade((226, 220, 208), KY))
    rnd = random.Random(int(x0 * 17))
    spines = [(160, 42, 40), (40, 70, 120), (210, 180, 70), (56, 108, 68), (36, 36, 40), (176, 96, 58)]
    for zz in (z0 + 6, z0 + 28, z0 + 50):
        box(x0 + 0.045, y0 + 0.02, x1 - 0.045, RD - 0.016, zz, zz + 3, shade(CAB, 0.94))
        u = x0 + 0.07
        while u < x1 - 0.1:
            bw = 0.055
            box(u, y0 + 0.06, u + bw, RD - 0.06, zz + 3, zz + 3 + rnd.uniform(14, 20), rnd.choice(spines), ol=False)
            u += bw + 0.008


def _hood(x0, x1):
    """Extractor over the range: white canopy, dark filter, chimney to the cornice."""
    box(x0 + 0.05, RD - 0.68, x1 - 0.05, RD - 0.012, 162, 198, (244, 244, 240))
    qy(RD - 0.68, x0 + 0.16, x1 - 0.16, 168, 190, shade((40, 42, 46), KY))
    qy(RD - 0.69, x0 + 0.08, x1 - 0.08, 160, 165, shade((186, 188, 190), KY))
    box(x0 + 0.32, RD - 0.36, x1 - 0.32, RD - 0.012, 198, 220, (244, 244, 240))


def _pans(x0, x1, z=116):
    """A rail of pans under the plate rack, flat on the wall."""
    y = RD - 0.05
    qy(y, x0, x1, z, z + 3, shade((64, 64, 68), KY))
    u = x0 + 0.18
    while u < x1 - 0.12:
        r = 0.11
        pts = [P(u + r * math.cos(a), y - 0.004, z - 6 + r * 48 * math.sin(a))
               for a in (2 * math.pi * i / 16 for i in range(16))]
        poly(pts, (48, 50, 54))
        qy(y - 0.006, u - 0.02, u + 0.02, z - 22, z - 8, shade((70, 70, 74), KY))
        u += 0.34


def _west_clock(y=6.95, z=164, r=0.48):
    """Large grey wall clock on the west wall, at the far (north) end."""
    x = KD_LEN - 0.02
    rz = r * 60
    ring = [P(x, y + r * math.cos(a), z + rz * math.sin(a)) for a in (i * math.pi / 16 for i in range(32))]
    face = [P(x - 0.004, y + r * 0.82 * math.cos(a), z + rz * 0.82 * math.sin(a)) for a in (i * math.pi / 16 for i in range(32))]
    poly(ring, shade((118, 120, 118), KX))
    poly(face, shade((226, 226, 220), KX))
    for i in range(12):
        a = i * math.pi / 6 - math.pi / 2
        pygame.draw.circle(hc.screen, (40, 40, 42), P(x - 0.006, y + r * 0.66 * math.cos(a), z + rz * 0.66 * math.sin(a)), max(1, int(1.4 * S)))
    c = P(x - 0.008, y, z)
    pygame.draw.line(hc.screen, (30, 30, 32), c, P(x - 0.01, y + r * 0.08, z + rz * 0.48), max(1, int(2 * S)))
    pygame.draw.line(hc.screen, (30, 30, 32), c, P(x - 0.01, y + r * 0.42, z - rz * 0.12), max(1, int(S)))


def kitchen_north_wall_front():
    """What the opposite camera sees on the garden wall: shaker cabinets, the
    hood, cubbies, metro tiles, and the plate rack at the far (west) end.
    Drawn after that wall, flush on it."""
    if not hc.FLIP:
        return
    y = RD - 0.012
    # splashback on the wall, behind the worktop, stopping at the windows
    _metro(9.50, 13.42, CH + 1, 144, y)          # between the two windows
    _metro(13.55, 14.62, CH + 1, 108, y)         # under the sink window, up to the sill
    _metro(14.78, 16.22, CH + 1, 124, y)         # under the plate rack
    _wall_cab(9.52, 10.30)
    _cubby(10.34, 10.90)
    _hood(10.98, 12.52)
    _cubby(12.58, 13.08)
    _wall_cab(13.12, 13.42, z0=146, z1=214)
    plate_rack(14.85, 16.22, z0=130, z1=208, d=0.30)
    _pans(14.95, 16.05)
    _west_clock()


def kitchen_run_hung():
    """Wall-hung on the garden wall, seen from behind in the usual view."""
    # the same spans the opposite view shows the fronts of
    box(9.52, RD - 0.42, 10.92, RD, 146, 216, CAB)
    box(12.58, RD - 0.42, 13.42, RD, 146, 216, CAB)
    box(10.98, RD - 0.70, 12.52, RD, 162, 200, CAB)
    box(11.28, RD - 0.38, 12.22, RD, 200, 220, CAB)
    plate_rack(14.85, 16.22, z0=130, z1=208, d=0.30)


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
    box(x0, y0, x1, y1, 6, CH - 5, CAB)
    n = 4
    for i in range(n):          # cupboard doors and drawers on the +x (kitchen) face
        a = y0 + .05 + i * (y1 - y0 - .1) / n + .02
        b = y0 + .05 + (i + 1) * (y1 - y0 - .1) / n - .02
        X = x1 - .039
        qx(X, a, b, 10, 62, shade(CAB, KX * .93))
        qx(X + .001, a + .05, b - .05, 14, 58, shade(CAB, KX * 1.02))
        qx(X, a, b, 66, 84, shade(CAB, KX * .93))
        fl_ellipse(X + .01, (a + b) / 2, .015, .03, (60, 60, 64), 75)
    qy(y0 + .001, x0, x1, 6, CH - 5, shade(CAB, KY))
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
    iso_paint.paint_box(x0, 0, x1, d, 8, 84, "dining_dresser", front="N", col=col)
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
    iso_paint.paint_box(0, c0, .8, c1, 0, 88, "dining_chest", front="W", col=wood)
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
