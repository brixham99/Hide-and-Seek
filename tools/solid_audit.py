#!/usr/bin/env python3
"""Look for furniture we can see 'inside' in either camera.

Every box() and occlude() volume is a closed solid, so in the finished
picture nothing behind its camera-facing surface should show. This builds
each view with an audit hook in house_common: it rasterises the
camera-facing faces of every solid (skipping faces that go on the ghost
near-wall layer), records the depth and call site of every face actually
painted on the room (painter's order in the usual view, z-buffer in the
opposite one), and flags pixels where what you see lies behind a solid's
front, i.e. a missing face, an open side, a back face, a seam, a detail
drawn inside the solid instead of on its face, or a sort-order slip. Raw pygame.draw strokes (outlines, knobs) count as
covering, as their depth isn't known.

    python tools/solid_audit.py              # every view, both cameras
    python tools/solid_audit.py hall hall_r  # some views

Writes shots/audit/<view>.png (flagged pixels magenta) and prints the worst
solid / visible-face pairs per view. Rebuilds cache/ as a side effect.
"""
import os
import sys
import traceback

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "rooms"))

import numpy as np  # noqa: E402
import pygame  # noqa: E402
import build_rooms  # noqa: E402
import house_common as hc  # noqa: E402

EPS = 0.08            # tiles of x+y depth a visible face may sit behind a solid's front
MIN_PX = 160          # flagged pixels (2x canvas) before a pair is reported
SKIP = ("house_common.py", "iso_paint.py", "solid_audit.py", "build_rooms.py")


def site():
    out = []
    for fr in reversed(traceback.extract_stack()[:-2]):
        fn = os.path.basename(fr.filename)
        if fn in SKIP or not fr.filename.startswith(HERE):
            continue
        out.append(f"{fn[:-3]}:{fr.lineno} {fr.name}")
        if len(out) == 2:
            break
    return " < ".join(out) or "?"


class Audit:
    def __init__(self, size):
        W, H = size
        self.pinf = {}
        self.vis = np.full((W, H), -np.inf, np.float32)
        self.vid = np.full((W, H), -1, np.int32)
        self.unk = np.zeros((W, H), bool)
        self.front = np.full((W, H), -np.inf, np.float32)
        self.fid = np.full((W, H), -1, np.int32)
        self.sites = []
        self.decals = {}          # site -> (px, faces) hidden just behind a nearer face
        self._site_ix = {}
        self.scratch = pygame.Surface(size)

    def sid(self):
        s = site()
        if s not in self._site_ix:
            self._site_ix[s] = len(self.sites)
            self.sites.append(s)
        return self._site_ix[s]

    def _raster(self, pts):
        """Yield (x0, y0, mask, depth) per triangle of a convex screen polygon."""
        ds = [self.pinf.get(p) for p in pts]
        if any(d is None for d in ds) or len(pts) < 3:
            return
        W, H = self.vis.shape
        for i in range(1, len(pts) - 1):
            a, b, c = pts[0], pts[i], pts[i + 1]
            da, db, dc = ds[0], ds[i], ds[i + 1]
            xs, ys = (a[0], b[0], c[0]), (a[1], b[1], c[1])
            x0, y0 = max(0, int(np.floor(min(xs)))), max(0, int(np.floor(min(ys))))
            x1, y1 = min(W, int(np.ceil(max(xs))) + 1), min(H, int(np.ceil(max(ys))) + 1)
            if x1 - x0 < 1 or y1 - y0 < 1:
                continue
            area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if abs(area) < 1:
                continue
            gx = np.arange(x0, x1, dtype=np.float32)[:, None] + 0.5
            gy = np.arange(y0, y1, dtype=np.float32)[None, :] + 0.5
            e = lambda p, q: (q[0] - p[0]) * (gy - p[1]) - (q[1] - p[1]) * (gx - p[0])
            w0, w1, w2 = e(b, c), e(c, a), e(a, b)
            if area < 0:
                w0, w1, w2, area = -w0, -w1, -w2, -area
            m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if m.any():
                yield x0, y0, m, (w0 * da + w1 * db + w2 * dc) / area

    def drawn(self, pts, near):
        if near or hc.screen is not hc._room_screen:
            return
        sid = self.sid()
        inside = behind = 0
        for x0, y0, m, d in self._raster(pts):
            w, h = m.shape
            if hc._zbuf is not None:
                z = hc._zbuf[x0:x0 + w, y0:y0 + h]
                gap = z - d
                inside += int(m.sum())
                behind += int((m & (gap > 1e-3) & (gap < 0.08)).sum())
            vis = self.vis[x0:x0 + w, y0:y0 + h]
            if hc._zbuf is not None:          # both cameras are z-buffered now
                m = m & (d >= vis - 1e-3)
            vis[m] = d[m]
            self.vid[x0:x0 + w, y0:y0 + h][m] = sid
            self.unk[x0:x0 + w, y0:y0 + h][m] = False
        if inside >= 40 and behind > 0.5 * inside:
            n, c = self.decals.get(sid, (0, 0))
            self.decals[sid] = (n + behind, c + 1)

    def zsync(self, x, y, w, h):
        """A drum body went straight into the z-buffer: take its depth."""
        if hc.screen is not hc._room_screen:
            return
        W, H = self.vis.shape
        x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        z = hc._zbuf[x0:x1, y0:y1]
        m = z > self.vis[x0:x1, y0:y1] + 1e-3
        self.vis[x0:x1, y0:y1][m] = z[m]
        self.vid[x0:x1, y0:y1][m] = self.sid()
        self.unk[x0:x1, y0:y1][m] = False

    def raw(self, surf, rect):
        if surf is not hc._room_screen or rect is None:
            return
        r = pygame.Rect(rect).clip(surf.get_rect())
        if r.w and r.h:
            self.unk[r.x:r.right, r.y:r.bottom] |= self._mask(r)

    def solid(self, x0, y0, x1, y1, z0, z1, faces, occ=False):
        if hc.screen is not hc._room_screen:
            return
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        z0, z1 = min(z0, z1), max(z0, z1)
        if x1 - x0 < 0.06 or y1 - y0 < 0.06 or z1 - z0 < 4:
            return                    # thin trims, rails and boards: not worth a solid
        yf, xf = (y0, x0) if hc.FLIP else (y1, x1)
        P = hc.P
        quads = [[P(x0, yf, z0), P(x1, yf, z0), P(x1, yf, z1), P(x0, yf, z1)],
                 [P(xf, y0, z0), P(xf, y1, z0), P(xf, y1, z1), P(xf, y0, z1)],
                 [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]]
        sid = self.sid() if not occ else self.sid()
        for q in quads:
            if hc.FLIP and not occ and hc._near_plane(q):
                continue              # this face is the ghost near wall's business
            for qx0, qy0, m, d in self._raster(q):
                w, h = m.shape
                fr = self.front[qx0:qx0 + w, qy0:qy0 + h]
                m = m & (d > fr)
                fr[m] = d[m]
                self.fid[qx0:qx0 + w, qy0:qy0 + h][m] = sid

    def _mask(self, r):
        a = pygame.surfarray.pixels_red(self.scratch)
        m = a[r.x:r.right, r.y:r.bottom] > 0
        a[r.x:r.right, r.y:r.bottom] = 0
        del a
        return m


AUD = None
_orig = {}


def _wrap(name):
    fn = getattr(pygame.draw, name)
    _orig[name] = fn

    def w(surf, col, *a, **k):
        r = fn(surf, col, *a, **k)
        if AUD is not None and surf is hc._room_screen:
            fn(AUD.scratch, (255, 255, 255), *a, **k)
            AUD.raw(surf, r)
        return r
    setattr(pygame.draw, name, w)


for _n in ("polygon", "rect", "circle", "line", "lines", "ellipse", "aaline", "aalines", "arc"):
    _wrap(_n)


def audit(view, out_dir):
    global AUD
    flip = view.endswith("_r")
    base = view[:-2] if flip else view
    real_init = hc.init_room

    def init_room(*a, **k):
        global AUD
        s = real_init(*a, **k)
        AUD = Audit(s.get_size())
        hc._AUDIT = AUD
        return s
    hc.init_room = init_room
    try:
        build_rooms.build(base, flip=flip)
    finally:
        hc.init_room = real_init
        hc._AUDIT = None
    a = AUD
    AUD = None
    with np.errstate(invalid="ignore"):
        bad = np.isfinite(a.front) & ~a.unk & (a.front - a.vis > EPS)
    # report pairs
    pairs = {}
    if bad.any():
        xs, ys = np.nonzero(bad)
        keys = a.fid[xs, ys].astype(np.int64) * 100000 + a.vid[xs, ys] + 1
        for k in np.unique(keys):
            sel = keys == k
            n = int(sel.sum())
            if n < MIN_PX:
                continue
            fx, vx = divmod(int(k), 100000)
            vx -= 1
            px, py = xs[sel], ys[sel]
            pairs[(fx, vx)] = (n, (int(px.min()) // 2, int(py.min()) // 2, int(px.max()) // 2, int(py.max()) // 2))
    img = pygame.transform.smoothscale(hc.screen, (hc.WIN_W, hc.WIN_H))
    arr = pygame.surfarray.pixels3d(img)
    small = bad[::2, ::2] | bad[1::2, ::2] | bad[::2, 1::2] | bad[1::2, 1::2]
    arr[small] = (255, 0, 255)
    del arr
    os.makedirs(out_dir, exist_ok=True)
    pygame.image.save(img, os.path.join(out_dir, f"{view}.png"))
    total = int(bad.sum()) // 4
    print(f"== {view}: {total} px flagged")
    for (fx, vx), (n, bb) in sorted(pairs.items(), key=lambda kv: -kv[1][0]):
        vs = a.sites[vx] if vx >= 0 else "(nothing drawn / blit)"
        print(f"   {n // 4:6d} px  bbox {bb}\n        solid: {a.sites[fx]}\n        seen : {vs}")
    for sid, (n, c) in sorted(a.decals.items(), key=lambda kv: -kv[1][0]):
        if n // 4 >= 30:
            print(f"   decal {n // 4:6d} px in {c} faces hidden just behind a face: {a.sites[sid]}")
    return total


def main():
    views = sys.argv[1:] or [v + s for v in build_rooms.VIEWS for s in ("", "_r")]
    out = os.path.join(HERE, "shots", "audit")
    tot = 0
    for v in views:
        tot += audit(v, out)
    print("TOTAL flagged px:", tot)


if __name__ == "__main__":
    main()
