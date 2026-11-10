"""Parametric painted furniture for Hide and Seek.

Drawn with house_common primitives (box / qx / qy / cyl) so occluders,
near-wall ghosting and both cameras keep working. Callers pass the same
footprints they already use; we do not change collisions. Colours and
materials follow the house photos: oak and pine grain, painted shaker
doors, velvet and boucle, brass knobs, wicker.

`front` is the side the drawers or seat face, using house axes:
S = south (y smaller), N = north, E = east (x smaller), W = west.
"""
import math
import random

import pygame

import house_common as hc
from house_common import (
    P, box, qx, qy, qz, cyl, cone, fl_ellipse, shade, KX, KY, KT, S,
    FLIP, turned_leg, farmhouse_table, ladder_chair,
)

BRASS = (196, 168, 88)
OAK = (168, 118, 72)
PINE = (196, 150, 96)
DARK_WOOD = (110, 72, 42)
WICKER = (168, 124, 72)
CREAM = (234, 226, 210)
WHITE_ = (244, 242, 236)


def _clamp(a, lo, hi):
    return max(lo, min(hi, a))


def face_quad(front, x0, y0, x1, y1, z0, z1, u0, u1, v0, v1, col, ol=None):
    """A quad on the front face: u across (0-1), v up (0-1)."""
    za = z0 + (z1 - z0) * v0
    zb = z0 + (z1 - z0) * v1
    if front == "S":
        qx_ = y0
        a = x0 + (x1 - x0) * u0
        b = x0 + (x1 - x0) * u1
        qy(qx_, a, b, za, zb, col, ol)
    elif front == "N":
        a = x0 + (x1 - x0) * u0
        b = x0 + (x1 - x0) * u1
        qy(y1, a, b, za, zb, col, ol)
    elif front == "E":
        a = y0 + (y1 - y0) * u0
        b = y0 + (y1 - y0) * u1
        qx(x0, a, b, za, zb, col, ol)
    else:
        a = y0 + (y1 - y0) * u0
        b = y0 + (y1 - y0) * u1
        qx(x1, a, b, za, zb, col, ol)


def knob(front, x0, y0, x1, y1, z0, z1, u, v, r=0.028, col=BRASS):
    z = z0 + (z1 - z0) * v
    if front == "S":
        cyl(x0 + (x1 - x0) * u, y0 - 0.015, r, z - 3, z + 3, col)
    elif front == "N":
        cyl(x0 + (x1 - x0) * u, y1 + 0.015, r, z - 3, z + 3, col)
    elif front == "E":
        cyl(x0 - 0.015, y0 + (y1 - y0) * u, r, z - 3, z + 3, col)
    else:
        cyl(x1 + 0.015, y0 + (y1 - y0) * u, r, z - 3, z + 3, col)


def drawer_front(front, x0, y0, x1, y1, z0, z1, u0, u1, v0, v1, col):
    """Shaker drawer: dark recess, lighter inset panel, highlight, brass knob."""
    face_quad(front, x0, y0, x1, y1, z0, z1, u0, u1, v0, v1, shade(col, 0.70))
    face_quad(front, x0, y0, x1, y1, z0, z1, u0 + 0.045, u1 - 0.045, v0 + 0.10, v1 - 0.10, shade(col, 0.92))
    face_quad(front, x0, y0, x1, y1, z0, z1, u0 + 0.045, u1 - 0.045, v1 - 0.14, v1 - 0.10,
              shade(col, 1.10), ol=False)
    knob(front, x0, y0, x1, y1, z0, z1, (u0 + u1) / 2, (v0 + v1) / 2)


def door_front(front, x0, y0, x1, y1, z0, z1, u0, u1, v0, v1, col, knob_u=None):
    """Shaker cupboard door with an inset panel and a round knob."""
    face_quad(front, x0, y0, x1, y1, z0, z1, u0, u1, v0, v1, shade(col, 0.74))
    face_quad(front, x0, y0, x1, y1, z0, z1, u0 + 0.06, u1 - 0.06, v0 + 0.08, v1 - 0.08, shade(col, 0.94))
    face_quad(front, x0, y0, x1, y1, z0, z1, u0 + 0.06, u1 - 0.06, v1 - 0.11, v1 - 0.08,
              shade(col, 1.12), ol=False)
    ku = knob_u if knob_u is not None else (u0 + 0.18 if u0 < 0.5 else u1 - 0.18)
    knob(front, x0, y0, x1, y1, z0, z1, ku, (v0 + v1) / 2)


def wood_top(x0, y0, x1, y1, z, col):
    """Pine/oak grain stamped on a table or chest top."""
    import paint
    w, d = max(0.3, x1 - x0), max(0.3, y1 - y0)
    tex = paint.pine_top(w, d, seed=int(x0 * 11 + y0 * 7) & 31,
                         c1=shade(col, 1.16), c2=shade(col, 0.78))
    paint.stamp(tex, x0, y0, x1, y1, z)


def fabric_box(x0, y0, x1, y1, z0, z1, col, faces="xyz"):
    """Upholstered box with a slight sheen on the camera-facing sides."""
    box(x0, y0, x1, y1, z0, z1, col, top=shade(col, 1.08), faces=faces)
    y_face, x_face = (y0, x0) if hc.FLIP else (y1, x1)
    if "y" in faces:
        span = x1 - x0
        for i in range(3):
            a = x0 + span * (0.18 + i * 0.28)
            qy(y_face, a, a + span * 0.08, z0 + 4, z1 - 4, shade(col, KY * 1.10), ol=False)
    if "x" in faces:
        span = y1 - y0
        for i in range(2):
            a = y0 + span * (0.22 + i * 0.36)
            qx(x_face, a, a + span * 0.07, z0 + 4, z1 - 4, shade(col, KX * 1.12), ol=False)


def chest(x0, y0, x1, y1, z0=0, z1=88, col=OAK, drawers=4, front="S"):
    """Chest of drawers with a wood top and shaker drawer fronts."""
    box(x0, y0, x1, y1, z0, z1 - 8, col, top=shade(col, 1.04))
    box(x0 - 0.03, y0 - 0.02, x1 + 0.03, y1 + 0.02, z1 - 8, z1, shade(col, 1.10))
    wood_top(x0 - 0.02, y0 - 0.015, x1 + 0.02, y1 + 0.015, z1, col)
    step = 0.88 / max(1, drawers)
    for i in range(drawers):
        v0 = 0.06 + i * step
        drawer_front(front, x0, y0, x1, y1, z0, z1 - 8, 0.06, 0.94, v0, v0 + step - 0.05, col)


def cabinet(x0, y0, x1, y1, z0=0, z1=96, col=WHITE_, doors=2, front="S", cornice=True):
    """Low painted cupboard, shaker doors, optional cornice."""
    top_z = z1 - (8 if cornice else 0)
    box(x0, y0, x1, y1, z0, top_z, col, top=shade(col, 1.06))
    if cornice:
        box(x0 - 0.03, y0 - 0.02, x1 + 0.03, y1 + 0.02, top_z, z1, shade(col, 1.10))
    for i in range(doors):
        u0, u1 = i / doors + 0.04, (i + 1) / doors - 0.04
        door_front(front, x0, y0, x1, y1, z0, top_z, u0, u1, 0.08, 0.94, col)


def wardrobe(x0, y0, x1, y1, z0=0, z1=220, col=(162, 170, 176), doors=2, front="S"):
    """Tall wardrobe: cornice, shaker doors, a plinth."""
    box(x0, y0, x1, y1, z0, 14, shade(col, 0.88))
    cabinet(x0, y0, x1, y1, 14, z1, col=col, doors=doors, front=front, cornice=True)


def bookcase(x0, y0, x1, y1, z0=0, z1=160, col=DARK_WOOD, front="S", shelves=4, seed=8):
    """Open bookcase with a dark interior, shelves and a row of spines."""
    box(x0, y0, x1, y1, z0, z1, col, top=shade(col, 1.14))
    box(x0 - 0.03, y0 - 0.02, x1 + 0.03, y1 + 0.02, z1, z1 + 6, shade(col, 1.08))
    rnd = random.Random(seed)
    spines = [(160, 40, 40), (40, 70, 120), (220, 190, 70), (60, 110, 70),
              (200, 120, 60), (230, 220, 200), (110, 40, 60), (30, 30, 30),
              (80, 90, 70), (140, 90, 50)]
    face_quad(front, x0, y0, x1, y1, z0, z1, 0.04, 0.96, 0.04, 0.96, (42, 30, 22))
    for s in range(shelves):
        v0 = 0.06 + s * (0.88 / shelves)
        v1 = v0 + (0.88 / shelves) - 0.04
        face_quad(front, x0, y0, x1, y1, z0, z1, 0.05, 0.95, v0, v0 + 0.035, shade(col, 1.08))
        u = 0.07
        while u < 0.93:
            bw = rnd.uniform(0.035, 0.07)
            ht = rnd.uniform(0.55, 0.92) * (v1 - v0 - 0.05)
            face_quad(front, x0, y0, x1, y1, z0, z1, u, min(0.93, u + bw),
                      v0 + 0.04, v0 + 0.04 + ht,
                      shade(rnd.choice(spines), rnd.uniform(0.85, 1.05)))
            u += bw + 0.006


def table(x0, y0, x1, y1, h=74, col=PINE, legs="turned"):
    """Four-legged table with a wood-grain top."""
    inset = 0.12
    if legs == "turned":
        for lx, ly in ((x0 + inset, y0 + inset), (x1 - inset, y0 + inset),
                       (x0 + inset, y1 - inset), (x1 - inset, y1 - inset)):
            turned_leg(lx, ly, 0, h - 8, shade(col, 0.85), 0.055)
    else:
        for lx, ly in ((x0 + inset, y0 + inset), (x1 - inset, y0 + inset),
                       (x0 + inset, y1 - inset), (x1 - inset, y1 - inset)):
            box(lx - 0.03, ly - 0.03, lx + 0.03, ly + 0.03, 0, h - 6, shade(col, 0.88), ol=False)
    box(x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, h - 16, h - 6, shade(col, 0.86), ol=False)
    box(x0, y0, x1, y1, h - 6, h, col, top=shade(col, 1.08))
    wood_top(x0, y0, x1, y1, h, col)


def chair(x, y, facing="E", col=WHITE_):
    """Ladder-back chair (wraps the shared helper, then adds a little seat grain)."""
    ladder_chair(x, y, facing=facing, col=col)


def armchair(x0, y0, x1, y1, col=CREAM, front="W", wood_arms=None, cushion=None):
    """Upholstered armchair. `front` is the way a sitter faces."""
    aw = min(0.22, (x1 - x0) * 0.18, (y1 - y0) * 0.18)
    seat_z, arm_z, back_z = 40, 60, 90
    fabric_box(x0 + 0.04, y0 + 0.04, x1 - 0.04, y1 - 0.04, 0, 10, shade(col, 0.72))
    # back is opposite the front
    if front == "W":
        fabric_box(x0, y0, x0 + 0.32, y1, 10, back_z, col)
        fabric_box(x0 + 0.32, y0 + aw, x1, y1 - aw, 10, seat_z, col)
        for ya, yb in ((y0, y0 + aw), (y1 - aw, y1)):
            fabric_box(x0 + 0.32, ya, x1, yb, 10, arm_z, col)
            if wood_arms:
                box(x0 + 0.32, ya, x1 + 0.02, yb, arm_z - 4, arm_z + 2, wood_arms,
                    top=shade(wood_arms, 1.12))
    elif front == "E":
        fabric_box(x1 - 0.32, y0, x1, y1, 10, back_z, col)
        fabric_box(x0, y0 + aw, x1 - 0.32, y1 - aw, 10, seat_z, col)
        for ya, yb in ((y0, y0 + aw), (y1 - aw, y1)):
            fabric_box(x0, ya, x1 - 0.32, yb, 10, arm_z, col)
    elif front == "S":
        fabric_box(x0, y0, x1, y0 + 0.32, 10, back_z, col)
        fabric_box(x0 + aw, y0 + 0.32, x1 - aw, y1, 10, seat_z, col)
        for xa, xb in ((x0, x0 + aw), (x1 - aw, x1)):
            fabric_box(xa, y0 + 0.32, xb, y1, 10, arm_z, col)
    else:
        fabric_box(x0, y1 - 0.32, x1, y1, 10, back_z, col)
        fabric_box(x0 + aw, y0, x1 - aw, y1 - 0.32, 10, seat_z, col)
        for xa, xb in ((x0, x0 + aw), (x1 - aw, x1)):
            fabric_box(xa, y0, xb, y1 - 0.32, 10, arm_z, col)
    if cushion:
        cx0, cy0, cx1, cy1 = cushion[0]
        fabric_box(cx0, cy0, cx1, cy1, seat_z, seat_z + 36, cushion[1])


def sofa_run(x0, y0, x1, y1, col, seat_z=42, back_z=86, along="x", back="S"):
    """One straight upholstered run (seat + back). Used to build L-shaped sofas."""
    fabric_box(x0, y0, x1, y1, 0, seat_z, col)
    if back == "S":
        fabric_box(x0, y0, x1, y0 + min(0.42, (y1 - y0) * 0.35), 0, back_z, col)
    elif back == "N":
        fabric_box(x0, y1 - min(0.42, (y1 - y0) * 0.35), x1, y1, 0, back_z, col)
    elif back == "E":
        fabric_box(x0, y0, x0 + min(0.42, (x1 - x0) * 0.35), y1, 0, back_z, col)
    else:
        fabric_box(x1 - min(0.42, (x1 - x0) * 0.35), y0, x1, y1, 0, back_z, col)


def radiator(side, u0, u1, z0=14, z1=44, col=(240, 240, 236)):
    """Column radiator on a named wall (house_common side: N/S/E/W drawing names)."""
    k = hc.wall_k(side)
    hc.wall_quad(side, u0, u1, z0, z1, shade(col, k), 0.06)
    u = u0 + 0.06
    while u < u1 - 0.03:
        hc.wall_quad(side, u, u + 0.016, z0 + 2, z1 - 2, shade(col, k * 0.82), 0.064)
        hc.wall_quad(side, u, u + 0.006, z0 + 4, z1 - 6, shade(col, k * 1.08), 0.066)
        u += 0.075


def lamp(cx, cy, z, shade_col=(124, 146, 128), base_col=(200, 220, 218), h=78):
    """Table lamp: glass or wood base, stem, drum shade."""
    cyl(cx, cy, 0.09, z, z + 12, base_col, top=shade(base_col, 1.12))
    pygame.draw.line(hc.screen, (160, 150, 120), P(cx, cy, z + 12), P(cx, cy, z + h * 0.55), max(2, int(2 * S)))
    cyl(cx, cy, 0.28, z + h * 0.52, z + h * 0.95, shade_col, top=shade(shade_col, 1.14))


def rug(x0, y0, x1, y1, style="persian", seed=1):
    import paint
    paint.stamp(paint.rug(x1 - x0, y1 - y0, style, seed=seed), x0, y0, x1, y1, 0.6)


def basket(x0, y0, x1, y1, z1=26, col=WICKER):
    """Round wicker basket: banded sides and a darker rim."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(x1 - x0, y1 - y0) / 2
    cyl(cx, cy, r, 0, z1 - 4, col, top=shade(col, 0.78))
    for z in (6, 14, max(4, z1 - 8)):
        cyl(cx, cy, r * 0.98, z, z + 2, shade(col, 1.12))
    cyl(cx, cy, r + 0.02, z1 - 4, z1, shade(col, 0.9), top=shade(col, 0.7))



def bed(x0, y0, x1, y1, head="N", wood=OAK, linen=(232, 226, 214),
        duvet=None, head_h=92, mattress_h=48):
    """Bed with a wood frame, headboard, mattress and folded bedding.
    `head` is the wall the headboard sits against."""
    duvet = duvet or (214, 80, 86)
    box(x0, y0, x1, y1, 0, 18, wood, top=shade(wood, 1.06))
    if head == "N":
        box(x0, y1 - 0.14, x1, y1, 18, head_h, wood, top=shade(wood, 1.12))
        face_quad("S", x0, y1 - 0.14, x1, y1, 18, head_h, 0.08, 0.92, 0.12, 0.88, shade(wood, 0.88))
    elif head == "S":
        box(x0, y0, x1, y0 + 0.14, 18, head_h, wood, top=shade(wood, 1.12))
        face_quad("N", x0, y0, x1, y0 + 0.14, 18, head_h, 0.08, 0.92, 0.12, 0.88, shade(wood, 0.88))
    elif head == "E":
        box(x0, y0, x0 + 0.14, y1, 18, head_h, wood, top=shade(wood, 1.12))
        face_quad("W", x0, y0, x0 + 0.14, y1, 18, head_h, 0.08, 0.92, 0.12, 0.88, shade(wood, 0.88))
    else:
        box(x1 - 0.14, y0, x1, y1, 18, head_h, wood, top=shade(wood, 1.12))
        face_quad("E", x1 - 0.14, y0, x1, y1, 18, head_h, 0.08, 0.92, 0.12, 0.88, shade(wood, 0.88))
    inset = 0.06
    fabric_box(x0 + inset, y0 + inset, x1 - inset, y1 - inset, 18, mattress_h, linen)
    # duvet folded toward the foot
    if head == "N":
        fabric_box(x0 + inset, y0 + inset, x1 - inset, y1 - 0.55, mattress_h, mattress_h + 10, duvet)
        fabric_box(x0 + 0.16, y1 - 0.52, x1 - 0.16, y1 - 0.22, mattress_h, mattress_h + 14, (244, 240, 232))
    elif head == "S":
        fabric_box(x0 + inset, y0 + 0.55, x1 - inset, y1 - inset, mattress_h, mattress_h + 10, duvet)
        fabric_box(x0 + 0.16, y0 + 0.22, x1 - 0.16, y0 + 0.52, mattress_h, mattress_h + 14, (244, 240, 232))
    elif head == "E":
        fabric_box(x0 + 0.55, y0 + inset, x1 - inset, y1 - inset, mattress_h, mattress_h + 10, duvet)
        fabric_box(x0 + 0.22, y0 + 0.16, x0 + 0.52, y1 - 0.16, mattress_h, mattress_h + 14, (244, 240, 232))
    else:
        fabric_box(x0 + inset, y0 + inset, x1 - 0.55, y1 - inset, mattress_h, mattress_h + 10, duvet)
        fabric_box(x1 - 0.52, y0 + 0.16, x1 - 0.22, y1 - 0.16, mattress_h, mattress_h + 14, (244, 240, 232))


def sash(side, u0, u1, ext, z0=52, z1=206, curtains=None):
    """Sash window with optional curtains; delegates to the house helper."""
    kw = {} if curtains is None else {"curtains": curtains}
    hc.sash_window(side, u0, u1, ext, z0=z0, z1=z1, **kw)


def picture(side, u0, u1, z0, z1, inner, frame=(48, 36, 28)):
    """Simple framed picture on a wall. `inner` is an RGB fill."""
    k = hc.wall_k(side)
    hc.wall_quad(side, u0, u1, z0, z1, shade(frame, k), 0.02)
    hc.wall_quad(side, u0 + 0.04, u1 - 0.04, z0 + 4, z1 - 4, shade(inner, k), 0.024)
