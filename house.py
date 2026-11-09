"""The downstairs on one house grid, in HOUSE_CAMERA (house_common.py): every room
uses the same axes, x = tiles west from the room's east wall, y = tiles north
from its south wall. ORIGIN is the room's (east wall, south wall) corner on the
house grid (house X west, Y north; the Kitchen + Dining Room's south-east corner
is 0, 0). The mocks were drawn at slightly different tile scales, so the grid
is approximate; the doorways themselves are paired exactly in PORTALS.

Walls: "S" = south (y = 0, back-right on screen), "N" = north (y = RD, near-right
ghost), "E" = east (x = 0, back-left), "W" = west (x = RW, near-left ghost).
The garage has no mock yet: its walls are solid.
"""

ROOMS = {
    #  id         label            RW     RD     origin (X, Y)   views: (view id, local x0, x from, x to)
    "hall":    dict(name="Hall", rw=3.2, rd=8.05, origin=(6.55, -8.25), views=[("hall", 0.0, 0, 99)]),
    "sitting": dict(name="Sitting Room", rw=7.1, rd=6.6, origin=(-0.75, -8.25), views=[("sitting", 0.0, 0, 99)]),
    "drawing": dict(name="Drawing Room", rw=7.3, rd=7.8, origin=(9.95, -8.0), views=[("drawing", 0.0, 0, 99)]),
    "kd":      dict(name="Kitchen", rw=16.4, rd=8.4, origin=(0.0, 0.0),
                    views=[("dining", 0.0, -99, 8.2), ("kitchen", 8.2, 8.2, 99)]),
    "boot":    dict(name="Boot Room", rw=6.4, rd=3.1, origin=(16.6, -0.65), views=[("boot", 0.0, 0, 99)]),
    "utility": dict(name="Utility", rw=3.6, rd=5.8, origin=(16.6, 2.65), views=[("utility", 0.0, 0, 99)]),
    "office":  dict(name="Office", rw=3.6, rd=6.0, origin=(20.85, 2.65), views=[("office", 0.0, 0, 99)]),
    "wc":      dict(name="Dragon Toilet", rw=1.65, rd=3.1, origin=(23.2, -0.65), views=[("wc", 0.0, 0, 99)]),
}
VIEW_NAMES = {"kitchen": "Kitchen", "dining": "Dining Room"}
KD_SPLIT = 8.2

# open internal doorways, paired: (room, wall, a, b) <-> (room, wall, a, b); a..b along the wall
PORTALS = [
    (("hall", "N", 1.9, 3.07), ("kd", "S", 8.45, 9.7)),
    (("hall", "E", .75, 1.8), ("sitting", "W", .75, 1.8)),
    (("hall", "W", .6, 1.85), ("drawing", "E", .4, 1.85)),
    (("drawing", "N", 5.75, 7.0), ("kd", "S", 14.9, 16.15)),
    (("kd", "W", .2, 1.5), ("boot", "E", .85, 2.3)),
    (("boot", "N", 2.15, 3.45), ("utility", "S", 2.3, 3.45)),
    (("boot", "N", 4.4, 5.7), ("office", "S", .15, 1.6)),
    (("boot", "W", .9, 2.3), ("wc", "E", .9, 2.3)),
]

# main furniture footprints (x0, y0, x1, y1), room-local tiles
SOLIDS = {
    "hall": [(0, 3.0, 1.85, 8.05), (2.82, 2.5, 3.2, 4.2)],                         # stairs, radiator cover
    "sitting": [(0, 0, 4.9, 1.6), (0, 0, 1.6, 3.0), (5.4, 0, 6.95, .55), (.08, 3.25, .66, 3.85),
                (.08, 4.75, 1.3, 5.95), (2.6, 2.8, 3.6, 3.8), (5.55, 2.05, 7.0, 5.35), (4.95, 6.05, 6.95, 6.6),
                (1.88, 5.72, 4.67, 6.6)],
    "drawing": [(3.45, 0, 7.3, 1.55), (5.75, 0, 7.3, 3.35), (.25, 0, 1.9, .6), (3.0, 2.3, 5.2, 3.2),
                (6.4, 3.9, 7.28, 6.15), (.85, 7.05, 3.55, 7.75), (0, 2.35, .55, 4.5), (0, 4.5, .55, 6.85)],
    "kd": [(8.3, 7.38, 16.4, 8.4), (7.15, 4.2, 8.17, 8.4), (10.1, 3.8, 13.5, 5.4), (10.75, 0, 11.35, .45),
           (11.4, 0, 12.45, .9), (12.55, 0, 14.55, 1.0), (1.9, 1.2, 4.2, 6.2), (2.4, 0, 5.5, .8),
           (5.65, .12, 6.1, .58), (6.2, 0, 6.7, .7), (0, 4.8, .6, 6.5), (0, 1.4, .38, 3.4),
           # ladder chairs round the dining table, island stools, peninsula stools
           (1.64, 1.98, 2.06, 2.42), (1.64, 3.48, 2.06, 3.92), (1.64, 4.98, 2.06, 5.42),
           (2.84, 0.84, 3.26, 1.26), (2.84, 6.14, 3.26, 6.56),
           (4.04, 1.98, 4.46, 2.42), (4.04, 3.48, 4.46, 3.92), (4.04, 4.98, 4.46, 5.42),
           (10.56, 3.02, 11.04, 3.48), (11.56, 3.02, 12.04, 3.48), (12.56, 3.02, 13.04, 3.48),
           (6.38, 4.68, 6.82, 5.12), (6.38, 5.53, 6.82, 5.97), (6.38, 6.38, 6.82, 6.82),
           (6.38, 7.23, 6.82, 7.67)],
    "boot": [(1.85, 0, 4.05, .75), (.15, 0, 1.38, .3)],
    "utility": [(0, 2.6, 1.0, 4.88), (0, 4.9, .9, 5.8), (.92, 4.8, 3.6, 5.8), (2.85, 1.2, 3.45, 1.8)],
    "office": [(.02, 1.65, .6, 3.6), (0, 3.8, 1.1, 5.92), (1.3, 4.65, 1.8, 5.15), (2.2, .25, 3.3, 1.35),
               (2.55, 3.95, 3.2, 4.6), (2.88, 4.95, 3.56, 5.95)],
    "wc": [(.6, 1.9, 1.08, 3.1), (0, 2.76, .36, 3.1), (.92, 0, 1.6, .6)],
}

R = 0.22                     # Archie's footprint radius (tiles)


def portals_of(room):
    """[(wall, a, b, (to_room, to_wall, ta, tb))] for one room."""
    out = []
    for p, q in PORTALS:
        if p[0] == room:
            out.append((p[1], p[2], p[3], q))
        if q[0] == room:
            out.append((q[1], q[2], q[3], p))
    return out


def blocked(room, x, y, r=R):
    for x0, y0, x1, y1 in SOLIDS[room]:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return True
    return False


def free(room, x, y, r=R):
    """Inside the room (or in one of its doorways) and clear of furniture."""
    rm = ROOMS[room]
    rw, rd = rm["rw"], rm["rd"]
    inside = r <= x <= rw - r and r <= y <= rd - r
    if not inside:
        for wall, a, b, _ in portals_of(room):
            u = x if wall in ("S", "N") else y
            n = {"S": -y, "N": y - rd, "E": -x, "W": x - rw}[wall]   # how far through the wall
            if a + r <= u <= b - r and n <= 0.5 and (n > -r - 1e-9):
                inside = True
                break
    return inside and not blocked(room, x, y, r)


def crossing(room, x, y):
    """If (x, y) is through one of the room's doorways, the (room, x, y) on the other side."""
    rm = ROOMS[room]
    rw, rd = rm["rw"], rm["rd"]
    for wall, a, b, (troom, twall, ta, tb) in portals_of(room):
        u = x if wall in ("S", "N") else y
        n = {"S": -y, "N": y - rd, "E": -x, "W": x - rw}[wall]
        if a <= u <= b and n > 0.05:
            t = (u - a) / (b - a)
            tu = ta + t * (tb - ta)
            trw, trd = ROOMS[troom]["rw"], ROOMS[troom]["rd"]
            inset = R + 0.1
            nx, ny = {"S": (tu, inset), "N": (tu, trd - inset), "E": (inset, tu), "W": (trw - inset, tu)}[twall]
            return troom, nx, ny
    return None


def view_for(room, x, prev=None):
    """Which pre-rendered view shows this spot (the kitchen + dining slide at the beam)."""
    views = ROOMS[room]["views"]
    if len(views) == 1:
        return views[0]
    if prev is not None and prev[0] in [v[0] for v in views]:
        lo, hi = prev[2], prev[3]
        if lo - .15 <= x <= hi + .15:      # a little hysteresis at the beam
            return prev
    for v in views:
        if v[2] <= x < v[3]:
            return v
    return views[-1]


def label(room, view):
    return VIEW_NAMES.get(view[0], ROOMS[room]["name"])


def house_xy(room, x, y):
    ox, oy = ROOMS[room]["origin"]
    return ox + x, oy + y
