#!/usr/bin/env python3
"""Static isometric mock-up of the Downstairs Office (the plan's STUDY, 3.3 m x 2.0 m)
for 'Hide and Seek', in the house camera convention (looking plan-south-east).

On the plan the study sits at the back of the house's west wing, between the
garage (west) and the utility (east), above the Boot Room. Room 2.0 m E-W x
3.3 m N-S = 3.6 x 6.0 tiles (x west from the east wall, y north from the south wall):
  back-left  (x = 0)  = east wall (to the utility): an assorted picture wall
                        (frames leaning on the rail shelf and hung above); grey desk on
                        a drawer pedestal with two monitors and the black chair
                        at the north end; the white low TV bench and big TV
                        (screen facing west into the room) south of it.
  back-right (y = 0)  = south wall (to the Boot Room): the grey-sage plank
                        door, open into the office against the east wall.
  near-right (y = RD) = north wall, ghost: the casement window and the three
                        clocks above it (faint; they face away).
  near-left  (x = RW) = west wall (to the garage), ghost and kept clear:
                        black metal shelving in the north-west corner, the
                        small white side table a little forward of it.
Grey-painted brick over white tongue-and-groove, the picture-rail shelf and
framed pictures on the east wall, terracotta quarry tiles; the tan
leather armchair with its Union Jack cushion at the door end.

    python mock_office.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(3.6, 6.0)
from house_common import *  # noqa: E402,F401,F403
import painted  # noqa: E402
import iso_paint  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_office_mock.png"

DOOR = (0.15, 1.6)            # south wall, east end (the Boot Room's Study door)
WINDOW = (1.0, 2.6)           # north wall, ghost
GREY_BRICK = (150, 152, 150)
SAGE_DOOR = (138, 158, 150)
TAN = (178, 118, 70)
PANEL_H = 100


def boot_room_beyond(side, rnd):
    import glimpses
    glimpses.boot_from_office()


def walls():
    if not hc.FLIP:
        for side, n in (("N", RW), ("W", RD)):
            tongue_and_groove(side, 0, n, 0, PANEL_H, WHITE, rail=False)
            brick_wall(side, 0, n, PANEL_H, WALL_H, GREY_BRICK, seed=3 if side == "N" else 4)
        picture_wall()
    boot = exterior_layer({"N": boot_room_beyond}, haze=(180, 190, 178))
    doorway_back("N", *DOOR, boot)


# hung on the brick above the picture rail: (y0, y1, z0, z1, frame colour, shape)
HUNG = [(1.6, 2.05, 150, 196, "wood", "rect"), (2.15, 2.4, 152, 180, "black", "rect"),
        (2.15, 2.4, 188, 216, "red", "rect"), (2.55, 3.25, 146, 196, "cream", "rect"),
        (3.4, 3.75, 150, 200, "sage", "oval"), (3.9, 4.6, 168, 214, "black", "rect"),
        (3.95, 4.2, 140, 160, "white", "rect"), (4.35, 4.6, 140, 160, "wood", "rect"),
        (4.75, 5.05, 150, 186, "red", "rect"), (5.2, 5.85, 154, 204, "wood", "rect")]


def picture_wall():
    """East wall: a mixed arrangement of framed pictures, some leaning on the picture-rail
    shelf, some hung on the brick above it; the door leaf covers the wall south of 1.5."""
    F = FRAME_COLOURS
    rnd = random.Random(5)
    photo_shelf("W", 1.55, RD - .05, PANEL_H + 6, rnd, frames=list(F.values()),
                interiors=[(150, 190, 220), (110, 150, 90), (220, 180, 120), (200, 80, 70), (90, 120, 170), (240, 220, 170)])
    plane = lambda a, b, za, zb, c: qx(0.021, a, b, za, zb, shade(c, KX))
    for y0, y1, z0, z1, fc, shape in HUNG:
        inner = colour_photo(random.Random(int(y0 * 100 + z0)))(plane)
        if shape == "rect":
            mount = F["cream"] if fc != "cream" else F["white"]
            frame_W(y0, y1, z0, z1, inner, mount=mount, fr=F[fc])
        else:      # an oval frame
            cy, cz, ry, rz = (y0 + y1) / 2, (z0 + z1) / 2, (y1 - y0) / 2, (z1 - z0) / 2
            ring = lambda f: [P(.02, cy + ry * f * math.cos(t), cz + rz * f * math.sin(t)) for t in [i * math.pi / 14 for i in range(28)]]
            poly(ring(1), shade(F[fc], KX))
            poly(ring(.8), shade((150, 190, 220), KX))
            poly([p for p in ring(.8) if p[1] >= P(.02, cy, cz)[1]], shade((110, 150, 90), KX))
            pygame.draw.circle(screen, shade((220, 180, 140), KX), P(.02, cy, cz + rz * .15), int(ry * 0.32 * HW * S))


def clocks_hung():
    """Three wall clocks over the window (red, white, black), faint: they face into the room, away from us."""
    import math
    with hung_layer():
        for u, col in ((1.2, (190, 40, 40)), (1.8, (236, 236, 232)), (2.4, (30, 30, 32))):
            pts = [P(u + .2 * math.cos(t), RD - .03, 214 + 13 * math.sin(t)) for t in [i * math.pi / 12 for i in range(24)]]
            poly(pts, shade(col, KY))


def door_leaf():
    """Grey-sage ledged door, hinged at the east jamb, open flat against the east wall."""
    a, b = DOOR
    Wf = lambda u, z: P(.08, u - a, z)
    box(.02, 0, .08, b - a, 0, DOOR_H - 3, SAGE_DOOR, faces="x")
    draw_polys(plank_door_face(Wf, a, b, DOOR_H - 3, SAGE_DOOR, KX, hinge="left"))


def shelving(y0, y1, x0=RW - .72, x1=RW - .04, h=190):
    """Black metal shelving unit in the north-west corner, against the west (ghost) wall."""
    blk = (34, 34, 36)
    for yy in (y0, y1 - .04):
        for xx in (x0, x1 - .04):
            box(xx, yy, xx + .04, yy + .04, 0, h, blk, ol=False)
    rnd = random.Random(8)
    for zz in (10, 56, 102, 148, h - 4):
        box(x0, y0, x1, y1, zz, zz + 3, blk, ol=False)
        if zz < h - 10:
            yy = y0 + .08
            while yy < y1 - .2:
                w = rnd.uniform(.15, .35)
                box(x0 + .1, yy, x1 - .1, yy + w, zz + 3, zz + rnd.uniform(16, 36), rnd.choice([(240, 240, 236), (180, 150, 110), (60, 90, 140), (90, 90, 96)]))
                yy += w + .05


def desk(y0, y1, d=1.1, h=74, col=(150, 154, 158)):
    iso_paint.paint_box(.05, y0 + .05, .6, y0 + .6, 0, h - 4, "office_desk", front="W", col=col)
    for yy in (y1 - .08,):
        box(d - .08, yy, d - .02, yy + .05, 0, h - 4, col, ol=False)
    iso_paint.paint_box(0, y0, d, y1, h - 4, h, "office_desk", front="W", col=col)
    # two monitors facing into the room, keyboard, mouse
    for c in (y0 + .55, y0 + 1.25):
        box(.2, c + .15, .3, c + .35, h, h + 12, (40, 40, 42), ol=False)
        box(.24, c - .05, .3, c + .62, h + 12, h + 52, (30, 30, 32))
        qx(.301, c - .02, c + .59, h + 15, h + 49, (40, 56, 76))
    qz(h + .5, .52, y0 + .55, .7, y0 + 1.5, (36, 36, 38))
    qz(h + .5, .55, y0 + 1.65, .65, y0 + 1.78, (36, 36, 38))


def office_chair(x, y):
    blk = (30, 30, 32)
    for a in range(5):
        import math
        t = a * 2 * math.pi / 5
        line((x, y, 6), (x + .28 * math.cos(t), y + .28 * math.sin(t), 4), blk, 3)
    cyl(x, y, .03, 6, 44, (80, 80, 84))
    iso_paint.paint_box(x - .25, y - .25, x + .25, y + .25, 44, 52, "office_black", front="W", col=blk)
    iso_paint.paint_box(x + .2, y - .22, x + .28, y + .22, 52, 118, "office_black", front="W", col=blk)


def side_table(y0, y1, x0, x1):
    w = (244, 244, 240)
    painted.table(x0, y0, x1, y1, h=60, col=w, legs="square")
    iso_paint.paint_box(x0, y0, x1, y1, 56, 60, "office_tv_bench", front="W", col=w)
    qz(60.5, x0 + .15, y0 + .1, x0 + .33, y1 - .1, (230, 230, 228))     # a spare keyboard


def armchair(x0, y0, x1, y1):
    """Tan leather club armchair facing north (+y), drawn back to front: plinth,
    backrest, far (east) arm, seat cushion, Union Jack cushion leaning on the
    backrest, then the near (west) arm, which only crosses the cushion's lower corner."""
    aw, back_d = .22, .3                  # arm width, backrest depth (tiles)
    seat_z, arm_z, back_z = 42, 62, 100
    dark = shade(TAN, .78)
    iso_paint.paint_box(x0 + .04, y0 + .04, x1 - .04, y1 - .04, 0, 10, "office_leather", front="S", col=shade(TAN, .55))
    iso_paint.paint_box(x0, y0, x1, y0 + back_d, 10, back_z, "office_leather", front="S", col=TAN)
    qy(y0 + back_d + .001, x0 + aw, x1 - aw, seat_z + 4, back_z - 6, shade(TAN, KY * 1.05))
    iso_paint.paint_box(x0, y0, x0 + aw, y1, 10, arm_z, "office_leather", front="S", col=TAN)
    iso_paint.paint_box(x0 + aw, y0 + back_d, x1 - aw, y1 - .02, 10, seat_z - 6, "office_leather", front="S", col=dark)
    iso_paint.paint_box(x0 + aw, y0 + back_d, x1 - aw, y1 - .02, seat_z - 6, seat_z, "office_leather", front="S", col=TAN)
    line((x0 + aw, y1 - .02, seat_z - 3), (x1 - aw, y1 - .02, seat_z - 3), shade(TAN, .65), 1)
    # Union Jack cushion standing on the seat, leaning back against the backrest
    c0, c1 = x0 + aw + .07, x1 - aw - .07
    yb, yt = y0 + back_d + .2, y0 + back_d + .04          # bottom edge forward, top edge against the back
    zb, zt = seat_z, seat_z + 44
    Wf = lambda u, z: P(u, yb + (yt - yb) * (z - zb) / (zt - zb), z)
    poly([P(c1, yb, zb), P(c1 + .05, yb - .05, zb), P(c1 + .05, yt - .05, zt), P(c1, yt, zt)], shade((20, 40, 110), KX * .8))   # its side
    draw_polys(union_jack(Wf, c0, c1, zb, zt, KY))
    iso_paint.paint_box(x1 - aw, y0, x1, y1, 10, arm_z, "office_leather", front="S", col=TAN)
    for ax in (x0, x1 - aw):                                                           # rolled arm fronts
        qy(y1 + .001, ax + .03, ax + aw - .03, arm_z - 10, arm_z - 3, shade(TAN, KY * 1.12))


def tv_bench(y0, y1, d=.6):
    """Low white TV bench against the east wall, the big TV's screen facing west into the room."""
    iso_paint.paint_box(.02, y0, d, y1, 0, 44, "office_tv_bench", front="W", col=(240, 240, 236))
    box(.2, (y0 + y1) / 2 - .12, .38, (y0 + y1) / 2 + .12, 44, 50, (30, 30, 32), ol=False)
    box(.24, y0 + .1, .32, y1 - .1, 52, 132, (26, 26, 28))
    qx(.321, y0 + .14, y1 - .14, 56, 128, (34, 44, 60))
    qx(.322, y0 + .3, y0 + .5, 60, 124, (50, 62, 80))


def main():
    background()
    floor_tiles(TERRACOTTA, size=.5, seed=6)
    floor_slab(TERRACOTTA)
    wall_shell(GREY_BRICK)
    walls()
    wall_trim(cornice=False, skirting=False)
    door_leaf()
    tv_bench(1.65, 3.6)
    desk(3.8, 5.92)
    office_chair(1.55, 4.9)
    place_sprite("archie", 1.7, 1.35)
    armchair(2.2, .25, 3.3, 1.35)
    side_table(3.95, 4.6, RW - 1.05, RW - .4)
    shelving(4.95, 5.95)
    if not hc.FLIP:
        clocks_hung()
    ghost_near_walls(GREY_BRICK, windows_S=() if hc.FLIP else [WINDOW],
                     window_z=(100, 200), window_cols=2, cornice=False, curtains=None)
    if hc.FLIP:
        tongue_and_groove("S", 0, RW, 0, PANEL_H, WHITE, rail=False)
        brick_wall("S", 0, RW, PANEL_H, WALL_H, GREY_BRICK, seed=3)
        tongue_and_groove("E", 0, RD, 0, PANEL_H, WHITE, rail=False)
        brick_wall("E", 0, RD, PANEL_H, WALL_H, GREY_BRICK, seed=4)
        def hedge(side, rnd):
            ext_lawn(side, -4, RW + 4, 0.15, 6.5, rnd, base=(58, 130, 52))
            ext_hedge(side, -4, RW + 4, 1.8, 2.7, h=110, rnd=rnd)
            ext_picket_fence(side, -4, RW + 4, 1.35, h=36)
        ext = exterior_layer({"S": hedge}, haze=(156, 184, 168))
        sash_on_far("S", *WINDOW, ext, z0=100, z1=200, cols=2)
        clocks_hung()
    img = finish("Hide and Seek - Downstairs Office (mock-up)", OUT)
    if not ARGS:      # close-up of the armchair
        a, b = P(2.2, 1.35, 0), P(3.3, .25, 104)
        cx, cy = (a[0] + b[0]) / 2 / S, (a[1] + b[1]) / 2 / S
        crop = img.subsurface((int(cx - 75), int(cy - 70), 150, 130)).copy()
        pygame.image.save(pygame.transform.smoothscale(crop, (600, 520)), "shots/hs_office_armchair_closeup.png")
        print("shots/hs_office_armchair_closeup.png")


if __name__ == "__main__":
    main()
