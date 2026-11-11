#!/usr/bin/env python3
"""Build Myrtle's sprites (a medium black Labrador) procedurally.

The dog is a small 3D model of ellipsoids and capsules in centimetres
(forward, side, up). Each pose is splatted with a z-buffer through the
house's 2:1 projection, shaded with the rooms' light (top and +y faces
brightest), then downsampled, so every facing and frame is the same dog.

Output (assets/myrtle/):
    myrtle_<k>.png            standing, k in se, sw, nw, ne (as Archie's facings)
    myrtle_<k>_walk.png       8-frame walk cycle, frames side by side
    myrtle_<k>_sit.png        sitting, looking up
    myrtle_<k>_lie.png        lying down (on her bed)
    myrtle.json               frame size, ground anchor, walk cycle length
    python3 tools/make_myrtle.py
"""
import json
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import numpy as np  # noqa: E402
import pygame  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "myrtle")
SS = 3                                   # supersampling
FW, FH = 180, 150                        # frame size (px)
AX, AY = 90, 118                         # ground point under the dog's middle
CM_TILE = 60.0                           # 1 tile = 60 cm on the floor
PX_CM = 1.07                             # vertical px per cm (Archie scale: Lab ~ hip height on a kid)
FRAMES = 8
CYCLE_TILES = 1.10                       # distance walked per walk cycle
FACINGS = {"se": (1, 0), "sw": (0, 1), "nw": (-1, 0), "ne": (0, -1)}

COAT = np.array([30, 30, 35], float)
SHEEN = np.array([118, 134, 158], float)  # blue-grey highlight
COLLAR = np.array([196, 40, 44], float)
EYE = np.array([104, 62, 28], float)
NOSE = np.array([22, 20, 22], float)
TONGUE = np.array([206, 104, 116], float)
LIGHT = np.array([0.35, 0.60, 1.0])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


# ------------------------------------------------------------------ model parts
def ell(c, r, col="coat", pitch=0.0, yaw=0.0, roll=0.0):
    return dict(kind="ell", c=np.array(c, float), r=np.array(r, float), col=col, pitch=pitch, yaw=yaw, roll=roll)


def cap(a, b, ra, rb, col="coat", n=None):
    """A smooth tapering capsule: a cone frustum with a sphere on each end."""
    a, b = np.array(a, float), np.array(b, float)
    return [dict(kind="cyl", a=a, b=b, ra=ra, rb=rb, col=col),
            ell(a, (ra, ra, ra), col), ell(b, (rb, rb, rb), col)]


def chain(pts, ra, rb, col="coat"):
    out = []
    for i in range(len(pts) - 1):
        t0, t1 = i / (len(pts) - 1), (i + 1) / (len(pts) - 1)
        out += cap(pts[i], pts[i + 1], ra + (rb - ra) * t0, ra + (rb - ra) * t1, col)
    return out


def head(c, look_up=0.0, tongue=False):
    """Skull, muzzle, nose, eyes and drop ears around skull centre c (forward is +f)."""
    cf, cs, cu = c
    lu = look_up
    parts = [ell((cf, 0, cu), (10.5, 8.2, 8.8), pitch=-lu),
             ell((cf + 9.5, 0, cu - 3.5 + lu * 8), (8.5, 5.4, 5.4), pitch=-lu),
             ell((cf + 17.5, 0, cu - 2.8 + lu * 14), (2.3, 2.5, 2.0), col="nose"),
             ell((cf + 6.5, 4.3, cu + 2.0 + lu * 4), (1.5, 1.4, 1.5), col="eye"),
             ell((cf + 6.5, -4.3, cu + 2.0 + lu * 4), (1.5, 1.4, 1.5), col="eye"),
             ell((cf - 1.5, 8.0, cu - 3.5), (5.4, 1.8, 8.0), roll=0.25),
             ell((cf - 1.5, -8.0, cu - 3.5), (5.4, 1.8, 8.0), roll=-0.25)]
    if tongue:
        parts.append(ell((cf + 12.5, 0, cu - 8.0 + lu * 8), (3.0, 2.4, 1.2), col="tongue"))
    return parts


def leg(top, knee, paw, r0=5.6, r1=3.9):
    return chain([top, knee, paw], r0, r1) + [ell((paw[0] + 1.8, paw[1], 2.6), (4.6, 3.4, 2.6))]


def pose_walk(p):
    """Standing / walking. p = gait phase in radians (None = standing still)."""
    s = 0.0 if p is None else 1.0
    ph = 0.0 if p is None else p
    bob = 1.2 * s * abs(math.sin(ph))
    parts = [ell((0, 0, 45 + bob), (33, 12.8, 13.5)),
             ell((17, 0, 43 + bob), (15, 12.5, 15.5)),
             ell((-21, 0, 46 + bob), (14, 12.2, 13)),
             ell((10, 0, 33 + bob), (14, 9, 6))]                     # belly line
    parts += cap((25, 0, 49 + bob), (36, 0, 63 + bob), 8.6, 7.2)
    parts += cap((29.5, 0, 55.5 + bob), (31.5, 0, 57.5 + bob), 8.9, 8.8, col="collar")
    parts += head((43, 0, 68 + bob))
    for side, off in ((7.0, 0.0), (-7.0, math.pi)):
        a = 24 * s * math.sin(ph + off)                              # front leg swing (deg)
        h = 24 * s * math.sin(ph + off + math.pi)                    # hind leg, diagonal pair
        lift_f = 5 * s * max(0.0, math.cos(ph + off))
        lift_h = 5 * s * max(0.0, math.cos(ph + off + math.pi))
        ra, rh = math.radians(a), math.radians(h)
        top = (20, side, 40 + bob)
        paw = (20 + 38 * math.sin(ra), side, 2 + lift_f)
        knee = ((top[0] + paw[0]) / 2 + 1.0, side, 20 + lift_f * .6)
        parts += leg(top, knee, paw)
        hip = (-21, side, 42 + bob)
        hpaw = (-23 + 38 * math.sin(rh), side, 2 + lift_h)
        hock = (hpaw[0] - 6, side, 15 + lift_h)
        stifle = (-15 + 10 * math.sin(rh), side, 28)
        parts += chain([hip, stifle, hock, hpaw], 7.2, 3.9) + [ell((hpaw[0] + 1.8, side, 2.6), (4.6, 3.4, 2.6))]
    wag = 0.35 * math.sin(2 * ph) if p is not None else 0.15
    tail = [(-33, 0, 47 + bob), (-41, 9 * math.sin(wag) * .5, 43 + bob), (-48, 14 * math.sin(wag), 36 + bob)]
    parts += chain(tail, 5.0, 2.6)
    return parts


def pose_sit():
    parts = [ell((-11, 0, 17), (16, 14, 15)),                       # haunches
             ell((1, 0, 32), (24, 13.2, 13.8), pitch=0.95),         # torso tilted up, one smooth back
             ell((11, 0, 45), (12.5, 12.8, 15)),                    # chest
             ell((-6, 9.5, 12), (12, 4.5, 10)), ell((-6, -9.5, 12), (12, 4.5, 10))]   # thighs
    parts += cap((15, 0, 54), (21, 0, 69), 8.6, 7.2)
    parts += cap((17.5, 0, 59.5), (18.5, 0, 61.5), 8.9, 8.8, col="collar")
    parts += head((27, 0, 76), look_up=0.35, tongue=True)
    for side in (6.5, -6.5):
        parts += leg((16, side, 40), (17, side, 20), (18, side, 2))
        parts += [ell((4, side * 1.45, 2.8), (6.5, 3.6, 2.8))]      # hind paws forward
    parts += chain([(-24, 0, 6), (-34, 7, 4), (-42, 13, 3.5)], 4.8, 2.6)
    return parts


def pose_lie():
    parts = [ell((-2, 0, 15), (33, 14.5, 12.5)),
             ell((15, 0, 16), (15, 13.5, 14)),
             ell((-20, 4, 14), (14, 13, 12))]
    parts += cap((26, 0, 22), (34, 0, 33), 8.4, 7.2)
    parts += cap((28.5, 0, 26.5), (30, 0, 28.5), 8.7, 8.6, col="collar")
    parts += head((40, 0, 35), look_up=0.05)
    for side in (6.0, -6.0):
        parts += chain([(24, side, 9), (36, side, 5), (48, side, 4)], 4.6, 3.6)
        parts += [ell((50, side, 3.4), (5.0, 3.6, 3.0))]
    parts += [ell((-10, 15.5, 5), (8, 4, 4)), ell((-8, -15.0, 5), (8, 4, 4))]   # folded hind legs
    parts += chain([(-32, 0, 10), (-42, 7, 5.5), (-49, 15, 4.5)], 4.8, 2.6)
    return parts


# ------------------------------------------------------------------ rendering
def _rot(pitch, yaw, roll):
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cr, sr = math.cos(roll), math.sin(roll)
    # local axes: f (forward), s (side), u (up). pitch tilts f towards u.
    Rp = np.array([[cp, 0, -sp], [0, 1, 0], [sp, 0, cp]])
    Ry = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    Rr = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    return Ry @ Rp @ Rr


def render(parts, facing):
    fx, fy = FACINGS[facing]
    fwd = np.array([fx, fy], float)
    side = np.array([-fy, fx], float)          # dog's left
    W, H = FW * SS, FH * SS
    img = np.zeros((W, H, 3), float)
    zb = np.full((W, H), -1e9)
    tile_px = math.hypot(56, 28)               # one tile edge on screen
    h_px = tile_px / CM_TILE                   # horizontal px per cm along a tile edge
    for prt in parts:
        if prt["kind"] == "cyl":
            a, b, ra, rb = prt["a"], prt["b"], prt["ra"], prt["rb"]
            ax = b - a
            L = np.linalg.norm(ax)
            ax = ax / L
            tmp = np.array([0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.array([1.0, 0, 0])
            e1 = np.cross(ax, tmp)
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(ax, e1)
            nt = int(max(10, L * 3))
            na = int(max(24, max(ra, rb) * 8))
            T, A = np.meshgrid(np.linspace(0, 1, nt), np.linspace(0, 2 * math.pi, na, endpoint=False), indexing="ij")
            T, A = T.ravel(), A.ravel()
            rr = ra + (rb - ra) * T
            radial = np.cos(A)[:, None] * e1 + np.sin(A)[:, None] * e2
            pl = a + T[:, None] * (b - a) + rr[:, None] * radial
            slope = (ra - rb) / L
            nn = radial + slope * ax
            nn /= np.linalg.norm(nn, axis=1, keepdims=True)
        else:
            r = prt["r"]
            n_t = int(max(18, (r.max() * 2.6)))
            th = np.linspace(0, math.pi, n_t)
            ph = np.linspace(0, 2 * math.pi, n_t * 2, endpoint=False)
            T, Pp = np.meshgrid(th, ph, indexing="ij")
            nl = np.stack([np.sin(T) * np.cos(Pp), np.sin(T) * np.sin(Pp), np.cos(T)], -1).reshape(-1, 3)
            R = _rot(prt["pitch"], prt["yaw"], prt["roll"])
            pl = (nl * r) @ R.T + prt["c"]                     # local (f, s, u) cm
            nn = (nl / r) @ R.T
            nn /= np.linalg.norm(nn, axis=1, keepdims=True)
        # local -> world: horizontal in tiles, up in px
        wx = (pl[:, 0] * fwd[0] + pl[:, 1] * side[0]) / CM_TILE
        wy = (pl[:, 0] * fwd[1] + pl[:, 1] * side[1]) / CM_TILE
        wz = pl[:, 2] * PX_CM
        nwx = nn[:, 0] * fwd[0] + nn[:, 1] * side[0]
        nwy = nn[:, 0] * fwd[1] + nn[:, 1] * side[1]
        nwz = nn[:, 2]
        sx = (AX + (wx - wy) * 56) * SS
        sy = (AY + (wx + wy) * 28 - wz) * SS
        depth = (wx + wy) * tile_px * 0.612 + wz * 0.5          # towards the camera
        # facing the camera? (view dir from the scene to the eye)
        vdot = nwx * 0.612 + nwy * 0.612 + nwz * 0.5
        keep = vdot > -0.15
        lam = np.clip(nwx * LIGHT[0] + nwy * LIGHT[1] + nwz * LIGHT[2], 0, 1)
        hv = LIGHT + np.array([0.612, 0.612, 0.5])
        hv /= np.linalg.norm(hv)
        spec = np.clip(nwx * hv[0] + nwy * hv[1] + nwz * hv[2], 0, 1) ** 10
        rim = np.clip(1 - np.abs(vdot), 0, 1) ** 3 * np.clip(nwz + 0.4, 0, 1)
        col = prt["col"]
        if col == "coat":
            c = COAT[None] * (0.55 + 0.75 * lam[:, None]) + SHEEN[None] * (0.42 * spec + 0.22 * rim)[:, None]
        elif col == "collar":
            c = COLLAR[None] * (0.55 + 0.6 * lam[:, None]) + 90 * spec[:, None]
        elif col == "eye":
            c = EYE[None] * (0.7 + 0.5 * lam[:, None]) + 160 * (spec ** 2)[:, None]
        elif col == "nose":
            c = NOSE[None] * (0.8 + 0.4 * lam[:, None]) + SHEEN[None] * 0.6 * spec[:, None]
        else:
            c = TONGUE[None] * (0.6 + 0.5 * lam[:, None])
        sx, sy, depth, c = sx[keep], sy[keep], depth[keep], c[keep]
        order = np.argsort(depth)
        sx, sy, depth, c = sx[order], sy[order], depth[order], c[order]
        rad = 2
        for ox in range(-rad, rad + 1):
            for oy in range(-rad, rad + 1):
                if ox * ox + oy * oy > rad * rad + 1:
                    continue
                ix = np.clip((sx + ox).astype(int), 0, W - 1)
                iy = np.clip((sy + oy).astype(int), 0, H - 1)
                d = depth - 0.02 * (abs(ox) + abs(oy))
                win = d > zb[ix, iy]
                # nearest last, so it wins duplicate writes
                ix, iy, d2, c2 = ix[win], iy[win], d[win], c[win]
                zb[ix, iy] = d2
                img[ix, iy] = c2
    mask = zb > -1e8
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
    # a soft cool rim round the silhouette so a black dog reads on dark boards
    alpha = pygame.surfarray.array_alpha(small).astype(float) / 255
    grow = alpha.copy()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow = np.maximum(grow, np.roll(np.roll(alpha, dx, 0), dy, 1))
    edge = np.clip(grow - alpha, 0, 1)
    out = pygame.Surface((FW, FH), pygame.SRCALPHA)
    rim = pygame.Surface((FW, FH), pygame.SRCALPHA)
    rim.fill((84, 92, 108, 0))
    ra = pygame.surfarray.pixels_alpha(rim)
    ra[:] = (edge * 150).astype(np.uint8)
    del ra
    out.blit(rim, (0, 0))
    out.blit(small, (0, 0))
    return out


def frame(parts, k):
    return to_surface(*render(parts, k))


def main():
    pygame.init()
    os.makedirs(OUT, exist_ok=True)
    for k in FACINGS:
        pygame.image.save(frame(pose_walk(None), k), os.path.join(OUT, f"myrtle_{k}.png"))
        sheet = pygame.Surface((FW * FRAMES, FH), pygame.SRCALPHA)
        for i in range(FRAMES):
            sheet.blit(frame(pose_walk(2 * math.pi * i / FRAMES), k), (i * FW, 0))
        pygame.image.save(sheet, os.path.join(OUT, f"myrtle_{k}_walk.png"))
        pygame.image.save(frame(pose_sit(), k), os.path.join(OUT, f"myrtle_{k}_sit.png"))
        pygame.image.save(frame(pose_lie(), k), os.path.join(OUT, f"myrtle_{k}_lie.png"))
        print("myrtle", k)
    with open(os.path.join(OUT, "myrtle.json"), "w") as f:
        json.dump({"size": [FW, FH], "anchor": [AX, AY], "frames": FRAMES, "cycle_tiles": CYCLE_TILES,
                   "facings": list(FACINGS)}, f, indent=1)


if __name__ == "__main__":
    main()
