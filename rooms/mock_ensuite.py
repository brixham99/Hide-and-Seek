#!/usr/bin/env python3
"""Static isometric mock-up of the En-suite for 'Hide and Seek'.

The 9'11 x 7'6 (3.0 m E-W x 2.3 m N-S) bathroom north of the Dressing
Room, west-aligned with it. Cream walls above grey-blue tongue-and-groove
panelling, patterned grey-and-cream encaustic floor. One sash, on the
north wall toward the east. South wall: open doorway back to the Dressing
Room at the west end, a chrome towel rail between that door and the
shower. South-east corner: a glass-screened shower with cream metro tiles
on the east and south returns. East wall, north of the shower: a dusty-
blue vanity with a white basin. North-west: a close-coupled loo against
the west wall. The west wall has no window. Ceiling spots left out. No
internal door leaf; no registration-plate lettering.
"""
import math
import random
import sys

import numpy as np
import pygame

import house_common as hc
hc.init_room(5.3, 4.2)
from house_common import *  # noqa: E402,F401,F403

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "shots/hs_ensuite_mock.png"

WALL = (232, 226, 214)
DADO = (162, 168, 170)
WHITE_ = (244, 242, 236)
CHROME = (196, 200, 206)
BLUE = (142, 174, 196)
METRO = (232, 226, 216)
GLASS = (186, 214, 220)

DRESSING_DOOR = (3.75, 5.10)    # south wall, west end -> dressing room
WIN_N = (0.25, 1.95)            # north wall, toward the east (the only sash)
SHOWER = (0.04, 0.04, 1.64, 1.68)
VANITY = (0.04, 1.80, 0.72, 4.00)
LOO = (4.55, 3.20, 5.26, 4.12)


def north_garden(side, rnd):
    """Trees close to the north sash, a step below."""
    ext_lawn(side, -8, RW + 8, 0.2, 12, rnd, base=(86, 142, 60))
    ext_tree(side, 0.8, 2.6, trunk=96, canopy=140, r=1.15, col=(78, 122, 50), rnd=random.Random(51))
    ext_tree(side, 2.6, 3.4, trunk=88, canopy=128, r=1.05, col=(88, 130, 54), rnd=random.Random(52))
    ext_hedge(side, -4, RW + 4, 4.4, 5.1, h=86, rnd=rnd)
    ext_house_shadow(side, -8, RW + 8, depth=0.9)


def encaustic_floor():
    """Grey-and-cream geometric tiles, as in the photos."""
    import paint
    ppm = 56
    tw, th = max(8, int(RW * ppm)), max(8, int(RD * ppm))
    ts = max(10, int(0.34 * ppm))
    grout = np.array((200, 196, 188), np.float32)
    img = np.empty((th, tw, 3), np.float32)
    img[:] = grout
    cream = np.array((226, 220, 210), np.float32)
    grey = np.array((148, 154, 158), np.float32)
    slate = np.array((120, 128, 134), np.float32)
    rng = np.random.RandomState(27)
    for iy, y in enumerate(range(0, th, ts)):
        for ix, x in enumerate(range(0, tw, ts)):
            y1, x1 = min(y + ts - 2, th), min(x + ts - 2, tw)
            tile = img[y:y1, x:x1]
            if tile.shape[0] < 6 or tile.shape[1] < 6:
                continue
            tile[:] = cream * rng.uniform(0.96, 1.04)
            hh, ww = tile.shape[:2]
            cy, cx = hh / 2.0, ww / 2.0
            yy = np.arange(hh)[:, None]
            xx = np.arange(ww)[None, :]
            star = (np.abs(yy - cy) / max(hh * 0.28, 1) + np.abs(xx - cx) / max(ww * 0.28, 1)) <= 1
            tile[star] = grey * rng.uniform(0.95, 1.05)
            core = ((yy - cy) / max(hh * 0.10, 1)) ** 2 + ((xx - cx) / max(ww * 0.10, 1)) ** 2 <= 1
            tile[core] = slate
    paint.stamp(np.clip(img, 0, 255).astype(np.uint8), 0, 0, RW, RD, 0)


def dado(side, u0, u1):
    """Grey-blue vertical panelling up to a dado rail."""
    k = wall_k(side)
    wall_quad(side, u0, u1, 14, 118, shade(DADO, k))
    u = u0 + 0.04
    while u < u1 - 0.04:
        wall_quad(side, u, u + 0.035, 16, 116, shade(DADO, k * 0.86), 0.012)
        u += 0.20
    wall_quad(side, u0, u1, 114, 120, shade(WHITE_, k))


def metro_on(side, u0, u1):
    """Cream metro tiles on one shower wall."""
    k = wall_k(side)
    grout = shade((200, 196, 188), k * 0.85)
    tile = shade(METRO, k)
    wall_quad(side, u0, u1, 14, WALL_H - 4, grout)
    tw, th = 0.22, 9.0
    row, z = 0, 16.0
    while z < WALL_H - 8:
        u = u0 + (0.11 if row % 2 else 0.0)
        while u < u1 - 0.04:
            b = min(u1 - 0.01, u + tw)
            wall_quad(side, u + 0.012, b - 0.012, z + 0.6, min(WALL_H - 6, z + th - 0.6), tile)
            u += tw
        z += th
        row += 1


def shower_tray():
    x0, y0, x1, y1 = SHOWER
    box(x0, y0, x1, y1, 0, 8, (236, 234, 230), top=shade(WHITE_, 1.04))
    box(x0, y1 - 0.05, x1, y1, 6, 12, CHROME)
    box(x1 - 0.05, y0, x1, y1, 6, 12, CHROME)


def rain_head():
    x0, y0, x1, y1 = SHOWER
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cyl(cx, cy, 0.03, 12, 210, CHROME)
    cyl(cx, cy, 0.20, 200, 212, CHROME, top=shade(CHROME, 1.1))


def glass_casing():
    """See-through glass on the open north and west sides of the SE shower.

    Drawn on an alpha layer so the panes never write occluders: Archie stays
    visible through them. Chrome posts and rails are thin enough that they
    do not note occluders either. The shower footprint stays solid in house.py.
    """
    x0, y0, x1, y1 = SHOWER
    z0, z1 = 12, 168
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    with drawing_on(layer):
        qx(x1, y0 + 0.05, y1 - 0.02, z0, z1, GLASS)
        qy(y1, x0 + 0.05, x1 - 0.02, z0, z1, GLASS)
        # brighter leading edges
        qx(x1 + 0.012, y0 + 0.05, y1 - 0.02, z0, z1, (228, 238, 240))
        qy(y1 + 0.012, x0 + 0.05, x1 - 0.02, z0, z1, (228, 238, 240))
    layer.set_alpha(88)
    screen.blit(layer, (0, 0))
    # chrome frame: corner posts and top rails
    post = 0.045
    box(x1 - post, y0 + 0.04, x1, y0 + 0.10, z0, z1, CHROME)
    box(x1 - post, y1 - 0.10, x1, y1, z0, z1, CHROME)
    box(x0 + 0.04, y1 - post, x0 + 0.10, y1, z0, z1, CHROME)
    box(x1 - 0.10, y1 - post, x1, y1, z0, z1, CHROME)
    box(x1 - post, y0 + 0.04, x1, y1, z1 - 6, z1, CHROME)
    box(x0 + 0.04, y1 - post, x1, y1, z1 - 6, z1, CHROME)
    # sliding-door handle on the west pane
    box(x1 - 0.02, (y0 + y1) / 2 - 0.04, x1 + 0.03, (y0 + y1) / 2 + 0.04, 78, 118, CHROME)


def vanity(full):
    """Dusty-blue cupboard and white basin on the east wall."""
    x0, y0, x1, y1 = VANITY
    if not full:
        box(x0, y0, x1, y1, 0, 16, BLUE, top=shade(BLUE, 1.06))
        return
    box(x0, y0, x1, y1, 0, 70, BLUE, top=shade(BLUE, 1.04))
    box(x0 + 0.08, y0 + 0.08, x1 - 0.06, y1 - 0.08, 8, 12, shade(BLUE, 0.88), ol=False)
    box(x0 + 0.16, y0 + 0.22, x1 - 0.14, y0 + 0.70, 12, 28, (168, 128, 80), ol=False)
    for ya, yb, z in ((y0 + 0.12, y0 + 0.72, 40), (y0 + 0.84, y1 - 0.12, 40),
                      (y0 + 0.12, y0 + 0.72, 56), (y0 + 0.84, y1 - 0.12, 56)):
        box(x0 + 0.06, ya, x1 - 0.04, yb, z, z + 12, shade(BLUE, 1.08), ol=False)
        box(x0 + 0.10, (ya + yb) / 2 - 0.08, x0 + 0.16, (ya + yb) / 2 + 0.08, z + 4, z + 8, CHROME, ol=False)
    box(x0, y0 - 0.02, x1 + 0.04, y1 + 0.04, 70, 78, WHITE_, top=shade(WHITE_, 1.08))
    box(x0 + 0.10, y0 + 0.28, x1 - 0.10, y1 - 0.22, 74, 80, (210, 218, 222), top=(198, 208, 214))
    box(x0 + 0.04, (y0 + y1) / 2 - 0.06, x0 + 0.16, (y0 + y1) / 2 + 0.06, 78, 90, CHROME)
    cyl(x0 + 0.22, y1 - 0.22, 0.07, 78, 92, (62, 118, 58))
    if not hc.FLIP:
        mid = (y0 + y1) / 2
        qx(0.04, mid - 0.28, mid + 0.28, 118, 176, shade((198, 202, 206), KX))
        qx(0.045, mid - 0.22, mid + 0.22, 124, 170, shade((186, 192, 198), KX))
        for v in (y0 + 0.22, y1 - 0.22):
            qx(0.03, v - 0.06, v + 0.06, 150, 168, shade((232, 220, 196), KX))


def loo(full):
    """Close-coupled white loo against the west wall, at the north end."""
    x0, y0, x1, y1 = LOO
    if not full:
        box(x0, y0, x1, y1, 0, 16, WHITE_, top=shade(WHITE_, 1.03))
        return
    box(x0 + 0.08, y0 + 0.08, x1 - 0.08, y1 - 0.08, 0, 40, WHITE_, top=shade(WHITE_, 1.03))
    box(x0 + 0.16, y0 + 0.16, x1 - 0.16, y1 - 0.16, 38, 44, (230, 232, 234), top=(214, 218, 222))
    box(x1 - 0.28, y0 + 0.10, x1, y1 - 0.10, 40, 82, WHITE_, top=shade(WHITE_, 1.05))
    box(x1 - 0.16, (y0 + y1) / 2 - 0.05, x1 - 0.04, (y0 + y1) / 2 + 0.05, 82, 88, CHROME)


def towel_rail(full):
    """Chrome heated rail on the south wall, between the shower and the door."""
    x0, x1, y0, y1 = 1.82, 3.28, 0.02, 0.18
    if not full:
        box(x0, y0, x1, y1, 0, 14, CHROME, top=shade(CHROME, 1.05))
        return
    box(x0, y0, x1, y0 + 0.04, 36, 138, CHROME)
    box(x0, y1 - 0.04, x1, y1, 36, 138, CHROME)
    for z in (48, 72, 96, 120):
        box(x0, y0, x1, y1, z, z + 5, CHROME)
    box(x0 + 0.12, y0 + 0.02, x0 + 0.55, y1 - 0.02, 40, 118, (220, 218, 224))
    box(x1 - 0.50, y0 + 0.02, x1 - 0.12, y1 - 0.02, 40, 100, (232, 228, 220))


def wicker_basket():
    box(4.12, 3.40, 4.48, 3.78, 0, 24, (148, 112, 72), top=shade((148, 112, 72), 0.8))


def scales():
    box(4.18, 3.05, 4.50, 3.32, 0, 6, (236, 236, 232), top=shade(WHITE_, 1.04))


def radiator_north():
    if not hc.FLIP:
        return
    a, b = WIN_N
    box(a + 0.10, RD - 0.16, b - 0.10, RD - 0.04, 0, 36, WHITE_, top=shade(WHITE_, 1.04))


def peg_rail():
    """Wooden peg rail on the west wall, by the dressing door."""
    if not hc.FLIP:
        return
    qx(RW - 0.04, 0.40, 1.45, 128, 136, shade((140, 108, 72), KX))


def dressing_door_ghost():
    if not hc.FLIP:
        return
    a, b = DRESSING_DOOR
    qy(0.03, a - 0.08, a + 0.06, 0, DOOR_H + 10, shade(WHITE_, KY))
    qy(0.03, b - 0.06, b + 0.08, 0, DOOR_H + 10, shade(WHITE_, KY))
    qy(0.03, a - 0.08, b + 0.08, DOOR_H - 2, DOOR_H + 10, shade(WHITE_, KY))


def main():
    background()
    encaustic_floor()
    wall_shell(WALL)
    import glimpses
    if not hc.FLIP:
        dado("N", 0, RW)
        dado("W", 0, RD)
        metro_on("W", SHOWER[1], SHOWER[3])     # east return
        metro_on("N", SHOWER[0], SHOWER[2])     # south return
        back_opening("N", *DRESSING_DOOR, glimpses.dressing_from_ensuite)
    wall_trim()
    shower_tray()
    # Near-wall tall fittings are cut down so Archie stays visible.
    if hc.FLIP:
        # east + south are near
        towel_rail(full=False)
        vanity(full=False)
        loo(full=True)
        rain_head()
    else:
        # north + west are near
        towel_rail(full=True)
        vanity(full=True)
        loo(full=False)
        with hung_layer(alpha=120):
            loo(full=True)
        rain_head()
    glass_casing()
    wicker_basket()
    scales()
    place_sprite("archie", 2.65, 2.50)
    ghost_near_walls(WALL,
                     windows_S=() if hc.FLIP else [WIN_N],
                     window_z=(70, 198), window_cols=2, curtains=None)
    if hc.FLIP:
        # North and west are the far walls here; paint them after
        # ghost_near_walls, which otherwise covers them in plain cream.
        dado("S", 0, RW)
        dado("E", 0, RD)
        ext = exterior_layer({"S": north_garden}, haze=(170, 188, 150))
        sash_on_far("S", *WIN_N, ext, z0=70, z1=198, curtains=None, cols=2)
        radiator_north()
        peg_rail()
        dressing_door_ghost()
    finish("Hide and Seek - En-suite (mock-up)", OUT,
           subtitle="First Floor", copies=() if ARGS else ("shots/hs_ensuite_mock.png",))


if __name__ == "__main__":
    main()
