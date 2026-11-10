#!/usr/bin/env python3
"""Static isometric mock-up of the first-floor Upstairs Corridor.

Not a long uniform box: a narrow east-west passage under Archie's Room
and the NE bedroom, widening at the east end into a deeper lobby that
bulges south beside the stairwell, in front of the bathroom door.

Bounding rectangle 11.4 x 3.85 tiles, origin (4.00, -1.85) so the
passage south edge (y = PASS_Y0) still meets the landing's north wall
and the arch stays lined up. The south-west of the rectangle is the
landing/stairwell, not corridor (no floor there).

South of the passage: arched opening to the landing. East of the lobby:
bathroom doorway. West dead end: clothes basket. North wall: Archie's
door, a gap with a radiator, then the NE bedroom door. Loft hatch left out.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(11.4, 3.85)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_corridor_mock.png"

WALL = (188, 190, 192)
OAK1, OAK2 = (198, 164, 104), (176, 140, 82)
WHITE_ = (244, 242, 236)
STEEL = (140, 144, 148)
FABRIC = (158, 160, 164)

# L-shape: lobby is the east (low-x) widening; passage runs west from it
PASS_Y0 = 1.65          # south edge of the narrow passage (= landing north)
LOBBY_X1 = 2.55         # west edge of the lobby bulge (= landing east)

# arch in the passage south wall (matches landing ARCH 0.35-2.85 -> x 2.90-5.40)
ARCH = (2.90, 5.40)
# east wall of the lobby: bathroom
BATH_DOOR = (0.65, 2.15)
# north wall: two doors with a gap (partition + radiator) between them
ARCHIE_DOOR = (2.65, 4.07)   # Archie's Room, east end of its south wall
NE_BED = (0.28, 1.60)        # NE bedroom, west end of its south wall
RAD = (1.72, 2.52)           # radiator on the north wall, in the gap


def oak_floor():
    """L-shaped floor: full-depth lobby at the east, narrow passage to the west."""
    import paint
    # lobby (including the north strip that continues the passage)
    paint.stamp(paint.timber(LOBBY_X1, RD, 9, OAK1, OAK2, along="x", plank=0.24),
                0, 0, LOBBY_X1, RD, 0)
    # narrow passage west of the lobby
    paint.stamp(paint.timber(RW - LOBBY_X1, RD - PASS_Y0, 10, OAK1, OAK2, along="x", plank=0.24),
                LOBBY_X1, PASS_Y0, RW, RD, 0)


def l_walls():
    """Opaque far walls of the L. Toward-camera faces are left for the ghosts."""
    # the inner corner (lobby's west face) reads the step in both views
    qx(LOBBY_X1, 0.0, PASS_Y0, 0, WALL_H, shade(WALL, KX))
    if not hc.FLIP:
        # south and east are far: lobby south, passage south (broken for the arch), east
        qy(0.0, 0.0, LOBBY_X1, 0, WALL_H, shade(WALL, KY))
        qy(PASS_Y0, LOBBY_X1, ARCH[0], 0, WALL_H, shade(WALL, KY))
        qy(PASS_Y0, ARCH[1], RW, 0, WALL_H, shade(WALL, KY))
        qx(0.0, 0.0, RD, 0, WALL_H, shade(WALL, KX))
    else:
        # west is far: cap the passage dead end
        qx(RW, PASS_Y0, RD, 0, WALL_H, shade(WALL, KX))


def l_skirting():
    """White skirting along the L's back walls only (not across the landing void)."""
    def skirt_y(y, a, b):
        qy(y, a, b, 0, 13, shade(WHITE_, KY))
        qy(y, a, b, 13, 15, shade(WHITE_, KY * 0.8))
        qy(y, a, b, WALL_H - 20, WALL_H, shade(WHITE_, KY))

    def skirt_x(x, a, b):
        qx(x, a, b, 0, 13, shade(WHITE_, KX))
        qx(x, a, b, 13, 15, shade(WHITE_, KX * 0.8))
        qx(x, a, b, WALL_H - 20, WALL_H, shade(WHITE_, KX))

    if not hc.FLIP:
        skirt_y(0.0, 0.0, LOBBY_X1)
        skirt_x(LOBBY_X1, 0.0, PASS_Y0)
        skirt_y(PASS_Y0, LOBBY_X1, ARCH[0])
        skirt_y(PASS_Y0, ARCH[1], RW)
        skirt_x(0.0, 0.0, BATH_DOOR[0])
        skirt_x(0.0, BATH_DOOR[1], RD)


def opening_at_y(y, a, b, draw, h=None):
    """Neighbour through a doorway in a south-facing wall at this y (not y = 0)."""
    h = DOOR_H + 16 if h is None else h
    layer = pygame.Surface(screen.get_size(), depth=24)
    layer.fill((226, 220, 208))
    with drawing_on(layer):
        draw()
    pts = [P(a, y, 0), P(b, y, 0), P(b, y, h), P(a, y, h)]
    show_through(layer, pts, tint_a=0)
    qy(y + 0.02, a - 0.08, a, 0, h + 8, shade(WHITE_, KY))
    qy(y + 0.02, b, b + 0.08, 0, h + 8, shade(WHITE_, KY))
    qy(y + 0.02, a - 0.08, b + 0.08, h, h + 10, shade(WHITE_, KY))


def niche(u0, u1):
    """Recessed arch niche in the passage's south wall, west of the landing arch."""
    if hc.FLIP:
        return
    z0, z1 = 28, 150
    y = PASS_Y0 + 0.10
    qy(y, u0, u1, z0, z1, shade(WALL, KY * 0.78))
    mid = (u0 + u1) / 2
    qy(y + 0.01, u0 + 0.08, u1 - 0.08, z1 - 22, z1, shade(WALL, KY * 0.7))
    qy(y + 0.02, mid - 0.16, mid + 0.16, z1 - 8, z1 + 6, shade(WALL, KY * 0.66))
    qy(PASS_Y0 + 0.02, u0 - 0.05, u0, 20, z1 + 4, shade(WHITE_, KY))
    qy(PASS_Y0 + 0.02, u1, u1 + 0.05, 20, z1 + 4, shade(WHITE_, KY))
    qy(PASS_Y0 + 0.02, u0 - 0.05, u1 + 0.05, z1, z1 + 8, shade(WHITE_, KY))


def radiator_north(x0, x1):
    """White radiator on the north (near) wall, in the gap between the bedroom doors."""
    y = RD - 0.24
    box(x0, y, x1, RD - 0.05, 8, 50, WHITE_, top=shade(WHITE_, 1.04))
    for i in range(6):
        xx = x0 + 0.05 + i * (x1 - x0 - 0.08) / 5
        qy(y, xx, xx + 0.03, 12, 46, shade(WHITE_, KY * 0.9))


def ghost_west_passage():
    """See-through west wall of the passage only (not down through the landing void)."""
    if hc.FLIP:
        return
    t = 0.08
    W = lambda u, z, n: P(RW + n, u, z)
    gc = shade(WALL, KX)
    faces = [(gc, [W(PASS_Y0, 0, t), W(RD, 0, t), W(RD, WALL_H, t), W(PASS_Y0, WALL_H, t)])]
    layer, at = HMG.polys_layer(faces)
    layer.set_alpha(34)
    screen.blit(layer, at)


def clothes_basket(cx, cy):
    """Fabric laundry basket on a metal frame, at the west dead end."""
    for dx, dy in ((-0.22, -0.16), (0.18, -0.16), (-0.22, 0.14), (0.18, 0.14)):
        box(cx + dx, cy + dy, cx + dx + 0.045, cy + dy + 0.045, 0, 40, STEEL)
    box(cx - 0.30, cy - 0.24, cx + 0.30, cy + 0.24, 36, 68, FABRIC, top=shade(FABRIC, 1.08))
    box(cx - 0.32, cy - 0.26, cx + 0.32, cy + 0.26, 66, 74, shade(STEEL, 1.05), top=shade(STEEL, 1.15))
    qz(74.4, cx - 0.22, cy - 0.16, cx + 0.22, cy + 0.16, (96, 98, 102))
    box(cx - 0.12, cy - 0.08, cx + 0.14, cy + 0.1, 74.5, 80, (232, 230, 224), ol=False)


def main():
    background()
    oak_floor()
    l_walls()
    import glimpses
    if not hc.FLIP:
        opening_at_y(PASS_Y0, *ARCH, glimpses.landing_from_corridor)
        mid = (ARCH[0] + ARCH[1]) / 2
        qy(PASS_Y0 + 0.03, ARCH[0] + 0.15, ARCH[1] - 0.15, DOOR_H + 4, DOOR_H + 22, shade(WALL, KY))
        qy(PASS_Y0 + 0.035, mid - 0.35, mid + 0.35, DOOR_H + 16, DOOR_H + 28, shade(WALL, KY * 0.92))
        back_opening("W", *BATH_DOOR, glimpses.bathroom_from_corridor)
        niche(7.15, 8.05)
    l_skirting()
    radiator_north(*RAD)
    place_sprite("archie", 6.2, 2.7)
    ghost_near_walls(WALL,
                     doors_S=[ARCHIE_DOOR, NE_BED],
                     doors_E=[],
                     open_E=True)
    ghost_west_passage()
    clothes_basket(RW - 1.15, (PASS_Y0 + RD) * 0.5)
    finish("Hide and Seek - Upstairs Corridor (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_corridor_mock.png",))


if __name__ == "__main__":
    main()
