"""Shared drawing kit for the 'Hide and Seek' room mock-ups (Anderson house).

Same geometry as the Haunted Mansion engine (2:1 iso, TILE 112x56, WALL_H 230,
Archie 160 px); 1 tile ~ 0.55 m. Engine axes: x runs along the upper-right
back wall (y = 0, side "N"), y along the upper-left back wall (x = 0, side
"W"); the near walls are y = RD (side "S") and x = RW (side "E"), drawn as
Haunted Mansion's see-through ghost walls with ghost door frames.

A room script does:
    import house_common as hc
    hc.init_room(w_tiles, d_tiles)
    from house_common import *        # after init_room, so RW/RD/screen are set
    ... draw back to front ...
    finish("Room name", out_path)

HOUSE-WIDE CAMERA (HOUSE_CAMERA below): every room is viewed the same way,
looking plan-south-east (plan: top = back/garden = "north", bottom = front
door = "south", left = west, right = east). Back-left wall (x = 0, "W") is
the room's EAST wall; back-right wall (y = 0, "N") is its SOUTH wall; the
nearest corner is north-west, so the near walls are the NORTH (y = RD, "S")
and WEST (x = RW, "E") walls. Room x runs westwards from the east wall,
room y northwards from the south wall.

Outside world: exterior_layer({side: drawer}) renders a real ground plane
behind the back walls, shown only through openings with show_through().
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
HM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repo root (assets/characters)
import pygame  # noqa: E402
import numpy as np  # noqa: E402
from hm_engine import TILE_W, TILE_H, WALL_H, DOOR_H  # noqa: E402
import hm_engine as art  # noqa: E402  (Haunted Mansion colour helpers)
import hm_engine as HMG  # noqa: E402  (Haunted Mansion: ghost door frame pieces)
# The real engine pieces, kept before build_rooms patches HMG for a view.
_HM_frame_polys = HMG.door_frame_polys
_HM_polys_layer = HMG.polys_layer

WIN_W, WIN_H = 1280, 720
S = 2                                  # supersampling
HW, HH = TILE_W / 2, TILE_H / 2
SLAB = 18
RW, RD = 6.0, 6.0
OX, OY = 640, 262
shade = art.shade

# ------------------------------------------------------------------ palette
GREEN = (46, 82, 72)                   # Drawing Room walls
WHITE = (234, 230, 218)
CREAM = (226, 216, 190)
PINE1_, PINE2_ = (196, 116, 56), (178, 100, 46)
PINK = (196, 150, 150)                 # dusky pink curtains
NAVY = (44, 52, 78)
GOLD = (206, 166, 92)
BRASS = (200, 164, 70)
DARK_WOOD = (92, 52, 32)
OAK = (150, 102, 60)
BLACK = (26, 26, 28)
TEAL = (40, 104, 118)
SAGE = (150, 166, 148)                 # Boot Room walls and doors
IRON = (30, 30, 32)
TERRACOTTA = (176, 84, 56)

screen = None
_inited = False
_room_screen = None          # the room canvas; glimpse/exterior layers are not this
_occluders = []              # (x0, y0, x1, y1, z0, z1) in view-local tiles


def init_room(rw, rd, ox=None, oy=None):
    """Set the room size (tiles) and screen origin, and make the 2x canvas."""
    global RW, RD, OX, OY, screen, _inited, _room_screen, _occluders
    RW, RD = rw, rd
    OX = ox if ox is not None else 640 - (rw - rd) * HW / 2
    if oy is None:     # centre the room (walls + floor) vertically
        span = (rw + rd) * HH + WALL_H
        oy = (WIN_H - span) / 2 + WALL_H + 10
    OY = oy
    if not _inited:
        pygame.init()
        pygame.display.set_mode((WIN_W, WIN_H))
        _inited = True
    # 24-bit, no per-pixel alpha. On macOS convert() matches a display format that
    # HAS alpha, and any later SRCALPHA blit (floors, vignette) then stores
    # source alpha into the canvas and the room interior is saved transparent.
    screen = pygame.Surface((WIN_W * S, WIN_H * S), depth=24)
    _room_screen = screen
    _occluders = []
    return screen


def _note_occluder(x0, y0, x1, y1, z0, z1):
    """Remember a solid volume so the game can hide Archie behind it.

    Coordinates are whatever `box` was given (world x under `world()`); they are
    stored in the view's local frame, matching game.to_screen.
    """
    if screen is not _room_screen:
        return
    x0, x1 = (x0 - X_OFF), (x1 - X_OFF)
    y0, y1 = (y0 - Y_OFF), (y1 - Y_OFF)
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    if w < 0.08 or d < 0.08:
        return
    tall = h >= 16 and min(w, d) >= 0.12
    top = z1 >= 24 and w * d >= 0.28 and h >= 3
    if not (tall or top):
        return
    if x1 < -0.4 or y1 < -0.4 or x0 > RW + 0.6 or y0 > RD + 0.6:
        return
    _occluders.append((x0, y0, x1, y1, z0, z1))


def occlude(x0, y0, x1, y1, z0, z1):
    """Mark a volume the character should render behind (stairs, and so on)."""
    _note_occluder(x0, y0, x1, y1, z0, z1)


def raster_depth():
    """Per-pixel occluder depth (view-local x + y) at the final 1280x720 frame.

    0 means nothing solid (floor, empty backdrop). Larger values are closer to
    the camera. Returns a float32 array indexed [x, y].
    """
    buf = np.zeros((WIN_W, WIN_H), np.float32)
    for x0, y0, x1, y1, z0, z1 in _occluders:
        _stamp_face(buf, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], "y", y1)
        _stamp_face(buf, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], "x", x1)
        _stamp_face(buf, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], "z", z1)
    return buf


def _proj1(x, y, z):
    """Unscaled screen point. When the opposite view is being built, spin the
    room 180° so the old near corner becomes the far one."""
    if FLIP:
        x, y = RW - x, RD - y
    return (OX + (x - y) * HW, OY + (x + y) * HH - z)


def _stamp_face(buf, corners, kind, val):
    poly = [_proj1(*c) for c in corners]
    area = 0.0
    for i in range(4):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % 4]
        area += ax * by - bx * ay
    if abs(area) < 8:
        return
    sign = 1.0 if area > 0 else -1.0
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0 = max(0, int(math.floor(min(xs))))
    y0 = max(0, int(math.floor(min(ys))))
    x1 = min(buf.shape[0], int(math.ceil(max(xs))) + 1)
    y1 = min(buf.shape[1], int(math.ceil(max(ys))) + 1)
    if x1 - x0 < 1 or y1 - y0 < 1:
        return
    gx = np.arange(x0, x1, dtype=np.float32)[:, None] + 0.5
    gy = np.arange(y0, y1, dtype=np.float32)[None, :] + 0.5
    m = np.ones((x1 - x0, y1 - y0), dtype=bool)
    for i in range(4):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % 4]
        cross = (bx - ax) * (gy - ay) - (by - ay) * (gx - ax)
        m &= cross * sign >= -0.75
    if not m.any():
        return
    if FLIP:
        # same world x+y as the normal view, from the spun projection
        if kind == "z":
            d = RW + RD - (gy - OY + val) / HH
        elif kind == "y":
            d = RW - RD + 2 * val - (gx - OX) / HW
        else:
            d = RD - RW + 2 * val + (gx - OX) / HW
    elif kind == "z":
        d = (gy - OY + val) / HH
    elif kind == "y":
        d = 2 * val + (gx - OX) / HW
    else:
        d = 2 * val - (gx - OX) / HW
    region = buf[x0:x1, y0:y1]
    region[:] = np.where(m & (d > region), d, region)


X_OFF = 0.0                            # world -> local x shift while drawing in world coords (see world())
Y_OFF = 0.0                            # same for y (a doorway glimpse of another room)
FLIP = False                           # opposite view: 180° around the room
_zbuf = None                           # closeness (larger = nearer the flipped camera)
_fg_surf = None                        # near walls, drawn over Archie
_pinf = {}                             # screen point -> (local x, local y, z, closeness)


def begin_flip(fg_surface):
    """Start the opposite-view build. `fg_surface` receives the new near walls."""
    global FLIP, _zbuf, _fg_surf, _pinf
    FLIP = True
    _zbuf = np.zeros((screen.get_width(), screen.get_height()), np.float32)
    _fg_surf = fg_surface
    _pinf = {}


def end_flip():
    global FLIP, _zbuf, _fg_surf, _pinf
    FLIP = False
    _zbuf = None
    _fg_surf = None
    _pinf = {}


def _flip_draw():
    """Z-sorted drawing only while painting the room itself, not a glimpse layer."""
    return FLIP and _zbuf is not None and (screen is _room_screen or screen is _fg_surf)


def P(x, y, z=0.0):
    xl = x - X_OFF
    yl = y - Y_OFF
    if FLIP:
        xd, yd = RW - xl, RD - yl
        close = xd + yd
    else:
        xd, yd = xl, yl
        close = xl + yl
    pt = ((OX + (xd - yd) * HW) * S, (OY + (xd + yd) * HH - z) * S)
    if FLIP:
        _pinf[pt] = (xl, yl, z, close)
    return pt


class placed:
    """Temporarily treat coordinates as local to another room.

    dx, dy are added to the current offsets. Pass (origin_here - origin_there)
    so a point in the other room's own tiles lands on this canvas in the right place.
    """
    def __init__(self, dx, dy=0.0):
        self.dx, self.dy = dx, dy

    def __enter__(self):
        global X_OFF, Y_OFF
        self.prev = (X_OFF, Y_OFF)
        X_OFF += self.dx
        Y_OFF += self.dy

    def __exit__(self, *a):
        global X_OFF, Y_OFF
        X_OFF, Y_OFF = self.prev


class world:
    """with world(x0): ... -> helpers take WORLD x for an open-plan room whose
    current view starts at world x0 (e.g. KD_VIEWS["kitchen"])."""
    def __init__(self, x0):
        self.x0 = x0

    def __enter__(self):
        global X_OFF
        self.prev, X_OFF = X_OFF, self.x0

    def __exit__(self, *a):
        global X_OFF
        X_OFF = self.prev


def _near_plane(pts):
    """A vertical face on the east (x ≈ 0) or south (y ≈ 0) wall.

    After the 180° spin those walls are nearest the camera, so they belong on
    the ghost layer: the wall slabs themselves, anything mounted on them
    (pictures, window frames, doors, bricks, panelling) and tall shallow
    fittings (a chimney breast, a wall-hung TV). Low, wide furniture such as
    a sofa back stays on the room so it can be drawn as a finished back.
    """
    infs = [_pinf.get(p) for p in pts]
    if any(i is None for i in infs):
        return False
    xs = [i[0] for i in infs]
    ys = [i[1] for i in infs]
    zs = [i[2] for i in infs]
    on_x = max(xs) - min(xs) < 0.25 and max(abs(v) for v in xs) < 0.58
    on_y = max(ys) - min(ys) < 0.25 and max(abs(v) for v in ys) < 0.58
    if not (on_x or on_y):
        return False
    # A narrow face lying in the plane of a FAR wall (x = RW or y = RD) next
    # to the corner, e.g. the wall or door architrave beside a doorway there,
    # is not on a near wall even though it sits close to it.
    if on_y and max(xs) - min(xs) < 0.02 and min(xs) > RW - 0.3:
        return False
    if on_x and max(ys) - min(ys) < 0.02 and min(ys) > RD - 0.3:
        return False
    zspan = max(zs) - min(zs)
    if zspan <= 6:
        return False
    uspan = (max(ys) - min(ys)) if on_x else (max(xs) - min(xs))
    if zspan > 140:
        return True
    return uspan < 2.05


def _tri_fill(target, a, b, c, da, db, dc, col, alpha, zwrite=True):
    xs, ys = (a[0], b[0], c[0]), (a[1], b[1], c[1])
    x0 = max(0, int(math.floor(min(xs))))
    y0 = max(0, int(math.floor(min(ys))))
    x1 = min(_zbuf.shape[0], int(math.ceil(max(xs))) + 1)
    y1 = min(_zbuf.shape[1], int(math.ceil(max(ys))) + 1)
    if x1 - x0 < 1 or y1 - y0 < 1:
        return
    gx = np.arange(x0, x1, dtype=np.float32)[:, None] + 0.5
    gy = np.arange(y0, y1, dtype=np.float32)[None, :] + 0.5
    area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if abs(area) < 1:
        return
    def edge(p, q):
        return (q[0] - p[0]) * (gy - p[1]) - (q[1] - p[1]) * (gx - p[0])
    w0, w1, w2 = edge(b, c), edge(c, a), edge(a, b)
    if area < 0:
        w0, w1, w2, area = -w0, -w1, -w2, -area
    m = (w0 >= -0.5) & (w1 >= -0.5) & (w2 >= -0.5)
    if not np.any(m):
        return
    depth = (w0 * da + w1 * db + w2 * dc) / area
    sub = _zbuf[x0:x1, y0:y1]
    m &= depth >= sub - 1e-4
    if not np.any(m):
        return
    if zwrite:
        sub[m] = depth[m]
    rgb = pygame.surfarray.pixels3d(target)
    rgb[x0:x1, y0:y1][m] = col
    del rgb
    if target.get_masks()[3] or (target.get_flags() & pygame.SRCALPHA):
        aa = pygame.surfarray.pixels_alpha(target)
        aa[x0:x1, y0:y1][m] = alpha
        del aa


def _fill_poly(target, pts, col, alpha, zwrite=True):
    infs = [_pinf.get(p) for p in pts]
    if any(i is None for i in infs) or len(pts) < 3:
        pygame.draw.polygon(target, col, pts)
        return
    col = tuple(int(c) for c in col[:3])
    ds = [i[3] for i in infs]
    for i in range(1, len(pts) - 1):
        _tri_fill(target, pts[0], pts[i], pts[i + 1], ds[0], ds[i], ds[i + 1], col, alpha, zwrite)


def poly(pts, col, outline=None, w=1):
    if _flip_draw():
        near = _near_plane(pts) and _fg_surf is not None
        # Near walls are the ghost layer: a light tint, and they must not
        # block the furniture drawn on the room behind them.
        if near:
            _fill_poly(_fg_surf, pts, col, 36, zwrite=False)
        else:
            _fill_poly(screen, pts, col, 255, zwrite=True)
        return
    pygame.draw.polygon(screen, col, pts)
    if outline:
        pygame.draw.polygon(screen, outline, pts, max(1, int(w * S)))


def line(a, b, col, w=1):
    pygame.draw.line(screen, col, P(*a), P(*b), max(1, int(w * S)))


# quads on planes: qy = plane y=const (faces +y, lower-left), qx = plane x=const (lower-right), qz = horizontal
def qy(y, xa, xb, za, zb, col, ol=None, w=1):
    poly([P(xa, y, za), P(xb, y, za), P(xb, y, zb), P(xa, y, zb)], col, ol, w)


def qx(x, ya, yb, za, zb, col, ol=None, w=1):
    poly([P(x, ya, za), P(x, yb, za), P(x, yb, zb), P(x, ya, zb)], col, ol, w)


def qz(z, xa, ya, xb, yb, col, ol=None, w=1):
    poly([P(xa, ya, z), P(xb, ya, z), P(xb, yb, z), P(xa, yb, z)], col, ol, w)


KY, KX, KT = 0.90, 0.72, 1.04          # light: +y faces brighter than +x faces


def box(x0, y0, x1, y1, z0, z1, col, top=None, ol=True, faces="xyz"):
    o = (lambda c: shade(c, 0.55)) if ol else (lambda c: None)
    # The opposite view looks at the faces the usual camera never sees.
    y_face, x_face = (y0, x0) if FLIP else (y1, x1)
    if "y" in faces:
        c = shade(col, KY); qy(y_face, x0, x1, z0, z1, c, o(c))
    if "x" in faces:
        c = shade(col, KX); qx(x_face, y0, y1, z0, z1, c, o(c))
    if "z" in faces:
        c = top or shade(col, KT); qz(z1, x0, y0, x1, y1, c, o(c))
    if "x" in faces or "y" in faces or "z" in faces:
        _note_occluder(x0, y0, x1, y1, z0, z1)


def fl_ellipse(cx, cy, rx, ry, col, z=0.0, n=24, ol=None):
    poly([P(cx + rx * math.cos(a), cy + ry * math.sin(a), z) for a in (2 * math.pi * i / n for i in range(n))], col, ol)


def cyl(cx, cy, r, z0, z1, col, top=None):
    """Upright cylinder / cone-less drum."""
    n = 24
    bot = [P(cx + r * math.cos(a), cy + r * math.sin(a), z0) for a in (2 * math.pi * i / n for i in range(n))]
    tp = [P(cx + r * math.cos(a), cy + r * math.sin(a), z1) for a in (2 * math.pi * i / n for i in range(n))]
    xs = [p[0] for p in bot]
    l, rr = min(xs), max(xs)
    yb = P(cx, cy, z0)[1]
    yt = P(cx, cy, z1)[1]
    poly(bot, shade(col, 0.75))
    pygame.draw.rect(screen, shade(col, 0.75), (l, yt, rr - l, yb - yt))
    pygame.draw.rect(screen, shade(col, 0.9), (l, yt, (rr - l) * 0.45, yb - yt))
    poly(tp, top or shade(col, 1.1), shade(col, 0.5))
    if r >= 0.16 and z1 >= 22:
        rr = r * 0.9
        _note_occluder(cx - rr, cy - rr, cx + rr, cy + rr, min(z0, z1), max(z0, z1))


def cone(cx, cy, r0, r1, z0, z1, col):
    """Lampshade: radius r0 at the bottom, r1 at the top (screen-space trapezoid + ellipses)."""
    n = 24
    b = [P(cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0) for a in (2 * math.pi * i / n for i in range(n))]
    t = [P(cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1) for a in (2 * math.pi * i / n for i in range(n))]
    bl, br = min(p[0] for p in b), max(p[0] for p in b)
    tl, tr = min(p[0] for p in t), max(p[0] for p in t)
    yb, yt = P(cx, cy, z0)[1], P(cx, cy, z1)[1]
    poly(b, shade(col, 0.85))
    poly([(bl, yb), (br, yb), (tr, yt), (tl, yt)], col)
    poly([(bl, yb), ((bl + br) / 2, yb), ((tl + tr) / 2, yt), (tl, yt)], shade(col, 1.12))
    poly(t, shade(col, 0.6))


# ================================================================== room shell
_BG = {}


def background():
    """Vertical night gradient. Built once per canvas size and blitted."""
    key = screen.get_size()
    if key not in _BG:
        h = key[1]
        top, bot = np.array((28, 27, 32), np.float32), np.array((8, 8, 10), np.float32)
        k = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        col = (top * (1 - k) + bot * k).astype(np.uint8)
        strip = pygame.Surface((1, h))
        pygame.surfarray.blit_array(strip, col[None, :, :])
        full = pygame.Surface(key)
        pygame.transform.scale(strip, key, full)
        _BG[key] = full
    screen.blit(_BG[key], (0, 0))


def floor_boards(c1=None, c2=None, bw=0.27, seed=4):
    """Painted pine boards running along x (Drawing Room, Sitting Room)."""
    import paint
    c1 = c1 or PINE1_
    c2 = c2 or PINE2_
    paint.stamp(paint.timber(RW, RD, seed, c1, c2, along="x", plank=bw), 0, 0, RW, RD, 0)
    floor_slab(c2)


def wall_shell(col=None, open_W=False):
    col = col or GREEN
    qy(0, 0, RW, 0, WALL_H, shade(col, KY))
    if not open_W:
        qx(0, 0, RD, 0, WALL_H, shade(col, KX))


def wall_trim(cornice=True, skirting=True, col=None, open_E=False, open_W=False):
    """White skirting and cornice, plus the dark cap along the wall tops."""
    WHITE_ = col or WHITE
    walls = ((KY, lambda a, b, za, zb, c: qy(0, a, b, za, zb, c)), (KX, lambda a, b, za, zb, c: qx(0, a, b, za, zb, c)))
    for k, Q in (walls[:1] if open_W else walls):
        n = RW if k == KY else RD
        if skirting:
            Q(0, n, 0, 13, shade(WHITE_, k))
            Q(0, n, 13, 15, shade(WHITE_, k * 0.8))
        if cornice:
            Q(0, n, WALL_H - 20, WALL_H, shade(WHITE_, k))
            Q(0, n, WALL_H - 24, WALL_H - 20, shade(WHITE_, k * 0.85))
            Q(0, n, WALL_H - 12, WALL_H - 10, shade(WHITE_, k * 0.82))
    cap = (60, 58, 54)
    t = 0.28
    poly([P(0, 0, WALL_H), P(RW, 0, WALL_H), P(RW, -t, WALL_H), P(-t, -t, WALL_H)], cap)
    if not open_E:     # the wall's cut end (an open-plan room's wall carries on instead)
        poly([P(RW, 0, WALL_H), P(RW, -t, WALL_H), P(RW, -t, -SLAB), P(RW, 0, -SLAB)], shade(cap, 0.55))
    if not open_W:
        poly([P(0, 0, WALL_H), P(0, RD, WALL_H), P(-t, RD, WALL_H), P(-t, -t, WALL_H)], shade(cap, 1.15))
        poly([P(-t, RD, WALL_H), P(0, RD, WALL_H), P(0, RD, -SLAB), P(-t, RD, -SLAB)], shade(cap, 0.75))


# ============================================================ outside world
# Reusable for every room: the exterior is a real ground plane in the same
# 2:1 projection, lying just below the floor beyond each back wall. It is
# rendered to its own layer (exterior_layer) and only ever shown through
# the glass of a window or an outside doorway (show_through), so nothing
# outside spills round the room. In this projection a window at height z on
# a back wall looks onto the ground t = (z - GROUND_Z) / TILE_H tiles behind
# the wall (~1 tile for a sill, ~4 tiles at the top of a tall sash), so the
# view is lawn, path and fence, not sky. Props further out than ~4 tiles only
# show if they are tall (trees, a neighbour's barn).
GROUND_Z = -10                         # the garden is a step down from the floor

# One camera convention for the whole house, so rooms tile into one map.
# Derived from the floor plan and the two approved rooms (Drawing Room:
# chimney breast + door on the back-left = its east wall, sash window onto
# the front on the back-right = its south wall, door to the kitchen on the
# north near wall at the west end; Boot Room: kitchen door on the back-left
# = its east wall, window + external door on the back-right = the house's
# south outside wall, Study/pantry on the north near wall, WC/garage door on
# the west near wall).
HOUSE_CAMERA = {
    "looks": "south-east on the plan (plan top = back/garden = north)",
    "back_left": "east wall   (engine x = 0, side 'W')",
    "back_right": "south wall (engine y = 0, side 'N')",
    "near_right": "north wall (engine y = RD, side 'S', ghost)",
    "near_left": "west wall   (engine x = RW, side 'E', ghost)",
    "nearest_corner": "north-west",
    "x": "tiles westwards from the room's east wall",
    "y": "tiles northwards from the room's south wall",
}


def wall_pt(side, u, z, n=0.0):
    """A point on a wall: u along it, z up, n into the room (negative = outside).
    "N" y = 0, "W" x = 0, "S" y = RD, "E" x = RW."""
    if side == "N":
        return P(u, n, z)
    if side == "S":
        return P(u, RD - n, z)
    if side == "E":
        return P(RW - n, u, z)
    return P(n, u, z)


class drawing_on:
    """with drawing_on(surface): ... -> all the helpers draw there instead."""
    def __init__(self, surf):
        self.surf = surf

    def __enter__(self):
        global screen
        self.prev, screen = screen, self.surf

    def __exit__(self, *a):
        global screen
        screen = self.prev


def out_pt(side, u, t, z=GROUND_Z):
    """World point outside a wall: u along the wall, t tiles out from it.
    "N" is the south wall (y = 0), "W" the east wall (x = 0), "S" the north
    wall (y = RD). The north wall faces the other way, so the iso shear
    that lands a window on the ground runs with +t instead of -t."""
    if side == "N":
        return (u, -t, z)
    if side == "S":
        return (u + t, RD + t, z)
    if side == "E":
        return (RW + t, u + t, z)
    return (-t, u, z)


def out_quad(side, u0, u1, t0, t1, col, z=GROUND_Z, ol=None):
    pts = [P(*out_pt(side, u, t, z)) for u, t in ((u0, t0), (u1, t0), (u1, t1), (u0, t1))]
    poly(pts, col, ol)


def ext_lawn(side, u0, u1, t0, t1, rnd, base=(68, 148, 54)):
    out_quad(side, u0, u1, t0, t1, base)
    w = 0.9                                         # mowing stripes running along the wall
    t = t0
    i = 0
    while t < t1:
        out_quad(side, u0, u1, t, min(t1, t + w), shade(base, 1.07 if i % 2 else 0.95))
        t += w
        i += 1
    for _ in range(int((u1 - u0) * (t1 - t0) * 6)):     # tufts
        u, tt = rnd.uniform(u0, u1), rnd.uniform(t0, t1)
        x, y = P(*out_pt(side, u, tt))
        pygame.draw.line(screen, shade(base, rnd.choice((0.8, 1.2))), (x, y), (x + rnd.uniform(-2, 2) * S, y - 3 * S), S)


def ext_paving(side, u0, u1, t0, t1, rnd, col=(168, 160, 146), slab=0.5):
    """Stone path / patio: flags on the ground plane, laid in staggered rows."""
    out_quad(side, u0, u1, t0, t1, shade(col, 0.6))
    t, row = t0, 0
    while t < t1 - 1e-6:
        tb = min(t1, t + slab)
        u = u0 - (slab / 2 if row % 2 else 0)
        while u < u1:
            a, b = max(u0, u + .03), min(u1, u + slab * rnd.uniform(.9, 1.4) - .03)
            if b > a:
                out_quad(side, a, b, t + .03, tb - .03, shade(col, rnd.uniform(.88, 1.08)))
            u += slab * 1.2
        t, row = tb, row + 1


def ext_gravel(side, u0, u1, t0, t1, rnd, col=(184, 172, 150)):
    out_quad(side, u0, u1, t0, t1, col)
    for _ in range(int((u1 - u0) * (t1 - t0) * 60)):
        x, y = P(*out_pt(side, rnd.uniform(u0, u1), rnd.uniform(t0, t1)))
        pygame.draw.circle(screen, shade(col, rnd.uniform(.75, 1.15)), (x, y), S)


def ext_border(side, u0, u1, t0, t1, rnd):
    """Flower bed: dark soil with low plants dotted along it."""
    out_quad(side, u0, u1, t0, t1, (86, 62, 44))
    for _ in range(int((u1 - u0) * 9)):
        u, t = rnd.uniform(u0, u1), rnd.uniform(t0, t1)
        x, y = P(*out_pt(side, u, t))
        r = rnd.uniform(5, 9) * S
        pygame.draw.ellipse(screen, rnd.choice(((70, 112, 54), (60, 100, 50), (84, 126, 60))), (x - r, y - r * 1.2, 2 * r, r * 1.4))
        if rnd.random() < .5:
            pygame.draw.circle(screen, rnd.choice(((230, 220, 230), (220, 120, 120), (240, 210, 90))), (x + rnd.uniform(-3, 3) * S, y - r * .7), 2 * S)


def ext_picket_fence(side, u0, u1, t, h=46, col=(236, 234, 226)):
    """White picket fence along the wall, t tiles out: two rails and pointed pickets."""
    for z in (12, h - 12):
        a, b = P(*out_pt(side, u0, t, GROUND_Z + z)), P(*out_pt(side, u1, t, GROUND_Z + z))
        pygame.draw.line(screen, shade(col, .8), a, b, 3 * S)
    u = u0
    while u < u1:
        w = 0.07
        p0, p1 = P(*out_pt(side, u, t, GROUND_Z)), P(*out_pt(side, u + w, t, GROUND_Z))
        p2, p3 = P(*out_pt(side, u + w, t, GROUND_Z + h)), P(*out_pt(side, u, t, GROUND_Z + h))
        tip = P(*out_pt(side, u + w / 2, t, GROUND_Z + h + 7))
        poly([p0, p1, p2, tip, p3], shade(col, KY if side != "W" else KX), shade(col, .55))
        u += 0.17
    for k in (0, 1):     # posts
        uu = u0 + (u1 - u0) * k
        if side in ("S", "E"):
            x, y, _ = out_pt(side, uu, t)
            box(x - .05, y - .05, x + .05, y + .05, GROUND_Z, GROUND_Z + h + 8, col)
        else:
            box(*([uu - .05, -t - .05, uu + .05, -t + .05] if side == "N" else [-t - .05, uu - .05, -t + .05, uu + .05]),
                GROUND_Z, GROUND_Z + h + 8, col)


def ext_hedge(side, u0, u1, t0, t1, h=70, col=(36, 102, 42), rnd=None):
    if side in ("S", "E"):
        # a sheared slab, so it lands in the north/west-wall windows rather than
        # an axis-aligned box on the wrong side of the house
        z0, z1 = GROUND_Z, GROUND_Z + h
        poly([P(*out_pt(side, u0, t0, z0)), P(*out_pt(side, u1, t0, z0)),
              P(*out_pt(side, u1, t0, z1)), P(*out_pt(side, u0, t0, z1))], col)
        poly([P(*out_pt(side, u0, t0, z1)), P(*out_pt(side, u1, t0, z1)),
              P(*out_pt(side, u1, t1, z1)), P(*out_pt(side, u0, t1, z1))], shade(col, 1.12))
    else:
        b = [u0, -t1, u1, -t0] if side == "N" else [-t1, u0, -t0, u1]
        box(b[0], b[1], b[2], b[3], GROUND_Z, GROUND_Z + h, col)
    rnd = rnd or random.Random(1)
    for _ in range(int((u1 - u0) * 10)):
        u = rnd.uniform(u0, u1)
        x, y = P(*out_pt(side, u, t0, GROUND_Z + rnd.uniform(6, h)))
        pygame.draw.circle(screen, shade(col, rnd.uniform(.8, 1.2)), (x, y), rnd.uniform(3, 6) * S)


def ext_shrub(side, u, t, r=0.45, h=60, col=(70, 116, 56), rnd=None):
    rnd = rnd or random.Random(int(u * 100 + t))
    cx, cy, _ = out_pt(side, u, t)
    fl_ellipse(cx, cy, r * 1.1, r * 1.1, (40, 60, 32), z=GROUND_Z)          # shadow at its foot
    for i in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0, r * .7)
        x, y = P(cx + rr * math.cos(a), cy + rr * math.sin(a), GROUND_Z + rnd.uniform(h * .25, h * .8))
        pygame.draw.circle(screen, shade(col, rnd.uniform(.8, 1.2)), (x, y), rnd.uniform(9, 15) * S)


def ext_tree(side, u, t, trunk=110, canopy=150, r=0.9, col=(84, 132, 60), rnd=None):
    """Trunk standing on the ground plane, a canopy of leafy blobs above it (willow-ish fronds)."""
    rnd = rnd or random.Random(int(u * 10 + t * 7))
    cx, cy, _ = out_pt(side, u, t)
    fl_ellipse(cx + .3, cy + .3, r * 1.2, r * .9, (52, 80, 40), z=GROUND_Z)
    cyl(cx, cy, .1, GROUND_Z, GROUND_Z + trunk + 30, (96, 80, 62))
    for i in range(40):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0, r)
        z = GROUND_Z + trunk + rnd.uniform(0, canopy)
        x, y = P(cx + rr * math.cos(a), cy + rr * math.sin(a), z)
        c = shade(col, rnd.uniform(.8, 1.25))
        pygame.draw.circle(screen, c, (x, y), rnd.uniform(10, 18) * S)
        if rnd.random() < .5:            # drooping fronds
            pygame.draw.line(screen, shade(c, .9), (x, y), (x + rnd.uniform(-4, 4) * S, y + rnd.uniform(20, 45) * S), 2 * S)


def ext_barn(side, u0, u1, t0, t1, h=150, roof=60):
    """Neighbour's black weatherboard barn with a red tile roof (front of house)."""
    b = [u0, -t1, u1, -t0] if side == "N" else [-t1, u0, -t0, u1]
    x0, y0, x1, y1 = b
    box(x0, y0, x1, y1, GROUND_Z, GROUND_Z + h, (40, 40, 42))
    for z in range(int(GROUND_Z + 10), int(GROUND_Z + h), 12):        # weatherboards
        line((x0, y1, z), (x1, y1, z), (24, 24, 26), 1)
        line((x1, y0, z), (x1, y1, z), (24, 24, 26), 1)
    zt = GROUND_Z + h
    ridge = (y0 + y1) / 2
    tile = (168, 74, 52)
    poly([P(x0, y1 + .15, zt), P(x1 + .15, y1 + .15, zt), P(x1 + .15, ridge, zt + roof), P(x0, ridge, zt + roof)], shade(tile, KY))
    poly([P(x1 + .15, y0, zt), P(x1 + .15, y1 + .15, zt), P(x1 + .15, ridge, zt + roof)], shade((40, 40, 42), KX))


def ext_house_shadow(side, u0, u1, depth=1.2):
    """The house's own soft shadow on the ground at the foot of the wall."""
    bands = []
    for k in range(6):
        t0, t1 = depth * k / 6, depth * (k + 1) / 6
        pts = [P(*out_pt(side, u, t)) for u, t in ((u0, t0), (u1, t0), (u1, t1), (u0, t1))]
        bands.append((pts, int(70 * (1 - k / 6))))
    xs = [p[0] for pts, _a in bands for p in pts]
    ys = [p[1] for pts, _a in bands for p in pts]
    if not xs:
        return
    x0, y0 = int(min(xs)) - 2, int(min(ys)) - 2
    w = int(max(xs)) - x0 + 4
    h = int(max(ys)) - y0 + 4
    if w < 2 or h < 2:
        return
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    for pts, a in bands:
        pygame.draw.polygon(layer, (0, 0, 0, a), [(p[0] - x0, p[1] - y0) for p in pts])
    screen.blit(layer, (x0, y0))


def exterior_layer(spec, haze=(168, 196, 214)):
    """Render the outside world for this room onto its own layer.
    spec: {side: callable(side, rnd)} drawing that side's garden, far things first.

    24-bit, like the room canvas. convert() on macOS is a per-pixel-alpha
    surface; the house-shadow blit then stores its own alpha over the lawn,
    and show_through drops those pixels. All that survives is this haze, so
    every window looks plain grey.
    """
    ext = pygame.Surface(screen.get_size(), depth=24)
    ext.fill(haze)                   # anything unpainted: distant sky
    with drawing_on(ext):
        for side, draw in spec.items():
            draw(side, random.Random(side))
    return ext


def ground_seen(side, u0, u1, z0, z1):
    """Where on the exterior ground a window (u0..u1, z0..z1) on `side` looks:
    -> (t_near, t_far) tiles out from the wall. Handy for placing props."""
    return (z0 - GROUND_Z) / TILE_H, (z1 - GROUND_Z) / TILE_H


def debug_exterior(ext, windows, floor=None):
    """Walls hidden: the exterior plane, the room floor, and (yellow) the patch
    of ground each window looks onto."""
    screen.blit(ext, (0, 0))
    (floor or floor_boards)()
    for side, u0, u1, z0, z1 in windows:
        tn, tf = ground_seen(side, u0, u1, z0, z1)
        # a ray through (u, z) lands at u - t along the wall in this projection (x - y is constant)
        pts = [P(*out_pt(side, u0 - tn, tn)), P(*out_pt(side, u1 - tn, tn)), P(*out_pt(side, u1 - tf, tf)), P(*out_pt(side, u0 - tf, tf))]
        pygame.draw.polygon(screen, (255, 220, 60), pts, 2 * S)
        for u in (u0, u1):
            pygame.draw.line(screen, (255, 220, 60), wall_pt(side, u, z0), P(*out_pt(side, u - tn, tn)), S)
    pygame.draw.lines(screen, (240, 240, 240), False, [P(0, RD), P(0, 0), P(RW, 0)], 2 * S)


def show_through(ext, pts, tint=(214, 230, 236), tint_a=22, glare=True):
    """Show the exterior layer through an opening (screen polygon `pts`):
    ext masked to the polygon, then a faint glass tint and reflection streaks."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 1, int(min(ys)) - 1
    w, h = int(max(xs)) - x0 + 2, int(max(ys)) - y0 + 2
    loc = [(x - x0, y - y0) for x, y in pts]
    view = pygame.Surface((w, h), pygame.SRCALPHA)
    # Copy colour, not alpha. A shadow blitted onto an alpha exterior zeros
    # the lawn; blitting that onto this view would leave the glass empty.
    if ext.get_bitsize() != 24:
        opaque = pygame.Surface(ext.get_size(), depth=24)
        opaque.blit(ext, (0, 0))
        ext = opaque
    view.blit(ext, (0, 0), (x0, y0, w, h))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 0))
    pygame.draw.polygon(mask, (255, 255, 255, 255), loc)
    view.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if tint_a:
        g = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(g, (*tint, tint_a), loc)
        if glare:     # two soft diagonal reflection streaks, clipped to the glass
            streak = pygame.Surface((w, h), pygame.SRCALPHA)
            for f, ww in ((0.18, 0.10), (0.34, 0.04)):
                cx = w * f
                pygame.draw.polygon(streak, (255, 255, 255, 46), [(cx, h), (cx + w * ww, h), (cx + w * ww + h * 0.55, 0), (cx + h * 0.55, 0)])
            m2 = pygame.Surface((w, h), pygame.SRCALPHA)
            m2.fill((255, 255, 255, 0))
            pygame.draw.polygon(m2, (255, 255, 255, 255), loc)
            streak.blit(m2, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            g.blit(streak, (0, 0))
        view.blit(g, (0, 0))
    if _flip_draw():
        # Near windows (glass tint) must not paint the garden over the room.
        # Near doorways have no glass (tint_a == 0) and should show the next room.
        _present_opening(view, x0, y0, pts, allow_near=False)
    else:
        screen.blit(view, (x0, y0))


def _present_opening(view, x0, y0, pts, allow_near=False):
    """Paste a masked opening onto the flipped room, in front of whatever is
    farther away. A window in a near (ghost) wall must not paint over the room;
    an open doorway in that wall should, so you can see through it."""
    if _near_plane(pts) and not allow_near:
        return
    infs = [_pinf.get(p) for p in pts]
    if any(i is None for i in infs):
        screen.blit(view, (x0, y0))
        return
    src = pygame.surfarray.array3d(view)
    salpha = pygame.surfarray.array_alpha(view)
    near = _near_plane(pts) and _fg_surf is not None
    ds = [i[3] for i in infs]
    rgb = pygame.surfarray.pixels3d(screen)
    fa = pygame.surfarray.pixels_alpha(_fg_surf) if near else None

    def tri(a, b, c, da, db, dc):
        xs, ys = (a[0], b[0], c[0]), (a[1], b[1], c[1])
        xa = max(0, int(math.floor(min(xs))))
        ya = max(0, int(math.floor(min(ys))))
        xb = min(_zbuf.shape[0], int(math.ceil(max(xs))) + 1)
        yb = min(_zbuf.shape[1], int(math.ceil(max(ys))) + 1)
        if xb - xa < 1 or yb - ya < 1:
            return
        gx = np.arange(xa, xb, dtype=np.float32)[:, None] + 0.5
        gy = np.arange(ya, yb, dtype=np.float32)[None, :] + 0.5
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(area) < 1:
            return
        def edge(p, q):
            return (q[0] - p[0]) * (gy - p[1]) - (q[1] - p[1]) * (gx - p[0])
        w0, w1, w2 = edge(b, c), edge(c, a), edge(a, b)
        if area < 0:
            w0, w1, w2, area = -w0, -w1, -w2, -area
        m = (w0 >= -0.5) & (w1 >= -0.5) & (w2 >= -0.5)
        depth = (w0 * da + w1 * db + w2 * dc) / area
        sub = _zbuf[xa:xb, ya:yb]
        m &= depth >= sub - 1e-4
        vx = np.broadcast_to((np.arange(xa, xb) - x0)[:, None], m.shape)
        vy = np.broadcast_to((np.arange(ya, yb) - y0)[None, :], m.shape)
        inside = (vx >= 0) & (vx < src.shape[0]) & (vy >= 0) & (vy < src.shape[1])
        m &= inside
        if not np.any(m):
            return
        vis = salpha[vx[m], vy[m]] > 16
        if not np.any(vis):
            return
        sel = np.zeros_like(m)
        sel[m] = vis
        sub[sel] = depth[sel]
        rgb[xa:xb, ya:yb][sel] = src[vx[sel], vy[sel]]
        if fa is not None:
            fa[xa:xb, ya:yb][sel] = 0

    for i in range(1, len(pts) - 1):
        tri(pts[0], pts[i], pts[i + 1], ds[0], ds[i], ds[i + 1])
    del src, salpha, rgb
    if fa is not None:
        del fa


def opening_into(side, a, b, draw, h=None, fill=(226, 220, 208), arch=False):
    """Neighbour room through a doorway on the old near wall (y = RD or x = RW).
    Used by the opposite view, where that wall is the far one.
    `fill` is the colour shown if the neighbour drawing leaves a gap."""
    h = DOOR_H if h is None else h
    layer = pygame.Surface(screen.get_size(), depth=24)
    layer.fill(fill)
    with drawing_on(layer):
        draw()
    if arch:
        W = (lambda u, z, n: P(u, RD, z)) if side == "S" else (lambda u, z, n: P(RW, u, z))
        pts = arch_opening_pts(W, a, b)
    elif side == "S":
        pts = [P(a, RD, 0), P(b, RD, 0), P(b, RD, h), P(a, RD, h)]
    else:
        pts = [P(RW, a, 0), P(RW, b, 0), P(RW, b, h), P(RW, a, h)]
    show_through(layer, pts, tint_a=0)


def sash_window(side, u0, u1, ext, z0=52, z1=206, curtains=PINK):
    """Georgian sash on a back wall: a real opening onto the exterior layer,
    then frame, 6-over-6 glazing bars, sill and curtains drawn over it."""
    k = KY if side == "N" else KX
    W = lambda u, z, n=0.0: wall_pt(side, u, z, n)
    quad = lambda a, b, za, zb, col, n=0.0: poly([W(a, za, n), W(b, za, n), W(b, zb, n), W(a, zb, n)], col)
    quad(u0 - .08, u1 + .08, z0 - 8, z1 + 8, shade(WHITE, k))           # architrave
    show_through(ext, [W(u0, z0), W(u1, z0), W(u1, z1), W(u0, z1)])
    wc = shade(WHITE, 1.02 * k / KY)
    zm = (z0 + z1) / 2
    for za, zb in ((z0, z0 + 5), (zm - 3, zm + 3), (z1 - 5, z1)):
        quad(u0, u1, za, zb, wc)
    for uu in (u0, u1 - .06):
        quad(uu, uu + .06, z0, z1, wc)
    for j in (1, 2):
        uu = u0 + (u1 - u0) * j / 3
        quad(uu - .02, uu + .02, z0, z1, wc)
    for zz in (z0 + (zm - z0) / 2, zm + (z1 - zm) / 2):
        quad(u0, u1, zz - 1.5, zz + 1.5, wc)
    quad(u0 - .12, u1 + .12, z0 - 10, z0 - 4, shade(WHITE, 1.05 * k / KY), n=.04)   # sill
    if curtains:
        a, b = W(u0 - .62, z1 + 18, .06), W(u1 + .62, z1 + 18, .06)
        pygame.draw.line(screen, (190, 186, 176), a, b, int(2.5 * S))
        for ca, cb in ((u0 - .55, u0 + .02), (u1 - .02, u1 + .55)):
            quad(ca, cb, 12, z1 + 16, shade(curtains, .55 * k / KY), n=.07)
            for f in range(5):
                fa, fb = ca + (cb - ca) * f / 5, ca + (cb - ca) * (f + 1) / 5
                quad(fa + .01, fb - .01, 13, z1 + 15, shade(curtains, (0.84 + 0.18 * (f % 2)) * k / KY), n=.07)


def frame_N(u0, u1, z0, z1, inner, mount=(240, 236, 228), fr=(30, 28, 26), k=KY):
    qy(0.02, u0, u1, z0, z1, shade(fr, k))
    m = 0.04 if u1 - u0 < 0.5 else 0.05
    qy(0.02, u0 + m, u1 - m, z0 + 3, z1 - 3, shade(mount, k))
    inner(u0 + m * 2.2, u1 - m * 2.2, z0 + 7, z1 - 7)


def frame_W(v0, v1, z0, z1, inner, mount=(240, 236, 228), fr=(30, 28, 26), x=0.02):
    k = KX
    qx(x, v0, v1, z0, z1, shade(fr, k))
    m = 0.04 if v1 - v0 < 0.5 else 0.05
    qx(x, v0 + m, v1 - m, z0 + 3, z1 - 3, shade(mount, k))
    inner(v0 + m * 2.2, v1 - m * 2.2, z0 + 7, z1 - 7)


def bw_photo(rnd, plane):
    def f(a, b, za, zb):
        g = rnd.randint(70, 150)
        plane(a, b, za, zb, (g, g, g))
        # a couple of blurry figures / horizon
        hz = za + (zb - za) * rnd.uniform(.3, .6)
        plane(a, b, za, hz, (g - 30, g - 30, g - 30))
        uu = a + (b - a) * rnd.uniform(.25, .65)
        plane(uu, uu + (b - a) * .18, za, za + (zb - za) * .7, (30, 30, 30))
    return f


def panel_door_W(v0, v1):
    """White four-panel door on the chimney wall (x=0), with black latch."""
    k = KX
    qx(0, v0 - .1, v1 + .1, 0, DOOR_H + 8, shade(WHITE, k * 1.02), shade(WHITE, 0.6))   # architrave
    qx(0.005, v0, v1, 0, DOOR_H, shade(WHITE, k * 0.95), shade(WHITE, 0.55))
    w = v1 - v0
    for (a, b), (za, zb) in [((.12, .45), (18, 80)), ((.55, .88), (18, 80)), ((.12, .45), (96, 172)), ((.55, .88), (96, 172))]:
        qx(0.01, v0 + w * a, v0 + w * b, za, zb, shade(WHITE, k * 0.86), shade(WHITE, 0.6))
    qx(0.012, v1 - w * .1, v1 - w * .06, 82, 112, (22, 22, 22))                      # latch
    qx(0.012, v1 - w * .14, v1 - w * .06, 92, 96, (22, 22, 22))


_VIG = {}
_GRADE = {}


def vignette(surf):
    w, h = surf.get_size()
    key = (w, h)
    if key not in _VIG:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = w * 0.5, h * 0.46
        d = np.sqrt(((xx - cx) / (w * 0.62)) ** 2 + ((yy - cy) / (h * 0.70)) ** 2)
        a = 96 * np.clip(d, 0, 1) ** 2.05
        s = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        s.fill((6, 5, 8, 0))
        al = pygame.surfarray.pixels_alpha(s)
        al[:] = np.clip(a, 0, 255).astype(np.uint8).T
        del al
        _VIG[key] = s
    if key not in _GRADE:
        # warm ceiling bounce, a little deeper toward the floor
        t = np.linspace(0, 1, h, dtype=np.float32)
        r = (255 - 22 * t).astype(np.uint8)
        g = (244 - 26 * t).astype(np.uint8)
        b = (220 - 18 * t).astype(np.uint8)
        col = np.stack([r, g, b], axis=1)
        strip = pygame.Surface((1, h))
        pygame.surfarray.blit_array(strip, col[None, :, :])
        full = pygame.Surface((w, h))
        pygame.transform.scale(strip, (w, h), full)
        _GRADE[key] = full
    # Destination must be 24-bit (no per-pixel alpha). Blitting this overlay onto
    # a surface that has alpha replaces the destination alpha, and the centre
    # of the vignette is 0, so the floor is stored fully transparent.
    surf.blit(_GRADE[key], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    surf.blit(_VIG[key], (0, 0))



# ================================================================ new shared bits
def floor_slab(col):
    """The floor's edge along the open front, as the engine draws it."""
    poly([P(0, RD), P(RW, RD), P(RW, RD, -SLAB), P(0, RD, -SLAB)], shade(col, 0.42))
    poly([P(RW, 0), P(RW, RD), P(RW, RD, -SLAB), P(RW, 0, -SLAB)], shade(col, 0.30))


def floor_flagstones(cols=((128, 118, 104), (112, 104, 94), (138, 126, 108), (104, 98, 90)), seed=5, row=0.85, z=0.0,
                     x0=0.0, y0=0.0, x1=None, y1=None, grout=None):
    """Worn flagstones (Boot Room, and the glimpses beyond it)."""
    import paint
    x1 = RW if x1 is None else x1
    y1 = RD if y1 is None else y1
    if z == 0.0 and (x0, y0) == (0.0, 0.0):
        floor_slab(cols[1])
    paint.stamp(paint.flagstones(x1 - x0, y1 - y0, seed, cols, row), x0, y0, x1, y1, z)


def floor_tiles(col=TERRACOTTA, size=0.5, x0=0.0, y0=0.0, x1=None, y1=None, z=0.0, seed=2):
    """Square quarry tiles (terracotta) with pale grout."""
    import paint
    x1 = RW if x1 is None else x1
    y1 = RD if y1 is None else y1
    paint.stamp(paint.quarry(x1 - x0, y1 - y0, seed, col, size), x0, y0, x1, y1, z)


def threshold(side, a, b, col, depth=0.8, k0=0.75):
    """The floor of the next room beyond a near-wall doorway, fading into the dark (as the engine)."""
    for kk in range(6):
        t0, t1 = kk / 6 * depth, (kk + 1) / 6 * depth
        c = shade(col, k0 * (1 - kk / 6))
        if side == "S":
            poly([P(a, RD + t0), P(b, RD + t0), P(b, RD + t1), P(a, RD + t1)], c)
        else:
            poly([P(RW + t0, a), P(RW + t0, b), P(RW + t1, b), P(RW + t1, a)], c)


def wall_quad(side, u0, u1, z0, z1, col, n=0.0, ol=None):
    W = lambda u, z: wall_pt(side, u, z, n)
    poly([W(u0, z0), W(u1, z0), W(u1, z1), W(u0, z1)], col, ol)


def wall_k(side):
    return KY if side in ("N", "S") else KX


def brick_wall(side, u0, u1, z0, z1, col=(232, 228, 218), seed=1, rows_h=13, per=0.42, n=0.0):
    """Painted brick: courses with staggered joints (white-painted brickwork)."""
    k = wall_k(side)
    rnd = random.Random(seed)
    wall_quad(side, u0, u1, z0, z1, shade(col, k * 0.8), n)
    j = 0
    z = z0
    while z < z1 - 1e-6:
        zt = min(z1, z + rows_h)
        u = u0 - (per / 2 if j % 2 else 0)
        while u < u1:
            a, b = max(u0, u + .012), min(u1, u + per - .012)
            if b > a:
                wall_quad(side, a, b, z + 1, zt - 1, shade(col, k * rnd.uniform(.94, 1.03)), n)
            u += per
        z, j = zt, j + 1


def tongue_and_groove(side, u0, u1, z0, z1, col, board=0.2, n=0.0, rail=True):
    """Vertical tongue-and-groove panelling with a capping rail."""
    k = wall_k(side)
    # One board at a time so a flipped near wall can ghost each plank
    # (a single full-width slab is too wide to count as wall-mounted).
    u = u0
    while u < u1 - 1e-6:
        uu = min(u1, u + board)
        wall_quad(side, u, uu, z0, z1, shade(col, k), n)
        if uu < u1:
            wall_quad(side, uu - .008, uu + .008, z0 + 2, z1 - 2, shade(col, k * .78), n)
        u = uu
    if rail:
        wall_quad(side, u0 - .02, u1 + .02, z1, z1 + 6, shade(col, k * 1.08), n + .03)
        wall_quad(side, u0 - .02, u1 + .02, z1 - 2, z1, shade(col, k * .7), n + .03)


def plank_door_face(Wf, a, b, h, col, k, hinge="left", strap=True, latch=True, cat_flap=False):
    """A ledged plank door drawn on any plane: Wf(u, z) -> screen point, u in [a, b].
    Returns the (colour, polygon) list so it can go on a ghost layer too."""
    out = [(shade(col, k), [Wf(a, 0), Wf(b, 0), Wf(b, h), Wf(a, h)])]
    w = b - a
    nb = max(3, int(round(w / .2)))
    for i in range(1, nb):
        u = a + w * i / nb
        out.append((shade(col, k * .75), [Wf(u - .006, 2), Wf(u + .006, 2), Wf(u + .006, h - 2), Wf(u - .006, h - 2)]))
    if strap:
        for zz in (h * .16, h * .84):
            u0, u1 = (a + .03, a + w * .62) if hinge == "left" else (b - w * .62, b - .03)
            out.append((IRON, [Wf(u0, zz - 2.5), Wf(u1, zz - 2.5), Wf(u1, zz + 2.5), Wf(u0, zz + 2.5)]))
    if latch:
        uu = b - w * .14 if hinge == "left" else a + w * .14
        out.append((IRON, [Wf(uu - .02, h * .5 - 14), Wf(uu + .02, h * .5 - 14), Wf(uu + .02, h * .5 + 14), Wf(uu - .02, h * .5 + 14)]))
        out.append((IRON, [Wf(uu - .1, h * .5 + 4), Wf(uu + .02, h * .5 + 4), Wf(uu + .02, h * .5 + 7), Wf(uu - .1, h * .5 + 7)]))
    if cat_flap:
        cu = a + w * .5
        out.append((shade((222, 222, 222), k), [Wf(cu - .17, 8), Wf(cu + .17, 8), Wf(cu + .17, 40), Wf(cu - .17, 40)]))
        out.append((shade((120, 130, 140), k), [Wf(cu - .12, 12), Wf(cu + .12, 12), Wf(cu + .12, 35), Wf(cu - .12, 35)]))
    return out


def draw_polys(polys):
    for c, pts in polys:
        poly(pts, c)


def architrave(side, a, b, h, col=WHITE, w=0.09, n=0.0):
    k = wall_k(side)
    wall_quad(side, a - w, a, 0, h + w * 60, shade(col, k), n)
    wall_quad(side, b, b + w, 0, h + w * 60, shade(col, k), n)
    wall_quad(side, a - w, b + w, h, h + w * 60, shade(col, k), n)


def doorway_back(side, a, b, view, h=DOOR_H, col=WHITE):
    """An open doorway in a back wall onto another room or outside: `view` is
    the layer behind it (exterior_layer), shown with no glass."""
    show_through(view, [wall_pt(side, a, 0), wall_pt(side, b, 0), wall_pt(side, b, h), wall_pt(side, a, h)], tint_a=0)
    architrave(side, a, b, h, col)


def opening_polygon(side, a, b, h=DOOR_H):
    """Screen quad of a doorway. side is the engine wall: N/W back, S/E near."""
    if side == "N":
        return [wall_pt("N", a, 0), wall_pt("N", b, 0), wall_pt("N", b, h), wall_pt("N", a, h)]
    if side == "W":
        return [wall_pt("W", a, 0), wall_pt("W", b, 0), wall_pt("W", b, h), wall_pt("W", a, h)]
    if side == "S":
        return [P(a, RD, 0), P(b, RD, 0), P(b, RD, h), P(a, RD, h)]
    return [P(RW, a, 0), P(RW, b, 0), P(RW, b, h), P(RW, a, h)]


def reveal(side, a, b, draw, h=DOOR_H):
    """Run `draw` (neighbour geometry, in its own tiles via `placed`) and show
    it only through this doorway, so the frame and the wall clip it."""
    layer = pygame.Surface(screen.get_size(), depth=24)
    layer.fill((226, 220, 208))
    with drawing_on(layer):
        draw()
    show_through(layer, opening_polygon(side, a, b, h), tint_a=0)


def reveal_near(side, a, b, draw, depth=1.55, fill=(232, 228, 216)):
    """Neighbour past a near (ghost) wall.

    The next room continues toward the camera, so its floor lies just outside
    the wall. The vertical door quad is filled with that room's wall colour
    (anything tall enough to project into the hole is drawn on top of it).
    Both are clipped to the opening; the ghost wall drawn afterwards hides spill.
    """
    layer = pygame.Surface(screen.get_size(), depth=24)
    layer.fill(fill)
    with drawing_on(layer):
        draw()
    # The vertical hole is the wall itself; the neighbour's floor projects just
    # outside it. Painting the hole with the fill colour reads as a shut door.
    if side == "S":
        pts = [P(a - 0.05, RD - 0.02, 0), P(b + 0.05, RD - 0.02, 0),
               P(b + 0.08, RD + depth, 0), P(a - 0.08, RD + depth, 0)]
    else:
        pts = [P(RW - 0.02, a - 0.05, 0), P(RW - 0.02, b + 0.05, 0),
               P(RW + depth, b + 0.08, 0), P(RW + depth, a - 0.08, 0)]
    show_through(layer, pts, tint_a=0)


def back_opening(side, a, b, draw, h=DOOR_H, col=WHITE):
    """Open doorway in a back wall: neighbour through the hole, architrave on top."""
    layer = pygame.Surface(screen.get_size(), depth=24)
    layer.fill((226, 220, 208))
    with drawing_on(layer):
        draw()
    doorway_back(side, a, b, layer, h=h, col=col)


def glazed_door_back(side, a, b, ext, col=SAGE, h=DOOR_H, panes=(2, 3), glass_z=(96, 176), cat_flap=True, hinge="left"):
    """Half-glazed external door on a back wall: real glass onto the exterior
    layer (show_through), glazing bars, panelled lower half, cat flap, black ironmongery."""
    k = wall_k(side)
    W = lambda u, z: wall_pt(side, u, z, 0.01)
    architrave(side, a, b, h, WHITE)
    wall_quad(side, a, b, 0, h, shade(col, k), .01, shade(col, .5))
    g0, g1 = glass_z
    ga, gb = a + .12, b - .12
    show_through(ext, [W(ga, g0), W(gb, g0), W(gb, g1), W(ga, g1)])
    bc = shade(col, k * 1.05)
    cols, rows = panes
    for i in range(1, cols):
        u = ga + (gb - ga) * i / cols
        wall_quad(side, u - .018, u + .018, g0, g1, bc, .012)
    for j in range(1, rows):
        z = g0 + (g1 - g0) * j / rows
        wall_quad(side, ga, gb, z - 1.6, z + 1.6, bc, .012)
    # lower panels
    for (pa, pb) in ((.12, .47), (.53, .88)):
        wall_quad(side, a + (b - a) * pa, a + (b - a) * pb, 14, g0 - 14, shade(col, k * .9), .012, shade(col, .55))
    if cat_flap:
        cu = (a + b) / 2
        wall_quad(side, cu - .16, cu + .16, 10, 44, shade((228, 228, 228), k), .014)
        wall_quad(side, cu - .11, cu + .11, 14, 38, shade((140, 150, 158), k), .016)
    uu = b - .12 if hinge == "left" else a + .12
    wall_quad(side, uu - .025, uu + .025, 92, 120, IRON, .016)
    wall_quad(side, uu - .1, uu + .02, 104, 108, IRON, .018)
    for zz in (h * .14, h * .86):
        u0, u1 = (a + .03, a + .4) if hinge == "left" else (b - .4, b - .03)
        wall_quad(side, u0, u1, zz - 2.5, zz + 2.5, IRON, .016)


def _far_wall_W(side):
    """Point on the north (S, y = RD) or west (E, x = RW) wall, n into the room."""
    if side == "S":
        return lambda u, z, n=0.0: P(u, RD - n, z)
    return lambda u, z, n=0.0: P(RW - n, u, z)


def sash_on_far(side, u0, u1, ext, z0=112, z1=208, curtains=None, cols=2):
    """A white sash on the north or west wall once that wall faces the camera."""
    W = _far_wall_W(side)
    k = KY if side == "S" else KX

    def quad(a, b, za, zb, col, n=0.0):
        poly([W(a, za, n), W(b, za, n), W(b, zb, n), W(a, zb, n)], col)

    show_through(ext, [W(u0, z0), W(u1, z0), W(u1, z1), W(u0, z1)], tint_a=12)
    frame = shade(WHITE, k)
    n = 0.02
    quad(u0 - 0.07, u0, z0 - 7, z1 + 7, frame, n)
    quad(u1, u1 + 0.07, z0 - 7, z1 + 7, frame, n)
    quad(u0 - 0.07, u1 + 0.07, z1, z1 + 7, frame, n)
    quad(u0 - 0.07, u1 + 0.07, z0 - 7, z0, frame, n)
    bar = shade((248, 248, 246), 1.02)
    mid = (z0 + z1) / 2
    for za, zb in ((z0, z0 + 4), (mid - 2.5, mid + 2.5), (z1 - 4, z1)):
        quad(u0, u1, za, zb, bar, n=0.028)
    step = (u1 - u0) / cols
    for i in range(cols + 1):
        uu = u0 + step * i - (0.025 if i == cols else 0)
        quad(uu, uu + 0.05, z0, z1, bar, n=0.028)
    quad(u0 - 0.1, u1 + 0.1, z0 - 9, z0 - 4, shade(WHITE, 1.04), n=0.045)
    if curtains:
        for ca, cb in ((u0 - 0.55, u0 + 0.02), (u1 - 0.02, u1 + 0.55)):
            quad(ca, cb, 12, z1 + 16, shade(curtains, 0.55 * k / KY), n=0.06)
            for f in range(5):
                fa = ca + (cb - ca) * f / 5
                fb = ca + (cb - ca) * (f + 1) / 5
                quad(fa + 0.01, fb - 0.01, 13, z1 + 15,
                     shade(curtains, (0.84 + 0.18 * (f % 2)) * k / KY), n=0.06)


def glazed_doors_on_S(a, b, ext, h=None, curtains=(226, 218, 196)):
    """A pair of glazed French doors on the north wall (y = RD), shut."""
    h = DOOR_H if h is None else h
    W = _far_wall_W("S")

    def quad(u0, u1, za, zb, col, n=0.0):
        poly([W(u0, za, n), W(u1, za, n), W(u1, zb, n), W(u0, zb, n)], col)

    mid = (a + b) / 2
    frame = shade(WHITE, KY)
    for u0, u1 in ((a + 0.04, mid - 0.015), (mid + 0.015, b - 0.04)):
        show_through(ext, [W(u0 + 0.04, 28, 0), W(u1 - 0.04, 28, 0), W(u1 - 0.04, h - 8, 0), W(u0 + 0.04, h - 8, 0)], tint_a=12)
        quad(u0 + 0.03, u1 - 0.03, 92, h - 10, (74, 134, 70), 0.02)
        quad(u0 + 0.03, u1 - 0.03, 28, 92, (50, 104, 46), 0.02)
        quad(u0, u1, 0, 28, shade(WHITE, KY * 0.95), 0.02)
        for i in range(3):
            uu = u0 + (u1 - u0) * i / 2
            quad(uu - 0.015, uu + 0.015, 28, h - 8, frame, 0.03)
        for kk in range(6):
            zz = 28 + (h - 36) * kk / 5
            quad(u0, u1, zz - 1.5, zz + 1.5, frame, 0.03)
    if curtains:
        for ca, cb in ((a - 0.55, a - 0.05), (b + 0.05, b + 0.55)):
            for f in range(5):
                fa = ca + (cb - ca) * f / 5
                fb = ca + (cb - ca) * (f + 1) / 5
                quad(fa, fb, 10, 214, shade(curtains, 0.86 + 0.16 * (f % 2)), n=0.04)
        quad(a - 0.65, b + 0.65, 214, 219, (120, 110, 96), n=0.045)


# ------------------------------------------------------------ arches
# A slim segmental arch (landing <-> upstairs corridor): springs a little
# below door height and rises to its crown inside the usual frame cut.
ARCH_SPRING = DOOR_H - 26
ARCH_CROWN = DOOR_H + 14
ARCH_BAND = 12          # depth of the white arch moulding (z units)
ARCH_JAMB = 0.12        # jamb width (tiles)


def arch_z(u, a, b, zs=ARCH_SPRING, zc=ARCH_CROWN):
    """Height of the arch soffit at u (elliptical segment from a to b)."""
    c = (b - a) / 2
    f = max(0.0, 1.0 - ((u - (a + b) / 2) / c) ** 2)
    return zs + (zc - zs) * math.sqrt(f)


def _arch_us(a, b, steps=18):
    return [a + (b - a) * i / steps for i in range(steps + 1)]


def arch_opening_pts(W, a, b, n=0.0, steps=18):
    """Convex outline of the arched opening (floor to soffit) on a wall plane."""
    us = _arch_us(a, b, steps)
    return [W(a, 0, n), W(b, 0, n)] + [W(u, arch_z(u, a, b), n) for u in reversed(us)]


def arch_frame_polys(W, a, b, col, k, n=0.0, wall=None, top=None, steps=18):
    """White painted arch: two slim jambs and a curved moulding following the
    soffit, with a soft inner shadow line and an outer highlight. With `wall`
    and `top`, the spandrels between the moulding and z = top are filled with
    wall colour (closing a rectangular frame cut round the arch)."""
    base, edge, hi = shade(col, k), shade(col, k * 0.84), shade(col, min(1.0, k * 1.08))
    q = lambda u0, u1, z0, z1, c: (c, [W(u0, z0, n), W(u1, z0, n), W(u1, z1, n), W(u0, z1, n)])
    j, bd = ARCH_JAMB, ARCH_BAND
    zs = ARCH_SPRING
    out = [q(a - j, a, 0, zs + bd, base), q(b, b + j, 0, zs + bd, base),
           q(a - 0.022, a, 0, zs, edge), q(b, b + 0.022, 0, zs, edge),
           q(a - j, a - j + 0.02, 0, zs + bd, hi), q(b + j - 0.02, b + j, 0, zs + bd, hi),
           q(a - j - 0.01, a, 0, 22, shade(col, k * 0.92)), q(b, b + j + 0.01, 0, 22, shade(col, k * 0.92))]
    us = _arch_us(a, b, steps)
    for u0, u1 in zip(us, us[1:]):
        z0a, z0b = arch_z(u0, a, b), arch_z(u1, a, b)
        out.append((base, [W(u0, z0a, n), W(u1, z0b, n), W(u1, z0b + bd, n), W(u0, z0a + bd, n)]))
        out.append((edge, [W(u0, z0a, n), W(u1, z0b, n), W(u1, z0b + 3, n), W(u0, z0a + 3, n)]))
        out.append((hi, [W(u0, z0a + bd - 3, n), W(u1, z0b + bd - 3, n), W(u1, z0b + bd, n), W(u0, z0a + bd, n)]))
    if wall is not None and top is not None:
        # spandrels: above the jambs and above the moulding, up to the cut top
        out.insert(0, q(a - 0.16, a - j, 0, top, wall))
        out.insert(0, q(b + j, b + 0.16, 0, top, wall))
        out.insert(0, q(a - j, a, zs + bd, top, wall))
        out.insert(0, q(b, b + j, zs + bd, top, wall))
        for u0, u1 in zip(us, us[1:]):
            z0a, z0b = arch_z(u0, a, b) + bd, arch_z(u1, a, b) + bd
            out.insert(0, (wall, [W(u0, z0a, n), W(u1, z0b, n), W(u1, top, n), W(u0, top, n)]))
    return out


def ghost_frame_col(side_k=1.0, col=WHITE):
    """The Haunted Mansion ghost-frame colour: the frame paint, a little cold."""
    return shade(art.lerp(col, (150, 170, 200), 0.12), side_k)


def ghost_door_frame(W, a, b, col, target=None, alpha=None, arch=False):
    """Haunted Mansion's translucent door frame on a near (ghost) wall.
    W(u, z, n) with n towards the camera. Drawn onto `target` (default the
    current screen) at GHOST_FRAME_ALPHA + 30, like the engine's front edges."""
    target = screen if target is None else target
    alpha = HMG.GHOST_FRAME_ALPHA + 30 if alpha is None else alpha
    if arch:
        polys = arch_frame_polys(W, a, b, col, 1.0, 0.05)
        polys = [(c, pts) for c, pts in polys]
    else:
        polys = _HM_frame_polys(W, a, b, col, -0.05, 0.05)
    layer, at = _HM_polys_layer(polys)
    layer.set_alpha(alpha)
    target.blit(layer, at)


def door_architrave_polys(W, a, b, col, k, n=0.0, w=0.16, top=DOOR_H + 32):
    """White painted architrave round a doorway (u in [a, b]) on a wall plane:
    jambs, head, a soft inner shadow line and a highlight on the outer edge."""
    base = shade(col, k)
    edge = shade(col, k * 0.84)
    hi = shade(col, min(1.0, k * 1.06) if k < 1 else k)
    q = lambda u0, u1, z0, z1, c: (c, [W(u0, z0, n), W(u1, z0, n), W(u1, z1, n), W(u0, z1, n)])
    out = [q(a - w, a, 0, top, base), q(b, b + w, 0, top, base), q(a - w, b + w, DOOR_H, top, base)]
    # inner quirk (shadow against the opening) and outer highlight
    out += [q(a - 0.025, a, 0, DOOR_H, edge), q(b, b + 0.025, 0, DOOR_H, edge),
            q(a - 0.025, b + 0.025, DOOR_H, DOOR_H + 4, edge)]
    out += [q(a - w, a - w + 0.02, 0, top, hi), q(b + w - 0.02, b + w, 0, top, hi),
            q(a - w, b + w, top - 4, top, hi)]
    # plinth blocks
    out += [q(a - w - 0.01, a, 0, 22, shade(col, k * 0.92)), q(b, b + w + 0.01, 0, 22, shade(col, k * 0.92))]
    return out


def ghost_near_walls(wall_col=GREEN, trim_col=WHITE, doors_S=(), doors_E=(), windows_E=(), windows_S=(),
                     frame_col=WHITE, cornice=True, extra_polys=(), curtains=PINK, open_E=False,
                     open_W=False, window_z=(52, 206), window_cols=3, openings=(), arches=()):
    """Haunted Mansion's see-through front edge for any room.
    openings: (side, a, b, draw) neighbour views, painted into the doorway holes
    before the wall so the wall and its frame clip them. side "S" is y = RD,
    side "E" is x = RW.
    doors_*: (a, b) doorways on the near wall y = RD ("S") / x = RW ("E"), each
    drawn with the engine's ghost door frame (game.door_frame_polys at
    GHOST_FRAME_ALPHA); windows_*: (u0, u1) sashes drawn faintly.
    extra_polys: (colour, polygon) things that belong to the near walls (closed doors, helmets...).
    open_E: no wall at x = RW at all (an open-plan join onto the next view of the same room);
    open_W: the back-left side is open instead (drop the near wall's corner post at x = 0).
    window_z / window_cols: sill/head height and vertical bars of the faint near-wall windows."""
    # Near-wall doorways are a ghost frame only. The next room is shown
    # solely through far-wall openings (doorway_back / opening_into).
    z0, z1 = window_z
    t = 0.0 if FLIP else 0.08
    WS = lambda u, z, n: P(u, RD + n, z)
    WE = lambda u, z, n: P(RW + n, u, z)
    faces, trim = [], []
    sides = ((WS, KY, RW, doors_S, windows_S),) + (() if open_E else ((WE, KX, RD, doors_E, windows_E),))
    for W, k, n_len, doors, wins in sides:
        gc = shade(wall_col, k)
        # wall face minus doorway openings and window glass
        cuts = sorted([(a - .16, b + .16, DOOR_H + 32) for a, b in doors] + [(w0 - .6, w1 + .6, None) for w0, w1 in wins])
        u = 0
        for a, b, top in cuts:
            if a > u:
                faces.append((gc, [W(u, 0, t), W(a, 0, t), W(a, WALL_H, t), W(u, WALL_H, t)]))
            if top is not None:
                faces.append((gc, [W(a, top, t), W(b, top, t), W(b, WALL_H, t), W(a, WALL_H, t)]))
            else:
                faces.append((gc, [W(a, 0, t), W(b, 0, t), W(b, z0 - 8, t), W(a, z0 - 8, t)]))
                faces.append((gc, [W(a, z1 + 8, t), W(b, z1 + 8, t), W(b, WALL_H, t), W(a, WALL_H, t)]))
            u = max(u, b)
        if u < n_len:
            faces.append((gc, [W(u, 0, t), W(n_len, 0, t), W(n_len, WALL_H, t), W(u, WALL_H, t)]))
        # skirting (between doors), cornice
        u = 0
        for a, b in sorted((a - .16, b + .16) for a, b in doors) + [(n_len, n_len)]:
            if a > u:
                trim.append((shade(trim_col, k), [W(u, 0, t), W(a, 0, t), W(a, 14, t), W(u, 14, t)]))
            u = b
        if cornice:
            trim.append((shade(trim_col, k), [W(0, WALL_H - 22, t), W(n_len, WALL_H - 22, t), W(n_len, WALL_H, t), W(0, WALL_H, t)]))
        if FLIP:
            # This wall is the far one now: fill the frame cut round each
            # doorway with white painted architrave instead of leaving the
            # dark backdrop showing as a black frame.
            for a, b in doors:
                if (a, b) in arches:
                    trim += arch_frame_polys(W, a, b, trim_col, k, t, wall=gc, top=DOOR_H + 32)
                else:
                    trim += door_architrave_polys(W, a, b, trim_col, k, t)
        else:
            # ghost wall over a near-wall arch: close the frame cut above the curve
            for a, b in doors:
                if (a, b) in arches:
                    faces += [pp for pp in arch_frame_polys(W, a, b, trim_col, k, t, wall=gc, top=DOOR_H + 32)
                              if pp[0] == gc]
        # windows
        wc = shade(WHITE, k)
        zm = (z0 + z1) / 2
        for w0, w1 in wins:
            trim += [(wc, [W(w0 - .08, z0 - 8, t), W(w1 + .08, z0 - 8, t), W(w1 + .08, z0, t), W(w0 - .08, z0, t)]),
                     (wc, [W(w0 - .08, z1, t), W(w1 + .08, z1, t), W(w1 + .08, z1 + 8, t), W(w0 - .08, z1 + 8, t)]),
                     (wc, [W(w0 - .08, zm - 3, t), W(w1 + .08, zm - 3, t), W(w1 + .08, zm + 3, t), W(w0 - .08, zm + 3, t)])]
            bars = [(w0 + i * (w1 - w0) / window_cols - .02, .04) for i in range(1, window_cols)]
            for uu, ww in [(w0 - .08, .08)] + bars + [(w1, .08)]:
                trim.append((wc, [W(uu, z0, t), W(uu + ww, z0, t), W(uu + ww, z1, t), W(uu, z1, t)]))
            if curtains:
                for ca, cb in ((w0 - .55, w0 - .02), (w1 + .02, w1 + .55)):
                    for f in range(5):
                        fa, fb = ca + (cb - ca) * f / 5, ca + (cb - ca) * (f + 1) / 5
                        trim.append((shade(curtains, (0.84 + 0.18 * (f % 2)) * k / KY), [W(fa, 12, t + .02), W(fb, 12, t + .02), W(fb, z1 + 16, t + .02), W(fa, z1 + 16, t + .02)]))
    cap = (60, 58, 54)
    trim.append((cap, [WS(0, WALL_H, 0), WS(RW + .22, WALL_H, 0), WS(RW + .22, WALL_H, .22), WS(0, WALL_H, .22)]))
    if not open_E:
        trim.append((cap, [WE(0, WALL_H, 0), WE(RD, WALL_H, 0), WE(RD, WALL_H, .22), WE(0, WALL_H, .22)]))
        trim.append((shade(cap, .7), [WS(RW + .22, -SLAB, .22), WS(RW + .22, WALL_H, .22), WS(RW + .22, WALL_H, 0), WS(RW + .22, -SLAB, 0)]))
    if not open_W:
        trim.append((shade(cap, .7), [WS(0, -SLAB, .22), WS(0, WALL_H, .22), WS(.06, WALL_H, .22), WS(.06, -SLAB, .22)]))
    if FLIP and not open_E:
        # close the hairline gap where the two far walls meet at (RW, RD)
        box(RW - 0.04, RD - 0.04, RW + 0.04, RD + 0.04, 0, WALL_H, wall_col, ol=False)
    if faces:
        layer, at = HMG.polys_layer(faces)
        layer.set_alpha(34)
        screen.blit(layer, at)
    layer, at = HMG.polys_layer(trim + list(extra_polys))
    layer.set_alpha(88)
    screen.blit(layer, at)
    col = art.lerp(frame_col, (150, 170, 200), 0.12)
    for side, doors in (("S", doors_S), ("E", doors_E)):
        W = WS if side == "S" else WE
        for a, b in doors:
            if (a, b) in arches:
                if not FLIP:
                    ghost_door_frame(W, a, b, shade(col, 1.0 if side == "S" else .8), arch=True)
                continue
            layer, at = HMG.polys_layer(HMG.door_frame_polys(W, a, b, shade(col, 1.0 if side == "S" else .8), t - 0.05, t + 0.05))
            layer.set_alpha(HMG.GHOST_FRAME_ALPHA + 30)
            screen.blit(layer, at)


def place_sprite(name, x, y, facing="sw"):
    """An existing Haunted Mansion character sprite standing at floor (x, y)."""
    ar = pygame.image.load(os.path.join(HM, "assets", "characters", f"{name}_{facing}.png")).convert_alpha()
    ar = pygame.transform.smoothscale(ar, (ar.get_width() * S, ar.get_height() * S))
    gx, gy = P(x, y)
    sh = art.soft_shadow(30 * S, 12 * S, 70)
    screen.blit(sh, (gx - sh.get_width() / 2, gy - sh.get_height() / 2))
    screen.blit(ar, (gx - 50 * S, gy - 162 * S))


def finish(title, out, subtitle="Ground Floor", copies=()):
    """Downscale, vignette, caption, save (plus any copies)."""
    out_img = pygame.transform.smoothscale(screen, (WIN_W, WIN_H))
    vignette(out_img)
    f = pygame.font.Font(None, 34)
    f2 = pygame.font.Font(None, 24)
    out_img.blit(f.render(title, True, (236, 226, 200)), (24, 20))
    out_img.blit(f2.render(subtitle, True, (190, 180, 160)), (24, 50))
    for p in (out,) + tuple(copies):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        pygame.image.save(out_img, p)
        print(p)
    return out_img


def casement_window(side, u0, u1, ext, z0=100, z1=204, cols=4, rows=1, col=WHITE, sill_col=WHITE, top_lights=False):
    """A long multi-pane casement on a back wall: a real opening onto the
    exterior layer (show_through), then frame, mullions/transoms and sill."""
    k = wall_k(side)
    W = lambda u, z, n=0.0: wall_pt(side, u, z, n)
    wall_quad(side, u0 - .08, u1 + .08, z0 - 6, z1 + 8, shade(col, k))
    show_through(ext, [W(u0, z0), W(u1, z0), W(u1, z1), W(u0, z1)])
    fc = shade(col, k * 1.03)
    for zz in (z0, z1 - 5):
        wall_quad(side, u0, u1, zz, zz + 5, fc, .005)
    for i in range(cols + 1):
        u = u0 + (u1 - u0) * i / cols
        wall_quad(side, u - .035, u + .035, z0, z1, fc, .006)
    for j in range(1, rows):
        z = z0 + (z1 - z0) * j / rows
        wall_quad(side, u0, u1, z - 2, z + 2, fc, .006)
    if top_lights:
        z = z1 - (z1 - z0) * .28
        wall_quad(side, u0, u1, z - 2, z + 2, fc, .006)
    wall_quad(side, u0 - .14, u1 + .14, z0 - 12, z0 - 5, shade(sill_col, k * 1.06), .05)


def ext_car(side, u0, u1, t0, t1, col=(150, 155, 160), h=34, cabin=24):
    """A parked car on the exterior ground plane: body, glassy cabin, wheels."""
    b = [u0, -t1, u1, -t0] if side == "N" else [-t1, u0, -t0, u1]
    x0, y0, x1, y1 = b
    for (wx, wy) in (((x0 + (x1 - x0) * .18), y1), ((x0 + (x1 - x0) * .82), y1)) if side == "N" else ((x1, y0 + (y1 - y0) * .18), (x1, y0 + (y1 - y0) * .82)):
        fl_ellipse(wx, wy, .13, .13, (20, 20, 22), z=GROUND_Z + 8)
    fl_ellipse((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * .6, (y1 - y0) * .6, (40, 40, 38), z=GROUND_Z)
    box(x0, y0, x1, y1, GROUND_Z + 8, GROUND_Z + h, col)
    if side == "N":
        cx0, cx1 = x0 + (x1 - x0) * .25, x1 - (x1 - x0) * .2
        box(cx0, y0 + .08, cx1, y1 - .08, GROUND_Z + h, GROUND_Z + h + cabin, (70, 84, 96), top=shade(col, 1.05))
        # side detail on the face towards the house: belt line, door seams, handles, wheel arches
        qy(y1 + .003, x0 + .1, x1 - .1, GROUND_Z + h * .62, GROUND_Z + h * .66, shade(col, KY * 1.35))
        for f in (.34, .56, .78):
            xs = x0 + (x1 - x0) * f
            qy(y1 + .003, xs, xs + .03, GROUND_Z + 14, GROUND_Z + h - 4, shade(col, KY * .6))
            qy(y1 + .004, xs - .22, xs - .1, GROUND_Z + h * .5, GROUND_Z + h * .55, (200, 200, 200))
        for f in (.18, .82):
            xs = x0 + (x1 - x0) * f
            qy(y1 + .003, xs - .35, xs + .35, GROUND_Z + 8, GROUND_Z + 34, (24, 24, 26))
        for f in (.4, .62):
            xs = cx0 + (cx1 - cx0) * f
            qy(y1 - .079, xs, xs + .06, GROUND_Z + h, GROUND_Z + h + cabin, shade(col, KY * .8))
    else:
        cy0, cy1 = y0 + (y1 - y0) * .25, y1 - (y1 - y0) * .2
        box(x0 + .08, cy0, x1 - .08, cy1, GROUND_Z + h, GROUND_Z + h + cabin, (70, 84, 96), top=shade(col, 1.05))



# ============================================================ open-plan rooms
# The Kitchen + Dining Room (10.2 m x 5.2 m, across the back of the house) is
# ONE room in ONE coordinate system, in the house camera convention: world
# x = tiles westwards from its east wall (0 .. KD_LEN, 0.62 m per tile),
# world y = tiles northwards from its south wall (0 .. KD_DEP; y = KD_DEP is
# the garden wall). Dining = world x 0 .. KD_SPLIT (east), kitchen = KD_SPLIT
# .. KD_LEN (west, by the Boot Room). Too big for one screen at engine scale,
# it is shown as two camera framings along x; each framing is an
# ordinary room for the helpers (local x = world x - its x0):
#   kitchen view (x0 = KD_SPLIT): open on its back-left side (x = 0, the
#       beam); the dining half recedes beyond it, faded (fade_x).
#   dining view  (x0 = 0): open on its near-left side (x = RW); the kitchen
#       comes nearer beyond it, faded.
# The beam across the ceiling at world x = KD_SPLIT marks the join.
KD_VIEWS = {"dining": 0.0, "kitchen": 8.2}      # each view's world x0
KD_LEN, KD_DEP, KD_SPLIT = 16.4, 8.4, 8.2

SLATE = ((196, 160, 84), (176, 104, 60), (118, 124, 98), (96, 98, 88), (208, 178, 104), (150, 128, 76), (134, 92, 62))
OFF_WHITE = (232, 228, 216)
PALE_GREY = (204, 206, 202)
GRANITE = (58, 60, 66)
STEEL = (178, 182, 186)
PINE_TOP = (200, 156, 100)
BURGUNDY = (104, 28, 38)


def floor_slate(x0=0.0, y0=0.0, x1=None, y1=None, seed=8, z=0.0):
    """Multicoloured riven slate (ochre, rust, grey-green) in staggered courses."""
    import paint
    x1 = RW if x1 is None else x1
    y1 = RD if y1 is None else y1
    paint.stamp(paint.slate(x1 - x0, y1 - y0, seed, SLATE), x0, y0, x1, y1, z)


def floor_edge_S(x0, x1, col):
    """The floor slab's front edge along y = RD (for rooms whose E side is open)."""
    poly([P(x0, RD), P(x1, RD), P(x1, RD, -SLAB), P(x0, RD, -SLAB)], shade(col, 0.42))


def wall_clock(side, u, z, r=0.42, col=(150, 152, 150)):
    """A round wall clock lying on a back wall (r in tiles along the wall)."""
    k = wall_k(side)
    rz = r * 63
    ring = [wall_pt(side, u + r * math.cos(a), z + rz * math.sin(a), .03) for a in [i * math.pi / 18 for i in range(36)]]
    face = [wall_pt(side, u + .86 * r * math.cos(a), z + .86 * rz * math.sin(a), .035) for a in [i * math.pi / 18 for i in range(36)]]
    poly(ring, shade(col, k * .8))
    poly(face, shade((214, 214, 210), k))
    for i in range(12):
        a = i * math.pi / 6
        pygame.draw.circle(screen, (60, 60, 60), wall_pt(side, u + .74 * r * math.cos(a), z + .74 * rz * math.sin(a), .04), S)
    c = wall_pt(side, u, z, .04)
    pygame.draw.line(screen, (40, 40, 40), c, wall_pt(side, u + .1 * r, z + .55 * rz, .04), 2 * S)
    pygame.draw.line(screen, (40, 40, 40), c, wall_pt(side, u + .5 * r, z - .2 * rz, .04), S)


def bar_stool(x, y, h=68, col=(176, 122, 70)):
    """Wooden bar stool: four splayed legs, two rungs, round seat."""
    r = .2
    for dx, dy in ((-r, -r), (r, -r), (-r, r), (r, r)):
        box(x + dx * .95 - .025, y + dy * .95 - .025, x + dx * .95 + .025, y + dy * .95 + .025, 0, h - 4, shade(col, .9), ol=False)
    for zz in (20, 44):
        line((x - r, y + r, zz), (x + r, y + r, zz), shade(col, .8), 2)
        line((x + r, y - r, zz), (x + r, y + r, zz), shade(col, .7), 2)
    cyl(x, y, .25, h - 6, h, col, top=shade(col, 1.12))


def turned_leg(x, y, z0, z1, col, r=.05):
    """A turned leg: shaft with a couple of bulbs."""
    box(x - r * .6, y - r * .6, x + r * .6, y + r * .6, z0, z1, col, ol=False)
    for f in (.25, .62):
        zz = z0 + (z1 - z0) * f
        cyl(x, y, r * 1.25, zz - 5, zz + 5, shade(col, .95))


def farmhouse_table(x0, y0, x1, y1, h=74, col=(196, 150, 96)):
    """Long pine farmhouse table with turned legs (dining)."""
    for lx, ly in ((x0 + .15, y0 + .15), (x1 - .15, y0 + .15), (x0 + .15, y1 - .15), (x1 - .15, y1 - .15)):
        turned_leg(lx, ly, 0, h - 8, shade(col, .85), .07)
    box(x0 + .1, y0 + .1, x1 - .1, y1 - .1, h - 16, h - 6, shade(col, .85), ol=False)
    import iso_paint
    iso_paint.paint_box(x0, y0, x1, y1, h - 6, h, "dining_pine", front="S", col=col)


def ladder_chair(x, y, facing="E", col=(236, 234, 228)):
    """White ladder-back chair; `facing` = the way a sitter faces (back on the other side)."""
    s = .2
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        box(x + dx - .025, y + dy - .025, x + dx + .025, y + dy + .025, 0, 44, shade(col, .92), ol=False)
    box(x - s - .03, y - s - .03, x + s + .03, y + s + .03, 44, 49, col, top=(206, 176, 120))   # rush seat
    if facing in ("E", "W"):
        bx = x - s if facing == "E" else x + s
        for dy in (-s, s):
            box(bx - .03, y + dy - .03, bx + .03, y + dy + .03, 49, 118, col, ol=False)
        for zz in (70, 86, 102, 115):
            box(bx - .02, y - s, bx + .02, y + s, zz - 3, zz + 3, col, ol=False)
    else:
        by = y - s if facing == "S" else y + s
        for dx in (-s, s):
            box(x + dx - .03, by - .03, x + dx + .03, by + .03, 49, 118, col, ol=False)
        for zz in (70, 86, 102, 115):
            box(x - s, by - .02, x + s, by + .02, zz - 3, zz + 3, col, ol=False)


def glimpse_layer():
    """A transparent full-canvas layer to draw the other half of an open-plan room on
    (use `with drawing_on(layer):`), then fade_beyond_E(layer, ...) and blit."""
    return pygame.Surface(screen.get_size(), pygame.SRCALPHA)


def _fade_content(layer, z_ref, tone):
    """Multiply the alpha of the non-empty part of `layer`. `tone(sx, sy) -> t`."""
    w, h = layer.get_size()
    a = pygame.surfarray.pixels_alpha(layer)
    cols = np.flatnonzero(a.any(axis=1))
    rows = np.flatnonzero(a.any(axis=0))
    if len(cols) == 0:
        del a
        return layer
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    sx = (np.arange(x0, x1)[:, None] / S - OX) / HW
    sy = (np.arange(y0, y1)[None, :] / S - OY + z_ref) / HH
    xd = (sx + sy) / 2
    if FLIP:
        # the layer was drawn through the spun projection, so recover room x
        xe = RW - xd
    else:
        xe = np.maximum(xd, np.broadcast_to(sx, (x1 - x0, y1 - y0)))
    t = np.clip(tone(xe), 0, 1)
    t = t * t * (3 - 2 * t)
    a[x0:x1, y0:y1] = (a[x0:x1, y0:y1] * t).astype(np.uint8)
    del a
    return layer


def fade_x(layer, x_opaque, x_gone, z_ref=0):
    """Fade a layer by room x: fully there at x_opaque, gone at x_gone (either
    direction), using the same per-pixel x estimate as fade_beyond_E, taking
    floor pixels to be at height z_ref (use ~table height for furniture)."""
    return _fade_content(layer, z_ref, lambda xe: (xe - x_gone) / (x_opaque - x_gone))


def fade_beyond_E(layer, xa, xb):
    """Fade a layer out with distance past the open E side: opaque up to world x = xa,
    gone by xb. x is estimated per pixel as max(floor x, back-wall u), which is exact
    for the floor and the y = 0 wall and close enough for furniture."""
    return _fade_content(layer, 0, lambda xe: (xb - xe) / (xb - xa))


# ============================================================ small-room kit (Office, Utility)
def union_jack(Wf, u0, u1, z0, z1, k=1.0):
    """A Union Jack on any plane: Wf(u, z) -> screen point (cushions, flags).
    Returns (colour, polygon) pieces so it can also go on a ghost layer."""
    blue, red, white = shade((20, 40, 110), k), shade((200, 30, 40), k), shade((245, 245, 245), k)
    U = lambda f: u0 + (u1 - u0) * f
    Z = lambda g: z0 + (z1 - z0) * g
    q = lambda a, b, c, d: [Wf(*a), Wf(*b), Wf(*c), Wf(*d)]
    out = [(blue, q((U(0), Z(0)), (U(1), Z(0)), (U(1), Z(1)), (U(0), Z(1))))]
    for w, c in ((.12, white), (.05, red)):            # the diagonals
        out.append((c, q((U(0), Z(w)), (U(w), Z(0)), (U(1), Z(1 - w)), (U(1 - w), Z(1)))))
        out.append((c, q((U(0), Z(1 - w)), (U(w), Z(1)), (U(1), Z(w)), (U(1 - w), Z(0)))))
    for w, c in ((.2, white), (.12, red)):             # the upright cross
        out.append((c, q((U(.5 - w / 2), Z(0)), (U(.5 + w / 2), Z(0)), (U(.5 + w / 2), Z(1)), (U(.5 - w / 2), Z(1)))))
        out.append((c, q((U(0), Z(.5 - w)), (U(1), Z(.5 - w)), (U(1), Z(.5 + w)), (U(0), Z(.5 + w)))))
    return out


def hung_layer(alpha=96):
    """Context for things hung on a ghost near wall (they face away): draw inside,
    then they are blitted faint, like the wall itself. In the opposite view those
    walls face the camera, so the same objects are drawn solid on the room."""
    class _Hung:
        def __enter__(self):
            if FLIP:
                self.skip = True
                return screen
            self.skip = False
            self.layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.ctx = drawing_on(self.layer)
            self.ctx.__enter__()
            return self.layer

        def __exit__(self, *a):
            if self.skip:
                return False
            self.ctx.__exit__(*a)
            self.layer.set_alpha(alpha)
            screen.blit(self.layer, (0, 0))
    return _Hung()


def photo_shelf(side, u0, u1, z, rnd, depth=0.12, col=WHITE, frames=None, interiors=None):
    """A picture-rail shelf on a back wall, crowded with small framed photos
    (frames / interiors: optional colour lists to pick from)."""
    k = wall_k(side)
    W = lambda u, zz, n=0.0: wall_pt(side, u, zz, n)
    poly([W(u0, z, 0), W(u1, z, 0), W(u1, z, depth), W(u0, z, depth)], shade(col, KT))
    poly([W(u0, z - 5, depth), W(u1, z - 5, depth), W(u1, z, depth), W(u0, z, depth)], shade(col, k * .95))
    u = u0 + .06
    while u < u1 - .2:
        w = rnd.uniform(.14, .26)
        h = rnd.uniform(18, 30)
        fr = rnd.choice(frames or [(30, 28, 26), (240, 238, 232), (150, 110, 70), (200, 170, 90)])
        n = depth * .5
        poly([W(u, z, n), W(u + w, z, n), W(u + w, z + h, n - .02), W(u, z + h, n - .02)], shade(fr, k))
        inner = shade(rnd.choice(interiors or [(190, 186, 176), (150, 160, 170), (210, 200, 180), (120, 130, 120)]), k)
        poly([W(u + .025, z + 3, n + .002), W(u + w - .025, z + 3, n + .002), W(u + w - .025, z + h - 3, n - .018), W(u + .025, z + h - 3, n - .018)], inner)
        u += w + rnd.uniform(.02, .07)


FRAME_COLOURS = {"wood": (160, 116, 72), "cream": (236, 230, 214), "white": (246, 246, 242),
                 "black": (30, 28, 26), "sage": (140, 164, 146), "red": (176, 44, 44)}


def colour_photo(rnd):
    """Inner for frame_N / frame_W given a plane(a, b, za, zb, col) drawer: a small
    colour snapshot (sky, land, a figure or two) or a bright print."""
    def make(plane):
        def f(a, b, za, zb):
            kind = rnd.random()
            if kind < .6:      # outdoor snapshot
                sky = rnd.choice([(150, 190, 220), (190, 210, 230), (230, 200, 160)])
                land = rnd.choice([(90, 140, 70), (200, 180, 120), (70, 110, 150), (120, 150, 90)])
                hz = za + (zb - za) * rnd.uniform(.35, .6)
                plane(a, b, hz, zb, sky)
                plane(a, b, za, hz, land)
                for _ in range(rnd.randint(1, 3)):
                    uu = a + (b - a) * rnd.uniform(.15, .75)
                    w = (b - a) * .12
                    plane(uu, uu + w, za + (zb - za) * .12, za + (zb - za) * rnd.uniform(.55, .75),
                          rnd.choice([(200, 60, 60), (40, 60, 120), (230, 200, 60), (60, 50, 40), (240, 240, 236)]))
            else:              # a bright print or a child's painting
                plane(a, b, za, zb, rnd.choice([(240, 226, 190), (210, 230, 220), (250, 240, 230)]))
                for _ in range(3):
                    u0 = a + (b - a) * rnd.uniform(0, .6)
                    z0 = za + (zb - za) * rnd.uniform(0, .6)
                    plane(u0, min(b, u0 + (b - a) * .35), z0, min(zb, z0 + (zb - za) * .35),
                          rnd.choice([(220, 80, 60), (60, 140, 200), (250, 190, 40), (90, 170, 90)]))
        return f
    return make
