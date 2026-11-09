"""The few Haunted Mansion engine pieces the room drawing code uses (geometry,
colour helpers, ghost door frames), copied from brixham99/Haunted-Mansion so
this repo stands alone."""
import math

import pygame

TILE_W, TILE_H, WALL_H, DOOR_H = 112, 56, 230, 185
GHOST_FRAME_ALPHA = 100          # ~39% on the open front edges


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + tuple(c[3:])


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def glow(radius, colour, strength=1.0, squash=1.6):
    """Soft elliptical glow, premultiplied: blit it with BLEND_RGB_ADD."""
    import numpy as np
    size = radius * 2 + 1
    yy, xx = np.mgrid[0:size, 0:size]
    d = np.sqrt((xx - radius) ** 2 + ((yy - radius) * squash) ** 2) / max(1, radius)
    fall = (np.clip(1.0 - d, 0.0, 1.0) ** 2) * strength
    arr = (np.array(colour, np.float32)[None, None, :] * fall[..., None]).clip(0, 255).astype(np.uint8)
    s = pygame.Surface((size, size))
    pygame.surfarray.blit_array(s, arr.transpose(1, 0, 2))
    return s


_SHADOWS = {}


def soft_shadow(rw, rh, alpha):
    """A soft-edged dark ellipse (radii rw x rh), cached; plain alpha blit."""
    import numpy as np
    key = (int(rw), int(rh), int(alpha))
    if key not in _SHADOWS:
        w, h = max(2, key[0] * 2 + 2), max(2, key[1] * 2 + 2)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt(((xx + 0.5 - w / 2) / max(1, key[0])) ** 2 + ((yy + 0.5 - h / 2) / max(1, key[1])) ** 2)
        a = np.clip((1.0 - d) / 0.45, 0, 1)
        a = a * a * (3 - 2 * a) * key[2]
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pa = pygame.surfarray.pixels_alpha(surf)
        pa[:, :] = a.T.astype(np.uint8)
        del pa
        _SHADOWS[key] = surf
    return _SHADOWS[key]


def door_frame_boxes(a, b, n0, n1):
    """Pieces of a door frame round the opening u in [a, b]: (u0, u1, z0, z1, n0, n1, k)."""
    mid = (a + b) / 2
    d = n1 - n0
    return [
        (a - .16, a, 0, DOOR_H, n0, n1, 1.0),
        (b, b + .16, 0, DOOR_H, n0, n1, 1.0),
        (a - .19, a + .02, 0, 26, n0, n1 + .3 * d, 0.85),
        (b - .02, b + .19, 0, 26, n0, n1 + .3 * d, 0.85),
        (a - .22, b + .22, DOOR_H, DOOR_H + 24, n0, n1 + .1 * d, 1.0),
        (a - .28, b + .28, DOOR_H + 24, DOOR_H + 32, n0, n1 + .6 * d, 1.18),
        (mid - .1, mid + .1, DOOR_H - 12, DOOR_H + 26, n0, n1 + .4 * d, 1.25),
    ]


def box_faces(W, box, col):
    u0, u1, z0, z1, n0, n1, k = box
    c = shade(col, k)
    return [
        (shade(c, 0.6), [W(u1, z0, n0), W(u1, z0, n1), W(u1, z1, n1), W(u1, z1, n0)]),
        (shade(c, 1.3), [W(u0, z1, n0), W(u1, z1, n0), W(u1, z1, n1), W(u0, z1, n1)]),
        (c, [W(u0, z0, n1), W(u1, z0, n1), W(u1, z1, n1), W(u0, z1, n1)]),
    ]


def door_frame_polys(W, a, b, col, n0, n1):
    """All the (colour, polygon) pieces of a door frame, mouldings included."""
    out = []
    for box in door_frame_boxes(a, b, n0, n1):
        out += box_faces(W, box, col)
    dark, light = shade(col, 0.55), shade(col, 1.45)
    for u in (a - .11, a - .06, b + .06, b + .11):
        out.append((dark, [W(u - .008, 34, n1), W(u + .008, 34, n1), W(u + .008, DOOR_H - 8, n1), W(u - .008, DOOR_H - 8, n1)]))
    for u0, u1 in ((a - .03, a - .012), (b + .012, b + .03)):
        out.append((light, [W(u0, 26, n1), W(u1, 26, n1), W(u1, DOOR_H + 4, n1), W(u0, DOOR_H + 4, n1)]))
    out.append((light, [W(a - .03, DOOR_H + 2, n1), W(b + .03, DOOR_H + 2, n1), W(b + .03, DOOR_H + 5, n1), W(a - .03, DOOR_H + 5, n1)]))
    return out


def polys_layer(polys, pad=2):
    """Render (colour, polygon) pieces onto their own transparent surface -> (surface, (x, y))."""
    xs = [p[0] for _, poly in polys for p in poly]
    ys = [p[1] for _, poly in polys for p in poly]
    x0, y0 = math.floor(min(xs)) - pad, math.floor(min(ys)) - pad
    w, h = math.ceil(max(xs)) - x0 + pad, math.ceil(max(ys)) - y0 + pad
    surf = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    surf.fill((0, 0, 0, 0))
    for c, poly in polys:
        pygame.draw.polygon(surf, (*c, 255), [(x - x0, y - y0) for x, y in poly])
    return surf, (x0, y0)
