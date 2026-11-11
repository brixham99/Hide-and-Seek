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


def _hall_beyond(side, rnd):
    import glimpses
    glimpses.hall_from_dining()


def _gl():
    """How much of the kitchen is drawn past the open side."""
    return KD_LEN - RW if hc.FLIP else GL


def kitchen_back():
    """The kitchen's floor and far wall carrying on past the open side.
    Usual view: its south wall, with the open doorway into the Hall (the Hall
    itself shows through it). Opposite view: the garden wall, with the east
    window over the bins (glass onto the garden)."""
    gl = _gl()
    floor_slate(RW, 0, RW + gl, RD, seed=8)
    if not hc.FLIP:
        floor_edge_S(RW, RW + gl, SLATE[1])
        qy(0, RW, RW + gl, 0, WALL_H, shade(OFF_WHITE, KY))
        qy(.001, RW, RW + gl, 0, 13, shade(WHITE, KY))
        a, b = F.K_HALL_DOOR
        hall = exterior_layer({"N": _hall_beyond}, haze=(196, 190, 204))
        doorway_back("N", a, b, hall)
        poly([P(RW, 0, WALL_H), P(RW + gl, 0, WALL_H), P(RW + gl, -.28, WALL_H), P(RW, -.28, WALL_H)], (60, 58, 54))
        return
    # opposite view: the garden wall is the far one
    qy(RD, RW, RW + gl, 0, WALL_H, shade(OFF_WHITE, KY))
    qy(RD - .001, RW, RW + gl, 0, 13, shade(WHITE, KY))
    a, b = F.K_WIN2
    qy(RD - .002, a - .07, b + .07, 105, 215, shade(WHITE, KY))
    qy(RD - .003, a, b, 112, 208, (150, 182, 206))                  # sky and hedge through the glass
    qy(RD - .004, a, b, 112, 150, (70, 112, 62))
    for u in (a, (a + b) / 2 - .02, b - .04):
        qy(RD - .005, u, u + .04, 112, 208, shade(WHITE, KY))
    qy(RD - .005, a, b, 158, 162, shade(WHITE, KY))
    poly([P(RW, RD, WALL_H), P(RW + gl, RD, WALL_H), P(RW + gl, RD + .28, WALL_H), P(RW, RD + .28, WALL_H)], (60, 58, 54))


def kitchen_front():
    if not hc.FLIP:
        F.kitchen_south_wall()
        F.kitchen_island_and_stools()
        F.kitchen_run_floor()
        return
    # opposite view: the run along the garden wall shows its fronts, the
    # cabinets, hood and cubbies hang on the wall; the island in front.
    # The south-wall pier and larders are on the near side, out of shot.
    F.kitchen_north_wall_front()
    F.kitchen_run_floor()
    F.kitchen_seen_from_south()
    F.kitchen_island_and_stools()


def beam_polys():
    # The ceiling beam at the join was drawn on the ghost layer, so it lay
    # across the other half of the room as a long white slab. The fade marks
    # the join instead; no beam in either camera.
    return []
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


def kitchen_beyond_front():
    """The kitchen's furniture past the open side, on its own depth-tested,
    faded layer, pasted onto the room."""
    front = glimpse_layer()
    zf = z_layer(front)
    with zf, world(X0):
        kitchen_front()
    ff = (RW + 1.2, RW + 7.6) if hc.FLIP else (RW + .3, RW + 3.6)
    paste_glimpse(fade_x(front, *ff, z_ref=70, zbuf=zf.zbuf), zf.zbuf)


def main():
    background()
    floor_slate(0, 0, RW, RD, seed=21)
    floor_edge_S(0, RW, SLATE[1])
    back = glimpse_layer()
    zb = z_layer(back)
    with zb, world(X0):
        kitchen_back()
    # usual view: the kitchen comes nearer (near-left), faded quickly;
    # opposite view: it is the far side, so more of it shows
    fb = (RW + 1.2, RW + 7.6) if hc.FLIP else (RW + .4, RW + 3.4)
    paste_glimpse(fade_x(back, *fb, zbuf=zb.zbuf), zb.zbuf)
    if hc.FLIP:
        # Opposite view: the kitchen is the FAR side, so its units go down
        # before the dining room's furniture. Blitted last they were pasted
        # over the peninsula (the bins showed through its worktop and doors).
        kitchen_beyond_front()
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
    if not hc.FLIP:
        kitchen_beyond_front()      # usual view: the kitchen is the nearer side, over the room
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
