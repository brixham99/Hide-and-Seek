"""Project painted orthographic face sheets onto Hide and Seek furniture.

Same idea as Haunted Mansion's tools/iso_box.py: a front, side and top image
are affine-mapped onto the three visible faces of a box. Drawing still goes
through house_common (P, box occluders, flip z-buffer and near-wall ghosting)
so footprints, collisions, depth sorting and both cameras stay unchanged.

Face sheets live in rooms/art/faces/<kind>_{front,side,top,back}.png and are
built by rooms/art/make_faces.py. Warped sprites are memoised for the rest
of the current room build.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

import house_common as hc
from house_common import P, box, shade

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DIR = os.path.join(HERE, "art", "faces")
_FACES = {}
_WARP = {}


def load(name):
    if name not in _FACES:
        path = os.path.join(FACE_DIR, name + ".png")
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        _FACES[name] = Image.open(path).convert("RGBA")
    return _FACES[name]


def kind_sheets(kind):
    """Return {front, side, top, back} images; missing back uses a darker front."""
    out = {}
    for role in ("front", "side", "top", "back"):
        name = f"{kind}_{role}"
        path = os.path.join(FACE_DIR, name + ".png")
        if os.path.exists(path):
            out[role] = load(name)
    if "back" not in out and "front" in out:
        a = np.asarray(out["front"]).astype(np.float32)
        a[..., :3] *= 0.78
        out["back"] = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    if "side" not in out and "front" in out:
        out["side"] = out["front"]
    if "top" not in out and "front" in out:
        out["top"] = out["front"]
    return out


def _role_for_y(front, y_is_south):
    if front == "S":
        return "front" if y_is_south else "back"
    if front == "N":
        return "front" if not y_is_south else "back"
    return "side"


def _role_for_x(front, x_is_east):
    if front == "E":
        return "front" if x_is_east else "back"
    if front == "W":
        return "front" if not x_is_east else "back"
    return "side"


def paint_box(x0, y0, x1, y1, z0, z1, kind, front="S", col=(90, 70, 50), shade_k=None, faces="xyz"):
    """Textured box on the existing footprint. `front` is the face with the
    front sheet (S/N/E/W in house axes)."""
    sheets = kind_sheets(kind)
    box(x0, y0, x1, y1, z0, z1, col, top=shade(col, 1.04), ol=False, faces=faces)
    y_face, x_face = (y0, x0) if hc.FLIP else (y1, x1)
    sk = shade_k or {"y": 1.0, "x": 0.88, "z": 1.06}
    # +y / -y face
    y_tex = sheets.get(_role_for_y(front, y_face == y0))
    if y_tex is not None and "y" in faces:
        A = P(x0, y_face, z1)
        B = P(x1, y_face, z1)
        C = P(x0, y_face, z0)
        D = P(x1, y_face, z0)
        paint_quad(y_tex, A, B, C, sk["y"], D=D)
    # +x / -x face
    x_tex = sheets.get(_role_for_x(front, x_face == x0))
    if x_tex is not None and "x" in faces:
        A = P(x_face, y1, z1)
        B = P(x_face, y0, z1)
        C = P(x_face, y1, z0)
        D = P(x_face, y0, z0)
        paint_quad(x_tex, A, B, C, sk["x"], D=D)
    # top
    z_tex = sheets.get("top")
    if z_tex is not None and "z" in faces:
        A = P(x0, y0, z1)
        B = P(x1, y0, z1)
        C = P(x0, y1, z1)
        D = P(x1, y1, z1)
        paint_quad(z_tex, A, B, C, sk["z"], D=D)


def paint_quad(tex, A, B, C, shade=1.0, pad=3, D=None):
    """Map `tex` onto the parallelogram A, B, C (image origin, +u, +v)."""
    A_pt, B_pt, C_pt = A, B, C
    A = np.array(A, dtype=np.float64)
    B = np.array(B, dtype=np.float64)
    C = np.array(C, dtype=np.float64)
    Dn = B + C - A
    D_pt = D if D is not None else (float(Dn[0]), float(Dn[1]))
    pts = [A_pt, B_pt, D_pt, C_pt]
    if hc._flip_draw() and hc.FLIP:
        _paint_quad_z(tex, A, B, C, Dn, pts, shade)
        if hc._AUDIT is not None:
            hc._AUDIT.drawn(pts, hc._near_plane(pts) and hc._fg_surf is not None)
        return
    layer = _warp(tex, A, B, C, shade, pad)
    if layer is None:
        return
    if hc._flip_draw() and not hc._on_far_wall(pts):
        _blit_z(layer[0], layer[1], pts)
    else:
        hc.screen.blit(layer[0], layer[1])
    if hc._AUDIT is not None:
        hc._AUDIT.drawn(pts, False)


def _blit_z(surf, at, pts):
    """Blit a warped face sheet through the usual view's z-buffer: only the
    pixels in front of what is already drawn land, and they write depth."""
    import pygame
    infs = [hc._pinf.get(p) for p in pts]
    if any(i is None for i in infs):
        hc.screen.blit(surf, at)
        return
    W, H = hc._zbuf.shape
    x0, y0 = at
    w, h = surf.get_size()
    cx0, cy0 = max(0, x0), max(0, y0)
    cx1, cy1 = min(W, x0 + w), min(H, y0 + h)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    gx = np.arange(cx0, cx1, dtype=np.float32)[:, None] + 0.5
    gy = np.arange(cy0, cy1, dtype=np.float32)[None, :] + 0.5
    # depth over the parallelogram from its first three corners (a plane)
    (ax, ay), (bx, by), (dx, dy) = pts[0], pts[1], pts[3]
    da, db, dd = infs[0][3], infs[1][3], infs[3][3]
    det = (bx - ax) * (dy - ay) - (by - ay) * (dx - ax)
    if abs(det) < 1e-6:
        hc.screen.blit(surf, at)
        return
    u = ((gx - ax) * (dy - ay) - (gy - ay) * (dx - ax)) / det
    v = ((bx - ax) * (gy - ay) - (by - ay) * (gx - ax)) / det
    depth = da + u * (db - da) + v * (dd - da)
    zb = hc._zbuf[cx0:cx1, cy0:cy1]
    ok = depth >= zb - 1e-4
    alpha = pygame.surfarray.pixels_alpha(surf)
    sub_a = alpha[cx0 - x0:cx1 - x0, cy0 - y0:cy1 - y0]
    keep = sub_a.copy()
    sub_a[~ok] = 0
    del sub_a, alpha
    hc.screen.blit(surf, at)
    alpha = pygame.surfarray.pixels_alpha(surf)
    alpha[cx0 - x0:cx1 - x0, cy0 - y0:cy1 - y0] = keep          # the warp is cached: put it back
    del alpha
    m = ok & (keep > 128)
    zb[m] = depth[m]


def _warp(tex, A, B, C, shade, pad):
    """Affine-warp tex into a tight pygame surface. Cached by size."""
    tex = tex.convert("RGBA")
    w, h = tex.size
    D = B + C - A
    xs = [A[0], B[0], C[0], D[0]]
    ys = [A[1], B[1], C[1], D[1]]
    minx = int(math.floor(min(xs))) - 1
    miny = int(math.floor(min(ys))) - 1
    maxx = int(math.ceil(max(xs))) + 1
    maxy = int(math.ceil(max(ys))) + 1
    W, H = maxx - minx, maxy - miny
    if W < 2 or H < 2:
        return None
    key = (id(tex), round(A[0], 1), round(A[1], 1), round(B[0], 1), round(B[1], 1),
           round(C[0], 1), round(C[1], 1), round(shade, 3), W, H)
    if key in _WARP:
        return _WARP[key]
    a = np.asarray(tex).astype(np.float32)
    if shade != 1.0:
        a[..., :3] *= shade
    a = np.pad(a, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    src = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    As = A - (minx, miny)
    Bs = B - (minx, miny)
    Cs = C - (minx, miny)
    M = np.column_stack([(Bs - As) / max(1, w), (Cs - As) / max(1, h)])
    if abs(np.linalg.det(M)) < 1e-9:
        return None
    Mi = np.linalg.inv(M)
    off = -Mi @ As + pad
    warped = src.transform((W, H), Image.AFFINE,
                           (Mi[0, 0], Mi[0, 1], off[0], Mi[1, 0], Mi[1, 1], off[1]),
                           Image.BICUBIC)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(
        [tuple(As), tuple(Bs), tuple(Bs + Cs - As), tuple(Cs)], fill=255)
    la = np.asarray(warped).copy()
    la[..., 3] = (la[..., 3].astype(np.uint16) * np.asarray(mask) // 255).astype(np.uint8)
    raw = np.ascontiguousarray(la)
    surf = pygame_from_rgba(raw)
    item = (surf, (minx, miny))
    _WARP[key] = item
    return item


def pygame_from_rgba(arr):
    import pygame
    h, w = arr.shape[:2]
    return pygame.image.frombuffer(arr.tobytes(), (w, h), "RGBA").convert_alpha()


def _paint_quad_z(tex, A, B, C, D, pts, shade):
    """Textured fill that honours the opposite-view z-buffer and ghost layer."""
    near = hc._near_plane(pts) and hc._fg_surf is not None
    target = hc._fg_surf if near else hc.screen
    alpha = 36 if near else 255
    zwrite = not near
    tw, th = tex.size
    a = np.asarray(tex).astype(np.float32)
    if shade != 1.0:
        a[..., :3] *= shade
    # two triangles covering the parallelogram
    # A(0,0), B(tw,0), D(tw,th) and A(0,0), D(tw,th), C(0,th)
    uvs = (
        (A, B, D, (0, 0), (tw - 1, 0), (tw - 1, th - 1)),
        (A, D, C, (0, 0), (tw - 1, th - 1), (0, th - 1)),
    )
    for p0, p1, p2, uv0, uv1, uv2 in uvs:
        _tex_tri(target, tuple(p0), tuple(p1), tuple(p2),
                 uv0, uv1, uv2, a, alpha, zwrite)


def _tex_tri(target, a, b, c, uva, uvb, uvc, tex, alpha, zwrite):
    infs = [hc._pinf.get(p) for p in (a, b, c)]
    xs, ys = (a[0], b[0], c[0]), (a[1], b[1], c[1])
    if hc._zbuf is None or any(i is None for i in infs):
        # fall back to a flat blit of this triangle's bbox warp
        return
    x0 = max(0, int(math.floor(min(xs))))
    y0 = max(0, int(math.floor(min(ys))))
    x1 = min(hc._zbuf.shape[0], int(math.ceil(max(xs))) + 1)
    y1 = min(hc._zbuf.shape[1], int(math.ceil(max(ys))) + 1)
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
    ds = [i[3] for i in infs]
    depth = (w0 * ds[0] + w1 * ds[1] + w2 * ds[2]) / area
    sub = hc._zbuf[x0:x1, y0:y1]
    m &= depth >= sub - 1e-4
    if not np.any(m):
        return
    if zwrite:
        sub[m] = depth[m]
    u = (w0 * uva[0] + w1 * uvb[0] + w2 * uvc[0]) / area
    v = (w0 * uva[1] + w1 * uvb[1] + w2 * uvc[1]) / area
    th, tw = tex.shape[:2]
    ui = np.clip(np.rint(u).astype(np.int32), 0, tw - 1)
    vi = np.clip(np.rint(v).astype(np.int32), 0, th - 1)
    samp = tex[vi, ui]
    rgb = pygame_pixels(target)
    am = m & (samp[..., 3] > 8)
    rgb[x0:x1, y0:y1][am] = samp[..., :3][am].astype(np.uint8)
    del rgb
    if target.get_masks()[3] or (target.get_flags() & 0x00010000):
        import pygame
        if target.get_flags() & pygame.SRCALPHA or target.get_masks()[3]:
            aa = pygame.surfarray.pixels_alpha(target)
            src_a = (samp[..., 3] * (alpha / 255.0)).astype(np.uint8)
            aa[x0:x1, y0:y1][am] = src_a[am]
            del aa


def pygame_pixels(target):
    import pygame
    return pygame.surfarray.pixels3d(target)
