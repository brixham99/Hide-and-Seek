#!/usr/bin/env python3
"""Static isometric mock-up of the Anderson house Drawing Room for 'Hide and Seek'.

4.3 m x 4.0 m room = 7.3 x 7.8 tiles. Back walls: y = 0 (bookcase, sash
window onto the side garden, photo grid) and x = 0 (door, chimney breast,
cupboards); see-through near walls: y = RD (TV wall, hall doorway) and
x = RW (piano wall, second window). Shared kit: house_common.py.

    python mock_drawing_room.py [out.png] [--exterior-debug]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(7.3, 7.8, oy=262)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DEBUG = "--exterior-debug" in sys.argv
OUT = ARGS[0] if ARGS else ("shots/hs_drawing_room_exterior_debug.png" if DEBUG else "shots/hs_drawing_room_mock_v3.png")
SOFA = (196, 194, 184)
RUG = (178, 86, 80)
HALL_DOOR = (5.75, 7.0)                 # on the TV wall (y = RD), right by the piano corner
SIDE_WIN = (0.75, 2.35)                 # the second sash window, on the x = RW wall behind the sofa


def garden_side(side, rnd, wall_len=RW):
    """The Drawing Room's side garden (photos: lawn, white picket fence, willow)."""
    u0, u1 = -6, wall_len + 6
    ext_lawn(side, u0, u1, 0, 12, rnd)
    ext_tree(side, 5.2, 5.4, trunk=140, canopy=180, r=1.4, rnd=random.Random(3))    # tall willow beyond the fence
    ext_hedge(side, u0, u1, 4.2, 4.7, h=58, rnd=rnd)
    ext_picket_fence(side, u0, u1, 3.45)
    ext_shrub(side, 1.6, 2.5, rnd=random.Random(8))
    ext_tree(side, 3.9, 2.6, trunk=95, canopy=110, r=0.75, col=(96, 140, 64), rnd=random.Random(4))
    ext_border(side, u0, u1, 1.85, 2.2, rnd)
    ext_paving(side, u0, u1, 0.3, 1.7, rnd)
    ext_house_shadow(side, u0, u1)


def photo_grid_N(u0, z0, cols=3, rows=3, pw=0.42, ph=26, gap=0.08, gz=8, seed=1):
    rnd = random.Random(seed)
    plane = lambda a, b, za, zb, c: qy(0.02, a, b, za, zb, shade(c, KY))
    for r in range(rows):
        for c in range(cols):
            a = u0 + c * (pw + gap)
            za = z0 + r * (ph + gz)
            frame_N(a, a + pw, za, za + ph, bw_photo(rnd, plane))


def painting_landscape_N(u0, u1, z0, z1):
    def inner(a, b, za, zb):
        qy(0.02, a, b, za, zb, shade((176, 196, 206), KY))
        qy(0.02, a, b, za, za + (zb - za) * .45, shade((96, 120, 70), KY))
        qy(0.02, a + (b - a) * .55, b, za + (zb - za) * .45, za + (zb - za) * .62, shade((80, 96, 80), KY))
    frame_N(u0, u1, z0, z1, inner, mount=(236, 232, 222))


def chimney():
    """Chimney breast proud of the x=0 wall: white mantel, black wood-burner, brass fender."""
    y0, y1, d = 2.35, 4.5, 0.55
    # breast: front face (x=d) and the side face toward the room's front (y=y1)
    qy(y1, 0, d, 0, WALL_H, shade(GREEN, KY))
    qx(d, y0, y1, 0, WALL_H, shade(GREEN, KX))
    qy(y1, 0, d, 0, 13, shade(WHITE, KY)); qx(d, y0, y1, 0, 13, shade(WHITE, KX))
    qy(y1, 0, d, WALL_H - 20, WALL_H, shade(WHITE, KY)); qx(d, y0, y1, WALL_H - 20, WALL_H, shade(WHITE, KX))
    qy(y1, 0, d, WALL_H - 24, WALL_H - 20, shade(WHITE, KY * .85)); qx(d, y0, y1, WALL_H - 24, WALL_H - 20, shade(WHITE, KX * .85))
    poly([P(0, y0, WALL_H), P(d, y0, WALL_H), P(d, y1, WALL_H), P(0, y1, WALL_H)], (60, 58, 54))
    # hearth (quarry tiles) in front
    hx = d + 0.5
    qz(1.5, d, y0 + .1, hx, y1 - .1, (132, 62, 44), (90, 40, 30))
    for i in range(1, 4):
        line((d + (hx - d) * i / 4, y0 + .1, 1.5), (d + (hx - d) * i / 4, y1 - .1, 1.5), (100, 46, 34), 1)
    for i in range(1, 6):
        yy = y0 + .1 + (y1 - y0 - .2) * i / 6
        line((d, yy, 1.5), (hx, yy, 1.5), (100, 46, 34), 1)
    # fireplace surround (white), black slate opening
    fy0, fy1 = y0 + .12, y1 - .12
    qx(d + .005, fy0, fy1, 0, 108, shade(WHITE, KX), shade(WHITE, .55))
    oy0, oy1 = fy0 + .32, fy1 - .32
    qx(d + .01, oy0, oy1, 0, 86, (30, 30, 32))
    qx(d + .01, oy0 + .2, oy1 - .2, 70, 82, (52, 52, 56))                 # cast iron ornament band
    # mantel shelf
    box(d, fy0 - .1, d + .2, fy1 + .1, 108, 116, WHITE)
    # wood-burner
    sx0, sx1, sy0, sy1 = d + .02, d + .42, oy0 + .32, oy1 - .32
    box(sx0, sy0, sx1, sy1, 4, 58, (36, 36, 38))
    qx(sx1 + .002, sy0 + .08, sy1 - .08, 14, 48, (20, 20, 22), (60, 60, 64))
    qx(sx1 + .004, sy0 + .14, sy1 - .14, 20, 42, (150, 70, 30))            # glow behind the glass
    qx(sx1 + .005, sy0 + .16, sy1 - .16, 22, 30, (230, 140, 50))
    box(sx0 + .1, (sy0 + sy1) / 2 - .06, sx0 + .22, (sy0 + sy1) / 2 + .06, 58, 84, (34, 34, 36))   # flue
    # brass fender round the hearth
    fz = 7
    for a, b in (((hx, y0 + .1), (hx, y1 - .1)), ((d, y0 + .1), (hx, y0 + .1)), ((d, y1 - .1), (hx, y1 - .1))):
        pygame.draw.line(screen, shade(BRASS, .7), P(a[0], a[1], 1), P(b[0], b[1], 1), 3 * S)
        pygame.draw.line(screen, BRASS, P(a[0], a[1], fz), P(b[0], b[1], fz), 3 * S)
        pygame.draw.line(screen, shade(BRASS, 1.2), P(a[0], a[1], fz + 1), P(b[0], b[1], fz + 1), 1 * S)
    # mantel ornaments: little black dog, candlesticks
    box(d + .06, fy0 + .15, d + .14, fy0 + .25, 116, 134, (24, 24, 24))
    for yy in (fy0 + .7, fy1 - .5):
        box(d + .07, yy, d + .11, yy + .04, 116, 132, (190, 150, 90))
    box(d + .05, fy1 - .28, d + .13, fy1 - .18, 116, 128, (150, 90, 50))
    # gilt-framed picture above the mantel
    def inner(a, b, za, zb):
        qx(d + .02, a, b, za, zb, shade((150, 160, 120), KX))
        qx(d + .02, a, b, za, za + (zb - za) * .4, shade((110, 120, 70), KX))
        qx(d + .02, a + (b - a) * .45, a + (b - a) * .65, za + (zb - za) * .5, za + (zb - za) * .75, shade((240, 210, 140), KX))
    frame_W(fy0 + .28, fy1 - .28, 132, 186, inner, mount=(220, 210, 180), fr=GOLD, x=d + .01)
    return y0, y1, d


def cupboards(y0, y1, d):
    """Tall built-in white panelled cupboards in the alcove: two doors below, two above."""
    col = WHITE
    box(0, y0, d, y1, 0, 96, col)
    box(0, y0, d, y1, 99, WALL_H - 24, col, ol=True)
    line((d, y0, 97.5), (d, y1, 97.5), shade(GREEN, .6), 2)
    w = y1 - y0
    for (za, zb) in ((8, 90), (106, WALL_H - 32)):
        for i in range(2):
            a = y0 + w * (0.04 + i * 0.5)
            b = y0 + w * (0.46 + i * 0.5)
            qx(d + .004, a, b, za, zb, shade(col, KX * .97), shade(col, .62))
            qx(d + .008, a + w * .06, b - w * .06, za + 10, zb - 10, shade(col, KX * .93), (196, 176, 130), 1)
        kv = y0 + w * 0.5
        qx(d + .01, kv - .07, kv - .05, (za + zb) / 2 - 3, (za + zb) / 2 + 3, (60, 54, 44))
    # top of the upper cupboards meets the cornice
    poly([P(0, y0, WALL_H - 24), P(d, y0, WALL_H - 24), P(d, y1, WALL_H - 24), P(0, y1, WALL_H - 24)], shade(col, KT))


def bookcase(x0, x1, dpt=0.6, h=108):
    """White glazed bookcase cabinet on the back (y=0) wall, red lamp on top."""
    col = WHITE
    box(x0, 0, x1, dpt, 0, 8, shade(col, .9))
    box(x0, 0, x1, dpt, 8, h, col)
    box(x0 - .04, -0.0, x1 + .04, dpt + .04, h, h + 6, col)
    rnd = random.Random(9)
    spines = [(160, 40, 40), (40, 70, 120), (220, 190, 70), (60, 110, 70), (200, 120, 60), (230, 220, 200), (110, 40, 60), (30, 30, 30)]
    shelves = [(16, 44), (50, 76), (82, 102)]
    for i in range(2):
        a = x0 + (x1 - x0) * (0.05 + i * 0.48)
        b = x0 + (x1 - x0) * (0.47 + i * 0.48)
        qy(dpt + .002, a, b, 12, h - 4, shade(col, KY * .9), shade(col, .55))
        ga, gb = a + .07, b - .07
        qy(dpt + .004, ga, gb, 16, h - 8, (48, 44, 40))
        for za, zb in shelves:
            u = ga + .01
            while u < gb - .03:
                bw = rnd.uniform(.035, .07)
                top = zb - rnd.uniform(0, 7)
                qy(dpt + .006, u, min(gb, u + bw), za, top, shade(rnd.choice(spines), KY * rnd.uniform(.85, 1.0)))
                u += bw + .004
            qy(dpt + .007, ga, gb, za - 3, za, shade(col, KY * .85))
        # glass sheen and glazing bars
        qy(dpt + .009, ga, gb, 44, 46, shade(col, KY))
        qy(dpt + .009, ga, gb, 76, 78, shade(col, KY))
        poly([P(ga + .05, dpt + .009, 20), P(ga + .1, dpt + .009, 20), P(ga + .22, dpt + .009, h - 12), P(ga + .17, dpt + .009, h - 12)], (255, 255, 255))
    # red lamp
    lx, ly = x0 + .35, dpt / 2
    cyl(lx, ly, .07, h + 6, h + 14, (60, 50, 44))
    pygame.draw.line(screen, (190, 170, 110), P(lx, ly, h + 14), P(lx, ly, h + 40), 2 * S)
    cone(lx, ly, .2, .12, h + 34, h + 58, (186, 40, 44))
    # trinkets
    box(x0 + .75, .22, x0 + .85, .32, h + 6, h + 14, (180, 90, 40))
    cyl(x0 + 1.05, .3, .06, h + 6, h + 18, (230, 230, 230))


def _puff(pts_fn, col):
    """A plump cushion face: corners pulled in, a lighter centre."""
    n = 28
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        cu, cv = math.cos(a), math.sin(a)
        su = math.copysign(abs(cu) ** .45, cu)
        sv = math.copysign(abs(cv) ** .45, cv)
        pts.append(pts_fn(.5 + .5 * su, .5 + .5 * sv))
    poly(pts, col, shade(col, .55), 1)
    inner = [pts_fn(.5 + .3 * math.copysign(abs(math.cos(a)) ** .6, math.cos(a)), .55 + .28 * math.copysign(abs(math.sin(a)) ** .6, math.sin(a)))
             for a in (2 * math.pi * i / n for i in range(n))]
    poly(inner, shade(col, 1.1))


def cushion_y(xa, xb, y, z0, z1, col):
    """Cushion leaning on a back that runs along x (faces +y), tilted back a little."""
    _puff(lambda u, v: P(xa + (xb - xa) * u, y - .12 * v, z0 + (z1 - z0) * v), shade(col, KY))


def cushion_x(x, ya, yb, z0, z1, col):
    _puff(lambda u, v: P(x - .12 * v, yb - (yb - ya) * u, z0 + (z1 - z0) * v), shade(col, KX))


def sofa():
    """Large L-shaped corner sofa in the window corner (x=RW, y=0)."""
    c = SOFA
    dep = 1.55
    xa = 3.45                                   # left end of the long leg along y=0
    yb = 3.35                                   # front end of the return along x=RW
    xr = RW - dep                               # inner edge of the return
    bh, sh, ah = 92, 44, 64
    # back cushions against the y=0 wall
    box(xa + .35, 0, RW, .5, 0, bh, c)
    # seat of the long leg and the return
    box(xa + .35, .5, xr, dep, 0, sh, c)
    box(xr, .5, RW - .5, yb - .35, 0, sh, c)
    # seat cushion seams
    for xx in (xa + .35 + (xr - xa - .35) / 2,):
        line((xx, .5, sh), (xx, dep, sh), shade(c, .7), 1)
        line((xx, dep, 6), (xx, dep, sh), shade(c, .7), 1)
    line((xr, (yb - .35 + .5) / 2 + .3, sh), (RW - .5, (yb - .35 + .5) / 2 + .3, sh), shade(c, .7), 1)
    # arm at the far-left end of the long leg
    box(xa, 0, xa + .35, dep, 0, ah, c)
    # back cushions along the x=RW (near) wall: we see their backs, nearer than the seat
    box(RW - .5, .5, RW, yb - .35, 0, bh, c)
    # arm at the front end of the return
    box(xr, yb - .35, RW, yb, 0, ah, c)
    # scatter cushions (green velvet, charcoal, pink, cream)
    cush = [((xa + .5, .52), (210, 170, 168), 0), ((xa + 1.0, .52), (226, 222, 206), 0),
            ((xa + 1.75, .52), (78, 78, 82), 0), ((xa + 2.35, .52), (34, 82, 64), 0), ((xr - .1, .52), (34, 82, 64), 0)]
    for (x, y), col, _ in cush:
        cushion_y(x, x + .55, y + .2, sh, sh + 40, col)
    return xa, yb


def coffee_table(x0, y0, x1, y1, h=46):
    """Rustic plank coffee table on splayed legs."""
    top = (172, 118, 66)
    for (lx, ly) in ((x0 + .15, y0 + .12), (x1 - .2, y0 + .12), (x0 + .15, y1 - .17), (x1 - .2, y1 - .17)):
        box(lx, ly, lx + .06, ly + .06, 0, h - 8, (110, 70, 40), ol=False)
    box(x0, y0, x1, y1, h - 8, h, top)
    for i in range(1, 3):                     # plank joints
        yy = y0 + (y1 - y0) * i / 3
        line((x0, yy, h), (x1, yy, h), shade(top, .65), 1)
    rnd = random.Random(3)
    for _ in range(8):                        # knots and grain
        gx, gy = rnd.uniform(x0 + .1, x1 - .2), rnd.uniform(y0 + .05, y1 - .05)
        line((gx, gy, h), (gx + rnd.uniform(.2, .5), gy, h), shade(top, .82), 1)
    # pink tray with remotes
    tx, ty = (x0 + x1) / 2 - .3, (y0 + y1) / 2
    fl_ellipse(tx, ty, .22, .22, (214, 150, 156), z=h + 1, ol=(150, 100, 104))
    fl_ellipse(tx, ty, .16, .16, (226, 176, 176), z=h + 3)
    box(tx - .1, ty - .03, tx + .1, ty + .02, h + 3, h + 6, (30, 30, 30), ol=False)


def rug(x0, y0, x1, y1):
    """Red and cream Persian rug (the snug, photos 10 and 12)."""
    import paint
    paint.stamp(paint.rug(x1 - x0, y1 - y0, "drawing", seed=12), x0, y0, x1, y1, 0.6)


def dog_bed(x0, y0, x1, y1):
    c = TEAL
    box(x0, y0, x1, y1, 0, 16, c)
    poly([P(x0 + .15, y0 + .15, 16), P(x1 - .15, y0 + .15, 16), P(x1 - .15, y1 - .15, 16), P(x0 + .15, y1 - .15, 16)], shade(c, .9))
    # piped edge
    pygame.draw.lines(screen, shade(c, 1.25), True, [P(x0, y0, 16), P(x1, y0, 16), P(x1, y1, 16), P(x0, y1, 16)], 1 * S)


def tv_stand(x0, x1, y0, y1):
    """Low wooden stand against the near (y=RD) wall; the TV faces the sofa, so we see its back."""
    c = OAK
    for (lx) in (x0 + .05, x1 - .15):
        box(lx, y0, lx + .1, y1, 0, 46, c)
    box(x0 + .1, y0 + .05, x1 - .1, y1 - .05, 18, 22, shade(c, .9))
    box(x0, y0, x1, y1, 46, 52, c)
    # games console + basket hint on the shelf
    box(x1 - .55, y0 + .1, x1 - .35, y0 + .5, 52, 92, (236, 236, 236))
    # TV (back view, black) on a centre foot
    tx0, tx1 = x0 + .25, x1 - .75
    ty = y0 + .32
    box((tx0 + tx1) / 2 - .25, ty - .12, (tx0 + tx1) / 2 + .25, ty + .12, 52, 56, BLACK)
    box((tx0 + tx1) / 2 - .05, ty - .02, (tx0 + tx1) / 2 + .05, ty + .04, 56, 72, BLACK)
    box(tx0, ty, tx1, ty + .07, 66, 158, BLACK, top=(40, 40, 44))
    qy(ty + .072, tx0 + .3, tx1 - .3, 80, 140, (34, 34, 36))


def piano(x0, x1, y0, y1, h=126):
    """Upright piano against the near (x=RW) wall, by the hall door; keyboard faces into the room."""
    c = (110, 62, 38)
    box(x0, y0, x1, y1, 0, h, c, top=shade(c, 1.12))
    # side panel detail (y1 face) and back panelling (x1 face)
    qy(y1 + .003, x0 + .08, x1 - .08, 12, h - 12, shade(c, KY * .9), shade(c, .55))
    for i in range(3):
        a = y0 + (y1 - y0) * (0.06 + i * 0.32)
        qx(x1 + .003, a, a + (y1 - y0) * .26, 14, h - 14, shade(c, KX * .92), shade(c, .5))
    # keyboard ledge sticking out on the room side (just visible at the far end)
    # lamp with a wicker shade, photo frames, plant
    lx, ly = x0 + .45, y0 + .35
    cyl(lx, ly, .07, h, h + 10, (210, 200, 180))
    pygame.draw.line(screen, (200, 180, 120), P(lx, ly, h + 10), P(lx, ly, h + 30), 2 * S)
    cone(lx, ly, .21, .13, h + 26, h + 52, (204, 150, 80))
    for (fy, fh, col) in ((y0 + .85, 26, (220, 200, 170)), (y0 + 1.25, 22, (40, 36, 32)), (y0 + 1.65, 30, (230, 225, 215))):
        box(x0 + .3, fy, x0 + .36, fy + .25, h, h + fh, col)
        qx(x0 + .362, fy + .04, fy + .21, h + 4, h + fh - 4, (120, 110, 100))
    # spider plant
    cyl(x0 + .45, y1 - .35, .1, h, h + 14, (236, 236, 236))
    rnd = random.Random(5)
    bx, by = P(x0 + .45, y1 - .35, h + 14)
    for _ in range(14):
        a = rnd.uniform(-2.6, -0.5)
        L = rnd.uniform(14, 26) * S
        pygame.draw.line(screen, (90, 150, 70), (bx, by), (bx + math.cos(a) * L, by + math.sin(a) * L * .9), 2 * S)


def pendant(x, y):
    """Ribbed glass globe pendant, hanging from the (cut-away) ceiling."""
    top = P(x, y, 330)
    bot = P(x, y, 222)
    pygame.draw.line(screen, (200, 170, 90), top, bot, 2 * S)
    cx, cy = P(x, y, 200)
    r = 22 * S
    glow = art.glow(110 * S // 2, (120, 96, 50), 0.5)
    screen.blit(glow, (cx - glow.get_width() / 2, cy - glow.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
    pygame.draw.ellipse(screen, (236, 214, 160), (cx - r, cy - r * 1.05, 2 * r, 2.1 * r))
    for i in range(-3, 4):
        xx = cx + i * r / 4
        hh = math.sqrt(max(0, r * r - (i * r / 4) ** 2)) * 1.0
        pygame.draw.line(screen, (210, 180, 120), (xx, cy - hh), (xx, cy + hh), max(1, S))
    pygame.draw.ellipse(screen, (255, 244, 210), (cx - r * .45, cy - r * .3, r * .9, r * .8))
    pygame.draw.rect(screen, (196, 160, 80), (cx - 5 * S, cy - r * 1.05 - 6 * S, 10 * S, 7 * S))



def main():
    background()
    if DEBUG:
        ext = exterior_layer({"N": garden_side})
        debug_exterior(ext, [("N", 2.55, 3.95, 52, 206)])
        out = pygame.transform.smoothscale(screen, (WIN_W, WIN_H))
        out.blit(pygame.font.Font(None, 30).render("Exterior layer (walls hidden); yellow = ground seen through the window", True, (255, 255, 255)), (24, 20))
        pygame.image.save(out, OUT)
        print(OUT)
        return
    floor_boards()
    threshold("S", *HALL_DOOR, (170, 150, 120))
    rug(1.25, 1.05, 6.05, 6.55)
    wall_shell(GREEN)
    ext = exterior_layer({"N": garden_side})
    sash_window("N", 2.55, 3.95, ext)
    photo_grid_N(4.55, 112, seed=2)
    painting_landscape_N(0.55, 1.6, 140, 188)
    panel_door_W(0.4, 1.85)
    wall_trim()
    cy0, cy1, cd = chimney()
    cupboards(cy1, 6.85, cd)
    rnd = random.Random(7)
    plane = lambda a, b, za, zb, c: qx(0.02, a, b, za, zb, shade(c, KX))
    for i in range(3):
        for j in range(2):
            frame_W(6.95 + i * .26, 7.17 + i * .26, 120 + j * 34, 148 + j * 34, bw_photo(rnd, plane))
    bookcase(0.25, 1.9)
    dog_bed(1.35, 4.55, 2.55, 5.65)
    coffee_table(3.0, 2.3, 5.2, 3.2)
    sofa()
    piano(RW - .9, RW - .02, 3.9, 6.15)
    tv_stand(0.85, 3.55, RD - .75, RD - .05)
    place_sprite("archie", 3.55, 4.3)
    ghost_near_walls(GREEN, doors_S=[HALL_DOOR], windows_E=[SIDE_WIN])
    finish("Hide and Seek - Drawing Room (mock-up)", OUT,
           copies=() if ARGS else ("shots/hs_drawing_room_mock.png",))


if __name__ == "__main__":
    main()
