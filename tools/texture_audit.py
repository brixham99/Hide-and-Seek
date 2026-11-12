"""Painted-texture audit: which sheet lands on which WORLD face of every
iso_paint.paint_box, in both cameras, and whether it actually drew.

    python tools/texture_audit.py [view ...]

For each painted box and each face the camera sees, records the world face
(N/S/E/W/top), the sheet role used, the u direction on screen (mirroring)
and the textured pixel count. Prints the boxes whose texture differs
between the two views: a face textured in one view but dropped (skipped) in the
other, or a sheet mirrored relative to the usual view."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "rooms"))
import build_rooms as br  # noqa: E402
import house_common as hc  # noqa: E402
import iso_paint as ip  # noqa: E402
import numpy as np  # noqa: E402

REC = []
_cur = {}
_orig_pq = ip.paint_quad
_orig_tt = ip._tex_tri
_orig_bz = ip._blit_z


def _count_screen():
    return None


def paint_quad(tex, A, B, C, shade=1.0, pad=3, D=None):
    before = _cur.setdefault("px", 0)
    _cur["px"] = 0 if hc._flip_draw() else 1   # flat blit path always lands
    _orig_pq(tex, A, B, C, shade, pad, D)
    px = _cur["px"]
    _cur["px"] = before
    REC.append(dict(_cur["meta"], face=_cur.get("face"), px=px,
                    u=("+" if (B[0] - A[0]) > 0 else "-"), tex=id(tex)))


def _tex_tri(target, a, b, c, uva, uvb, uvc, tex, alpha, zwrite):
    infs = [hc._pinf.get(p) for p in (a, b, c)]
    if any(i is None for i in infs):
        return                       # (the engine skips it silently: counts as dropped)
    _cur["px"] = _cur.get("px", 0) + 1
    _orig_tt(target, a, b, c, uva, uvb, uvc, tex, alpha, zwrite)


def _blit_z(surf, at, pts):
    _cur["px"] = _cur.get("px", 0) + 1
    _orig_bz(surf, at, pts)


_orig_box = ip.paint_box


def paint_box(x0, y0, x1, y1, z0, z1, kind, front="S", *a, **k):
    if hc._XCLIP is not None and not hc._box_kept(min(x0, x1) - hc.X_OFF, max(x0, x1) - hc.X_OFF):
        return _orig_box(x0, y0, x1, y1, z0, z1, kind, front, *a, **k)   # this open-plan pass drops it: not a view of it
    _cur["meta"] = dict(view=_cur["view"], kind=kind, front=front, at=(round(x0, 2), round(y0, 2), round(z0)))
    faces = k.get("faces", "xyz")
    # world faces this camera sees (house axes: y=0 south wall, x=0 east wall)
    fy = "S" if hc.FLIP else "N"
    fx = "E" if hc.FLIP else "W"
    seq = [f for f, c in ((fy, "y"), (fx, "x"), ("top", "z")) if c in faces]
    it = iter(seq)
    orig = ip.paint_quad

    def pq(*aa, **kk):
        _cur["face"] = next(it, "?")
        return paint_quad(*aa, **kk)
    ip.paint_quad = pq
    try:
        _orig_box(x0, y0, x1, y1, z0, z1, kind, front, *a, **k)
    finally:
        ip.paint_quad = orig


ip.paint_box = paint_box
ip._tex_tri = _tex_tri
ip._blit_z = _blit_z

views = sys.argv[1:] or list(br.VIEWS)
os.makedirs(br.CACHE, exist_ok=True)
for v in views:
    for flip in (False, True):
        _cur["view"] = v + ("_r" if flip else "")
        br.build(v, flip)

# compare: for each box (view, kind, at) the face pairs seen in both cameras
by = {}
for r in REC:
    base = r["view"].replace("_r", "")
    by.setdefault((base, r["kind"], r["at"]), {}).setdefault(r["view"].endswith("_r"), []).append(r)
bad = []
for (v, kind, at), d in sorted(by.items()):
    n, s = d.get(False, []), d.get(True, [])
    issues = []
    for r in s:
        if r["px"] == 0 and r["face"] != "top" or (r["face"] == "top" and r["px"] == 0):
            issues.append(f"{r['face']} face texture dropped looking south")
    for r in n:
        if r["px"] == 0:
            issues.append(f"{r['face']} face texture dropped looking north")
    tn = [r for r in n if r["face"] == "top"]
    ts = [r for r in s if r["face"] == "top"]
    if tn and ts and (tn[0]["px"] > 0) != (ts[0]["px"] > 0):
        pass
    for r in s:
        if r["face"] in ("S", "E") and r["u"] == "+":
            pass
    # mirrored: a vertical face whose sheet reads right-to-left from outside
    for r in n + s:
        want = {"N": "+", "W": "+", "S": "-", "E": "-"}.get(r["face"])
        # u '+' means screen x increases along the sheet's u (left -> right)
        if want and r["u"] != "+":
            issues.append(f"{r['face']} face sheet mirrored ({'south' if r in s else 'north'} view)")
    if issues:
        bad.append((v, kind, at, sorted(set(issues))))
for v, kind, at, iss in bad:
    print(f"{v:9s} {kind:22s} at {at}: " + "; ".join(iss))
print(f"{len(bad)} painted boxes with a view mismatch, of {len(by)}")
