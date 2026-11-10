#!/usr/bin/env python3
"""Static isometric mock-up of the first-floor Upstairs Corridor.

A narrow east-west passage north of the Landing (11.4 x 2.2 tiles). South
wall: arched opening back to the landing (aligned with the landing's north
arch) and a recessed niche. East wall: open doorway into the bathroom (blue
glimpse). North wall: two doorways opposite a shared lobby — Archie's Room
(the 11'8 x 11'4 bedroom, nearest the arch) and the north-east
bedroom. The dressing room and north-west bathroom do not open
onto this corridor. West end: a dead-end with a grey clothes basket (fabric bag on a
metal frame). Pale oak laminate, light grey walls, white skirting, a
radiator. The loft hatch is left out (no ceiling in the cut-away view).
"""
import math
import random
import sys

import house_common as hc
hc.init_room(11.4, 2.2)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_corridor_mock.png"

WALL = (188, 190, 192)
OAK1, OAK2 = (198, 164, 104), (176, 140, 82)
WHITE_ = (244, 242, 236)
STEEL = (140, 144, 148)
FABRIC = (158, 160, 164)

# south wall: arch back to the landing (matches landing ARCH 0.35-2.85 -> x 2.90-5.40)
ARCH = (2.90, 5.40)
# east wall: bathroom
BATH_DOOR = (0.35, 1.85)
# north wall: only two doors, facing a small lobby just west of the bathroom
# (floorplan). East of the pair is the bathroom at the corridor's end.
ARCHIE_DOOR = (1.85, 3.27)   # Archie's Room (11'8 x 11'4), east end of its south wall
NE_BED = (0.20, 1.55)        # NE bedroom (11'6 x 11'4), SW corner onto the same lobby


def oak_floor():
    import paint
    paint.stamp(paint.timber(RW, RD, 9, OAK1, OAK2, along="x", plank=0.24), 0, 0, RW, RD, 0)


def niche(u0, u1):
    """Recessed arch niche in the south (far) wall."""
    if hc.FLIP:
        return
    z0, z1 = 28, 150
    qy(0.10, u0, u1, z0, z1, shade(WALL, KY * 0.78))
    mid = (u0 + u1) / 2
    qy(0.11, u0 + 0.08, u1 - 0.08, z1 - 22, z1, shade(WALL, KY * 0.7))
    qy(0.12, mid - 0.16, mid + 0.16, z1 - 8, z1 + 6, shade(WALL, KY * 0.66))
    qy(0.02, u0 - 0.05, u0, 20, z1 + 4, shade(WHITE_, KY))
    qy(0.02, u1, u1 + 0.05, 20, z1 + 4, shade(WHITE_, KY))
    qy(0.02, u0 - 0.05, u1 + 0.05, z1, z1 + 8, shade(WHITE_, KY))


def radiator(x0, x1, y=0.14):
    box(x0, y, x1, y + 0.20, 8, 50, WHITE_, top=shade(WHITE_, 1.04))
    for i in range(6):
        xx = x0 + 0.05 + i * (x1 - x0 - 0.08) / 5
        qy(y + 0.20, xx, xx + 0.03, 12, 46, shade(WHITE_, KY * 0.9))


def clothes_basket(cx, cy):
    """Fabric laundry basket on a metal frame, at the west dead end."""
    for dx, dy in ((-0.22, -0.16), (0.18, -0.16), (-0.22, 0.14), (0.18, 0.14)):
        box(cx + dx, cy + dy, cx + dx + 0.045, cy + dy + 0.045, 0, 40, STEEL)
    # fabric bag
    box(cx - 0.30, cy - 0.24, cx + 0.30, cy + 0.24, 36, 68, FABRIC, top=shade(FABRIC, 1.08))
    # metal rim
    box(cx - 0.32, cy - 0.26, cx + 0.32, cy + 0.26, 66, 74, shade(STEEL, 1.05), top=shade(STEEL, 1.15))
    # open top, darker lining
    qz(74.4, cx - 0.22, cy - 0.16, cx + 0.22, cy + 0.16, (96, 98, 102))
    # a hint of folded linen
    box(cx - 0.12, cy - 0.08, cx + 0.14, cy + 0.1, 74.5, 80, (232, 230, 224), ol=False)


def main():
    background()
    oak_floor()
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        back_opening("N", *ARCH, glimpses.landing_from_corridor, h=DOOR_H + 16)
        # a simple arched head over the landing opening
        mid = (ARCH[0] + ARCH[1]) / 2
        qy(0.03, ARCH[0] + 0.15, ARCH[1] - 0.15, DOOR_H + 4, DOOR_H + 22, shade(WALL, KY))
        qy(0.035, mid - 0.35, mid + 0.35, DOOR_H + 16, DOOR_H + 28, shade(WALL, KY * 0.92))
        back_opening("W", *BATH_DOOR, glimpses.bathroom_from_corridor)
        niche(7.15, 8.05)
        radiator(6.15, 7.05)
    wall_trim()
    clothes_basket(RW - 0.48, RD * 0.52)
    place_sprite("archie", 4.2, 1.1)
    ghost_near_walls(WALL,
                     doors_S=[ARCHIE_DOOR, NE_BED],
                     doors_E=[])
    finish("Hide and Seek - Upstairs Corridor (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_corridor_mock.png",))


if __name__ == "__main__":
    main()
