#!/usr/bin/env python3
"""Static isometric mock-up of the first-floor Upstairs Corridor.

Not a long uniform box: a narrow east-west passage under Archie's Room
and the NE bedroom, widening at the east end into a deeper lobby that
bulges south beside the stairwell, in front of the bathroom door.

Bounding rectangle 7.75 x 3.85 tiles, origin (4.00, -1.85) so the
passage south edge (y = PASS_Y0) still meets the landing's north wall
and the arch stays lined up. The west dead end (house X = 11.75) stops at
the Dressing Room's east wall, as on the first-floor plate: only a short
blank run (~1.3 m) west of the arch. The south-west of the rectangle is
the landing/stairwell, not corridor (no floor there).

South of the passage: a slim curved arch to the landing. East of the lobby:
bathroom doorway. West dead end: clothes basket, plain wall (no niche or
door). North wall: Archie's door, a gap with a radiator, then the Upstairs
Office door. Loft hatch left out.
"""
import math
import random
import sys

import house_common as hc
hc.init_room(7.75, 3.85)
from house_common import *  # noqa: E402,F401,F403
import iso_paint  # noqa: E402

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
NE_BED = (0.28, 1.60)        # Upstairs Office, west end of its south wall
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


def _WP(u, z, n=0.0):
    """A point on the passage's south wall plane (y = PASS_Y0), n towards +y."""
    return P(u, PASS_Y0 + n, z)


def wall_over_arch(col, n=0.0):
    """The wall above the arch: strips from the curved soffit up to the wall top."""
    a, b = ARCH
    us = [a + (b - a) * i / 18 for i in range(19)]
    out = [(col, [_WP(a - ARCH_JAMB, ARCH_SPRING, n), _WP(a, ARCH_SPRING, n), _WP(a, WALL_H, n), _WP(a - ARCH_JAMB, WALL_H, n)]),
           (col, [_WP(b, ARCH_SPRING, n), _WP(b + ARCH_JAMB, ARCH_SPRING, n), _WP(b + ARCH_JAMB, WALL_H, n), _WP(b, WALL_H, n)])]
    for u0, u1 in zip(us, us[1:]):
        out.append((col, [_WP(u0, arch_z(u0, a, b), n), _WP(u1, arch_z(u1, a, b), n), _WP(u1, WALL_H, n), _WP(u0, WALL_H, n)]))
    return out


def _ghost(pts, col, alpha=36):
    """Opposite view: a near wall face on the ghost layer (see-through)."""
    if hc._fg_surf is not None:
        hc._fill_poly(hc._fg_surf, pts, col, alpha, zwrite=False)


def ghost_walls_flip():
    """Opposite view: the lobby's south and east walls, the passage's south
    wall with the arch, and the step between them are the near walls now,
    so they are see-through ghosts like every other near wall (no solid
    pillar in front of the player), with Haunted Mansion ghost frames on the
    arch and the bathroom doorway. Nothing beyond shows through them."""
    gy, gx = shade(WALL, KY), shade(WALL, KX)
    a, b = ARCH
    _ghost([P(0, 0, 0), P(LOBBY_X1, 0, 0), P(LOBBY_X1, 0, WALL_H), P(0, 0, WALL_H)], gy)
    _ghost([P(LOBBY_X1, 0, 0), P(LOBBY_X1, PASS_Y0, 0), P(LOBBY_X1, PASS_Y0, WALL_H), P(LOBBY_X1, 0, WALL_H)], gx)
    for u0, u1 in ((LOBBY_X1, a - ARCH_JAMB), (b + ARCH_JAMB, RW)):
        _ghost([_WP(u0, 0), _WP(u1, 0), _WP(u1, WALL_H), _WP(u0, WALL_H)], gy)
    for c, pts in wall_over_arch(gy):
        _ghost(pts, c)
    d0, d1 = BATH_DOOR
    for v0, v1, z0, z1 in ((0, d0 - .16, 0, WALL_H), (d1 + .16, RD, 0, WALL_H), (d0 - .16, d1 + .16, DOOR_H + 32, WALL_H)):
        _ghost([P(0, v0, z0), P(0, v1, z0), P(0, v1, z1), P(0, v0, z1)], gx)
    if hc._fg_surf is not None:
        # arch frame on the passage wall, towards the camera (-y)
        ghost_door_frame(lambda u, z, n: _WP(u, z, -n), a, b, ghost_frame_col(1.0), target=hc._fg_surf, arch=True)


def l_walls():
    """Opaque far walls of the L. Toward-camera faces are left for the ghosts."""
    if not hc.FLIP:
        # the inner corner (lobby's west face) reads the step
        qx(LOBBY_X1, 0.0, PASS_Y0, 0, WALL_H, shade(WALL, KX))
        # south and east are far: lobby south, passage south (broken for the arch), east
        qy(0.0, 0.0, LOBBY_X1, 0, WALL_H, shade(WALL, KY))
        qy(PASS_Y0, LOBBY_X1, ARCH[0] - ARCH_JAMB, 0, WALL_H, shade(WALL, KY))
        qy(PASS_Y0, ARCH[1] + ARCH_JAMB, RW, 0, WALL_H, shade(WALL, KY))
        for c, pts in wall_over_arch(shade(WALL, KY)):
            poly(pts, c)
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
        skirt_y(PASS_Y0, LOBBY_X1, ARCH[0] - ARCH_JAMB)
        skirt_y(PASS_Y0, ARCH[1] + ARCH_JAMB, RW)
        skirt_x(0.0, 0.0, BATH_DOOR[0])
        skirt_x(0.0, BATH_DOOR[1], RD)


def opening_at_y(y, a, b, draw):
    """Neighbour through the arch in the south-facing passage wall at this y,
    then the slim white arch frame over it."""
    layer = pygame.Surface(screen.get_size(), depth=24)
    layer.fill((226, 220, 208))
    with drawing_on(layer):
        draw()
    W = lambda u, z, n=0.0: P(u, y + n, z)
    show_through(layer, arch_opening_pts(W, a, b), tint_a=0)
    for c, pts in arch_frame_polys(W, a, b, WHITE_, KY, 0.02):
        poly(pts, c)


def radiator_north(x0, x1):
    """White radiator on the north (near) wall, in the gap between the bedroom doors."""
    y = RD - 0.24
    iso_paint.paint_box(x0, y, x1, RD - 0.05, 8, 50, "hall_radiator", front="S", col=WHITE_)
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
    iso_paint.paint_box(cx - 0.30, cy - 0.24, cx + 0.30, cy + 0.24, 36, 68, "basket_fabric", front="S", col=FABRIC)
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
        back_opening("W", *BATH_DOOR, glimpses.bathroom_from_corridor)
    l_skirting()
    radiator_north(*RAD)
    place_sprite("archie", 6.2, 2.7)
    ghost_near_walls(WALL,
                     doors_S=[ARCHIE_DOOR, NE_BED],
                     doors_E=[],
                     open_E=True)
    ghost_west_passage()
    if hc.FLIP:
        ghost_walls_flip()
    clothes_basket(RW - 1.15, (PASS_Y0 + RD) * 0.5)
    finish("Hide and Seek - Upstairs Corridor (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_corridor_mock.png",))


if __name__ == "__main__":
    main()
