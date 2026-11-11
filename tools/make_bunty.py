#!/usr/bin/env python3
"""Paint Bunty's sprites (the family cat, a small dark tabby).

Same method as Myrtle (tools/make_myrtle.py): a signed-distance model in
centimetres (forward, side, up) built from round cones and ellipsoids with
smooth unions, ray-marched through the house's 2:1 camera at 3x, shaded with
the rooms' light and edged in a soft dark line. The coat is painted on the
model: a grey-brown ground with dark tabby bands that run round each part
(body, legs, tail rings), a dark dorsal stripe and back, a warped noise so
the bands break up into blotches like the photo, a white chin and muzzle,
white front toes and white hind legs up to the hock, green eyes, a pink nose.

She is about 45 cm nose to rump and 25 cm at the shoulder, so on screen she
is clearly smaller than Myrtle.

Output (assets/bunty/):
    bunty_<k>.png           standing, tail up        k in se, sw, nw, ne
    bunty_<k>_walk.png      8-frame walk cycle, frames side by side
    bunty_<k>_sit.png       sitting, tail round her feet
    bunty_<k>_sleep.png     curled up asleep
    bunty_<k>_jump.png      mid-hop (stretched out, up onto / down off things)
    bunty.json              frame size, ground anchor, walk cycle length

    python3 tools/make_bunty.py
"""
import json
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import numpy as np  # noqa: E402
import pygame  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_myrtle import RC, EL_, smin, vnoise, ik, FACINGS, EL, SCALE, SS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "bunty")
FW, FH = 112, 96                          # frame size (px)
AX, AY = 56, 74                           # ground point under her middle
FRAMES = 8
CYCLE_TILES = 0.55                        # tiles per walk cycle (short legs)

GROUND = np.array([118, 104, 86], np.float32)      # grey-brown agouti
BELLY = np.array([150, 138, 118], np.float32)
STRIPE = np.array([30, 26, 23], np.float32)
WHITE = np.array([226, 224, 218], np.float32)
EYE = np.array([128, 166, 70], np.float32)
PUPIL = np.array([16, 16, 14], np.float32)
NOSE = np.array([206, 136, 126], np.float32)
EAR_IN = np.array([168, 120, 110], np.float32)
LID = np.array([40, 34, 30], np.float32)
LINE = (16, 13, 11)
MATS = {"coat": 0, "white": 1, "eye": 2, "pupil": 3, "nose": 4, "ear": 5, "lid": 6}
FUR = {"coat", "white"}                   # blended smoothly into each other


class Model:
    """Like Myrtle's, but 'coat' and 'white' blend, and the closest part is
    remembered so each part can carry its own stripe direction."""
    def __init__(self, parts):
        self.parts = parts

    def d(self, p, mats=False):
        dist = best = mat = who = None
        for i, prt in enumerate(self.parts):
            di = prt.d(p)
            if dist is None:
                dist, best = di, di
                mat = np.full(len(p), MATS[prt.mat], np.int8)
                who = np.zeros(len(p), np.int16)
                continue
            dist = smin(dist, di, prt.k) if prt.mat in FUR else np.minimum(dist, di)
            if mats:
                closer = di < best
                best = np.where(closer, di, best)
                mat = np.where(closer, MATS[prt.mat], mat)
                who = np.where(closer, i, who)
        return (dist, mat, who) if mats else dist

    def bounds(self):
        pts = np.array([b for prt in self.parts for b in prt.bound()], np.float32)
        return pts.min(0), pts.max(0)


def axis_of(prt):
    """The direction a part's tabby bands run across (its long axis)."""
    if getattr(prt, "band", None) is not None:
        a = np.array(prt.band, np.float32)
    elif isinstance(prt, RC):
        a = prt.b - prt.a
    else:
        a = prt.R[:, 0]
    return a / (np.linalg.norm(a) + 1e-9)


def P(prt, band=None, freq=None, solid=False, phase=None):
    """Tag a part with its tabby band direction / frequency. `phase` (a start
    point and the distance already run) keeps bands continuous along a chain
    of round cones, so the tail reads as rings, not as joints."""
    prt.band, prt.freq, prt.solid, prt.phase = band, freq, solid, phase
    return prt


# ------------------------------------------------------------------ anatomy
def head(c, yaw=0.0, look=0.0, asleep=False):
    """Round skull, short muzzle with white chin, upright ears, green eyes."""
    cf, cs, cu = c
    cy, sy = math.cos(yaw), math.sin(yaw)

    def at(f, s, u):
        fu = f * math.cos(look) - u * math.sin(look)
        uu = f * math.sin(look) + u * math.cos(look)
        return (cf + fu * cy - s * sy, cs + fu * sy + s * cy, cu + uu)

    up = (-math.sin(look) * cy, -math.sin(look) * sy, math.cos(look))
    out = [P(EL_(at(0, 0, 0), (5.0, 4.9, 4.4), k=1.6, yaw=yaw, pitch=look), band=up, freq=1.3),      # skull, M-lines across the brow
           P(EL_(at(-2.4, 0, -1.6), (4.0, 4.4, 3.8), k=2.0, yaw=yaw), band=up, freq=1.2),
           EL_(at(1.6, 3.4, -1.0), (2.6, 2.0, 2.4), k=1.4, yaw=yaw),                                    # cheeks
           EL_(at(1.6, -3.4, -1.0), (2.6, 2.0, 2.4), k=1.4, yaw=yaw),
           P(EL_(at(4.4, 0, -1.2), (1.9, 2.4, 1.7), k=1.0, yaw=yaw, pitch=look), solid=True),           # muzzle
           EL_(at(4.0, 1.25, -1.9), (1.4, 1.3, 1.1), mat="white", k=0.8, yaw=yaw),                       # white whisker pads
           EL_(at(4.0, -1.25, -1.9), (1.4, 1.3, 1.1), mat="white", k=0.8, yaw=yaw),
           EL_(at(3.4, 0, -3.0), (1.8, 1.7, 1.1), mat="white", k=1.0, yaw=yaw, pitch=look),             # white chin
           EL_(at(5.9, 0, -0.5), (0.55, 0.75, 0.5), mat="nose", yaw=yaw, pitch=look)]
    for s in (1, -1):
        base = at(-0.6, 2.7 * s, 3.4)
        tip = at(-1.1, 3.4 * s, 7.6)
        out += [P(RC(base, tip, 1.9, 0.25, k=0.8), solid=True),                                         # ears
                EL_(at(0.2, 2.75 * s, 4.6), (0.35, 1.0, 1.5), mat="ear", yaw=yaw, roll=-0.2 * s)]
        if asleep:
            out.append(EL_(at(3.7, 2.05 * s, 0.9), (0.45, 1.1, 0.22), mat="lid", yaw=yaw + 0.5 * s))
        else:
            out += [EL_(at(3.5, 2.0 * s, 0.9), (0.9, 1.15, 1.0), mat="eye", yaw=yaw + 0.45 * s),
                    EL_(at(4.25, 2.15 * s, 0.9), (0.3, 0.3, 0.8), mat="pupil", yaw=yaw + 0.45 * s)]
    return out


def tail(pts, r0=2.0, r1=1.3):
    out = []
    n = len(pts) - 1
    run = 0.0
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        out.append(P(RC(pts[i], pts[i + 1], ra, rb, k=2.5), freq=1.05, phase=(pts[i], run)))
        run += math.dist(pts[i], pts[i + 1])
    return out


def body(z=0.0, arch=0.0):
    return [P(EL_((8, 0, 20 + z), (8.5, 6.2, 7.6), k=3)),                      # chest
            P(RC((8, 0, 21 + z + arch * 0.4), (-10, 0, 21.5 + z + arch), 6.4, 6.6, k=4), band=(1, 0, 0)),
            P(EL_((-12, 0, 20 + z), (7.6, 6.2, 7.6), k=4)),                    # hips
            EL_((-1, 0, 16.5 + z), (10, 5.2, 3.6), k=4),                       # belly
            EL_((14, 0, 19.5 + z), (3.6, 4.6, 6), k=3)]                         # forechest


def legs(ph, moving, z=0.0, stride=6.5, lift_h=3.0):
    out = []
    for side, off in ((3.3, 0.0), (-3.3, math.pi)):
        for front in (True, False):
            p = ph + off + (0.0 if front else math.pi * 0.5)
            swing = math.sin(p) if moving else 0.0
            lift = max(0.0, math.cos(p)) ** 1.5 * (lift_h if moving else 0.0)
            if front:
                sh = (11, side, 18 + z)
                paw = (12.5 + stride * swing, side, 1.2 + lift)
                wrist = (paw[0] - 0.3 - lift * 0.4, side, 4.2 + lift * 0.8)
                elbow = ik(sh, wrist, 8.5, 8.6, -1)
                out += [RC(sh, elbow, 2.9, 2.1, k=2.2), RC(elbow, wrist, 2.0, 1.6, k=1.2),
                        EL_((paw[0] + 0.9, side, 1.2 + lift), (2.0, 1.7, 1.25), mat="white", k=0.9),
                        RC(wrist, (paw[0] + 0.4, side, paw[2] + 0.4), 1.6, 1.6, mat="white", k=0.8)]
            else:
                hip = (-13, side, 19 + z)
                paw = (-13 + stride * swing, side, 1.2 + lift)
                hock = (paw[0] - 3.2, side, 6.4 + lift)
                stifle = ik(hip, hock, 9.5, 9.5, 1)
                out += [EL_((-12, side * 1.15, 15.5 + z), (5.4, 3.0, 6.2), k=3, pitch=0.25),
                        RC(hip, stifle, 3.4, 2.4, k=2.2),
                        RC(stifle, hock, 2.1, 1.5, mat="white", k=1.0),
                        RC(hock, (paw[0] + 0.3, side, paw[2] + 0.4), 1.5, 1.5, mat="white", k=0.8),
                        EL_((paw[0] + 0.9, side, 1.2 + lift), (2.0, 1.7, 1.25), mat="white", k=0.9)]
    return out


def pose_walk(i=None):
    moving = i is not None
    ph = 0.0 if not moving else 2 * math.pi * i / FRAMES
    bob = 0.5 * abs(math.sin(ph * 2)) if moving else 0.0
    parts = body(bob)
    parts += [P(RC((14, 0, 22 + bob), (17.5, 0, 27 + bob), 4.2, 3.6, k=2.5), band=(0, 0, 1))]
    parts += head((20.5, 0, 29.5 + bob), look=0.05)
    sw = 0.25 * math.sin(ph) if moving else 0.0
    parts += tail([(-18, 0, 22 + bob), (-22, sw * 2, 28 + bob), (-23.5, sw * 4, 37 + bob),
                   (-22.5, sw * 5, 45 + bob), (-19.5, sw * 5, 49 + bob), (-17, sw * 4, 48 + bob)])
    parts += legs(ph, moving, bob)
    return Model(parts)


def pose_sit():
    parts = [P(EL_((-5, 0, 8), (8.0, 6.6, 7.6), k=3)),                          # haunches
             P(EL_((0.5, 0, 15.5), (11, 6.0, 6.6), k=4, pitch=1.15), band=(0.4, 0, 1)),   # back, upright
             P(EL_((5, 0, 20), (5.6, 5.8, 7.2), k=3)),                            # chest
             EL_((8, 0, 18), (2.6, 4.2, 5.6), k=2.5),
             EL_((-4, 5.2, 7), (6.8, 2.6, 5.4), k=2.5), EL_((-4, -5.2, 7), (6.8, 2.6, 5.4), k=2.5)]   # thighs
    parts += [P(RC((6, 0, 24), (8, 0, 28.5), 4.0, 3.5, k=2.5), band=(0, 0, 1))]
    parts += head((10.5, 0, 31), look=0.08)
    for s in (2.6, -2.6):
        parts += [RC((7, s, 18), (8.6, s, 3.4), 2.4, 1.6, k=1.6),
                  RC((8.6, s, 3.4), (9.4, s, 1.4), 1.6, 1.6, mat="white", k=0.8),
                  EL_((10.2, s, 1.2), (2.0, 1.7, 1.2), mat="white", k=0.9),               # front paws
                  EL_((1.5, s * 2.3, 1.4), (3.6, 1.9, 1.4), mat="white", k=1.0),          # hind feet forward
                  EL_((-4.0, s * 2.3, 3.4), (1.9, 1.6, 2.4), mat="white", k=1.0)]         # hocks
    parts += tail([(-12, 0, 3), (-11, -6, 1.8), (-4, -9.5, 1.7), (4, -8.6, 1.6), (9, -5.6, 1.5)], 1.9, 1.3)
    return Model(parts)


def pose_sleep():
    """Curled up: a round loaf, head tucked on the forepaws, tail round the front."""
    parts = [P(EL_((-1, 0, 7.2), (12.5, 10, 7.2), k=4, yaw=0.25), band=(math.cos(0.25), math.sin(0.25), 0)),
             P(EL_((-8, 3, 7.4), (7.5, 7.5, 6.6), k=4)),                          # hips rolled round
             P(EL_((6.5, -3.5, 6.6), (6.4, 6.4, 6.0), k=4))]                      # shoulders
    parts += head((9.0, -4.5, 9.6), yaw=-0.75, look=0.28, asleep=True)
    parts += [EL_((12.2, -1.0, 1.4), (2.6, 1.8, 1.3), mat="white", k=1.0, yaw=-0.6),       # forepaws tucked
              EL_((10.5, 2.2, 1.6), (2.4, 1.8, 1.3), mat="white", k=1.0, yaw=-0.3),
              EL_((-5, 9.5, 3.0), (4.6, 2.2, 2.4), mat="white", k=1.0, yaw=0.6)]          # a white hind leg showing
    parts += tail([(-13, 4, 4), (-11, 10.5, 2.6), (-3, 13, 2.4), (6, 11.5, 2.4), (12.5, 6, 2.2)], 2.1, 1.4)
    return Model(parts)


def pose_jump():
    """Mid-hop: stretched long, forelegs reaching forward-down, hind legs pushing back."""
    a = 0.30                                                                     # body tipped nose-up

    def T(f, s, u):                                                               # pitch about the middle
        return (f * math.cos(a) - (u - 18) * math.sin(a), s, 18 + f * math.sin(a) + (u - 18) * math.cos(a))

    parts = [P(EL_(T(8, 0, 20), (8.5, 6.0, 7.2), k=3, pitch=a)),
             P(RC(T(8, 0, 21), T(-11, 0, 21), 6.2, 6.2, k=4)),
             P(EL_(T(-13, 0, 20), (7.4, 6.0, 7.2), k=4, pitch=a)),
             EL_(T(-1, 0, 16.5), (10, 5.0, 3.4), k=4, pitch=a)]
    parts += [P(RC(T(14, 0, 22), T(18, 0, 26.5), 4.0, 3.5, k=2.5))]
    parts += head(T(21, 0, 28.5), look=a * 0.3)
    for s in (3.0, -3.0):
        sh = T(11, s, 18)
        parts += [RC(sh, T(17, s, 9), 2.8, 1.9, k=2.0), RC(T(17, s, 9), T(21, s, 3), 1.8, 1.5, k=1.2),
                  EL_(T(22, s, 2.0), (2.0, 1.6, 1.2), mat="white", k=0.9, pitch=a)]
        hip = T(-13, s, 19)
        parts += [EL_(T(-12, s * 1.15, 15.5), (5.4, 3.0, 6.0), k=3, pitch=a + 0.4),
                  RC(hip, T(-19, s, 12), 3.2, 2.2, k=2.0),
                  RC(T(-19, s, 12), T(-26, s, 7), 2.0, 1.5, mat="white", k=1.0),
                  EL_(T(-28, s, 6.0), (2.0, 1.6, 1.2), mat="white", k=0.9, pitch=a + 0.6)]
    parts += tail([T(-19, 0, 22), T(-26, 0, 25), T(-33, 0, 29), T(-39, 0, 35)])
    return Model(parts)


# ------------------------------------------------------------------ rendering
def render(model, facing):
    fx, fy = FACINGS[facing]

    def to_local(w):
        return np.array([w[0] * fx + w[1] * fy, -w[0] * fy + w[1] * fx, w[2]], np.float32)

    ce, se_ = math.cos(EL), math.sin(EL)
    r45 = 1 / math.sqrt(2)
    d_w = np.array([-ce * r45, -ce * r45, -se_])
    right_w = np.array([r45, -r45, 0.0])
    up_w = np.array([-se_ * r45, -se_ * r45, ce])
    L_w = np.array([0.35, 0.60, 1.0])
    L_w /= np.linalg.norm(L_w)
    d, right, up, L = (to_local(v) for v in (d_w, right_w, up_w, L_w))
    V = -d
    H = (L + V) / np.linalg.norm(L + V)
    s = SCALE * SS
    W, Hh = FW * SS, FH * SS
    lo, hi = model.bounds()
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    sx = AX * SS + (corners @ right) * s
    sy = AY * SS - (corners @ up) * s
    x0, x1 = max(0, int(sx.min()) - 4), min(W, int(sx.max()) + 5)
    y0, y1 = max(0, int(sy.min()) - 4), min(Hh, int(sy.max()) + 5)
    gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5, indexing="ij")
    gx, gy = gx.ravel().astype(np.float32), gy.ravel().astype(np.float32)
    plane = ((gx - AX * SS) / s)[:, None] * right + (-(gy - AY * SS) / s)[:, None] * up
    org = plane - d * 120.0
    t = np.zeros(len(gx), np.float32)
    hit = np.zeros(len(gx), bool)
    alive = np.arange(len(gx))
    for _ in range(110):
        if len(alive) == 0:
            break
        p = org[alive] + t[alive, None] * d
        dist = model.d(p)
        t[alive] += dist * 0.9
        done = dist < 0.02
        hit[alive[done]] = True
        gone = t[alive] > 240
        alive = alive[~(done | gone)]
    idx = np.flatnonzero(hit)
    img = np.zeros((W, Hh, 3), np.float32)
    mask = np.zeros((W, Hh), bool)
    if len(idx) == 0:
        return img, mask
    p = org[idx] + t[idx, None] * d
    _, mat, who = model.d(p, mats=True)
    e = 0.05
    k = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], np.float32)
    n = sum(k[i][None] * model.d(p + e * k[i])[:, None] for i in range(4))
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    nl = n @ L
    wrap = np.clip((nl + 0.35) / 1.35, 0, 1)
    nh = np.clip(n @ H, 0, 1)
    nv = np.clip(n @ V, 0, 1)
    ao = np.clip(0.6 + 0.4 * (model.d(p + n * 1.5) / 1.5 + model.d(p + n * 3.5) / 3.5) * 0.5, 0.4, 1.0)
    upz = n[:, 2]

    # -- tabby: bands round each part's long axis, warped by noise into blotches
    ax = np.stack([axis_of(prt) for prt in model.parts])[who]
    fr = np.array([getattr(prt, "freq", None) or 0.78 for prt in model.parts], np.float32)[who]
    solid = np.array([bool(getattr(prt, "solid", False)) for prt in model.parts])[who]
    org = np.array([(ph[0] if (ph := getattr(prt, "phase", None)) else (0, 0, 0)) for prt in model.parts], np.float32)[who]
    run = np.array([(ph[1] if (ph := getattr(prt, "phase", None)) else 0.0) for prt in model.parts], np.float32)[who]
    along = np.einsum("ij,ij->i", p - org, ax) + run
    tailp = np.array([getattr(prt, "phase", None) is not None for prt in model.parts])[who]
    warp = vnoise(p * 0.32 + 7.0) - 0.5
    warp2 = vnoise(p * 0.9 + 3.0) - 0.5
    band = np.sin(along * fr + np.where(tailp, warp * 1.2, warp * 5.5 + warp2 * 1.6))
    dark = np.clip((band + 0.02) * 2.4, 0, 1)
    # a dark dorsal stripe down the spine and a darker back, the underside paler
    dorsal = np.clip((upz - 0.6) * 3, 0, 1) * np.clip(1 - np.abs(p[:, 1]) / 2.2, 0, 1)
    back = np.clip((upz - 0.45) * 2.0, 0, 1) * 0.5
    dark = np.maximum(dark, np.maximum(dorsal * 0.95, back))
    dark = np.where(solid, 0.55, dark)
    pale = np.clip(-upz * 1.4, 0, 1) * (1 - dark)
    ticks = vnoise(p * 2.4) - 0.5
    coat = GROUND[None] * (1 - pale[:, None]) + BELLY[None] * pale[:, None]
    coat = coat * (1 - dark[:, None]) + STRIPE[None] * dark[:, None]
    coat = coat * (1 + 0.22 * ticks[:, None])
    key = (0.5 + 0.85 * wrap) * ao
    soft = 0.10 * nh ** 6
    rim = np.clip(0.16 * (1 - nv) ** 3 * np.clip(upz + 0.6, 0, 1.2), 0, 1)
    col = np.zeros((len(idx), 3), np.float32)
    m = mat == MATS["coat"]
    c_coat = coat * key[:, None] + 255 * soft[:, None] + np.array([90, 92, 100], np.float32) * rim[:, None]
    col[m] = c_coat[m]
    lit = (0.45 + 0.8 * wrap)[:, None]
    spec = (nh ** 30)[:, None]
    mw = mat == MATS["white"]
    c_white = WHITE[None] * (0.55 + 0.55 * wrap)[:, None] * ao[:, None] * (1 + 0.06 * ticks[:, None])
    col[mw] = c_white[mw]
    for name, base, gl in (("eye", EYE, 220), ("pupil", PUPIL, 200), ("nose", NOSE, 40),
                           ("ear", EAR_IN, 10), ("lid", LID, 0)):
        mm = mat == MATS[name]
        col[mm] = (base[None] * lit * ao[:, None] + gl * spec)[mm]
    ix = gx[idx].astype(int)
    iy = gy[idx].astype(int)
    img[ix, iy] = col
    mask[ix, iy] = True
    return img, mask


def to_surface(img, mask):
    W, H = img.shape[:2]
    big = pygame.Surface((W, H), pygame.SRCALPHA)
    rgb = pygame.surfarray.pixels3d(big)
    rgb[:] = np.clip(img, 0, 255).astype(np.uint8)
    del rgb
    a = pygame.surfarray.pixels_alpha(big)
    a[:] = (mask * 255).astype(np.uint8)
    del a
    small = pygame.transform.smoothscale(big, (FW, FH))
    alpha = pygame.surfarray.array_alpha(small).astype(np.float32) / 255
    grow = alpha.copy()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow = np.maximum(grow, np.roll(np.roll(alpha, dx, 0), dy, 1))
    edge = np.clip(grow - alpha, 0, 1)
    out = pygame.Surface((FW, FH), pygame.SRCALPHA)
    line = pygame.Surface((FW, FH), pygame.SRCALPHA)
    line.fill((*LINE, 0))
    la = pygame.surfarray.pixels_alpha(line)
    la[:] = (edge * 190).astype(np.uint8)
    del la
    out.blit(line, (0, 0))
    out.blit(small, (0, 0))
    return out


def frame(model, k):
    return to_surface(*render(model, k))


def main():
    pygame.init()
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    for k in FACINGS:
        if only and k not in only:
            continue
        pygame.image.save(frame(pose_walk(None), k), os.path.join(OUT, f"bunty_{k}.png"))
        sheet = pygame.Surface((FW * FRAMES, FH), pygame.SRCALPHA)
        for i in range(FRAMES):
            sheet.blit(frame(pose_walk(i), k), (i * FW, 0))
        pygame.image.save(sheet, os.path.join(OUT, f"bunty_{k}_walk.png"))
        pygame.image.save(frame(pose_sit(), k), os.path.join(OUT, f"bunty_{k}_sit.png"))
        pygame.image.save(frame(pose_sleep(), k), os.path.join(OUT, f"bunty_{k}_sleep.png"))
        pygame.image.save(frame(pose_jump(), k), os.path.join(OUT, f"bunty_{k}_jump.png"))
        print("bunty", k, flush=True)
    with open(os.path.join(OUT, "bunty.json"), "w") as f:
        json.dump({"size": [FW, FH], "anchor": [AX, AY], "frames": FRAMES, "cycle_tiles": CYCLE_TILES,
                   "facings": list(FACINGS)}, f, indent=1)


if __name__ == "__main__":
    main()
