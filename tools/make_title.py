#!/usr/bin/env python3
"""Paint the title screen background: the front of our house, stylised.

A simplified painted illustration in the game's 2:1 isometric, drawn from
scratch with Pillow (no photo is used or stored). Red-brick Georgian front,
white six-over-six sashes, an arched hood over the navy front door, hipped
slate roof with two chimneys, lawn and trees on a bright afternoon. No house
number or address. Writes assets/title/house.png (1280x720); the title text,
Archie and Myrtle are drawn on top at run time by title.py.

    python3 tools/make_title.py
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "title", "house.png")
SS = 2
W, H = 1280 * SS, 720 * SS
A = 32 * SS            # px per metre along the ground axes
ZK = 37 * SS           # px per metre up
OX, OY = 760 * SS, 290 * SS
HW, HD, EAVES = 11.0, 7.0, 6.2      # house width (u), depth (v), eaves height
PPM = 80               # texture pixels per metre
R = random.Random(7)


def P(u, v, z=0.0):
    return (OX + (u - v) * A, OY + (u + v) * A / 2 - z * ZK)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def jitter(c, n):
    return tuple(max(0, min(255, int(ch + R.uniform(-n, n)))) for ch in c)


def warp(canvas, tex, o, ax1, ax2, mask_poly=None):
    """Paste tex so its (0,0) lands at world o, +x along ax1 (m), +y along ax2 (m)."""
    ox, oy = P(*o)
    p1 = P(*(o[i] + ax1[i] for i in range(3)))
    p2 = P(*(o[i] + ax2[i] for i in range(3)))
    tw, th = tex.size
    a = ((p1[0] - ox) / tw, (p2[0] - ox) / th)
    b = ((p1[1] - oy) / tw, (p2[1] - oy) / th)
    m = np.array([[a[0], a[1]], [b[0], b[1]]])
    inv = np.linalg.inv(m)
    c = -inv @ np.array([ox, oy])
    data = (inv[0, 0], inv[0, 1], c[0], inv[1, 0], inv[1, 1], c[1])
    rgba = tex.convert("RGBA")
    out = rgba.transform((W, H), Image.AFFINE, data, resample=Image.BICUBIC)
    if mask_poly is not None:
        mk = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mk).polygon(mask_poly, fill=255)
        alpha = Image.fromarray(np.minimum(np.asarray(out.getchannel("A")), np.asarray(mk)))
        out.putalpha(alpha)
    canvas.alpha_composite(out)


# ------------------------------------------------------------------ textures
BRICK = (168, 82, 56)
RUBBED = (196, 104, 66)
MORTAR = (196, 170, 140)
WHITE = (240, 238, 228)
NAVY = (28, 44, 86)


def brick_wall(w_m, h_m, light=1.0):
    tw, th = int(w_m * PPM), int(h_m * PPM)
    img = Image.new("RGB", (tw, th), lerp(MORTAR, (0, 0, 0), 1 - light))
    d = ImageDraw.Draw(img)
    bh, bw = 0.075 * PPM, 0.225 * PPM
    row = 0
    y = th
    while y > -bh:
        off = (bw / 2) if row % 2 else 0
        x = -off
        while x < tw:
            base = BRICK if R.random() > 0.12 else (150, 70, 52)
            if R.random() < 0.06:
                base = (185, 104, 72)
            c = lerp(jitter(base, 14), (0, 0, 0), 1 - light)
            d.rectangle([x + 1, y - bh + 1, x + bw - 1, y - 1], fill=c)
            x += bw
        y -= bh
        row += 1
    return img, d


def zy(th, z):
    return th - z * PPM


def window(d, th, uc, z0, z1, w=1.15, light=1.0):
    x0, x1 = (uc - w / 2) * PPM, (uc + w / 2) * PPM
    y0, y1 = zy(th, z1), zy(th, z0)
    # rubbed-brick flat arch and stone sill
    d.rectangle([x0 - 0.12 * PPM, y0 - 0.28 * PPM, x1 + 0.12 * PPM, y0], fill=lerp(RUBBED, (0, 0, 0), 1 - light))
    for i in range(9):
        xx = x0 - 0.12 * PPM + i * (x1 - x0 + 0.24 * PPM) / 8
        d.line([xx, y0 - 0.28 * PPM, xx, y0], fill=lerp((160, 84, 56), (0, 0, 0), 1 - light), width=2)
    d.rectangle([x0 - 0.1 * PPM, y1, x1 + 0.1 * PPM, y1 + 0.09 * PPM], fill=lerp((226, 220, 204), (0, 0, 0), 1 - light))
    # frame and glass
    d.rectangle([x0, y0, x1, y1], fill=lerp(WHITE, (0, 0, 0), 1 - light))
    f = 0.07 * PPM
    gx0, gy0, gx1, gy1 = x0 + f, y0 + f, x1 - f, y1 - f
    for i in range(int(gy1 - gy0)):
        t = i / max(1, gy1 - gy0)
        c = lerp((70, 92, 118), (30, 38, 52), t)
        d.line([gx0, gy0 + i, gx1, gy0 + i], fill=lerp(c, (0, 0, 0), 1 - light))
    # sky glint
    d.polygon([(gx0, gy0 + (gy1 - gy0) * 0.35), (gx0 + (gx1 - gx0) * 0.45, gy0), (gx0 + (gx1 - gx0) * 0.7, gy0),
               (gx0, gy0 + (gy1 - gy0) * 0.62)], fill=lerp((132, 160, 188), (0, 0, 0), 1 - light))
    # six over six
    bar = lerp(WHITE, (0, 0, 0), 1 - light)
    for k in (1, 2):
        xx = gx0 + (gx1 - gx0) * k / 3
        d.line([xx, gy0, xx, gy1], fill=bar, width=3)
    for k in (1, 3):
        yy = gy0 + (gy1 - gy0) * k / 4
        d.line([gx0, yy, gx1, yy], fill=bar, width=3)
    mid = (gy0 + gy1) / 2
    d.line([gx0, mid, gx1, mid], fill=bar, width=6)


def facade():
    img, d = brick_wall(HW, EAVES)
    th = img.size[1]
    # plinth and cornice
    d.rectangle([0, zy(th, 0.35), img.size[0], th], fill=(132, 62, 46))
    d.rectangle([0, 0, img.size[0], 0.16 * PPM], fill=(232, 228, 216))
    d.rectangle([0, 0.16 * PPM, img.size[0], 0.22 * PPM], fill=(120, 96, 80))
    for uc in (2.0, 5.5, 9.0):
        window(d, th, uc, 3.75, 5.45, w=1.15)
    for uc in (2.0, 9.0):
        window(d, th, uc, 0.75, 2.65, w=1.25)
    # front door: navy blue, six panels, arched fanlight and white hood
    dx0, dx1 = 5.0 * PPM, 6.0 * PPM
    dz1 = zy(th, 2.15)
    d.rectangle([dx0 - 0.1 * PPM, dz1 - 0.05 * PPM, dx1 + 0.1 * PPM, th], fill=WHITE)
    d.rectangle([dx0, dz1, dx1, th - 0.02 * PPM], fill=NAVY)
    for r in range(3):
        for c in range(2):
            px0 = dx0 + 0.12 * PPM + c * 0.42 * PPM
            py0 = dz1 + 0.12 * PPM + r * 0.66 * PPM
            d.rectangle([px0, py0, px0 + 0.32 * PPM, py0 + 0.52 * PPM], outline=(46, 66, 116), width=3)
            d.line([px0, py0 + 0.52 * PPM, px0 + 0.32 * PPM, py0 + 0.52 * PPM], fill=(16, 24, 50), width=2)
    d.ellipse([dx0 + 0.78 * PPM, dz1 + 1.0 * PPM, dx0 + 0.86 * PPM, dz1 + 1.08 * PPM], fill=(214, 180, 90))  # brass knob
    cx = (dx0 + dx1) / 2
    rr = 0.6 * PPM
    d.pieslice([cx - rr - 0.12 * PPM, dz1 - rr - 0.2 * PPM, cx + rr + 0.12 * PPM, dz1 + rr], 180, 360, fill=WHITE)
    d.pieslice([cx - rr + 0.04 * PPM, dz1 - rr + 0.0 * PPM, cx + rr - 0.04 * PPM, dz1 + rr - 0.1 * PPM], 180, 360,
               fill=(48, 62, 84))
    for k in range(1, 6):
        ang = math.pi + k * math.pi / 6
        d.line([cx, dz1 - 0.05 * PPM, cx + math.cos(ang) * rr, dz1 - 0.05 * PPM + math.sin(ang) * rr],
               fill=WHITE, width=3)
    d.line([cx - rr - 0.12 * PPM, dz1 + 0.02 * PPM, cx + rr + 0.12 * PPM, dz1 + 0.02 * PPM], fill=(200, 196, 186), width=5)
    # climbing plant beside the door
    for _ in range(140):
        x = R.uniform(dx1 + 0.3 * PPM, dx1 + 0.75 * PPM)
        y = R.uniform(zy(th, 2.0), th)
        rr2 = R.uniform(3, 7)
        d.ellipse([x - rr2, y - rr2, x + rr2, y + rr2], fill=jitter((70, 108, 54), 18))
    return img


def side():
    img, d = brick_wall(HD, EAVES, light=0.7)
    th = img.size[1]
    d.rectangle([0, zy(th, 0.35), img.size[0], th], fill=(92, 44, 34))
    d.rectangle([0, 0, img.size[0], 0.16 * PPM], fill=(170, 166, 158))
    # four windows, as the house: two upstairs over two downstairs, evenly
    # spaced along the side, the front's sashes in the side wall's shade
    for uc in (HD / 3, HD * 2 / 3):
        window(d, th, uc, 3.75, 5.45, w=1.05, light=0.7)
        window(d, th, uc, 0.75, 2.65, w=1.15, light=0.7)
    return img


def slate(w_m, h_m, light):
    tw, th = int(w_m * PPM), int(h_m * PPM)
    base = lerp((96, 98, 110), (0, 0, 0), 1 - light)
    img = Image.new("RGB", (tw, th), base)
    d = ImageDraw.Draw(img)
    sh = 0.22 * PPM
    y = 0
    row = 0
    while y < th:
        x = -(0.15 * PPM if row % 2 else 0)
        while x < tw:
            c = lerp(jitter((104, 106, 120), 10), (0, 0, 0), 1 - light)
            d.rectangle([x + 1, y + 1, x + 0.3 * PPM - 1, y + sh - 1], fill=c)
            x += 0.3 * PPM
        d.line([0, y + sh - 1, tw, y + sh - 1], fill=lerp((60, 60, 70), (0, 0, 0), 1 - light), width=2)
        y += sh
        row += 1
    # a little moss and weathering
    for _ in range(int(w_m * h_m * 6)):
        x, yy = R.uniform(0, tw), R.uniform(0, th)
        r = R.uniform(2, 6)
        d.ellipse([x - r, yy - r * 0.5, x + r, yy + r * 0.5], fill=lerp(jitter((112, 116, 96), 10), (0, 0, 0), 1 - light))
    return img


# ------------------------------------------------------------------ painting
def dabs(layer, cx, cy, rx, ry, pal, n, size=(6, 16), light_dir=(-0.6, -0.8)):
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        a = R.uniform(0, 2 * math.pi)
        rad = math.sqrt(R.random())
        x = cx + math.cos(a) * rx * rad
        y = cy + math.sin(a) * ry * rad
        lit = -((x - cx) / rx * light_dir[0] + (y - cy) / ry * light_dir[1])  # -1..1, +1 towards the sun
        t = max(0.0, min(1.0, 0.5 + 0.5 * lit + R.uniform(-0.25, 0.25)))
        c = lerp(pal[0], pal[1], t)
        s = R.uniform(*size) * SS
        ang = R.uniform(-0.5, 0.5)
        pts = [(x + math.cos(ang + k * math.pi / 3) * s * (1.0 if k % 3 else 0.55),
                y + math.sin(ang + k * math.pi / 3) * s * 0.6) for k in range(6)]
        d.polygon(pts, fill=c + (255,))


def tree(layer, cx, base_y, h, w, pal, trunk=(84, 66, 52)):
    d = ImageDraw.Draw(layer)
    d.polygon([(cx - 8 * SS, base_y), (cx + 8 * SS, base_y), (cx + 4 * SS, base_y - h * 0.5), (cx - 4 * SS, base_y - h * 0.5)],
              fill=trunk + (255,))
    for k in range(5):
        dabs(layer, cx + R.uniform(-w * 0.3, w * 0.3), base_y - h * (0.55 + 0.1 * k), w * (0.55 - 0.06 * k),
             h * (0.25 - 0.02 * k), pal, 260)


def willow(layer, cx, top_y, base_y, w):
    """A weeping willow at the right edge: a soft crown and long hanging fronds."""
    d = ImageDraw.Draw(layer)
    d.polygon([(cx - 6 * SS, base_y), (cx + 30 * SS, base_y), (cx + 6 * SS, top_y + 160 * SS), (cx - 30 * SS, top_y + 140 * SS)],
              fill=(88, 72, 58, 255))
    for k in range(4):
        d.line([(cx - 10 * SS, top_y + 150 * SS), (cx - w * (0.3 + 0.18 * k), top_y + (20 + 25 * k) * SS)],
               fill=(96, 80, 62, 255), width=(8 - k) * SS)
    dabs(layer, cx - w * 0.45, top_y + 40 * SS, w * 0.7, 90 * SS, ((92, 126, 56), (178, 200, 108)), 700, size=(5, 12))
    for _ in range(520):
        x0 = cx + R.uniform(-w * 1.05, w * 0.3)
        y0 = top_y + R.uniform(0, 110 * SS)
        L = R.uniform(140, 380) * SS
        c = lerp((88, 124, 52), (190, 210, 118), R.random())
        bend = R.uniform(-14, 6) * SS
        pts = [(x0 + bend * t * t, y0 + t * L) for t in np.linspace(0, 1, 12)]
        d.line(pts, fill=c + (235,), width=R.randint(2, 3) * SS)


def main():
    canvas = Image.new("RGBA", (W, H))
    # sky: bright afternoon, warm near the horizon
    sky = np.zeros((H, W, 3), np.float32)
    t = np.linspace(0, 1, H)[:, None]
    top, bot = np.array([86, 140, 206]), np.array([214, 226, 232])
    sky[:] = (top * (1 - t) + bot * t)[:, None, :].reshape(H, 1, 3)
    canvas.paste(Image.fromarray(sky.astype(np.uint8)), (0, 0))
    clouds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for cx, cy, s in ((300, 120, 1.0), (980, 70, 0.8), (640, 180, 0.6), (1180, 210, 0.7)):
        for _ in range(16):
            x = (cx + R.uniform(-90, 90) * s) * SS
            y = (cy + R.uniform(-18, 18) * s) * SS
            r = R.uniform(28, 60) * s * SS
            cd.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(255, 255, 252, 150))
    canvas.alpha_composite(clouds.filter(ImageFilter.GaussianBlur(16 * SS)))

    # distant trees along the horizon
    back = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(-40, 1340, 70):
        dabs(back, (x + R.uniform(-20, 20)) * SS, R.uniform(330, 380) * SS, 80 * SS, 70 * SS,
             ((70, 98, 72), (128, 156, 104)), 150, size=(8, 18))
    canvas.alpha_composite(back.filter(ImageFilter.GaussianBlur(1.5 * SS)))

    # ground: lawn, with the path along the front
    g = ImageDraw.Draw(canvas)
    g.rectangle([0, 360 * SS, W, H], fill=(104, 150, 62, 255))
    lawn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lawn)
    for _ in range(9000):
        x, y = R.uniform(0, W), R.uniform(360 * SS, H)
        depth = (y - 360 * SS) / (H - 360 * SS)
        c = lerp((92, 138, 54), (150, 190, 84), R.random())
        s = (2 + depth * 6) * SS
        ld.line([(x, y), (x + R.uniform(-1, 1) * s, y - s * 1.6)], fill=c + (200,), width=max(1, int(s * 0.5)))
    canvas.alpha_composite(lawn)
    stripes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for k in range(-12, 14, 2):           # mowing stripes along the house's front
        sd.polygon([P(-30, HD + 2 + k), P(40, HD + 2 + k), P(40, HD + 3 + k), P(-30, HD + 3 + k)], fill=(255, 255, 220, 22))
    stripes = stripes.filter(ImageFilter.GaussianBlur(3 * SS))
    ImageDraw.Draw(stripes).rectangle([0, 0, W, 362 * SS], fill=(0, 0, 0, 0))
    canvas.alpha_composite(stripes)
    hedge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(-20, 1300, 26):
        dabs(hedge, x * SS, 362 * SS, 26 * SS, 10 * SS, ((56, 84, 44), (104, 136, 70)), 26, size=(4, 9))
    canvas.alpha_composite(hedge)
    path = [P(-1.5, HD + 0.6), P(HW + 0.6, HD + 0.6), P(HW + 0.6, HD + 1.6), P(-1.5, HD + 1.6)]
    g.polygon(path, fill=(196, 182, 156, 255))
    door_path = [P(5.0, HD + 1.6), P(6.0, HD + 1.6), P(6.0, HD + 6.5), P(5.0, HD + 6.5)]
    g.polygon(door_path, fill=(190, 176, 150, 255))
    # soft shadow of the house on the lawn, to the right (sun from the left)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([P(HW, 0), P(HW + 3.2, 1.0), P(HW + 3.2, HD + 0.6), P(HW, HD)], fill=(30, 50, 20, 90))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6 * SS)))

    # walls
    warp(canvas, facade(), (0, HD, EAVES), (HW, 0, 0), (0, 0, -EAVES))
    warp(canvas, side(), (HW, HD, EAVES), (0, -HD, 0), (0, 0, -EAVES))
    # roof: hipped
    e, rz = 0.3, 9.0
    r0, r1, rv = 3.6, 7.4, HD / 2
    front = [P(-e, HD + e, EAVES), P(HW + e, HD + e, EAVES), P(r1, rv, rz), P(r0, rv, rz)]
    hip = [P(HW + e, HD + e, EAVES), P(HW + e, -e, EAVES), P(r1, rv, rz)]
    slope_len = math.hypot(HD / 2 + e, rz - EAVES)
    warp(canvas, slate(HW + 2 * e, slope_len, 0.95), (-e, rv, rz), (HW + 2 * e, 0, 0), (0, HD / 2 + e, EAVES - rz), front)
    warp(canvas, slate(HD + 2 * e, HW / 2, 0.66), (r1, HD + e, rz), (0, -(HD + 2 * e), 0), (HW + e - r1, 0, EAVES - rz), hip)
    g = ImageDraw.Draw(canvas)
    g.line([P(r0, rv, rz), P(r1, rv, rz)], fill=(70, 70, 80, 255), width=4 * SS)
    g.line([P(r1, rv, rz), P(HW + e, HD + e, EAVES)], fill=(70, 70, 80, 255), width=4 * SS)
    g.line([P(-e, HD + e, EAVES), P(HW + e, HD + e, EAVES)], fill=(58, 56, 60, 255), width=3 * SS)  # gutter
    # chimneys
    for u0 in (2.3, 7.5):
        u1, v0, v1, zb, zt = u0 + 0.9, rv - 0.4, rv + 0.4, 8.3, 10.2
        fc = Image.new("RGB", (int(0.9 * PPM), int((zt - zb) * PPM)), BRICK)
        bimg, _ = brick_wall(0.9, zt - zb)
        warp(canvas, bimg, (u0, v1, zt), (0.9, 0, 0), (0, 0, -(zt - zb)))
        simg, _ = brick_wall(0.8, zt - zb, light=0.68)
        warp(canvas, simg, (u1, v1, zt), (0, -0.8, 0), (0, 0, -(zt - zb)))
        g.polygon([P(u0 - 0.05, v0 - 0.05, zt + 0.12), P(u1 + 0.05, v0 - 0.05, zt + 0.12),
                   P(u1 + 0.05, v1 + 0.05, zt + 0.12), P(u0 - 0.05, v1 + 0.05, zt + 0.12)], fill=(150, 72, 52, 255))
        for k, uu in enumerate((u0 + 0.25, u0 + 0.65)):
            x, y = P(uu, (v0 + v1) / 2, zt + 0.1)
            pw, ph = 6 * SS, 18 * SS + k * 4 * SS
            g.rectangle([x - pw, y - ph, x + pw, y], fill=(176, 92, 58, 255))
            g.ellipse([x - pw, y - ph - 3 * SS, x + pw, y - ph + 3 * SS], fill=(120, 60, 40, 255))
            g.rectangle([x + pw * 0.3, y - ph, x + pw, y], fill=(146, 74, 48, 255))

    # planting along the front of the house, a flower bed, and the trees
    front_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for k in range(22):
        u = -0.4 + k * 0.55
        if 4.6 < u < 6.4:
            continue
        x, y = P(u, HD + 0.25)
        dabs(front_layer, x, y - 10 * SS, 22 * SS, 14 * SS, ((58, 96, 46), (132, 170, 86)), 40, size=(4, 9))
        if R.random() < 0.35:
            dabs(front_layer, x, y - 14 * SS, 10 * SS, 6 * SS, ((176, 120, 170), (236, 200, 220)), 10, size=(2, 4))
    bx, by = P(HW - 1.0, HD + 3.4)
    dabs(front_layer, bx, by, 120 * SS, 34 * SS, ((62, 104, 50), (150, 186, 96)), 500, size=(5, 12))
    dabs(front_layer, bx, by - 6 * SS, 100 * SS, 22 * SS, ((214, 196, 120), (250, 240, 200)), 50, size=(2, 4))
    tree(front_layer, 1180 * SS, 470 * SS, 330 * SS, 230 * SS, ((58, 92, 52), (140, 172, 92)))
    tree(front_layer, 455 * SS, 405 * SS, 240 * SS, 160 * SS, ((52, 86, 50), (124, 158, 86)))
    canvas.alpha_composite(front_layer)
    wl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    willow(wl, 1275 * SS, -30 * SS, 720 * SS, 190 * SS)
    canvas.alpha_composite(wl)
    # foreground leaves in the corners, as through the garden
    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dabs(fl, -20 * SS, 700 * SS, 200 * SS, 110 * SS, ((40, 70, 36), (100, 140, 70)), 500, size=(10, 24))
    canvas.alpha_composite(fl.filter(ImageFilter.GaussianBlur(2 * SS)))

    # painterly finish: merge into strokes, a hint of warm light, then size down
    img = canvas.convert("RGB").filter(ImageFilter.ModeFilter(5)).filter(ImageFilter.SMOOTH_MORE)
    arr = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    warm = np.clip(1 - np.hypot(xx - 0.2 * W, yy + 0.2 * H) / (1.4 * W), 0, 1)[..., None]
    arr = arr * (1 + 0.08 * warm) + np.array([10, 6, -4]) * warm
    rng = np.random.default_rng(3)
    arr += rng.normal(0, 3.0, arr.shape[:2])[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img = img.resize((W // SS, H // SS), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT))


if __name__ == "__main__":
    main()
