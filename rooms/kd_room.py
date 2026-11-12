"""The Kitchen + Dining Room, described ONCE in world coordinates (house_common
KD_*: x = tiles west from the dining room's east wall, y = tiles north from the
south wall), and drawn for any view and either camera.

Both pictures of the room (mock_kitchen: world x 8.2 .. 16.4; mock_dining:
0 .. 8.2) call render(). Each draws the whole room twice:
  * the room itself: the view's own x range, depth-tested;
  * beyond its open side: the other half, from the same description, on a
    depth-tested glimpse layer, faded with distance and pasted by depth.
So the kitchen seen from the dining room and the kitchen's own view are the
same objects, and what hides what comes from their 3D positions.

Walls and their openings are listed once (OPENINGS). Whether a wall is far
(solid, real window / doorway onto the next room) or near (ghost, faint frame)
comes from the camera (house_common.wall_is_far), not from the view.
"""
import random

import numpy as np

import house_common as hc
from house_common import (P, poly, qy, KY, KX, WALL_H, DOOR_H, WHITE, OFF_WHITE, SLATE,
                          KD_LEN, KD_DEP, KD_SPLIT, GREEN, shade, world)
import kd_furniture as F
import glimpses

RD = KD_DEP
FLOOR_SEED = ((0.0, KD_SPLIT, 21), (KD_SPLIT, KD_LEN, 8))     # one slate pattern per half, whichever view
FADE_FAR = (1.6, 8.2)       # beyond a FAR open side: opaque .. gone (tiles past the edge)
FADE_NEAR = (0.3, 3.6)      # beyond a NEAR open side (it lies over the room): fades sooner


# ------------------------------------------------------------- outside
def garden_north(side, rnd):
    """Lawn, path, border, fence and hedge outside the garden wall, world x."""
    hc.ext_lawn(side, -6, 26, 0.15, 6.5, rnd)
    hc.ext_paving(side, -6, 26, 0.2, 1.15, rnd)
    hc.ext_border(side, -6, 26, 1.2, 1.7, rnd)
    hc.ext_picket_fence(side, -6, 26, 2.05, h=40)
    hc.ext_hedge(side, -6, 26, 3.05, 3.65, h=100, rnd=rnd)
    hc.ext_shrub(side, 9.3, 2.35, r=0.32, h=48, rnd=random.Random(4))
    hc.ext_shrub(side, 14.8, 2.45, r=0.36, h=52, rnd=random.Random(7))


def garden_east(side, rnd):
    """Beyond the dining room's east wall: paved path, lawn, the tall hedge."""
    hc.ext_tree(side, 6.0, 5.2, trunk=150, canopy=200, r=1.4, rnd=random.Random(7))
    hc.ext_lawn(side, -10, 20, 0.8, 9, rnd)
    hc.ext_hedge(side, -10, 20, 3.6, 4.4, h=130, col=(36, 102, 42), rnd=random.Random(8))
    hc.ext_picket_fence(side, -10, 20, 2.9)
    hc.ext_border(side, -10, 20, 1.7, 2.15, rnd)
    hc.ext_paving(side, -10, 20, 0.15, 1.55, rnd, col=(170, 160, 142), slab=0.5)
    hc.ext_house_shadow(side, -10, 20, depth=1.0)


# ------------------------------------------------------------- walls and openings
# (kind, engine side, span, extra). Sides: N y = 0 (south wall), S y = RD
# (garden wall), W x = 0 (dining east wall, span = y range), E x = KD_LEN
# (kitchen west wall, span = y range).
OPENINGS = [
    ("door", "N", F.K_HALL_DOOR, (glimpses.hall_from_kd, (226, 222, 212))),
    ("door", "N", F.K_DRAWING_DOOR, (glimpses.drawing_from_kd, shade(GREEN, KY))),
    ("sash", "W", F.D_SASH, (garden_east, (150, 172, 190))),
    ("french", "S", F.D_FRENCH, (garden_north, (156, 190, 216))),
    ("window", "S", F.K_WIN2, (garden_north, (156, 190, 216))),
    ("window", "S", F.K_WIN1, (garden_north, (156, 190, 216))),
    ("door", "E", F.K_BOOT_DOOR, None),          # the next room is the build's (glimpses.boot_from_kitchen)
]
WINDOW_Z = (112, 208)


def _wx(side, span):
    """World x extent of an opening."""
    if side in ("N", "S"):
        return span
    return (0.0, 0.0) if side == "W" else (KD_LEN, KD_LEN)


def _ext(spec):
    fn, haze = spec
    return hc.exterior_layer({"S": fn} if fn is garden_north else {"W": fn}, haze=haze)


def far_openings(w0, w1, in_room, sides="NSWE"):
    """Real openings on whichever walls face the camera, world x in [w0, w1].
    Inside the room a window on a near back wall is still drawn: the engine
    puts it on the ghost layer. A doorway in a near wall shows nothing.
    Beyond an open side only the long walls are drawn (the end walls are
    faded out by then)."""
    exts = {}
    for kind, side, span, extra in OPENINGS:
        if side not in sides or (not in_room and side in "WE"):
            continue
        a, b = _wx(side, span)
        if b < w0 - 0.01 or a > w1 + 0.01:
            continue
        far = hc.wall_is_far(side)
        if kind == "door" and side in ("N", "W") and far:
            fn, haze = extra
            view = hc.exterior_layer({side: lambda s, rnd, fn=fn: fn()}, haze=haze)
            hc.doorway_back(side, *span, view)
        elif kind == "sash" and (far or in_room):
            key = id(extra[0])
            exts.setdefault(key, _ext(extra))
            hc.sash_window(side, *span, exts[key], curtains=(226, 218, 196))
        elif kind in ("window", "french") and far:
            key = id(extra[0])
            exts.setdefault(key, _ext(extra))
            if kind == "window":
                hc.sash_on_far(side, *span, exts[key], *WINDOW_Z, cols=2)
            else:
                hc.glazed_doors_on_S(*span, exts[key])


def french_door_polys():
    """Glazing bars and cream curtains of the French doors, faint in a ghost garden wall."""
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


def sage_cupboard_frame():
    """The sage cupboard in the west wall as a faint frame (a near wall: its doors face away)."""
    c = (150, 176, 164)
    a, b = F.K_SAGE
    WE = lambda u, z: P(KD_LEN + .1, u, z)
    out = []
    for u0, u1, z0, z1 in ((a - .06, a, 0, 156), (b, b + .06, 0, 156), (a - .06, b + .06, 150, 156), ((a + b) / 2 - .01, (a + b) / 2 + .01, 0, 150)):
        out.append((shade(c, KX), [WE(u0, z0), WE(u1, z0), WE(u1, z1), WE(u0, z1)]))
    return out


def near_wall_kwargs(x0):
    """ghost_near_walls arguments for the room's S and E walls (view-local spans).
    Near: faint window frames, ghost door frames, the French doors' bars.
    Far (the build paints them solid): doorways only; windows and the French
    doors are drawn for real by far_openings."""
    rw = hc.RW
    kw = {"doors_S": [], "doors_E": [], "windows_S": [], "extra_polys": []}
    near_s = not hc.wall_is_far("S")
    for kind, side, span, extra in OPENINGS:
        a, b = _wx(side, span)
        if side == "S":
            loc = (span[0] - x0, span[1] - x0)
            if loc[1] < 0 or loc[0] > rw:
                continue
            if kind == "window" and near_s:
                kw["windows_S"].append(loc)
            elif kind == "french" and near_s:
                kw["doors_S"].append(loc)
                with world(x0):
                    kw["extra_polys"] += french_door_polys()
        elif side == "E" and x0 <= a - 0.01 <= x0 + rw:
            if kind == "door":
                kw["doors_E"].append(span)
    if x0 + rw >= KD_LEN - 0.01:          # the kitchen's west wall is in this view
        with world(x0):
            kw["extra_polys"] += sage_cupboard_frame()
    return kw


# ------------------------------------------------------------- floor and plain walls
def floor(w0, w1):
    """Slate over the halves touching [w0, w1]: each half has one pattern."""
    for a, b, seed in FLOOR_SEED:
        if b > w0 + 0.01 and a < w1 - 0.01:
            hc.floor_slate(a, 0, b, RD, seed=seed)


def far_wall_run(w0, w1):
    """The plain run of whichever long wall faces the camera, world x w0..w1:
    slab, skirting and its dark cap (beyond an open side)."""
    if hc.wall_is_far("N"):
        y, out = 0.0, -.28
    else:
        y, out = RD, RD + .28
    qy(y, w0, w1, 0, WALL_H, shade(OFF_WHITE, KY))
    qy(y + (.001 if y == 0 else -.001), w0, w1, 0, 13, shade(WHITE, KY))
    poly([P(w0, y, WALL_H), P(w1, y, WALL_H), P(w1, out, WALL_H), P(w0, out, WALL_H)], (60, 58, 54))
    if not hc.wall_is_far("S"):
        hc.floor_edge_S(w0, w1, SLATE[1])         # the floor's lip along a near garden wall


# ------------------------------------------------------------- what stands in the room
def contents():
    """Every piece of furniture and fitting in the room, world coordinates.
    No camera checks: faces are tagged (hc.facing / hc.on_wall) and the
    z-buffer sorts the rest."""
    F.dining_east_wall_furniture()
    F.dining_south_wall()
    F.round_rug((F.D_FRENCH[0] + F.D_FRENCH[1]) / 2, 7.5)
    F.dining_table_set()
    F.peninsula_chairs()
    F.peninsula()
    F.kitchen_south_wall()
    F.kitchen_island_and_stools()
    F.kitchen_run_floor()
    F.kitchen_seen_from_south()
    F.kitchen_north_wall_front()
    with hc.hung_layer(96):               # cupboard over the boot door (west wall): faint when that wall is near
        hc.box(KD_LEN - .55, 0, KD_LEN, F.K_BOOT_DOOR[1] + .2, DOOR_H + 8, WALL_H, F.CAB)


# ------------------------------------------------------------- one view
def render(mod, x0, title, subtitle, out, copies=(), sprite=None):
    """Draw the view whose local x = 0 is world x0 (KD_VIEWS). `mod` is the
    calling room module: the build patches its ghost_near_walls / finish /
    place_sprite, so those are looked up there."""
    rw = hc.RW
    open_lo = x0 > 0.01                   # open on the local x = 0 side (kitchen)
    open_hi = x0 + rw < KD_LEN - 0.01     # open on the local x = RW side (dining)
    hc.FAR_X0 = not open_lo               # an open x = 0 side is not a backdrop wall

    # beyond the open side: the other half, same description, faded by distance
    edge, toward = (0.0, -1) if open_lo else (rw, 1)
    far = hc.sees("+x") if toward < 0 else hc.sees("-x")
    d0, d1 = FADE_FAR if far else FADE_NEAR
    b0, b1 = sorted((x0 + edge, x0 + edge + toward * d1))
    # Two layers, both depth-tested: the shell (floor, far wall, its openings)
    # and the furniture, so faded furniture still shows its own floor behind
    # it rather than the dark backdrop.
    # A near open side lies over the room: its still-opaque first stretch must
    # hide a character walking behind it, like the room's own furniture.
    occ = None if far else tuple(sorted((edge, edge + toward * (d0 + d1) / 2)))
    shell, stuff = hc.glimpse_layer(), hc.glimpse_layer()
    zs, zf = hc.z_layer(shell), hc.z_layer(stuff, occ_window=occ)
    with zs, world(x0):
        floor(b0, b1)
        far_wall_run(b0, b1)
        far_openings(b0, b1, in_room=False)
    with zf, world(x0), hc.x_clip(0, rw, inside=False):
        contents()
    for lay, z in ((shell, zs), (stuff, zf)):
        hc.fade_x(lay, edge + toward * d0, edge + toward * d1, zbuf=z.zbuf)

    # the room itself
    hc.background()
    with world(x0):
        floor(x0, x0 + rw)
    hc.floor_slab(SLATE[1]) if not open_hi else hc.floor_edge_S(0, rw, SLATE[1])
    hc.wall_shell(OFF_WHITE, open_W=open_lo)
    hc.wall_trim(cornice=False, col=WHITE, open_W=open_lo, open_E=open_hi)
    with world(x0):
        far_openings(x0, x0 + rw, in_room=True, sides="NW")     # back walls (x = 0 / y = 0)
        with hc.x_clip(0, rw, inside=True):
            contents()
    if sprite:
        mod.place_sprite(*sprite)
    mod.ghost_near_walls(OFF_WHITE, window_z=WINDOW_Z, window_cols=2, cornice=False, curtains=None,
                         open_E=open_hi, open_W=open_lo, **near_wall_kwargs(x0))
    with world(x0):
        far_openings(x0, x0 + rw, in_room=True, sides="SE")     # on the walls just painted, when they are far
    shell.blit(stuff, (0, 0))              # faded furniture over its own faded floor and wall
    zb = np.where(zf.zbuf > -1e8, zf.zbuf, zs.zbuf)
    hc.paste_glimpse(shell, zb, depth_test=True)
    mod.finish(title, out, subtitle=subtitle, copies=copies)
