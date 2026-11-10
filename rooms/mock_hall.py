#!/usr/bin/env python3
"""Static isometric mock-up of the ground-floor Hall for 'Hide and Seek', in the
house camera convention (looking plan-south-east).

On the plan (14'5 x 5'9 = 4.4 m N-S x 1.8 m E-W) the hall runs from the front
door ('IN', south) up to the kitchen (north), between the Drawing Room (west)
and the Sitting Room (east); the stairs are on the east side and rise north.
3.2 x 8.05 tiles (x west from the east wall, y north from the south wall):
  back-left  (x = 0)  = east wall: doorway into the Sitting Room near the
                        front-door end (matches the Sitting Room's hall door),
                        showing its blue-grey south wall and low bookcase beyond;
                        the staircase against it from 1.65 m north of the front
                        wall, bullnose bottom tread and turned mahogany newel at
                        the south end, rising north; white panelled string, white
                        square spindles, mahogany handrail, grey-beige carpet;
                        white tongue-and-groove under the high (north) end with
                        a ledged cupboard door (thumb latch) and a small hatch
                        (brass knob).
  back-right (y = 0)  = south wall: white six-panel front door with the arched
                        fanlight, black knob, brass letterbox and bolts; light switch.
  near-right (y = RD) = north wall, ghost: open doorway to the kitchen at the
                        west end, slate flagstones beyond.
  near-left  (x = RW) = west wall, ghost: Drawing Room door (six-panel, seen from
                        behind) near the south end, slatted radiator cover with
                        the big dark-framed mirror above (its back), and the
                        kitchen doorway's door folded back against the wall at
                        the north end.
Dark stained boards with a long Persian runner; pale lilac-grey walls. The
crystal chandelier is left out (ceiling lights that overlap things are).

    python mock_hall.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(3.2, 8.05)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_hall_mock.png"
CLOSE = "shots/hs_hall_door_closeup.png"

WALL = (196, 190, 204)        # pale lilac-grey
BOARD1, BOARD2 = (96, 62, 40), (78, 50, 32)
CARPET = (198, 188, 172)
MAHOGANY = (112, 48, 32)
BRASS = (200, 162, 70)
FRONT_DOOR = (1.0, 2.2)       # south wall
FRONT_H = 154                 # leaf height: keeps the whole fanlight arch below the cornice
SITTING_DOOR = (0.75, 1.8)    # east wall (the Sitting Room's HALL_DOOR, same y)
DRAWING_DOOR = (0.6, 1.85)    # west wall, ghost (the Drawing Room's east-wall door)
KITCHEN_DOOR = (1.9, 3.07)    # north wall, ghost
SW, Y0, NSTEP = 1.62, 3.0, 12  # stair width, bottom nosing, number of treads
RUN = (RD - .02 - Y0) / NSTEP
RISE = WALL_H / NSTEP


# ------------------------------------------------------------- beyond
def front_garden(side, rnd):
    ext_lawn(side, -6, 10, 0, 12, rnd)
    ext_hedge(side, -6, 10, 4.6, 5.3, h=92, rnd=rnd)
    ext_picket_fence(side, -6, 10, 3.6)
    ext_paving(side, -1.5, 1.5, 0.2, 6, rnd, col=(170, 160, 144), slab=0.5)
    ext_paving(side, -6, 10, 0.15, 1.15, rnd, col=(160, 152, 138))
    ext_house_shadow(side, -6, 10)


SR_WALL = (170, 184, 194)     # the Sitting Room's blue-grey (mock_sitting_room.WALL)
SR_WOOD = (84, 56, 38)        # its dark bookcase
SR_RW, SR_T = 7.1, 0.2        # Sitting Room width (tiles) and the party wall's thickness
SR = lambda xs: xs - SR_RW - SR_T   # Sitting Room x (west from its east wall) -> hall x; y is shared


def sitting_beyond(side, rnd):
    """Through the east doorway, in the Sitting Room's true geometry (same south
    wall and y as the hall): its pine boards, the blue-grey south wall with
    skirting, the low dark bookcase at its west end and the butterfly frames."""
    x_end = SR(0)
    for i in range(16):
        y0 = i * .27
        qz(0, x_end, y0, -SR_T, y0 + .26, shade(PINE1_, rnd.uniform(.72, .86)))
    qy(0, x_end, -SR_T, 0, WALL_H, shade(SR_WALL, KY))
    qy(0.001, x_end, -SR_T, 0, 13, shade(WHITE, KY))
    # butterflies (mock_sitting_room: x 5.62 / 6.28, 0.5 wide, z 126-170)
    for u0 in (5.62, 6.28):
        a, b = SR(u0), SR(u0 + .5)
        qy(.01, a, b, 126, 170, shade((26, 26, 28), KY))
        qy(.012, a + .05, b - .05, 129, 167, shade((236, 232, 222), KY))
        cu = (a + b) / 2
        for sgn in (-1, 1):
            for dz, r, col in ((5, 7, (60, 110, 170)), (-4, 5, (214, 120, 50))):
                x, y = P(cu + sgn * .085, .013, 148 + dz)
                pygame.draw.circle(hc.screen, shade(col, KY), (x, y), r * S)   # hc.screen: the glimpse layer
    # low dark-wood bookcase (mock_sitting_room.bookcase(5.4, 6.95), 0.55 deep, 92 high)
    x0, x1, d, h = SR(5.4), SR(6.95), .55, 92
    box(x0, 0, x1, d, 0, h, SR_WOOD, top=shade(SR_WOOD, 1.18))
    spines = [(160, 40, 40), (40, 70, 120), (220, 190, 70), (60, 110, 70), (200, 120, 60), (230, 220, 200), (110, 40, 60), (30, 30, 30)]
    r2 = random.Random(14)
    qy(d + .002, x0 + .05, x1 - .05, 6, h - 6, (40, 28, 20))
    for za, zb in ((8, 40), (46, 84)):
        u = x0 + .06
        while u < x1 - .08:
            bw = r2.uniform(.035, .07)
            qy(d + .004, u, min(x1 - .06, u + bw), za, zb - r2.uniform(0, 8), shade(r2.choice(spines), KY * r2.uniform(.85, 1.0)))
            u += bw + .004
        qy(d + .005, x0 + .05, x1 - .05, za - 3, za, shade(SR_WOOD, KY * 1.1))
    for j, (u, col) in enumerate(((x0 + .8, (120, 180, 200)), (x0 + 1.05, (200, 140, 180)), (x0 + 1.25, (160, 200, 150)))):
        cyl(u, .28, .05, h, h + 14 + 6 * j, col, top=shade(col, 1.2))
    # the doorway's south reveal through the party wall
    a = SITTING_DOOR[0]
    qy(a, -SR_T, 0, 0, DOOR_H, shade(WALL, KY * .92))
    qz(0.5, -SR_T, a, 0, SITTING_DOOR[1], (150, 120, 84))     # threshold strip


# ------------------------------------------------------------- floor
def boards():
    import paint
    paint.stamp(paint.timber(RW, RD, 14, BOARD1, BOARD2, along="y", plank=0.27), 0, 0, RW, RD, 0)
    floor_slab(BOARD2)


def runner(x0, x1, y0, y1):
    """Long Persian runner: cream border, deep red field, navy and green medallions."""
    import paint
    paint.stamp(paint.rug(x1 - x0, y1 - y0, "hall", seed=4), x0, y0, x1, y1, 0.6)


# ------------------------------------------------------------- walls
def front_door(ext):
    a, b = FRONT_DOOR
    k = KY
    W = lambda u, z, n=.01: wall_pt("N", u, z, n)
    H = FRONT_H
    uc, ru, rz = (a + b) / 2, (b - a) / 2, 27
    arch = lambda f, n=.01: [W(uc + ru * f * math.cos(t), H + 6 + rz * f * math.sin(t), n) for t in [i * math.pi / 20 for i in range(21)]]
    poly(arch(1.18, .005), shade(WHITE, k))                                  # architrave round the fanlight
    architrave("N", a, b, H + 6, WHITE)
    show_through(ext, arch(1.0))
    for i in range(1, 6):                                                    # radial glazing bars
        t = i * math.pi / 6
        pygame.draw.line(screen, shade(WHITE, k), W(uc, H + 6), W(uc + ru * math.cos(t), H + 6 + rz * math.sin(t)), 2 * S)
    poly(arch(.25), shade(WHITE, k))
    wall_quad("N", a, b, H, H + 6, shade(WHITE, k))                         # transom
    # six-panel door leaf
    wall_quad("N", a, b, 0, H, shade((244, 242, 236), k), .012)
    cols = ((a + .1, uc - .05), (uc + .05, b - .1))
    for za, zb in ((10, 56), (64, 124), (132, H - 8)):
        for p, q in cols:
            wall_quad("N", p, q, za, zb, shade((244, 242, 236), k * .86), .014)
            wall_quad("N", p + .03, q - .03, za + 3, zb - 3, shade((244, 242, 236), k * 1.02), .016)
    x, y = W(uc, 82, .03)
    pygame.draw.circle(screen, (24, 24, 26), (x, y), 5 * S)                   # black knob
    wall_quad("N", uc - .2, uc + .2, 60, 66, BRASS, .02)                       # letterbox
    for zz in (24, 140):                                                     # brass bolts
        wall_quad("N", b - .2, b - .14, zz, zz + 14, BRASS, .02)
    wall_quad("N", b + .2, b + .32, 104, 116, shade(WHITE, k * 1.05), .01)   # light switch
    wall_quad("N", b + .24, b + .28, 107, 113, shade(WHITE, k * .8), .012)


# ------------------------------------------------------------- stairs
def tread_z(i):
    return (i + 1) * RISE


def stairs():
    """Straight flight against the east wall, bottom at y = Y0 rising north."""
    white = (240, 238, 232)
    # treads, bottom to top: each step's carpeted top runs back to the north wall,
    # so the next one up hides what it really would
    for i in range(NSTEP):
        y = Y0 + i * RUN
        z = tread_z(i)
        qz(z, 0, y, SW, RD - .01, shade(CARPET, KT * (1.0 if i % 2 else .96)))
        line((0, y, z), (SW, y, z), shade(CARPET, .72), 1)                # nosing
        if i == 0:
            cyl(SW, y + RUN / 2, RUN / 2, 0, z, white, top=shade(CARPET, KT))   # bullnose end
    # west side of the flight, up to the top of the closed string
    side = [P(SW, Y0, 0), P(SW, Y0, tread_z(0))]
    for i in range(1, NSTEP):
        y = Y0 + i * RUN
        side += [P(SW, y, (y - Y0) / RUN * RISE + RISE + 6)]
    side += [P(SW, RD - .01, WALL_H + 6), P(SW, RD - .01, 0)]
    poly(side, shade(white, KX))
    # side face below the flight: tongue-and-groove at the high end, cupboard door, hatch
    y = 5.0
    while y < RD - .05:
        zt = min((y - Y0) / RUN * RISE + RISE - 16, WALL_H)
        line((SW + .001, y, 3), (SW + .001, y, zt), shade(white, KX * .78), 1)
        y += .2
    Wf = lambda u, z: P(SW + .004, u, z)
    draw_polys(plank_door_face(Wf, 6.3, 7.25, 140, white, KX * 1.02, hinge="left", strap=False, latch=True))
    qx(SW + .004, 5.15, 5.75, 12, 64, shade(white, KX * .95), shade(white, .6))
    x, yy = P(SW + .006, 5.3, 38)
    pygame.draw.circle(screen, BRASS, (x, yy), 3 * S)
    # closed string, white and panelled, along the slope
    st = lambda y, dz: P(SW + .006, y, (y - Y0) / RUN * RISE + RISE + dz)
    poly([st(Y0 + RUN, 6), st(RD, 6), st(RD, -14), st(Y0 + RUN, -14)], shade(white, KX * 1.06))
    poly([st(Y0 + RUN + .2, 2), st(RD - .2, 2), st(RD - .2, -10), st(Y0 + RUN + .2, -10)], shade(white, KX * .92))
    poly([st(Y0 + RUN + .23, 0), st(RD - .23, 0), st(RD - .23, -8), st(Y0 + RUN + .23, -8)], shade(white, KX * 1.0))
    # each tread is its own occluder so a person at the foot isn't hidden by the landing
    for i in range(NSTEP):
        y = Y0 + i * RUN
        occlude(0, y, SW, min(RD - .01, y + RUN), 0, tread_z(i))


def balustrade():
    hx = SW - .04
    hz = lambda y: (y - Y0) / RUN * RISE + RISE + 84
    # spindles: two per tread, from the string top to the handrail
    y = Y0 + RUN + .1
    while y < RD - .1:
        z0 = (y - Y0) / RUN * RISE + RISE + 6
        qx(hx + .02, y - .015, y + .015, z0, hz(y) - 3, shade((246, 246, 242), KX * 1.05))
        y += RUN / 2
    # newel on the bullnose, then the handrail
    nx, ny = SW, Y0 + RUN / 2
    z = tread_z(0)
    box(nx - .07, ny - .07, nx + .07, ny + .07, z, z + 34, MAHOGANY, top=shade(MAHOGANY, 1.2))
    cyl(nx, ny, .05, z + 34, z + 86, MAHOGANY)
    cyl(nx, ny, .08, z + 86, z + 96, MAHOGANY, top=shade(MAHOGANY, 1.25))
    cyl(nx, ny, .06, z + 96, z + 108, MAHOGANY, top=shade(MAHOGANY, 1.3))
    pygame.draw.line(screen, MAHOGANY, P(nx, ny + .05, z + 92), P(hx + .02, RD, hz(RD)), int(5 * S))
    pygame.draw.line(screen, shade(MAHOGANY, 1.35), P(nx, ny + .05, z + 95), P(hx + .02, RD, hz(RD) + 3), int(1.5 * S))


# ------------------------------------------------------------- near walls
def kitchen_glimpse():
    """The kitchen is drawn into the doorway itself (see ghost_near_walls openings)."""


def west_wall_hung():
    """Faint: radiator cover, the mirror's back, the kitchen door folded back."""
    with hung_layer(alpha=120):
        c = (242, 242, 238)
        box(RW - .38, 2.5, RW - .02, 4.2, 0, 88, c, top=shade(c, 1.02))
        for i in range(14):
            yy = 2.6 + i * .11
            qx(RW - .379, yy, yy + .04, 10, 76, shade(c, KX * .78))
        box(RW - .1, 2.65, RW - .03, 4.05, 112, 206, (34, 32, 34), ol=False)   # mirror, from behind
        a, b = KITCHEN_DOOR
        L = b - a
        box(RW - .1, RD - L - .02, RW - .04, RD - .05, 0, DOOR_H - 3, (240, 238, 232))


def drawing_door_polys():
    """The Drawing Room door, closed, its hall face seen from behind: six panels."""
    a, b = DRAWING_DOOR
    WE = lambda u, z: P(RW + .1, u, z)
    c = shade((244, 242, 236), KX)
    out = [(c, [WE(a, 0), WE(b, 0), WE(b, DOOR_H), WE(a, DOOR_H)])]
    m = (a + b) / 2
    for za, zb in ((10, 66), (76, 150), (158, DOOR_H - 8)):
        for p, q in ((a + .1, m - .05), (m + .05, b - .1)):
            out.append((shade(c, .86), [WE(p, za), WE(q, za), WE(q, zb), WE(p, zb)]))
    for zz in (20, DOOR_H - 30):                               # brass hinges at the south edge
        out.append((BRASS, [WE(a + .01, zz), WE(a + .06, zz), WE(a + .06, zz + 12), WE(a + .01, zz + 12)]))
    return out


def main():
    background()
    boards()
    runner(1.72, 2.92, .45, RD - .3)
    kitchen_glimpse()
    wall_shell(WALL)
    front = exterior_layer({"N": front_garden}, haze=(170, 180, 186))
    sitting = exterior_layer({"W": sitting_beyond}, haze=shade(SR_WALL, .8))
    front_door(front)
    doorway_back("W", *SITTING_DOOR, sitting)
    wall_trim()
    stairs()
    balustrade()
    import paint
    paint.chandelier(1.55, 2.05, 248)
    place_sprite("archie", 2.05, 4.9)
    west_wall_hung()
    ghost_near_walls(WALL, doors_S=[KITCHEN_DOOR], doors_E=[DRAWING_DOOR], extra_polys=drawing_door_polys())
    img = finish("Hide and Seek - Hall (mock-up)", OUT)
    if not ARGS:      # close-up of the front door and the Sitting Room doorway
        pts = [P(0, SITTING_DOOR[1] + .35, 0), P(0, SITTING_DOOR[1] + .35, WALL_H + 8), P(FRONT_DOOR[1] + .5, 0, WALL_H + 8),
               P(FRONT_DOOR[1] + .5, 0, 0), P(FRONT_DOOR[1] + .5, SITTING_DOOR[1] + .2, 0)]
        x0, x1 = int(min(p[0] for p in pts) / S) - 8, int(max(p[0] for p in pts) / S) + 8
        y0, y1 = int(min(p[1] for p in pts) / S) - 8, int(max(p[1] for p in pts) / S) + 8
        crop = img.subsurface(pygame.Rect(x0, y0, x1 - x0, y1 - y0)).copy()
        crop = pygame.transform.smoothscale(crop, (crop.get_width() * 2, crop.get_height() * 2))
        pygame.image.save(crop, CLOSE)
        print(CLOSE)


if __name__ == "__main__":
    main()
