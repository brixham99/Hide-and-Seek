#!/usr/bin/env python3
"""Static isometric mock-up of the DINING HALF of the Anderson house
Kitchen + Dining Room for 'Hide and Seek', in the house-wide camera
convention (house_common.HOUSE_CAMERA: looking plan-south-east).

This view is world x 0 .. KD_SPLIT (local x = world x; furniture lives in
kd_furniture, shared with the kitchen view):
  back-left  (x = 0)  = east wall: sash window with cream curtains over a
                        radiator cover; chest of drawers, mirror, green lamp,
                        plants. The side garden shows through the sash.
  back-right (y = 0)  = south wall: grey-white dresser, bread maker, the pier
                        (its poster and radiator face east, unseen).
  near-right (y = RD) = garden wall, ghost: the French doors as a faint frame
                        with glazing and curtains; round rug in front.
  near-left  (x = RW) = OPEN: the beam; the kitchen comes nearer beyond it, faded.
Middle: the north-south pine table with ladder-back chairs, and the granite
peninsula on white cupboards (doors on the kitchen side) with its iMac and
folding chairs, at the split.

    python mock_dining.py [out.png]
"""
import random
import sys

import house_common as hc
hc.init_room(hc.KD_SPLIT, hc.KD_DEP, ox=570)
from house_common import *  # noqa: E402,F401,F403
import kd_furniture as F  # noqa: E402

X0 = KD_VIEWS["dining"]                 # 0: local x = world x
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_dining_mock.png"
GL = 3.8                                # how much of the kitchen is drawn beyond the open side


def side_garden(side, rnd):
    """Beyond the east wall: a paved path, lawn and the tall hedge."""
    ext_tree(side, 6.0, 5.2, trunk=150, canopy=200, r=1.4, rnd=random.Random(7))
    ext_lawn(side, -10, 20, 0.8, 9, rnd)
    ext_hedge(side, -10, 20, 3.6, 4.4, h=130, col=(36, 102, 42), rnd=random.Random(8))
    ext_picket_fence(side, -10, 20, 2.9)
    ext_border(side, -10, 20, 1.7, 2.15, rnd)
    ext_paving(side, -10, 20, 0.15, 1.55, rnd, col=(170, 160, 142), slab=0.5)
    ext_house_shadow(side, -10, 20, depth=1.0)


def kitchen_back():
    """The kitchen's floor and south wall carrying on past the beam (with the hall door, open)."""
    floor_slate(RW, 0, RW + GL, RD, seed=8)
    floor_edge_S(RW, RW + GL, SLATE[1])
    qy(0, RW, RW + GL, 0, WALL_H, shade(OFF_WHITE, KY))
    qy(.001, RW, RW + GL, 0, 13, shade(WHITE, KY))
    a, b = F.K_HALL_DOOR
    qy(.002, a, b, 0, DOOR_H, shade((150, 112, 74), KY * .8))          # the hall beyond
    qy(.003, a + .05, a + .12, 0, DOOR_H - 3, shade((238, 236, 230), KY))   # the open leaf, edge-on
    architrave("N", a, b, DOOR_H)
    poly([P(RW, 0, WALL_H), P(RW + GL, 0, WALL_H), P(RW + GL, -.28, WALL_H), P(RW, -.28, WALL_H)], (60, 58, 54))


def kitchen_front():
    F.kitchen_south_wall()
    F.kitchen_island_and_stools()
    F.kitchen_run_floor()


def beam_polys():
    if hc.FLIP:
        return []
    c = (238, 236, 230)
    a, b, z0 = RW - .16, RW + .16, WALL_H - 20
    return [(shade(c, KT), [P(a, 0, WALL_H), P(b, 0, WALL_H), P(b, RD, WALL_H), P(a, RD, WALL_H)]),
            (shade(c, KY), [P(a, RD, z0), P(b, RD, z0), P(b, RD, WALL_H), P(a, RD, WALL_H)]),
            (shade(c, KX), [P(b, 0, z0), P(b, RD, z0), P(b, RD, WALL_H), P(b, 0, WALL_H)])]


def french_door_polys():
    """Glazing bars and cream curtains of the French doors, faint in the ghost garden wall."""
    a, b = F.D_FRENCH
    t = .1
    W = lambda u, z, n=0: P(u, RD + t + n, z)
    c = shade(WHITE, KY)
    out = []
    m = (a + b) / 2
    for u0, u1 in ((a + .05, m - .02), (m + .02, b - .05)):
        for i in range(3):
            uu = u0 + (u1 - u0) * i / 2
            out.append((c, [W(uu - .015, 30), W(uu + .015, 30), W(uu + .015, DOOR_H - 8), W(uu - .015, DOOR_H - 8)]))
        for k in range(6):
            zz = 30 + (DOOR_H - 38) * k / 5
            out.append((c, [W(u0, zz - 1.5), W(u1, zz - 1.5), W(u1, zz + 1.5), W(u0, zz + 1.5)]))
        out.append((c, [W(u0, 0), W(u1, 0), W(u1, 30), W(u0, 30)]))
    cur = (226, 218, 196)
    for ca, cb in ((a - .55, a - .05), (b + .05, b + .55)):
        for f in range(5):
            fa, fb = ca + (cb - ca) * f / 5, ca + (cb - ca) * (f + 1) / 5
            out.append((shade(cur, .86 + .16 * (f % 2)), [W(fa, 10, .03), W(fb, 10, .03), W(fb, 214, .03), W(fa, 214, .03)]))
    out.append(((120, 110, 96), [W(a - .65, 214, .04), W(b + .65, 214, .04), W(b + .65, 219, .04), W(a - .65, 219, .04)]))
    return out


def main():
    background()
    floor_slate(0, 0, RW, RD, seed=21)
    floor_edge_S(0, RW, SLATE[1])
    back = glimpse_layer()
    with drawing_on(back), world(X0):
        kitchen_back()
    screen.blit(fade_x(back, RW + .4, RW + 3.4), (0, 0))
    wall_shell(OFF_WHITE)
    wall_trim(cornice=False, col=WHITE, open_E=True)
    ext = exterior_layer({"W": side_garden}, haze=(150, 172, 190))
    with world(X0):
        F.dining_east_wall_items(ext)
        F.dining_south_wall()
        F.round_rug((F.D_FRENCH[0] + F.D_FRENCH[1]) / 2, 7.5)
        F.dining_table_set()
        F.peninsula_chairs()
        F.peninsula()
    place_sprite("archie", 5.3, 3.0)
    front = glimpse_layer()
    with drawing_on(front), world(X0):
        kitchen_front()
    screen.blit(fade_x(front, RW + .3, RW + 3.6, z_ref=70), (0, 0))
    if hc.FLIP:
        ghost_near_walls(OFF_WHITE, doors_S=(), cornice=False, open_E=True,
                         extra_polys=beam_polys())
        def garden(side, rnd):
            ext_lawn(side, -4, RW + 6, 0.15, 6.5, rnd)
            ext_paving(side, -4, RW + 6, 0.2, 1.15, rnd)
            ext_border(side, -4, RW + 6, 1.2, 1.7, rnd)
            ext_picket_fence(side, -4, RW + 6, 2.05, h=40)
            ext_hedge(side, -4, RW + 6, 3.05, 3.65, h=100, rnd=rnd)
        ext_n = exterior_layer({"S": garden}, haze=(156, 190, 216))
        glazed_doors_on_S(*F.D_FRENCH, ext_n)
    else:
        ghost_near_walls(OFF_WHITE, doors_S=[F.D_FRENCH], cornice=False, open_E=True,
                         extra_polys=french_door_polys() + beam_polys())
    finish("Hide and Seek - Dining Room (mock-up)", OUT, subtitle="Ground Floor - dining half of the Kitchen + Dining Room")


if __name__ == "__main__":
    main()
