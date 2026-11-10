#!/usr/bin/env python3
"""Static isometric mock-up of the Anderson house Boot Room for 'Hide and Seek'.

3.5 m x 1.7 m = 6.4 x 3.1 tiles. Camera looks south-east-ish into the room:
  back wall y = 0  (side "N") = the house's outside wall: radiator + coats
                   under white brick (east end), panelling, long casement
                   window over the settle bench, wire basket, half-glazed
                   external door with cat flap (west end).
  back wall x = 0  (side "W") = east end: white brick, open white plank door
                   into the Kitchen (flagstones and the island beyond).
  near wall y = RD (side "S") = Study door and open pantry/utility doorway.
  near wall x = RW (side "E") = west end: sage plank door to the WC/garage.
Shared kit: house_common.py.

    python mock_boot_room.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(6.4, 3.1)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_boot_room_mock.png"
CLOSE = "shots/hs_boot_room_window_closeup.png"

SAGE_WALL = (180, 190, 178)
SAGE_DOOR = (138, 158, 150)
BRICK_WHITE = (232, 230, 222)
OLD_PINE = (156, 126, 92)

WINDOW = (1.6, 4.55, 104, 204)
EXT_DOOR = (4.95, 6.22)
KITCHEN_DOOR = (0.85, 2.3)              # on the x = 0 end wall
PANTRY = (2.15, 3.45)                   # near wall y = RD
STUDY = (4.4, 5.7)
BEAMS = (1.9, 4.05)                     # beam x positions (helmets hang off the first)
WC_DOOR = (0.9, 2.3)                    # near wall x = RW


# ------------------------------------------------------------- outside: the drive
def drive_side(side, rnd):
    """Beyond the outside wall: gravel drive, shrubs, a parked car, the
    neighbour's black weatherboard barn with its red tile roof. Placed for
    what this projection shows through the window (ground 2-4 tiles out)."""
    ext_gravel(side, -12, 16, 0, 14, rnd)
    ext_barn(side, -9, 1.2, 2.0, 5.0, h=62, roof=56)            # its wall and the foot of the roof show
    ext_car(side, 1.6, 9.5, 1.25, 4.3, col=(58, 78, 112), h=92, cabin=56)
    ext_paving(side, -12, 16, 0.0, 0.55, rnd, col=(150, 142, 130), slab=0.45)
    for u, t in ((-1.6, 1.0), (-0.6, 0.85), (0.4, 1.0)):
        ext_shrub(side, u, t, r=0.45, h=120, col=(76, 108, 60), rnd=random.Random(int(u * 10 + 50)))
    ext_house_shadow(side, -12, 16, depth=0.9)


def kitchen_side(side, rnd):
    """Beyond the kitchen door: slate floor, the island and the west-end run."""
    import glimpses
    glimpses.kitchen_from_boot()


# ---------------------------------------------------------------- furniture
def radiator(x0, x1):
    box(x0, 0, x1, 0.12, 12, 74, (238, 238, 234))
    u = x0 + .06
    while u < x1 - .04:
        qy(0.121, u, u + .012, 15, 71, (200, 200, 196))
        u += .07


def coats(x0, x1):
    """Dark coats on a peg rail over the radiator."""
    wall_quad("N", x0, x1, 190, 197, shade(OLD_PINE, KY * .8), .03)
    for (a, w, col, top, hem) in ((x0 + .05, .55, (36, 46, 74), 192, 96), (x0 + .5, .5, (30, 30, 34), 190, 104),
                                  (x0 + .82, .3, (214, 190, 50), 186, 128), (x0 + .9, .4, (52, 58, 64), 188, 112)):
        c = shade(col, KY)
        poly([wall_pt("N", a + w * .3, top, .1), wall_pt("N", a + w * .7, top, .1), wall_pt("N", a + w, hem, .16), wall_pt("N", a, hem, .16)], c, shade(c, .6))
        poly([wall_pt("N", a + w * .45, top - 4, .12), wall_pt("N", a + w * .55, top - 4, .12), wall_pt("N", a + w * .52, hem + 10, .17), wall_pt("N", a + w * .48, hem + 10, .17)], shade(c, .8))


def settle(x0, x1, d=0.72):
    """Wooden settle bench: sage ends, old pine seat, spindle back, shoe rack under."""
    rnd = random.Random(3)
    # shoes on the floor under it, then the rack shelf with more shoes
    shoe_cols = [(240, 240, 236), (40, 40, 44), (120, 70, 40), (70, 110, 150), (200, 60, 60), (150, 150, 150)]
    for i in range(7):
        sx = x0 + .2 + i * (x1 - x0 - .4) / 7
        box(sx, .18, sx + .22, .5, 0, 9, rnd.choice(shoe_cols), ol=False)
    box(x0 + .1, .1, x1 - .1, d - .08, 18, 21, shade(OLD_PINE, .9))
    for i in range(6):
        sx = x0 + .25 + i * (x1 - x0 - .5) / 6
        box(sx, .16, sx + .24, .46, 21, 30, rnd.choice(shoe_cols), ol=False)
    # spindle back against the wall
    box(x0, 0, x1, .06, 48, 52, SAGE_DOOR)
    u = x0 + .1
    while u < x1 - .05:
        box(u, .02, u + .03, .05, 52, 96, shade(SAGE_DOOR, 1.05), ol=False)
        u += .11
    box(x0, 0, x1, .07, 96, 104, SAGE_DOOR)
    # seat
    box(x0 + .06, .06, x1 - .06, d, 40, 48, OLD_PINE)
    for i in range(1, 3):
        line((x0 + .06, .06 + (d - .06) * i / 3, 48), (x1 - .06, .06 + (d - .06) * i / 3, 48), shade(OLD_PINE, .7), 1)
    # yellow bag on the seat
    box(x1 - .8, .2, x1 - .3, .55, 48, 58, (232, 200, 40))
    # sage end panels
    for ex in (x0, x1 - .1):
        box(ex, 0, ex + .1, d, 0, 74, SAGE_DOOR)
        qy(d + .002, ex + .02, ex + .08, 30, 60, shade(SAGE_DOOR, KY * .85))


def wire_basket(x0, x1, z0, z1, n=0.22):
    k = KY
    c = (34, 34, 36)
    for i in range(7):
        u = x0 + (x1 - x0) * i / 6
        pygame.draw.line(screen, c, wall_pt("N", u, z0, n), wall_pt("N", u, z1, n), max(1, S))
    for j in range(5):
        z = z0 + (z1 - z0) * j / 4
        pygame.draw.line(screen, c, wall_pt("N", x0, z, n), wall_pt("N", x1, z, n), max(1, S))
    for u in (x0, x1):
        pygame.draw.line(screen, c, wall_pt("N", u, z0, n), wall_pt("N", u, z0, 0), max(1, S))
    poly([wall_pt("N", x0, z0, 0.02), wall_pt("N", x1, z0, 0.02), wall_pt("N", x1, z0, n), wall_pt("N", x0, z0, n)], shade(c, 1.4))


def mat(x0, y0, x1, y1):
    """Cream mat with a blue diamond lattice."""
    z = 0.6
    qz(z, x0, y0, x1, y1, (226, 222, 210), (180, 176, 168))
    blue = (70, 88, 140)
    n = 9
    for i in range(-n, 2 * n):
        a = x0 + (x1 - x0) * i / n
        pts = []
        for s in (0, 1):
            pass
        # diagonal lines both ways, clipped by hand to the mat
        for sgn in (1, -1):
            p0 = (a, y0) if sgn == 1 else (a, y1)
            p1 = (a + (y1 - y0), y1) if sgn == 1 else (a + (y1 - y0), y0)
            # clip along the parametric line
            ts = [0.0, 1.0]
            dx = p1[0] - p0[0]
            if dx:
                for xb in (x0 + .06, x1 - .06):
                    tt = (xb - p0[0]) / dx
                    if 0 < tt < 1:
                        ts.append(tt)
            ts.sort()
            seg = None
            for k in range(len(ts) - 1):
                tm = (ts[k] + ts[k + 1]) / 2
                xm = p0[0] + dx * tm
                if x0 + .06 <= xm <= x1 - .06:
                    seg = (ts[k], ts[k + 1])
            if seg:
                A = (p0[0] + dx * seg[0], p0[1] + (p1[1] - p0[1]) * seg[0])
                B = (p0[0] + dx * seg[1], p0[1] + (p1[1] - p0[1]) * seg[1])
                if y0 + .05 <= A[1] <= y1 - .05 or True:
                    line((A[0], max(y0 + .06, min(y1 - .06, A[1])), z), (B[0], max(y0 + .06, min(y1 - .06, B[1])), z), blue, 2)
    for i in range(n):
        for j in range(4):
            cx = x0 + (x1 - x0) * (i + .5) / n
            cy = y0 + (y1 - y0) * (j + .5) / 4
            fl_ellipse(cx, cy, .035, .035, blue, z, n=8)
    qz(z, x0, y0, x1, y0 + .06, shade(blue, .9)); qz(z, x0, y1 - .06, x1, y1, shade(blue, .9))
    qz(z, x0, y0, x0 + .06, y1, shade(blue, .9)); qz(z, x1 - .06, y0, x1, y1, shade(blue, .9))


def kitchen_leaf(hinge_y, dx=1.25, dy=0.68):
    """The white plank kitchen door standing open into the boot room, hinged on the
    south jamb and swung back towards the camera (~40 degrees off edge-on), so the
    kitchen stays visible through the doorway."""
    hx, hy = 0.05, hinge_y
    L = math.hypot(dx, dy)
    Wf = lambda u, z: P(hx + dx * u / L, hy + dy * u / L, z)
    h = DOOR_H - 3
    col = (236, 234, 226)
    # leaf edge (thickness) at the free end, then the face
    ex, ey = hx + dx, hy + dy
    poly([P(ex, ey, 0), P(ex + .05, ey - .05, 0), P(ex + .05, ey - .05, h), P(ex, ey, h)], shade(col, KX * .9))
    draw_polys(plank_door_face(Wf, 0, L, h, col, (KY + KX) / 2 + .1, hinge="left", strap=True, latch=True))


def helmet(x, y, z, col):
    cx, cy = P(x, y, z)
    r = 15 * S
    pygame.draw.ellipse(screen, shade(col, .6), (cx - r, cy - r * .75, 2 * r, r * 1.5))
    pygame.draw.ellipse(screen, col, (cx - r * .92, cy - r * .78, 1.84 * r, r * 1.3))
    for i in (-1, 0, 1):    # vents
        pygame.draw.line(screen, shade(col, .5), (cx + i * r * .4, cy - r * .7), (cx + i * r * .5, cy - r * .1), 2 * S)
    pygame.draw.line(screen, (20, 20, 20), (cx - r * .6, cy + r * .4), (cx + r * .2, cy + r * 1.2), S)


def beam_ends():
    """The white ceiling beams, shown only as their ends bedded in the ghosted near wall
    (full-length beams smeared across the window in this view)."""
    polys = []
    c = (236, 234, 228)
    for x in BEAMS:
        a, b, y0 = x - .13, x + .13, RD - .3
        polys.append((shade(c, KT), [P(a, y0, WALL_H), P(b, y0, WALL_H), P(b, RD, WALL_H), P(a, RD, WALL_H)]))
        polys.append((shade(c, KY), [P(a, RD, WALL_H - 18), P(b, RD, WALL_H - 18), P(b, RD, WALL_H), P(a, RD, WALL_H)]))
        polys.append((shade(c, KX), [P(b, y0, WALL_H - 18), P(b, RD, WALL_H - 18), P(b, RD, WALL_H), P(b, y0, WALL_H)]))
    return polys


def main():
    background()
    floor_flagstones(seed=5)
    if not hc.FLIP:
        threshold("S", *PANTRY, TERRACOTTA, depth=0.6)
        threshold("S", *STUDY, TERRACOTTA, depth=0.6)
    mat(2.25, 1.15, 3.85, 2.25)
    wall_shell(SAGE_WALL)
    ext = exterior_layer({"N": drive_side}, haze=(196, 202, 206))
    kitchen = exterior_layer({"W": kitchen_side}, haze=(200, 204, 190))
    if not hc.FLIP:
        # back wall y = 0
        brick_wall("N", 0, 1.45, 0, WALL_H, BRICK_WHITE, seed=2)
        tongue_and_groove("N", 1.45, EXT_DOOR[0] - .14, 0, 94, SAGE_DOOR)
        brick_wall("N", EXT_DOOR[0] - .14, EXT_DOOR[0], 0, WALL_H, BRICK_WHITE, seed=3)
        casement_window("N", *WINDOW[:2], ext, z0=WINDOW[2], z1=WINDOW[3], cols=4, top_lights=True)
        glazed_door_back("N", *EXT_DOOR, ext, col=SAGE_DOOR)
        # back wall x = 0: white brick with the kitchen doorway
        brick_wall("W", 0, RD, 0, WALL_H, BRICK_WHITE, seed=4)
    doorway_back("W", *KITCHEN_DOOR, kitchen)
    wall_trim(cornice=False, skirting=False)
    radiator(0.15, 1.35)
    coats(0.2, 1.38)
    wire_basket(4.12, 4.5, 60, 98)
    settle(1.85, 4.05)
    kitchen_leaf(KITCHEN_DOOR[0])
    place_sprite("archie", 3.1, 1.75)
    for hx, hy, hz, hc_ in ((BEAMS[0] - .12, RD - .32, 172, (214, 150, 190)), (BEAMS[0] + .14, RD - .2, 160, (40, 46, 50))):
        pygame.draw.line(screen, (30, 30, 30), P(hx, hy, hz + 14), P(BEAMS[0], RD - .18, WALL_H - 18), S)
        helmet(hx, hy, hz, hc_)
    # near walls: Study door + pantry doorway (y = RD), WC/garage plank door (x = RW)
    WE = lambda u, z: P(RW + .08, u, z)
    wc = plank_door_face(WE, *WC_DOOR, DOOR_H, SAGE_DOOR, KX, hinge="right")
    ghost_near_walls(SAGE_WALL, doors_S=[PANTRY, STUDY], doors_E=[WC_DOOR], cornice=False,
                     extra_polys=list(wc) + beam_ends())
    img = finish("Hide and Seek - Boot Room (mock-up)", OUT)
    if ARGS:
        return
    # close-up of the window and the external door
    a = P(WINDOW[0] - .3, 0, WINDOW[3] + 20)
    b = P(EXT_DOOR[1] + .1, 0, -10)
    x0, y0 = int(a[0] / S) - 10, int(a[1] / S) - 10
    x1, y1 = int(b[0] / S) + 10, int(b[1] / S) + 10
    if x1 > x0 > 0 and y1 > y0 > 0 and x1 <= img.get_width() and y1 <= img.get_height():
        crop = img.subsurface((x0, y0, x1 - x0, y1 - y0)).copy()
        crop = pygame.transform.smoothscale(crop, (crop.get_width() * 3, crop.get_height() * 3))
        pygame.image.save(crop, CLOSE)
        print(CLOSE)


if __name__ == "__main__":
    main()
