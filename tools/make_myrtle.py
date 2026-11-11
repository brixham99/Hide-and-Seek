#!/usr/bin/env python3
"""Paint Myrtle's sprites (a medium black Labrador).

The dog is a signed-distance model in centimetres (forward, side, up):
round cones and ellipsoids blended with smooth unions, so the silhouette is
organic (deep chest, tucked waist, rounded skull, drop ears, otter tail,
shaped legs and paws). Each pose is ray-marched through the house's 2:1
orthographic camera at 3x, shaded with the rooms' light (key from the
upper left, a cool blue-grey sheen and rim so a black coat reads on dark
boards, a warm floor bounce), given a streaky fur texture, then downsampled
and edged in a soft dark line like Archie's sprites. One model, so every
facing and frame is the same dog.

Output (assets/myrtle/), same layout and anchors as before:
    myrtle_<k>.png            standing, k in se, sw, nw, ne (Archie's facings)
    myrtle_<k>_walk.png       8-frame walk cycle, frames side by side
    myrtle_<k>_sit.png        sitting, looking up
    myrtle_<k>_lie.png        lying down, curled a little (on her bed)
    myrtle.json               frame size, ground anchor, walk cycle length

    python3 tools/make_myrtle.py
"""
import json
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import numpy as np  # noqa: E402
import pygame  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "myrtle")
SS = 3                                   # supersampling
FW, FH = 180, 150                        # frame size (px)
AX, AY = 90, 118                         # ground point under the dog's middle
FRAMES = 8
CYCLE_TILES = 1.10
FACINGS = {"se": (1, 0), "sw": (0, 1), "nw": (-1, 0), "ne": (0, -1)}
# the house camera: a tile edge (60 cm) is (56, 28) px -> orthographic, 45 deg, 30 deg down
PX_CM = math.hypot(56, 28) / 60 / math.cos(math.radians(45)) * math.cos(math.radians(45))
SCALE = 1.32 * 0.94                      # px per cm on screen; 0.94 keeps her at her old size
EL = math.radians(30)

COAT = np.array([19, 19, 23], np.float32)
SHEEN = np.array([128, 142, 166], np.float32)
RIM = np.array([92, 108, 136], np.float32)
WARM = np.array([78, 54, 34], np.float32)
COLLAR = np.array([196, 34, 40], np.float32)
TAG = np.array([214, 178, 88], np.float32)
EYE = np.array([112, 64, 26], np.float32)
NOSE = np.array([30, 28, 31], np.float32)
TONGUE = np.array([212, 108, 120], np.float32)
MATS = {"coat": 0, "collar": 1, "tag": 2, "eye": 3, "nose": 4, "tongue": 5}


# ------------------------------------------------------------------ SDF pieces
def v3(*a):
    return np.array(a, np.float32)


class RC:
    """Round cone from a (radius ra) to b (radius rb)."""
    def __init__(self, a, b, ra, rb, mat="coat", k=4.0):
        self.a, self.b, self.ra, self.rb, self.mat, self.k = v3(*a), v3(*b), ra, rb, mat, k

    def bound(self):
        r = max(self.ra, self.rb)
        return [self.a - r, self.a + r, self.b - r, self.b + r]

    def d(self, p):
        a, b, r1, r2 = self.a, self.b, self.ra, self.rb
        ba = b - a
        l2 = float(ba @ ba)
        rr = r1 - r2
        a2 = l2 - rr * rr
        il2 = 1.0 / l2
        pa = p - a
        y = pa @ ba
        z = y - l2
        q = pa * l2 - y[:, None] * ba
        x2 = np.einsum("ij,ij->i", q, q)
        y2 = y * y * l2
        z2 = z * z * l2
        k = math.copysign(1, rr) * rr * rr * x2
        out = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
        m1 = np.sign(z) * a2 * z2 > k
        m2 = np.sign(y) * a2 * y2 < k
        out = np.where(m2, np.sqrt(x2 + y2) * il2 - r1, out)
        out = np.where(m1, np.sqrt(x2 + z2) * il2 - r2, out)
        return out


class EL_:
    """Ellipsoid at c with radii r, rotated by yaw (about up), pitch (nose up), roll."""
    def __init__(self, c, r, mat="coat", k=4.0, yaw=0.0, pitch=0.0, roll=0.0):
        self.c, self.r, self.mat, self.k = v3(*c), v3(*r), mat, k
        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)
        Ry = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]], np.float32)
        Rp = np.array([[cp, 0, -sp], [0, 1, 0], [sp, 0, cp]], np.float32)
        Rr = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]], np.float32)
        self.R = (Ry @ Rp @ Rr).astype(np.float32)

    def bound(self):
        m = float(self.r.max())
        return [self.c - m, self.c + m]

    def d(self, p):
        q = (p - self.c) @ self.R
        k0 = np.linalg.norm(q / self.r, axis=1)
        k1 = np.linalg.norm(q / (self.r * self.r), axis=1)
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


class TOR:
    """Thin torus (the collar strap) round axis `ax` at c."""
    def __init__(self, c, ax, R, r, mat="collar"):
        self.c, self.R, self.r, self.mat, self.k = v3(*c), R, r, mat, 0.0
        a = v3(*ax)
        self.ax = a / np.linalg.norm(a)

    def bound(self):
        m = self.R + self.r
        return [self.c - m, self.c + m]

    def d(self, p):
        q = p - self.c
        h = q @ self.ax
        rad = np.linalg.norm(q - h[:, None] * self.ax, axis=1)
        return np.sqrt((rad - self.R) ** 2 + h * h) - self.r


def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


class Model:
    def __init__(self, parts):
        self.parts = parts

    def d(self, p, mats=False):
        dist = None
        best = None
        mat = None
        for prt in self.parts:
            di = prt.d(p)
            if dist is None:
                dist, best = di, di
                mat = np.full(len(p), MATS[prt.mat], np.int8)
                continue
            if prt.mat == "coat":
                dist = smin(dist, di, prt.k)
            else:
                dist = np.minimum(dist, di)
            if mats:
                closer = di < best
                best = np.where(closer, di, best)
                mat = np.where(closer, MATS[prt.mat], mat)
        return (dist, mat) if mats else dist

    def bounds(self):
        pts = np.array([b for prt in self.parts for b in prt.bound()], np.float32)
        return pts.min(0), pts.max(0)


# ------------------------------------------------------------------ anatomy
def ik(root, target, l1, l2, bend):
    """2-bone IK in the (forward, up) plane: the middle joint, bending towards
    +forward (bend = 1, a hind stifle) or -forward (bend = -1, a front elbow)."""
    rf, ru = root[0], root[2]
    tf, tu = target[0], target[2]
    dx, dz = tf - rf, tu - ru
    d = max(1e-3, min(math.hypot(dx, dz), l1 + l2 - 1e-3))
    a = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    base = math.atan2(dz, dx)
    ang = base + bend * a
    return (rf + l1 * math.cos(ang), root[1], ru + l1 * math.sin(ang))


def head_parts(c, look_up=0.0, yaw=0.0, tongue=False):
    """Rounded skull, stop, muzzle and jaw, nose, eyes, drop ears.
    c = skull centre; look_up tilts the muzzle (radians); yaw turns the head."""
    cf, cs, cu = c
    cy, sy = math.cos(yaw), math.sin(yaw)

    def at(f, s, u):           # head-local (forward, side, up) -> body local
        # tilt about the skull centre, then turn
        fu = f * math.cos(look_up) - u * math.sin(look_up)
        uu = f * math.sin(look_up) + u * math.cos(look_up)
        return (cf + fu * cy - s * sy, cs + fu * sy + s * cy, cu + uu)

    out = [EL_(at(0, 0, 0), (9.6, 7.8, 8.2), k=3.0, yaw=yaw, pitch=look_up),
           EL_(at(-4, 0, -2), (7, 7.2, 7), k=4.0, yaw=yaw),                          # back of skull into neck
           RC(at(5.5, 0, -1.5), at(15.5, 0, -3.2), 5.9, 4.4, k=3.0),               # muzzle
           EL_(at(11, 0, -6.2), (6.0, 4.0, 2.6), k=2.5, yaw=yaw, pitch=look_up),    # jaw / chin
           EL_(at(5, 0, 3.8), (3.6, 4.6, 2.2), k=2.0, yaw=yaw),                     # brow
           EL_(at(17.6, 0, -2.4), (2.2, 2.6, 1.9), mat="nose", yaw=yaw, pitch=look_up),
           EL_(at(6.8, 4.4, 2.2), (1.25, 1.25, 1.25), mat="eye"),
           EL_(at(6.8, -4.4, 2.2), (1.25, 1.25, 1.25), mat="eye"),
           EL_(at(-1.2, 7.6, -3.2), (4.8, 1.5, 7.4), k=1.2, yaw=yaw, roll=0.32),     # drop ears
           EL_(at(-1.2, -7.6, -3.2), (4.8, 1.5, 7.4), k=1.2, yaw=yaw, roll=-0.32)]
    if tongue:
        out.append(EL_(at(12.5, 0, -7.6), (3.0, 2.3, 0.9), mat="tongue", yaw=yaw, pitch=look_up))
    return out


def collar(a, b, ra, rb, t=0.42):
    """A narrow strap round the neck round-cone (a -> b) at fraction t, with a tag."""
    a, b = np.array(a, float), np.array(b, float)
    c = a + (b - a) * t
    r = ra + (rb - ra) * t
    ax = b - a
    axn = ax / np.linalg.norm(ax)
    down = np.array([0, 0, -1.0]) - axn * axn[2] * -1
    down = np.array([0, 0, -1.0]) + axn * axn[2]
    down /= np.linalg.norm(down)
    tag = c + down * (r + 1.6) + np.array([1.2, 0, -0.6])
    return [TOR(c, ax, r - 0.15, 0.95), EL_(tuple(tag), (0.9, 1.5, 1.5), mat="tag")]


def body_stand(bob=0.0):
    z = bob
    return [EL_((13, 0, 44 + z), (17.5, 12.6, 16.5), k=5),                 # deep chest
            RC((14, 0, 47 + z), (-17, 0, 47.5 + z), 13.2, 11.8, k=6),       # ribs and back
            EL_((-20, 0, 46.5 + z), (13.5, 11.6, 12.2), k=6),               # croup / hips
            EL_((-6, 0, 39 + z), (14, 10.2, 7.0), k=6),                     # tucked waist
            EL_((22, 0, 41 + z), (7, 9.5, 11), k=5)]                       # forechest


def legs(ph, moving, bob):
    """Four legs for gait phase ph (radians). Walk: lateral sequence, 2 then 3 feet down."""
    out = []
    for side, off in ((6.6, 0.0), (-6.6, math.pi)):
        for front in (True, False):
            p = ph + off + (0.0 if front else math.pi * 0.5)
            swing = math.sin(p) if moving else 0.0
            lift = max(0.0, math.cos(p)) ** 1.5 * (6.0 if moving else 0.0)
            if front:
                sh = (18, side, 41 + bob)
                paw = (19 + 13 * swing, side, 3.0 + lift)
                wrist = (paw[0] - 0.8 - lift * 0.5, side, 9 + lift * 0.8)
                elbow = ik(sh, wrist, 16.5, 17.0, -1)
                out += [RC(sh, elbow, 7.2, 5.0, k=4), RC(elbow, wrist, 4.8, 3.5, k=2.5),
                        RC(wrist, (paw[0] + 0.6, side, paw[2] + 0.5), 3.5, 3.6, k=1.5),
                        EL_((paw[0] + 1.8, side, 2.5 + lift), (4.3, 3.5, 2.5), k=1.5)]
            else:
                hip = (-21, side, 44 + bob)
                paw = (-22 + 13 * swing, side, 3.0 + lift)
                hock = (paw[0] - 4.5, side, 13.5 + lift)
                stifle = ik(hip, hock, 18.0, 18.5, 1)
                out += [EL_((-20, side * 1.05, 36 + bob), (10, 5.6, 12), k=5, pitch=0.25),   # thigh
                        RC(hip, stifle, 8.2, 5.6, k=4), RC(stifle, hock, 5.2, 3.4, k=3),
                        RC(hock, (paw[0] + 0.4, side, paw[2] + 0.5), 3.4, 3.5, k=1.5),
                        EL_((paw[0] + 1.8, side, 2.5 + lift), (4.3, 3.5, 2.5), k=1.5)]
    return out


def tail(pts, r0=5.4, r1=2.0):
    out = []
    n = len(pts) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        out.append(RC(pts[i], pts[i + 1], ra, rb, k=3))
    return out


def pose_walk(i=None):
    moving = i is not None
    ph = 0.0 if not moving else 2 * math.pi * i / FRAMES
    bob = 1.0 * abs(math.sin(ph * 2)) if moving else 0.0
    parts = body_stand(bob)
    na, nb = (22, 0, 51 + bob), (33, 0, 63 + bob)
    parts += [RC(na, nb, 9.6, 7.4, k=5)]
    parts += head_parts((39.5, 0, 67.5 + bob), look_up=-0.08)
    wag = 0.45 * math.sin(ph) if moving else 0.18
    parts += tail([(-30, 0, 46 + bob), (-39, 6 * math.sin(wag), 40 + bob), (-46, 12 * math.sin(wag), 31 + bob),
                   (-49, 16 * math.sin(wag), 21 + bob)], 6.4, 2.2)
    parts += legs(ph, moving, bob)
    parts += collar(na, nb, 9.6, 7.4)
    return Model(parts)


def pose_sit():
    parts = [EL_((-10, 0, 16), (15, 13.6, 14.5), k=6),                  # haunches
             EL_((1, 0, 31), (23, 12.6, 13.2), k=6, pitch=0.95),          # back, tilted up
             EL_((11, 0, 44), (12.5, 12.4, 15.5), k=5),                   # chest
             EL_((-7, 9.8, 13), (12, 4.8, 9.5), k=4), EL_((-7, -9.8, 13), (12, 4.8, 9.5), k=4)]   # thighs
    na, nb = (14, 0, 55), (20, 0, 70)
    parts += [RC(na, nb, 9.2, 7.2, k=5)]
    parts += head_parts((26, 0, 76), look_up=0.32, tongue=True)
    for side in (6.4, -6.4):
        parts += [RC((15, side, 40), (16, side, 22), 6.0, 4.2, k=4), RC((16, side, 22), (17, side, 5), 4.2, 3.2, k=2.5),
                  EL_((19.5, side, 2.5), (4.4, 3.5, 2.5), k=1.5),
                  EL_((3, side * 1.6, 2.7), (6.2, 3.4, 2.7), k=2)]           # hind paws forward
    parts += tail([(-23, 0, 7), (-31, 6, 4), (-38, 12, 3.2), (-42, 18, 3.0)], 5.0, 2.2)
    parts += collar(na, nb, 9.2, 7.2, t=0.45)
    return Model(parts)


def pose_lie():
    """Sphinx-ish but curled: hips rolled to one side, tail round alongside,
    head turned a touch; about 75 cm long so she fits the bed."""
    parts = [EL_((2, 0, 15), (26, 14.0, 12.0), k=6, yaw=0.10),
             EL_((14, 0, 17), (14, 13, 13.5), k=5),
             EL_((-17, 3, 13), (13, 14, 11.5), k=6, yaw=0.25)]
    na, nb = (22, 0, 23), (29, 0, 34)
    parts += [RC(na, nb, 8.8, 7.2, k=5)]
    parts += head_parts((34, 1.5, 36), look_up=0.02, yaw=0.18)
    for side in (6.0, -6.0):
        parts += [RC((20, side, 9), (32, side, 4.5), 4.8, 3.6, k=3), EL_((35, side, 3.2), (4.8, 3.6, 2.8), k=1.5)]
    parts += [EL_((-9, 15.5, 5.5), (8, 4.2, 4.5), k=3), EL_((-3, 16, 3.0), (4.6, 3.2, 2.6), k=1.5),   # folded hind leg
              EL_((-11, -14.5, 5), (7.5, 4, 4), k=3)]
    parts += tail([(-28, 2, 10), (-33, 10, 6), (-30, 18, 4), (-20, 22, 3.2)], 4.8, 2.2)   # curled round the side
    parts += collar(na, nb, 8.8, 7.2, t=0.45)
    return Model(parts)


# ------------------------------------------------------------------ rendering
def _hash3(ix, iy, iz):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF).astype(np.float32) / 65535.0


def vnoise(p):
    """Trilinear value noise, p (N, 3) in cells."""
    f = np.floor(p)
    t = p - f
    t = t * t * (3 - 2 * t)
    i = f.astype(np.int64)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[:, 0] if dx else 1 - t[:, 0]) * (t[:, 1] if dy else 1 - t[:, 1]) * (t[:, 2] if dz else 1 - t[:, 2])
                out = out + w * _hash3(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return out


def render(model, facing):
    fx, fy = FACINGS[facing]
    # world (x, y, z) from dog-local (f, s, u): x = f*fx - s*fy, y = f*fy + s*fx
    def to_local(w):
        return np.array([w[0] * fx + w[1] * fy, -w[0] * fy + w[1] * fx, w[2]], np.float32)

    ce, se_ = math.cos(EL), math.sin(EL)
    r45 = 1 / math.sqrt(2)
    d_w = np.array([-ce * r45, -ce * r45, -se_])                # view direction, into the scene
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
    org = plane - d * 160.0
    t = np.zeros(len(gx), np.float32)
    hit = np.zeros(len(gx), bool)
    alive = np.arange(len(gx))
    for _ in range(90):
        if len(alive) == 0:
            break
        p = org[alive] + t[alive, None] * d
        dist = model.d(p)
        t[alive] += dist * 0.9
        done = dist < 0.04
        hit[alive[done]] = True
        gone = t[alive] > 320
        alive = alive[~(done | gone)]
    idx = np.flatnonzero(hit)
    img = np.zeros((W, Hh, 3), np.float32)
    mask = np.zeros((W, Hh), bool)
    if len(idx) == 0:
        return img, mask
    p = org[idx] + t[idx, None] * d
    _, mat = model.d(p, mats=True)
    e = 0.08
    k = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], np.float32)
    n = sum(k[i][None] * model.d(p + e * k[i])[:, None] for i in range(4))
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    nl = n @ L
    wrap = np.clip((nl + 0.35) / 1.35, 0, 1)
    nh = np.clip(n @ H, 0, 1)
    nv = np.clip(n @ V, 0, 1)
    ao = np.clip(0.55 + 0.45 * (model.d(p + n * 2.5) / 2.5 + model.d(p + n * 6.0) / 6.0) * 0.5, 0.35, 1.0)
    upz = n[:, 2]
    # fur: streaks that run back along the body, finer across it
    fur = vnoise(p * np.array([0.16, 0.9, 0.9], np.float32)) * 0.6 + vnoise(p * np.array([0.5, 2.2, 2.2], np.float32)) * 0.4
    col = np.zeros((len(idx), 3), np.float32)
    m = mat == 0
    key = COAT[None] * (0.55 + 1.45 * wrap[:, None]) * ao[:, None]
    sheen = SHEEN[None] * ((0.55 * nh ** 18 + 0.16 * nh ** 5) * (0.55 + 0.9 * fur))[:, None]
    rim = RIM[None] * (0.8 * (1 - nv) ** 2.4 * np.clip(upz + 0.6, 0, 1.2))[:, None]
    warm = WARM[None] * (0.32 * np.clip(-upz, 0, 1))[:, None]
    coat = key * (0.86 + 0.28 * fur[:, None]) + sheen + rim + warm
    col[m] = coat[m]
    lit = (0.45 + 0.8 * wrap)[:, None]
    spec = (nh ** 30)[:, None]
    for name, base, gloss in (("collar", COLLAR, 90), ("tag", TAG, 200), ("eye", EYE, 230), ("nose", NOSE, 120), ("tongue", TONGUE, 60)):
        mm = mat == MATS[name]
        col[mm] = (base[None] * lit * ao[:, None] + gloss * spec)[mm]
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
    # a soft dark edge just outside the silhouette, like Archie's painted line
    alpha = pygame.surfarray.array_alpha(small).astype(np.float32) / 255
    grow = alpha.copy()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow = np.maximum(grow, np.roll(np.roll(alpha, dx, 0), dy, 1))
    edge = np.clip(grow - alpha, 0, 1)
    out = pygame.Surface((FW, FH), pygame.SRCALPHA)
    line = pygame.Surface((FW, FH), pygame.SRCALPHA)
    line.fill((10, 10, 13, 0))
    la = pygame.surfarray.pixels_alpha(line)
    la[:] = (edge * 170).astype(np.uint8)
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
        pygame.image.save(frame(pose_walk(None), k), os.path.join(OUT, f"myrtle_{k}.png"))
        sheet = pygame.Surface((FW * FRAMES, FH), pygame.SRCALPHA)
        for i in range(FRAMES):
            sheet.blit(frame(pose_walk(i), k), (i * FW, 0))
        pygame.image.save(sheet, os.path.join(OUT, f"myrtle_{k}_walk.png"))
        pygame.image.save(frame(pose_sit(), k), os.path.join(OUT, f"myrtle_{k}_sit.png"))
        pygame.image.save(frame(pose_lie(), k), os.path.join(OUT, f"myrtle_{k}_lie.png"))
        print("myrtle", k, flush=True)
    with open(os.path.join(OUT, "myrtle.json"), "w") as f:
        json.dump({"size": [FW, FH], "anchor": [AX, AY], "frames": FRAMES, "cycle_tiles": CYCLE_TILES,
                   "facings": list(FACINGS)}, f, indent=1)


if __name__ == "__main__":
    main()
