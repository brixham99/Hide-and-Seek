"""Self-made painted textures for Hide and Seek.

Floors, rugs and tabletops are drawn here (numpy / pygame canvas) and mapped
into the isometric floor plane by `stamp`. Nothing in this module is copied
from a third-party image; the patterns are original, coloured after the
house photographs.
"""
import math

import numpy as np
import pygame

_CACHE = {}


def _key(name, *parts):
    return (name,) + tuple(parts)


def _rng(seed):
    return np.random.RandomState(seed & 0xFFFFFFFF)


def timber(w_tiles, h_tiles, seed, c1, c2, along="x", plank=0.28, ppm=64):
    """Honey or dark floorboards. `along` is the direction a board runs."""
    key = _key("timber", round(w_tiles, 3), round(h_tiles, 3), seed, c1, c2, along, round(plank, 3))
    if key in _CACHE:
        return _CACHE[key]
    tw, th = max(8, int(w_tiles * ppm)), max(8, int(h_tiles * ppm))
    rng = _rng(seed)
    img = np.empty((th, tw, 3), np.float32)
    c1 = np.array(c1[:3], np.float32)
    c2 = np.array(c2[:3], np.float32)
    # boards are strips perpendicular to `along`
    span = th if along == "x" else tw
    other = tw if along == "x" else th
    plank_px = max(6, int(plank * ppm))
    y = 0
    bi = 0
    while y < span:
        bh = int(plank_px * rng.uniform(0.82, 1.18))
        y1 = min(span, y + bh)
        mix = rng.uniform(0.25, 0.85)
        base = (c1 * mix + c2 * (1 - mix)) * rng.uniform(0.9, 1.08)
        sl = slice(y, y1)
        if along == "x":
            img[sl, :, :] = base
            # end joints, staggered
            x = int(rng.uniform(0, other * 0.3))
            while x < other:
                x += int(rng.uniform(1.6, 3.4) * ppm)
                if 1 < x < other - 1:
                    img[sl, x - 1:x + 1, :] *= 0.72
            # long grain
            yy = np.linspace(0, 1, y1 - y, dtype=np.float32)[:, None]
            xx = np.arange(other, dtype=np.float32)[None, :]
            wave = np.sin(xx / rng.uniform(9, 18) + bi) * 0.035
            wave = wave + np.sin(xx / rng.uniform(3, 6) + yy * 2) * 0.02
            img[sl, :, :] *= (1 + wave)[..., None]
            # a knot, sometimes
            if rng.random() < 0.55 and y1 - y > 8:
                kx = int(rng.randint(4, max(5, other - 4)))
                ky = (y + y1) // 2
                rad = int(rng.uniform(2.2, 4.5))
                yy2, xx2 = np.ogrid[y:y1, 0:other]
                d = ((xx2 - kx) / (rad * 1.4)) ** 2 + ((yy2 - ky) / rad) ** 2
                knot = np.clip(1 - d, 0, 1)[..., None]
                img[sl, :, :] = img[sl, :, :] * (1 - 0.45 * knot) + np.array((48, 30, 18)) * (0.45 * knot)
        else:
            img[:, sl, :] = base
            yy = int(rng.uniform(0, other * 0.3))
            while yy < other:
                yy += int(rng.uniform(1.6, 3.4) * ppm)
                if 1 < yy < other - 1:
                    img[yy - 1:yy + 1, sl, :] *= 0.72
            ys = np.arange(other, dtype=np.float32)[:, None]
            wave = np.sin(ys / rng.uniform(9, 18) + bi) * 0.035
            img[:, sl, :] *= (1 + wave)[..., None]
        # seam shadow at the start of the board
        if along == "x" and y > 0:
            img[y:y + 1, :, :] *= 0.62
        elif along != "x" and y > 0:
            img[:, y:y + 1, :] *= 0.62
        y = y1
        bi += 1
    img += _rng(seed + 3).randn(th, tw, 1) * 2.2
    out = np.clip(img, 0, 255).astype(np.uint8)
    _CACHE[key] = out
    return out


def slate(w_tiles, h_tiles, seed, palette, ppm=56):
    """Irregular riven slate: ochre, rust and grey-green, pale grout."""
    key = _key("slate", round(w_tiles, 3), round(h_tiles, 3), seed, tuple(tuple(c) for c in palette))
    if key in _CACHE:
        return _CACHE[key]
    tw, th = max(8, int(w_tiles * ppm)), max(8, int(h_tiles * ppm))
    rng = _rng(seed)
    grout = np.array((62, 56, 46), np.float32)
    img = np.empty((th, tw, 3), np.float32)
    img[:] = grout
    pal = [np.array(c[:3], np.float32) for c in palette]
    y = 0
    row = 0
    while y < th - 1:
        bh = int(rng.choice((0.58, 0.7, 0.82)) * ppm)
        y1 = min(th - 1, y + bh)
        x = -int(rng.uniform(0, ppm)) if row % 2 else 0
        while x < tw - 1:
            bw = int(rng.choice((0.72, 0.9, 1.15, 1.35)) * ppm)
            x1 = min(tw - 1, x + bw)
            if x1 - max(0, x) > 3 and y1 - y > 3:
                col = pal[int(rng.randint(0, len(pal)))] * rng.uniform(0.86, 1.08)
                # mix a neighbour colour so tiles aren't flat
                col = col * 0.82 + pal[int(rng.randint(0, len(pal)))] * 0.18
                xa, xb = max(0, x + 1), x1
                ya, yb = y + 1, y1
                tile = np.empty((yb - ya, xb - xa, 3), np.float32)
                tile[:] = col
                yy = np.linspace(0, 1, yb - ya, dtype=np.float32)[:, None, None]
                xx = np.linspace(0, 1, xb - xa, dtype=np.float32)[None, :, None]
                tile *= 0.93 + 0.1 * xx + 0.05 * (1 - yy)
                n = rng.randn(yb - ya, xb - xa).astype(np.float32)
                tile += n[..., None] * 7
                # a darker rift
                if rng.random() < 0.7:
                    ry = int(rng.randint(0, max(1, yb - ya)))
                    tile[ry:ry + 1, :, :] *= 0.82
                img[ya:yb, xa:xb] = tile
            x += bw
        y += bh
        row += 1
    _CACHE[key] = np.clip(img, 0, 255).astype(np.uint8)
    return _CACHE[key]


def flagstones(w_tiles, h_tiles, seed, palette, row=0.85, ppm=52):
    """Worn flags: large irregular stones, scuffed, with dark recessed joints."""
    key = _key("flags", round(w_tiles, 3), round(h_tiles, 3), seed, tuple(tuple(c) for c in palette), round(row, 2))
    if key in _CACHE:
        return _CACHE[key]
    tw, th = max(8, int(w_tiles * ppm)), max(8, int(h_tiles * ppm))
    rng = _rng(seed + 11)
    img = np.empty((th, tw, 3), np.float32)
    img[:] = np.array((78, 72, 64), np.float32)
    pal = [np.array(c[:3], np.float32) for c in palette]
    y = 0
    r = 0
    while y < th - 2:
        bh = int(row * ppm * rng.uniform(0.75, 1.3))
        y1 = min(th - 1, y + max(8, bh))
        x = -int((row * ppm) / 2) if r % 2 else 0
        while x < tw - 2:
            bw = int(rng.uniform(0.85, 1.55) * ppm)
            x1 = min(tw - 1, x + bw)
            xa, xb = max(0, x + 2), max(0, x1 - 1)
            ya, yb = min(th - 1, y + 2), y1
            if xb - xa > 4 and yb - ya > 4:
                col = pal[int(rng.randint(0, len(pal)))] * rng.uniform(0.9, 1.1)
                tile = np.empty((yb - ya, xb - xa, 3), np.float32)
                tile[:] = col
                n = rng.randn(yb - ya, xb - xa).astype(np.float32)
                # low-frequency wear
                k = max(2, (yb - ya) // 4)
                coarse = rng.randn(k, max(2, (xb - xa) // 4)).astype(np.float32)
                cy = (np.linspace(0, coarse.shape[0] - 1, yb - ya)).astype(np.int32)
                cx = (np.linspace(0, coarse.shape[1] - 1, xb - xa)).astype(np.int32)
                tile += (n * 4 + coarse[cy][:, cx] * 10)[..., None]
                # lighter worn centre
                yy = np.linspace(-1, 1, yb - ya)[:, None]
                xx = np.linspace(-1, 1, xb - xa)[None, :]
                tile += (np.clip(1 - xx * xx - yy * yy, 0, 1) * 12)[..., None]
                img[ya:yb, xa:xb] = tile
            x += bw
        y = y1
        r += 1
    _CACHE[key] = np.clip(img, 0, 255).astype(np.uint8)
    return _CACHE[key]


def quarry(w_tiles, h_tiles, seed, colour, size=0.5, ppm=56):
    """Terracotta quarry tiles and pale grout, a little scuffed."""
    key = _key("quarry", round(w_tiles, 3), round(h_tiles, 3), seed, tuple(colour[:3]), round(size, 3))
    if key in _CACHE:
        return _CACHE[key]
    tw, th = max(8, int(w_tiles * ppm)), max(8, int(h_tiles * ppm))
    rng = _rng(seed + 5)
    img = np.empty((th, tw, 3), np.float32)
    grout = np.array(colour[:3], np.float32) * 0.55 + np.array((40, 32, 28), np.float32)
    img[:] = grout
    step = max(6, int(size * ppm))
    base = np.array(colour[:3], np.float32)
    for y in range(0, th, step):
        for x in range(0, tw, step):
            ya, yb = y + 1, min(th, y + step - 1)
            xa, xb = x + 1, min(tw, x + step - 1)
            if yb <= ya or xb <= xa:
                continue
            col = base * rng.uniform(0.86, 1.1)
            tile = np.empty((yb - ya, xb - xa, 3), np.float32)
            tile[:] = col
            tile += rng.randn(yb - ya, xb - xa, 1).astype(np.float32) * 5
            if rng.random() < 0.4:
                sy = int(rng.randint(0, yb - ya))
                tile[sy:sy + 1, :, :] *= 0.9
            img[ya:yb, xa:xb] = tile
    _CACHE[key] = np.clip(img, 0, 255).astype(np.uint8)
    return _CACHE[key]


def marble(px=160, seed=2):
    """Pale marble disc texture (coffee table), soft grey veins."""
    key = _key("marble", px, seed)
    if key in _CACHE:
        return _CACHE[key]
    rng = _rng(seed)
    yy, xx = np.mgrid[0:px, 0:px].astype(np.float32)
    img = np.ones((px, px, 3), np.float32)
    img[..., 0] = 228
    img[..., 1] = 226
    img[..., 2] = 220
    for i in range(7):
        ang = rng.uniform(0, math.pi)
        phase = rng.uniform(0, px)
        width = rng.uniform(1.2, 3.4)
        bend = rng.uniform(2.5, 7)
        t = xx * math.cos(ang) + yy * math.sin(ang)
        t = t + np.sin(yy / bend + i) * 6
        vein = np.exp(-((t - phase) ** 2) / (2 * width * width))
        tone = 150 + rng.uniform(-30, 20)
        img -= vein[..., None] * np.array((tone * 0.15, tone * 0.16, tone * 0.2))
    img += rng.randn(px, px, 1).astype(np.float32) * 2.5
    _CACHE[key] = np.clip(img, 0, 255).astype(np.uint8)
    return _CACHE[key]


def pine_top(w_tiles, h_tiles, seed=4, c1=(214, 164, 104), c2=(168, 116, 64), ppm=70):
    """Chunky pine table top: wide boards, knots, a warm highlight."""
    return timber(w_tiles, h_tiles, seed, c1, c2, along="x", plank=max(0.22, w_tiles / 5), ppm=ppm)


def _surf(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    return s


def rug(w_tiles, h_tiles, style="persian", seed=1, ppm=88):
    """A hand-drawn rug. Styles: hall (red runner), sitting (faded pale), drawing (red field)."""
    key = _key("rug", round(w_tiles, 3), round(h_tiles, 3), style, seed, ppm)
    if key in _CACHE:
        return _CACHE[key]
    tw, th = max(24, int(w_tiles * ppm)), max(24, int(h_tiles * ppm))
    if style == "sitting":
        field, edge, band, accent, ink = (224, 216, 198), (236, 230, 214), (126, 146, 168), (186, 164, 140), (86, 108, 138)
    elif style == "drawing":
        field, edge, band, accent, ink = (152, 54, 52), (222, 198, 160), (42, 52, 92), (206, 164, 132), (96, 32, 36)
    else:  # hall runner: deep red, navy, cream, a little green
        field, edge, band, accent, ink = (138, 32, 40), (232, 220, 196), (32, 44, 86), (64, 110, 78), (244, 232, 206)
    s = _surf(tw, th)
    s.fill((*field, 255))
    b = max(2, min(tw, th) // 18)
    # borders: dark edge, cream, navy, cream, back to the field
    for inset, col, width in (
        (0, (36, 28, 26), max(2, b // 3)),
        (max(2, b // 3), edge, max(2, b // 2)),
        (b, band, max(2, b // 2)),
        (b + max(2, b // 2), edge, max(1, b // 4)),
    ):
        pygame.draw.rect(s, col, pygame.Rect(inset, inset, tw - 2 * inset, th - 2 * inset), width=width)
    m = b + b // 2 + 6
    fringe = (236, 228, 208)
    for x in range(m, tw - m, 3):
        pygame.draw.line(s, fringe, (x, 0), (x, max(3, m // 5)), 1)
        pygame.draw.line(s, fringe, (x, th - max(3, m // 5)), (x, th - 1), 1)
    cx = tw // 2
    # a calm lattice of small flowers, so the field reads as woven rather than stained
    gap = max(16, min(tw, th) // 7)
    flower = accent if style == "drawing" else ink
    centre = edge if style != "sitting" else band
    gy = m + gap // 2
    row = 0
    while gy < th - m:
        gx = m + gap // 2 + (gap // 2 if row % 2 else 0)
        while gx < tw - m:
            _rosette(s, gx, gy, max(3, gap // 6), flower, centre)
            gx += gap
        gy += gap
        row += 1
    # medallions down the long axis, drawn over the lattice
    step = max(gap + 8, (th - 2 * m) // (7 if style == "hall" else 3))
    rad = max(8, min(tw // 5, step // 3))
    y = m + step // 2
    while y < th - m:
        _medallion(s, cx, y, rad, field, band, edge, accent)
        y += step
    # corner diamonds
    cr = max(5, b)
    for px, py, dx, dy in ((m, m, 1, 1), (tw - m, m, -1, 1), (m, th - m, 1, -1), (tw - m, th - m, -1, -1)):
        pygame.draw.polygon(s, band, [(px, py), (px + dx * cr, py), (px, py + dy * cr)])
        pygame.draw.polygon(s, edge, [(px + dx * 2, py + dy * 2), (px + dx * cr // 2, py + dy * 2), (px + dx * 2, py + dy * cr // 2)])
    arr = pygame.surfarray.array3d(s).transpose(1, 0, 2)
    _CACHE[key] = arr
    return arr


def _rosette(s, x, y, r, petal, centre):
    for i in range(6):
        a = i * math.pi / 3
        pygame.draw.circle(s, petal, (int(x + math.cos(a) * r * 0.7), int(y + math.sin(a) * r * 0.7)), max(2, r // 2))
    pygame.draw.circle(s, centre, (int(x), int(y)), max(2, r // 3))


def _medallion(s, x, y, r, field, band, edge, accent):
    """Navy diamond, cream ring, field-coloured centre, four small leaves."""
    r = int(r)
    diamond = [(x, y - r), (x + int(r * 0.72), y), (x, y + r), (x - int(r * 0.72), y)]
    pygame.draw.polygon(s, band, diamond)
    inner = [(x, y - int(r * 0.72)), (x + int(r * 0.48), y), (x, y + int(r * 0.72)), (x - int(r * 0.48), y)]
    pygame.draw.polygon(s, edge, inner)
    core = [(x, y - int(r * 0.40)), (x + int(r * 0.26), y), (x, y + int(r * 0.40)), (x - int(r * 0.26), y)]
    pygame.draw.polygon(s, field, core)
    pygame.draw.circle(s, accent, (int(x), int(y)), max(2, r // 7))
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        pygame.draw.circle(s, accent, (int(x + dx * r * 1.05), int(y + dy * r * 1.05)), max(2, r // 8))


def stamp(tex, x0, y0, x1, y1, z=0.0, mask="rect"):
    """Map a world-space RGB image `tex` (rows = y, cols = x) onto the floor plane.

    Coordinates are the same ones the room drawers pass to `qz` / `box` (world x
    when a `world()` shift is active). Works on the current house_common canvas,
    including transparent glimpse layers.
    """
    import house_common as hc
    screen = hc.screen
    if screen is None or tex is None:
        return
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    if x1 - x0 < 1e-4 or y1 - y0 < 1e-4:
        return
    S, OX, OY, HW, HH = hc.S, hc.OX, hc.OY, hc.HW, hc.HH
    X_OFF = hc.X_OFF
    Y_OFF = hc.Y_OFF
    corners = [hc.P(x, y, z) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    sws, shs = screen.get_size()
    ix0 = max(0, int(min(xs)) - 1)
    iy0 = max(0, int(min(ys)) - 1)
    ix1 = min(sws, int(max(xs)) + 2)
    iy1 = min(shs, int(max(ys)) + 2)
    sw, sh = ix1 - ix0, iy1 - iy0
    if sw < 2 or sh < 2:
        return
    sx = (ix0 + np.arange(sw) + 0.5) / S
    sy = (iy0 + np.arange(sh) + 0.5) / S
    xmy = (sx[:, None] - OX) / HW
    xpy = (sy[None, :] - OY + z) / HH
    wx = (xpy + xmy) / 2 + X_OFF
    wy = (xpy - xmy) / 2 + Y_OFF
    m = (wx >= x0) & (wx <= x1) & (wy >= y0) & (wy <= y1)
    if mask == "ellipse":
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = max(1e-4, (x1 - x0) / 2), max(1e-4, (y1 - y0) / 2)
        m &= ((wx - cx) / rx) ** 2 + ((wy - cy) / ry) ** 2 <= 1.0
    if not m.any():
        return
    th, tw = tex.shape[:2]
    u = (wx - x0) / (x1 - x0)
    v = (wy - y0) / (y1 - y0)
    tx = np.clip((u * (tw - 1)).astype(np.int32), 0, tw - 1)
    ty = np.clip((v * (th - 1)).astype(np.int32), 0, th - 1)
    col = np.zeros((sw, sh, 3), np.uint8)
    col[m] = tex[ty[m], tx[m]]
    # Write the floor pixels straight into the canvas. An SRCALPHA blit onto a
    # macOS surface that itself has alpha clears every pixel whose source alpha
    # is 0, which erases the room inside the floor's bounding box.
    rgb = pygame.surfarray.pixels3d(screen)
    view = rgb[ix0:ix1, iy0:iy1]
    view[m] = col[m]
    del rgb
    if screen.get_masks()[3]:
        aa = pygame.surfarray.pixels_alpha(screen)
        aa[ix0:ix1, iy0:iy1][m] = 255
        del aa


def chandelier(x, y, z=236):
    """Crystal chandelier, drawn from scratch: brass ring, hanging drops, warm glow."""
    import house_common as hc
    import hm_engine as art
    screen = hc.screen
    S = hc.S
    top = hc.P(x, y, z + 78)
    hub = hc.P(x, y, z + 8)
    pygame.draw.line(screen, (70, 64, 58), top, hub, max(1, S))
    glow = art.glow(int(70 * S), (255, 214, 150), 0.45, squash=1.15)
    screen.blit(glow, (hub[0] - glow.get_width() / 2, hub[1] - glow.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
    # brass ring
    ring = []
    for i in range(20):
        a = 2 * math.pi * i / 20
        ring.append(hc.P(x + 0.34 * math.cos(a), y + 0.34 * math.sin(a), z))
    pygame.draw.polygon(screen, (176, 140, 64), ring, max(2, S))
    pygame.draw.circle(screen, (210, 176, 90), (int(hub[0]), int(hub[1])), int(5 * S))
    pygame.draw.circle(screen, (255, 236, 190), (int(hub[0] - S), int(hub[1] - S)), max(1, int(2 * S)))
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.2
        cx, cy = x + 0.34 * math.cos(a), y + 0.34 * math.sin(a)
        p0 = hc.P(cx, cy, z)
        p1 = hc.P(cx, cy, z - 18)
        p2 = hc.P(cx, cy, z - 42)
        pygame.draw.line(screen, (200, 206, 214), p0, p1, max(1, S))
        # a faceted drop
        d = max(3, int(4.2 * S))
        dx, dy = p2
        poly = [(dx, dy - d * 1.4), (dx + d * 0.7, dy - d * 0.2), (dx, dy + d * 0.9), (dx - d * 0.7, dy - d * 0.2)]
        pygame.draw.polygon(screen, (214, 226, 234), poly)
        pygame.draw.polygon(screen, (255, 255, 255), [(dx - d * 0.15, dy - d * 0.8), (dx + d * 0.15, dy - d * 0.5),
                                                      (dx - d * 0.05, dy - d * 0.15)])
        # a smaller inner drop on alternate arms
        if i % 2 == 0:
            q = hc.P(x + 0.16 * math.cos(a), y + 0.16 * math.sin(a), z - 28)
            pygame.draw.circle(screen, (232, 240, 246), (int(q[0]), int(q[1])), max(2, int(2.4 * S)))
            pygame.draw.circle(screen, (255, 255, 255), (int(q[0] - 1), int(q[1] - 1)), max(1, S))
