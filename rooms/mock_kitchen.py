#!/usr/bin/env python3
"""Static isometric mock-up of the KITCHEN HALF of the Anderson house
Kitchen + Dining Room for 'Hide and Seek', in the house-wide camera
convention (house_common.HOUSE_CAMERA: looking plan-south-east).

The open-plan room is KD_LEN x KD_DEP world tiles (10.2 m x 5.2 m); this
view is world x KD_SPLIT .. KD_LEN (local x = world x - KD_SPLIT):
  back-left  (x = 0)  = OPEN: the beam; beyond it the granite peninsula on
                        white cupboards, its folding chairs, the north-south
                        pine table and the dresser recede, faded.
  back-right (y = 0)  = south wall: hall door, wine fridge under an oak
                        counter with two shelves, larder fridge + larder
                        freezer side by side, doorway to the Drawing Room -
                        all facing into the room (visible).
  near-right (y = RD) = north/garden wall, ghost: the run of units (fronts
                        face away, so only tops and backs show), two windows
                        as faint frames.
  near-left  (x = RW) = west wall, ghost: Boot Room doorway frame, cupboards
                        above it, the sage cupboard as a faint frame.
Everything stands where it really is; anything facing away stays unseen.

    python mock_kitchen.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(hc.KD_LEN - hc.KD_SPLIT, hc.KD_DEP, ox=700)
from house_common import *  # noqa: E402,F401,F403
import kd_furniture as F  # noqa: E402

X0 = KD_VIEWS["kitchen"]                # world x of this view's local x = 0 (the beam)

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_kitchen_mock_v3.png"
COPIES = () if ARGS else ("shots/hs_kitchen_mock.png",)

# view-local positions of the openings (world positions live in kd_furniture)
L = lambda ab: (ab[0] - X0, ab[1] - X0)
WIN2, WIN1 = L(F.K_WIN2), L(F.K_WIN1)  # garden wall (near-right ghost)
HALL_DOOR = L(F.K_HALL_DOOR)           # south wall (back-right)
DRAWING_DOOR = L(F.K_DRAWING_DOOR)     # the Drawing Room's door (its north wall, west end)
BOOT_DOOR = F.K_BOOT_DOOR              # west wall (near-left ghost), y range
SAGE_CUPBOARD = F.K_SAGE


# ------------------------------------------------------------- rooms seen through doorways
def hall_beyond(side, rnd):
    """The stair hall through the hall door, in the hall's own tiles."""
    import glimpses
    glimpses.hall_from_kitchen()


def drawing_room_beyond(side, rnd):
    """The snug through its door: green walls, boards, the red rug."""
    import glimpses
    glimpses.drawing_from_kitchen()


def beam_polys():
    c = (238, 236, 230)
    a, b, z0 = -.16, .16, WALL_H - 20
    return [(shade(c, KT), [P(a, 0, WALL_H), P(b, 0, WALL_H), P(b, RD, WALL_H), P(a, RD, WALL_H)]),
            (shade(c, KY), [P(a, RD, z0), P(b, RD, z0), P(b, RD, WALL_H), P(a, RD, WALL_H)]),
            (shade(c, KX), [P(b, 0, z0), P(b, RD, z0), P(b, RD, WALL_H), P(b, 0, WALL_H)])]


def near_wall_extras():
    """Things in the ghost walls themselves: the sage cupboard's frame (its doors face away)."""
    c = (150, 176, 164)
    a, b = SAGE_CUPBOARD
    WE = lambda u, z: P(RW + .1, u, z)
    out = []
    for u0, u1, z0, z1 in ((a - .06, a, 0, 156), (b, b + .06, 0, 156), (a - .06, b + .06, 150, 156), ((a + b) / 2 - .01, (a + b) / 2 + .01, 0, 150)):
        out.append((shade(c, KX), [WE(u0, z0), WE(u1, z0), WE(u1, z1), WE(u0, z1)]))
    return out + beam_polys()




# ------------------------------------------------------------- the dining half, beyond the beam
GL = 8.2                               # the whole dining half is drawn, fading out


def dining_back():
    floor_slate(-GL, 0, 0, RD, seed=21)
    floor_edge_S(-GL, 0, SLATE[1])
    qy(0, -GL, 0, 0, WALL_H, shade(OFF_WHITE, KY))
    qy(.001, -GL, 0, 0, 13, shade(WHITE, KY))
    poly([P(-GL, 0, WALL_H), P(0, 0, WALL_H), P(0, -.28, WALL_H), P(-GL, -.28, WALL_H)], (60, 58, 54))


def dining_front():
    with world(X0):            # (the dresser on the far south wall is left out: it would sit under the caption)
        F.round_rug((F.D_FRENCH[0] + F.D_FRENCH[1]) / 2, 7.5)
        F.dining_table_set()
        F.peninsula_chairs()
        F.peninsula()


def main():
    background()
    floor_slate(seed=8)
    floor_slab(SLATE[1])
    back = glimpse_layer()
    with drawing_on(back):
        dining_back()
    screen.blit(fade_x(back, -1.0, -6.5), (0, 0))
    wall_shell(OFF_WHITE, open_W=True)
    hall = exterior_layer({"N": hall_beyond}, haze=(226, 222, 212))
    drawing = exterior_layer({"N": drawing_room_beyond}, haze=shade(GREEN, KY))
    doorway_back("N", *HALL_DOOR, hall)
    doorway_back("N", *DRAWING_DOOR, drawing)
    wall_trim(cornice=False, col=WHITE, open_W=True)
    front = glimpse_layer()
    with drawing_on(front):
        dining_front()
    screen.blit(fade_x(front, -1.4, -7.0, z_ref=70), (0, 0))
    with world(X0):
        F.kitchen_south_wall()
        F.kitchen_island_and_stools()
    place_sprite("archie", 6.7, 2.7)
    hung = glimpse_layer()                 # wall-hung on the ghost walls: faint, like the walls
    with drawing_on(hung), world(X0):
        box(KD_LEN - .55, 0, KD_LEN, BOOT_DOOR[1] + .2, DOOR_H + 8, WALL_H, F.CAB)
    hung.set_alpha(96)
    screen.blit(hung, (0, 0))
    with world(X0):
        F.kitchen_run_floor()
    hung = glimpse_layer()
    with drawing_on(hung), world(X0):
        F.kitchen_run_hung()
    hung.set_alpha(96)
    screen.blit(hung, (0, 0))
    import glimpses
    ghost_near_walls(OFF_WHITE, doors_E=[BOOT_DOOR], windows_S=[WIN2, WIN1], window_z=(112, 208), window_cols=2,
                     cornice=False, curtains=None, open_W=True, extra_polys=near_wall_extras(),
                     openings=[("E", *BOOT_DOOR, glimpses.boot_from_kitchen, (150, 142, 128))])
    finish("Hide and Seek - Kitchen (mock-up)", OUT, subtitle="Ground Floor - kitchen half of the Kitchen + Dining Room", copies=COPIES)


if __name__ == "__main__":
    main()
