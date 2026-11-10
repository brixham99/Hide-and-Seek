"""High-resolution orthographic furniture face sheets (front / side / top).

These are the flat elevations that iso_paint.py wraps onto 2:1 isometric
boxes, in the same spirit as Haunted Mansion's tools/iso_box.py sheets.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "faces")


def save(name, img):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    img.convert("RGBA").save(path)
    print("wrote", path, img.size)
    return path


def _noise(h, w, scale, seed, octaves=4):
    rnd = np.random.RandomState(seed)
    acc = np.zeros((h, w), np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        sh, sw = max(2, int(h / scale) + 2), max(2, int(w / scale) + 2)
        grid = rnd.randn(sh, sw).astype(np.float32)
        ys = np.linspace(0, sh - 1.001, h)
        xs = np.linspace(0, sw - 1.001, w)
        y0 = np.floor(ys).astype(int)
        x0 = np.floor(xs).astype(int)
        fy = (ys - y0)[:, None]
        fx = (xs - x0)[None, :]
        y1 = np.clip(y0 + 1, 0, sh - 1)
        x1 = np.clip(x0 + 1, 0, sw - 1)
        y0 = np.clip(y0, 0, sh - 1)
        x0 = np.clip(x0, 0, sw - 1)
        v = (grid[y0[:, None], x0[None, :]] * (1 - fy) * (1 - fx)
             + grid[y0[:, None], x1[None, :]] * (1 - fy) * fx
             + grid[y1[:, None], x0[None, :]] * fy * (1 - fx)
             + grid[y1[:, None], x1[None, :]] * fy * fx)
        acc += v * amp
        total += amp
        amp *= 0.5
        scale = max(2.0, scale / 2)
    return acc / total


def _fbm(h, w, seed, stretch=(1.0, 1.0), scale=18):
    n = _noise(max(8, int(h / stretch[0])), max(8, int(w / stretch[1])), scale, seed)
    return np.array(Image.fromarray(((n - n.min()) / max(1e-6, n.max() - n.min()) * 255).astype(np.uint8), "L")
                    .resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def _rgb(img):
    a = np.asarray(img).astype(np.float32)
    if a.shape[-1] == 3:
        a = np.concatenate([a, np.full(a.shape[:2] + (1,), 255, np.float32)], 2)
    return a


def _to(img_arr):
    return Image.fromarray(img_arr.clip(0, 255).astype(np.uint8), "RGBA")


def _ao(h, w, inset=0.06):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = xx / max(1, w - 1), yy / max(1, h - 1)
    e = np.minimum(np.minimum(nx, 1 - nx), np.minimum(ny, 1 - ny))
    return np.clip(e / inset, 0, 1)


def wood(w, h, c1, c2, seed=1, plank=70, vertical=False):
    """Streaky timber: planks, pores, knots, varnish streak, edge AO."""
    rnd = random.Random(seed)
    n = _fbm(h, w, seed, stretch=(0.25, 3.5) if not vertical else (3.5, 0.25), scale=22)
    n2 = _fbm(h, w, seed + 3, stretch=(0.4, 2.2) if not vertical else (2.2, 0.4), scale=10)
    grain = 0.62 * n + 0.38 * n2
    # plank seams
    if plank:
        yy, xx = np.mgrid[0:h, 0:w]
        axis = xx if not vertical else yy
        seam = np.abs(((axis + rnd.randint(0, plank)) % plank) - 0) < 1
        grain = np.where(seam, grain * 0.55, grain)
    # knots
    a = np.zeros((h, w, 4), np.float32)
    c1, c2 = np.array(c1, np.float32), np.array(c2, np.float32)
    col = c2[None, None, :] + (c1 - c2)[None, None, :] * grain[..., None]
    # varnish highlight band
    yy = np.linspace(0, 1, h)[:, None, None]
    col = col * (0.88 + 0.22 * np.sin(yy * math.pi) ** 1.4)
    # a few knots
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(overlay)
    for _ in range(rnd.randint(2, 5)):
        kx, ky = rnd.randint(w // 8, 7 * w // 8), rnd.randint(h // 8, 7 * h // 8)
        rw, rh = rnd.randint(8, 18), rnd.randint(6, 12)
        kc = tuple(int(x * 0.65) for x in c2) + (180,)
        dr.ellipse((kx - rw, ky - rh, kx + rw, ky + rh), fill=kc)
        dr.ellipse((kx - rw // 2, ky - rh // 2, kx + rw // 2, ky + rh // 2),
                   outline=tuple(int(x * 0.45) for x in c2) + (200,), width=1)
    a[..., :3] = col
    a[..., 3] = 255
    img = _to(a)
    img = Image.alpha_composite(img, overlay)
    ao = _ao(h, w, 0.05)
    arr = _rgb(img)
    arr[..., :3] *= (0.72 + 0.28 * ao)[..., None]
    return _to(arr)


def painted_panel(w, h, col, seed=2, grain=0.12):
    """Painted timber: faint grain under eggshell paint, dirt in the pores."""
    base = wood(w, h, tuple(min(255, c + 18) for c in col),
                tuple(max(0, c - 22) for c in col), seed=seed, plank=0)
    arr = _rgb(base)
    n = _fbm(h, w, seed + 9, stretch=(1.0, 1.2), scale=16)
    c = np.array(col, np.float32)
    arr[..., :3] = arr[..., :3] * grain + c[None, None, :] * (1 - grain)
    arr[..., :3] *= (0.92 + 0.16 * n)[..., None]
    # fine brush strokes
    stroke = _fbm(h, w, seed + 11, stretch=(0.2, 4.0), scale=8)
    arr[..., :3] *= (0.96 + 0.08 * stroke)[..., None]
    arr[..., :3] *= (0.74 + 0.26 * _ao(h, w, 0.07))[..., None]
    return _to(arr)


def bevel(arr, x0, y0, x1, y1, width=10):
    """Inset bevel: light top/left, dark bottom/right, AO in the well."""
    h, w = arr.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return
    well = arr[y0:y1, x0:x1].copy()
    well[..., :3] *= 0.86
    hh, ww = well.shape[:2]
    bw = max(3, min(width, hh // 5, ww // 5))
    for i in range(bw):
        k = i / bw
        # top highlight
        well[i, :, :3] *= 1.18 - 0.08 * k
        well[i, :, :3] = np.clip(well[i, :, :3] + 18 * (1 - k), 0, 255)
        # bottom shadow
        well[hh - 1 - i, :, :3] *= 0.72 + 0.18 * k
        # left highlight
        well[:, i, :3] *= 1.10 - 0.06 * k
        # right shadow
        well[:, ww - 1 - i, :3] *= 0.78 + 0.16 * k
    arr[y0:y1, x0:x1] = well


def knob(arr, cx, cy, r=9, col=(196, 168, 88)):
    yy, xx = np.ogrid[0:arr.shape[0], 0:arr.shape[1]]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    m = d <= r
    nrm_x = (xx - cx) / max(1, r)
    nrm_y = (yy - cy) / max(1, r)
    light = np.clip(0.55 + 0.55 * (-0.6 * nrm_x - 0.8 * nrm_y), 0.25, 1.35)
    c = np.array(col, np.float32)
    arr[..., :3][m] = np.clip(c[None, :] * light[..., None][m], 0, 255)
    arr[..., 3][m] = 255
    rim = (d > r - 1.2) & (d <= r + 0.6)
    arr[..., :3][rim] *= 0.45


def shaker_front(w, h, col, doors=2, drawers=0, seed=4, knobs=True):
    """Painted shaker doors (and optional top drawers)."""
    img = painted_panel(w, h, col, seed=seed)
    arr = _rgb(img)
    # plinth and cornice
    corn, plinth = int(h * 0.08), int(h * 0.10)
    arr[:corn, :, :3] *= 1.08
    arr[h - plinth:, :, :3] *= 0.84
    body_y0, body_y1 = corn + 2, h - plinth - 2
    # drawers along the top of the body
    dw_h = int((body_y1 - body_y0) * 0.22) if drawers else 0
    if drawers:
        for i in range(drawers):
            x0 = int(w * (i / drawers)) + 8
            x1 = int(w * ((i + 1) / drawers)) - 8
            y0, y1 = body_y0 + 6, body_y0 + dw_h
            bevel(arr, x0, y0, x1, y1, width=8)
            if knobs:
                knob(arr, (x0 + x1) // 2, (y0 + y1) // 2, r=max(6, w // 70))
        body_y0 = body_y0 + dw_h + 6
    for i in range(doors):
        x0 = int(w * (i / doors)) + 8
        x1 = int(w * ((i + 1) / doors)) - 8
        bevel(arr, x0, body_y0, x1, body_y1, width=max(8, w // 40))
        if knobs:
            kx = x0 + int((x1 - x0) * (0.18 if i == 0 else 0.82)) if doors > 1 else (x0 + x1) // 2
            knob(arr, kx, (body_y0 + body_y1) // 2, r=max(7, w // 64))
    # hairline division
    for i in range(1, doors):
        x = int(w * i / doors)
        arr[:, x:x + 1, :3] *= 0.55
    return _to(arr)


def bookcase_front(w, h, wood_col=(84, 56, 38), shelves=2, seed=14):
    frame = wood(w, h, tuple(min(255, c + 30) for c in wood_col),
                 tuple(max(0, c - 20) for c in wood_col), seed=seed, plank=0)
    arr = _rgb(frame)
    # dark interior well
    m = int(w * 0.07)
    t, b = int(h * 0.08), int(h * 0.08)
    bevel(arr, m, t, w - m, h - b, width=max(8, w // 36))
    interior = (42, 30, 22)
    arr[t + 10:h - b - 10, m + 10:w - m - 10, :3] = interior
    rnd = random.Random(seed)
    spines = [(160, 40, 40), (40, 70, 120), (220, 190, 70), (60, 110, 70),
              (200, 120, 60), (230, 220, 200), (110, 40, 60), (30, 30, 30),
              (80, 90, 70), (140, 90, 50), (70, 50, 110), (180, 90, 40)]
    inner_y0, inner_y1 = t + 12, h - b - 12
    inner_x0, inner_x1 = m + 12, w - m - 12
    step = (inner_y1 - inner_y0) / shelves
    for s in range(shelves):
        y1 = int(inner_y0 + (s + 1) * step)
        y0 = int(inner_y0 + s * step)
        # shelf board
        sh_y0, sh_y1 = y1 - max(8, h // 50), y1
        arr[sh_y0:sh_y1, inner_x0:inner_x1, :3] = np.array(wood_col) * 1.15
        arr[sh_y0:sh_y0 + 2, inner_x0:inner_x1, :3] *= 1.2
        # AO under the shelf above
        if s:
            arr[y0:y0 + 6, inner_x0:inner_x1, :3] *= np.linspace(0.55, 1.0, 6)[:, None, None]
        x = inner_x0 + 4
        top = sh_y0 - 3
        while x < inner_x1 - 8:
            bw = rnd.randint(max(8, w // 50), max(14, w // 28))
            bh = rnd.randint(int((top - y0) * 0.62), int((top - y0) * 0.96))
            col = np.array(rnd.choice(spines), np.float32) * rnd.uniform(0.82, 1.05)
            arr[top - bh:top, x:x + bw, :3] = col
            # spine highlight and foot shadow
            arr[top - bh:top, x:x + 1, :3] = np.clip(col * 1.25, 0, 255)
            arr[top - bh:top, x + bw - 1:x + bw, :3] *= 0.7
            # title lines
            if bw > 10 and rnd.random() < 0.7:
                ty = top - bh + bh // 3
                arr[ty:ty + 2, x + 2:x + bw - 2, :3] = np.clip(col * 1.35, 0, 255)
            x += bw + 2
    # outer frame already wood; dark outline
    arr[:2, :, :3] *= 0.5
    arr[-2:, :, :3] *= 0.5
    arr[:, :2, :3] *= 0.5
    arr[:, -2:, :3] *= 0.5
    return _to(arr)


def fabric(w, h, col, seed=5, folds=1.0, pile="weave"):
    """Upholstery: weave or velvet pile, large folds, piping-ready edges."""
    c = np.array(col, np.float32)
    n = _fbm(h, w, seed, stretch=(1.6, 2.2), scale=28)
    n2 = _fbm(h, w, seed + 2, stretch=(0.8, 0.8), scale=7)
    fold = _fbm(h, w, seed + 4, stretch=(2.8, 1.1), scale=40)
    arr = np.zeros((h, w, 4), np.float32)
    shade = 0.78 + 0.34 * fold * folds + 0.10 * n
    if pile == "velvet":
        # directional sheen bands
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        sheen = 0.5 + 0.5 * np.sin(xx / w * math.pi * 3.2 + n * 2)
        shade = shade * (0.82 + 0.38 * sheen)
        shade = shade * (0.94 + 0.12 * n2)
    else:
        # boucle / woven: two-axis thread
        yy, xx = np.mgrid[0:h, 0:w]
        weave = 0.5 + 0.5 * np.sin(xx * 0.55) * np.sin(yy * 0.55)
        shade = shade * (0.90 + 0.16 * weave) * (0.95 + 0.10 * n2)
    arr[..., :3] = c[None, None, :] * shade[..., None]
    # contrast specks (boucle nubs)
    if pile != "velvet":
        rnd = np.random.RandomState(seed)
        spec = rnd.rand(h, w) > 0.97
        arr[..., :3][spec] = np.clip(arr[..., :3][spec] * 1.25, 0, 255)
    arr[..., 3] = 255
    arr[..., :3] *= (0.70 + 0.30 * _ao(h, w, 0.09))[..., None]
    return _to(arr)


def fabric_top(w, h, col, seed=5, pile="weave", cushions=0):
    img = fabric(w, h, col, seed=seed, pile=pile)
    arr = _rgb(img)
    if cushions:
        for i in range(cushions):
            x0 = int(w * i / cushions) + 6
            x1 = int(w * (i + 1) / cushions) - 6
            # seam
            if i:
                arr[:, x0 - 3:x0, :3] *= 0.62
            # piping around this cushion
            arr[4:8, x0:x1, :3] = np.clip(arr[4:8, x0:x1, :3] * 1.15, 0, 255)
            arr[h - 8:h - 4, x0:x1, :3] *= 0.75
    return _to(arr)


def side_from_front_palette(front, w, h, kind="wood", seed=1):
    a = np.asarray(front).astype(np.float32)
    m = a[..., 3] > 0
    col = tuple(int(x) for x in np.median(a[..., :3][m], 0)) if m.any() else (120, 90, 60)
    if kind == "fabric":
        pile = "velvet" if "velvet" in str(seed) else "weave"
        return fabric(w, h, col, seed=seed + 20, pile=pile)
    if kind == "paint":
        return painted_panel(w, h, col, seed=seed + 20)
    return wood(w, h, tuple(min(255, c + 24) for c in col),
                tuple(max(0, c - 24) for c in col), seed=seed + 20, vertical=True)


def build_all():
    # ----- sitting room -----
    # sage TV cabinet
    sage = (140, 160, 138)
    save("sitting_tv_cabinet_front", shaker_front(560, 320, sage, doors=2, drawers=0, seed=6))
    save("sitting_tv_cabinet_side", painted_panel(220, 320, sage, seed=7))
    save("sitting_tv_cabinet_top", painted_panel(560, 220, tuple(min(255, c + 12) for c in sage), seed=8))

    # dark oak bookcase with books
    save("sitting_bookcase_front", bookcase_front(640, 420, (84, 56, 38), shelves=2, seed=14))
    save("sitting_bookcase_side", wood(200, 420, (110, 74, 48), (70, 44, 28), seed=15, vertical=True))
    save("sitting_bookcase_top", wood(640, 200, (124, 86, 56), (78, 50, 32), seed=16, plank=90))

    # slate sofa
    slate = (52, 64, 88)
    save("sitting_slate_sofa_front", fabric(720, 400, slate, seed=21, pile="weave"))
    save("sitting_slate_sofa_side", fabric(280, 400, slate, seed=22, pile="weave"))
    save("sitting_slate_sofa_top", fabric_top(720, 300, slate, seed=23, pile="weave", cushions=3))
    save("sitting_slate_sofa_back", fabric(720, 400, tuple(int(c * 0.82) for c in slate), seed=24, pile="weave"))

    # pink velvet sofa
    pink = (204, 150, 152)
    save("sitting_pink_sofa_front", fabric(700, 420, pink, seed=31, pile="velvet"))
    save("sitting_pink_sofa_side", fabric(300, 420, pink, seed=32, pile="velvet"))
    save("sitting_pink_sofa_top", fabric_top(700, 320, pink, seed=33, pile="velvet", cushions=2))
    save("sitting_pink_sofa_back", fabric(700, 420, tuple(int(min(255, c * 0.9)) for c in pink), seed=34, pile="velvet"))

    # cream boucle armchair
    cream = (234, 226, 210)
    save("sitting_armchair_front", fabric(420, 460, cream, seed=41, pile="weave"))
    save("sitting_armchair_side", fabric(360, 460, cream, seed=42, pile="weave"))
    save("sitting_armchair_top", fabric_top(420, 360, cream, seed=43, pile="weave", cushions=1))
    save("sitting_armchair_back", fabric(420, 460, tuple(int(c * 0.88) for c in cream), seed=44, pile="weave"))

    # dark wood side table
    dw1, dw2 = (110, 74, 48), (70, 44, 26)
    save("sitting_darkwood_front", wood(360, 280, dw1, dw2, seed=51, plank=0))
    save("sitting_darkwood_side", wood(280, 280, dw1, dw2, seed=52, vertical=True, plank=0))
    save("sitting_darkwood_top", wood(400, 360, (130, 88, 56), dw2, seed=53, plank=110))

    oak1, oak2 = (214, 172, 118), (168, 120, 72)
    save("sitting_oak_front", wood(240, 240, oak1, oak2, seed=61, plank=0))
    save("sitting_oak_side", wood(200, 240, oak1, oak2, seed=62, vertical=True, plank=0))
    save("sitting_oak_top", wood(280, 240, oak1, oak2, seed=63, plank=80))

    # ----- drawing room (ready if we get to it) -----
    grey = (196, 194, 184)
    save("drawing_sofa_front", fabric(720, 420, grey, seed=71, pile="weave"))
    save("drawing_sofa_side", fabric(300, 420, grey, seed=72, pile="weave"))
    save("drawing_sofa_top", fabric_top(720, 320, grey, seed=73, pile="weave", cushions=3))
    save("drawing_sofa_back", fabric(720, 420, tuple(int(c * 0.86) for c in grey), seed=74, pile="weave"))

    white = (244, 242, 236)
    save("drawing_cupboard_front", shaker_front(400, 640, white, doors=2, seed=81))
    save("drawing_cupboard_side", painted_panel(200, 640, white, seed=82))
    save("drawing_cupboard_top", painted_panel(400, 220, white, seed=83))

    oak = (150, 102, 60)
    save("drawing_oak_front", wood(480, 260, (172, 118, 66), (110, 70, 40), seed=91, plank=0))
    save("drawing_oak_side", wood(220, 260, (172, 118, 66), (110, 70, 40), seed=92, vertical=True, plank=0))
    save("drawing_oak_top", wood(520, 360, (178, 124, 70), (118, 74, 42), seed=93, plank=120))


if __name__ == "__main__":
    build_all()
