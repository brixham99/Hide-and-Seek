#!/usr/bin/env python3
"""Static isometric mock-up of the Utility (plan: UTILITY 3.2 m x 2.0 m) for
'Hide and Seek', in the house camera convention (looking plan-south-east).

On the plan it sits at the back of the house between the Study (west) and the
Kitchen (east), above the Boot Room. Room 2.0 m E-W x 3.2 m N-S = 3.6 x 5.8
tiles (x west from the east wall, y north from the south wall):
  back-left  (x = 0)  = east wall (to the kitchen), north -> south: tall white
                        cupboard in the north-east corner; wooden worktop over
                        the second washing machine and a grey low two-door
                        cupboard; white shelves above with storage boxes and
                        the cat carrier on top; the rope-hung clothes rail
                        further south.
  back-right (y = 0)  = south wall (to the Boot Room): the grey-green ledged
                        door, open into the utility.
  near-right (y = RD) = north wall, ghost: small casement window (faint frame)
                        over the belfast sink in the north-west corner; a short
                        worktop east of it over the first washing machine (its
                        door faces away).
  near-left  (x = RW) = west wall (to the study), ghost: coats on hooks near the
                        south end with the wicker basket below; the ironing
                        board hanger higher up near the north end (faint).

    python mock_utility.py [out.png]
"""
import math
import random
import sys

import house_common as hc
hc.init_room(3.6, 5.8)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_utility_mock.png"

DOOR = (2.3, 3.45)            # south wall, west side: the Boot Room's pantry/utility doorway
WINDOW = (2.55, 3.45)         # north wall, ghost, over the sink in the north-west corner
DOOR_COL = (128, 146, 136)    # grey-green
WOOD = (176, 128, 80)
CH = 90


def boot_room_beyond(side, rnd):
    floor_flagstones(x0=-2, y0=-4, x1=7, y1=0, seed=5)


def door_leaf():
    """Ledged door hinged at its east jamb, swung into the utility (+y)."""
    a, b = DOOR
    Wf = lambda u, z: P(a + .04, u - a, z)
    box(a, 0, a + .06, b - a, 0, DOOR_H - 3, DOOR_COL, faces="xz")
    draw_polys(plank_door_face(Wf, a, b, DOOR_H - 3, DOOR_COL, KX, hinge="left"))


def washer(y0, y1, x1=.95):
    """White front-loader under the worktop, door facing west into the room (+x)."""
    box(.02, y0, x1 - .04, y1, 4, CH - 6, (244, 244, 242))
    cy, cz = (y0 + y1) / 2, 40
    ring = [P(x1 - .039, cy + .27 * math.cos(t), cz + 17 * math.sin(t)) for t in [i * math.pi / 12 for i in range(24)]]
    poly(ring, (190, 194, 198))
    ring = [P(x1 - .035, cy + .2 * math.cos(t), cz + 12.5 * math.sin(t)) for t in [i * math.pi / 12 for i in range(24)]]
    poly(ring, (70, 82, 96))
    qx(x1 - .039, y0 + .06, y1 - .06, CH - 22, CH - 12, (220, 222, 224))


def east_run(y0, y1, d=1.0):
    """East wall, north -> south under one worktop: the second washing machine,
    then the grey low two-door cupboard; white shelves above."""
    grey = (130, 134, 136)
    washer(y1 - 1.02, y1 - .02)
    box(0, y0, d - .04, y1 - 1.06, 4, CH - 6, grey)
    m = (y0 + y1 - 1.06) / 2
    for a, b in ((y0 + .05, m - .02), (m + .02, y1 - 1.1)):
        qx(d - .039, a, b, 10, CH - 12, shade(grey, KX * 1.04))
    for yy in (m - .07, m + .04):
        qx(d - .037, yy, yy + .03, 60, 66, (60, 60, 64))
    box(0, y0, d, y1, CH - 6, CH, WOOD, top=shade(WOOD, 1.12))
    rnd = random.Random(4)
    for zz in (132, 180):
        box(0, y0 + .1, .42, y1 - .1, zz, zz + 4, (242, 242, 238))
        yy = y0 + .2
        while yy < y1 - .4:
            w = rnd.uniform(.35, .55)
            box(.04, yy, .38, yy + w, zz + 4, zz + 4 + rnd.uniform(22, 32), rnd.choice([(236, 236, 230), (200, 210, 220), (150, 160, 170)]))
            yy += w + .06
    box(.04, y0 + .5, .4, y0 + 1.1, 184, 216, (120, 130, 140))            # cat carrier, on top
    qx(.401, y0 + .65, y0 + .95, 190, 210, (50, 54, 60))


def north_run(x0, x1, sink, d=1.0):
    """North wall: short worktop over the first washer (door faces away), belfast sink in the NW corner."""
    a, b = sink
    box(x0, RD - d, a, RD, 4, CH - 6, (244, 244, 242))                    # washer 1 (seen from behind)
    box(x0, RD - d - .02, a, RD, CH - 6, CH, WOOD, top=shade(WOOD, 1.12))
    box(a, RD - d, x1, RD, 4, 56, (240, 240, 236))
    box(a, RD - d - .06, x1 - .05, RD - .05, 56, CH + 1, (248, 248, 246), top=(236, 238, 238))
    qz(CH + 1.2, a + .08, RD - d + .04, x1 - .13, RD - .2, (176, 182, 186))
    cyl((a + x1) / 2, RD - .12, .035, CH, CH + 28, (200, 202, 206))


def tall_cupboard(y0, y1, d=.9, h=212):
    c = (242, 242, 238)
    box(0, y0, d, y1, 0, h, c)
    m = (y0 + y1) / 2
    for a, b in ((y0 + .04, m - .015), (m + .015, y1 - .04)):
        qx(d + .001, a, b, 8, h - 8, shade(c, KX * .96))
    for yy in (m - .06, m + .03):
        qx(d + .003, yy, yy + .02, 96, 118, (120, 120, 124))


def clothes_rail(x, y0, y1, z=196):
    """A drying rail hung from the ceiling on ropes, clothes on it."""
    rope = (200, 190, 160)
    for yy in (y0, y1):
        line((x, yy, z), (x, yy, WALL_H), rope, 1)
    box(x - .03, y0, x + .03, y1, z - 3, z + 3, (190, 160, 110), ol=False)
    rnd = random.Random(6)
    yy = y0 + .1
    while yy < y1 - .2:
        w = rnd.uniform(.2, .34)
        col = rnd.choice([(80, 100, 150), (220, 220, 214), (150, 60, 60), (60, 60, 64), (120, 150, 110)])
        poly([P(x + .01, yy, z - 3), P(x + .01, yy + w, z - 3), P(x + .01, yy + w + .02, z - rnd.uniform(40, 70)), P(x + .01, yy - .02, z - rnd.uniform(40, 70))], shade(col, KX))
        yy += w + .05


def wicker_basket(cx, cy):
    c = (176, 140, 90)
    cyl(cx, cy, .3, 0, 32, c, top=shade(c, .7))
    for zz in (8, 16, 24):
        line((cx - .3, cy + .3, zz), (cx + .3, cy + .3, zz), shade(c, .75), 1)


def west_wall_hung():
    """West (ghost) wall, faint: coats on hooks near the south end, the ironing board
    hanger high up near the north end."""
    with hung_layer():
        box(RW - .06, .8, RW - .02, 2.3, 186, 192, (110, 80, 50), ol=False)
        for y0, w, col in ((.85, .5, (40, 50, 70)), (1.3, .45, (90, 70, 50)), (1.75, .55, (50, 60, 50))):
            poly([P(RW - .12, y0 + w * .3, 190), P(RW - .12, y0 + w * .7, 190), P(RW - .2, y0 + w, 96), P(RW - .2, y0, 96)], shade(col, KX))
        box(RW - .1, 4.0, RW - .02, 4.5, 206, 212, (40, 40, 42), ol=False)           # hanger
        poly([P(RW - .1, 4.05, 206), P(RW - .1, 4.45, 206), P(RW - .1, 4.38, 96), P(RW - .1, 4.12, 96)], shade((90, 120, 150), KX))
        box(RW - .14, 4.15, RW - .08, 4.35, 170, 186, (200, 200, 204), ol=False)     # the iron


def main():
    background()
    floor_tiles(TERRACOTTA, size=.5, seed=9)
    floor_slab(TERRACOTTA)
    wall_shell(WHITE)
    boot = exterior_layer({"N": boot_room_beyond}, haze=(180, 190, 178))
    doorway_back("N", *DOOR, boot)
    wall_trim(cornice=False)
    east_run(2.6, 4.88)
    tall_cupboard(4.9, RD)
    door_leaf()
    clothes_rail(1.2, .5, 2.2)
    place_sprite("archie", 2.0, 2.9)
    wicker_basket(RW - .45, 1.5)
    north_run(.92, RW, (2.55, 3.6))
    west_wall_hung()
    ghost_near_walls(WHITE, windows_S=[WINDOW], window_z=(118, 200), window_cols=2, cornice=False, curtains=None)
    finish("Hide and Seek - Utility (mock-up)", OUT)


if __name__ == "__main__":
    main()
