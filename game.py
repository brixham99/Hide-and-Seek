#!/usr/bin/env python3
"""Hide and Seek - walkable prototype of the downstairs.

Archie walks the house with Haunted Mansion's tank controls: Left/Right (A/D)
turn a quarter turn, Up/Down (W/S) walk forward/back. V looks at the room from
the opposite side. Walking stays camera-relative: Up always goes away from the
camera, so the same key still moves him the way he is facing on screen.
A gamepad works too
(stick or d-pad). Esc quits. Rooms are the mock-up renders (build_rooms.py);
every internal doorway is open, and walking through one switches the view
(the Kitchen and Dining Room slide at the beam). The room images are built
into cache/ automatically on the first run.

    python3 game.py
"""
import json
import math
import os

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import numpy as np  # noqa: E402
import pygame  # noqa: E402

import house  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
HM_CHARS = os.path.join(HERE, "assets", "characters")
WIN_W, WIN_H = 1280, 720
HW, HH = 56, 28
SPEED = 3.0                      # tiles/s, as Haunted Mansion's PLAYER_SPEED
TURN_S = 0.22                    # a quarter turn; held keys repeat at this pace
FACING_ORDER = ("E", "S", "W", "N")          # clockwise on screen (Right = +1)
DIRS = {"E": (1, 0), "S": (0, 1), "W": (-1, 0), "N": (0, -1)}   # engine facings: E = +x (screen SE) ...
SPRITE = {"N": "ne", "E": "se", "S": "sw", "W": "nw"}
FADE_S, SLIDE_S = 0.35, 0.55
SLIDE_NUDGE = 0.30               # how far Archie will sidestep to pass a corner, tiles


def _font(size, bold=False):
    for name in ("liberation serif", "dejavuserif", "times new roman", "georgia", "freeserif"):
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size + 10)


def load_views():
    import build_rooms
    if not build_rooms.cache_ok():
        print("Building the room images (first run only)...")
        build_rooms.build_all(quiet=True)
    views = {}
    names = ("hall", "sitting", "drawing", "kitchen", "dining", "boot", "utility", "office", "wc",
             "landing", "corridor")
    for v in names:
        for suffix in ("", "_r"):
            key = v + suffix
            p = os.path.join(CACHE, f"{key}_bg.png")
            with open(os.path.join(CACHE, f"{key}.json")) as f:
                meta = json.load(f)
            depth_path = os.path.join(CACHE, f"{key}_depth.npy")
            depth = np.load(depth_path) if os.path.exists(depth_path) else None
            views[key] = dict(bg=pygame.image.load(p).convert(),
                              fg=pygame.image.load(os.path.join(CACHE, f"{key}_fg.png")).convert_alpha(),
                              depth=depth, **meta)
    return views


def load_archie():
    with open(os.path.join(HM_CHARS, "archie_walk.json")) as f:
        meta = json.load(f)
    fw, fh = meta["size"]
    stand, walk = {}, {}
    for k in ("se", "sw", "nw", "ne"):
        stand[k] = pygame.image.load(os.path.join(HM_CHARS, f"archie_{k}.png")).convert_alpha()
        sheet = pygame.image.load(os.path.join(HM_CHARS, f"archie_{k}_walk.png")).convert_alpha()
        walk[k] = [sheet.subsurface((i * fw, 0, fw, fh)).copy() for i in range(meta["frames"])]
    return stand, walk, meta


def _fg_crop(fg):
    """Tight sprite of the ghost walls, and where it sits on the frame."""
    # array_alpha is [x, y]; a full-frame scan once per view at load
    alpha = pygame.surfarray.array_alpha(fg)
    cols = np.flatnonzero(alpha.any(axis=1))
    rows = np.flatnonzero(alpha.any(axis=0))
    if len(cols) == 0:
        return fg.subsurface((0, 0, 1, 1)).copy(), pygame.Rect(0, 0, 0, 0)
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    rect = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
    return fg.subsurface(rect).copy(), rect


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.views = load_views()
        self.stand, self.walk, self.meta = load_archie()
        self.font = _font(26, bold=True)
        self.small = _font(15)
        self.shadow = pygame.Surface((60, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (0, 0, 0, 80), self.shadow.get_rect())
        self.room, self.x, self.y, self.facing = "hall", 1.6, 1.2, "N"
        self.flipped = False          # True: camera on the opposite side of every room
        self.view = house.view_for(self.room, self.x)
        self.dist = 0.0
        self.moving = False
        self.turn_cd = 0.0
        self.trans = None            # (kind, t, from_surface, from_view, to_view)
        self.pad = None
        pygame.joystick.init()
        if pygame.joystick.get_count():
            self.pad = pygame.joystick.Joystick(0)
        self.log = []                # (room, view) changes, for the tests
        self._fg = {vid: _fg_crop(m["fg"]) for vid, m in self.views.items()}
        # 24-bit, no per-pixel alpha. On macOS the window surface has alpha, and
        # blitting the ghost walls (mostly transparent) straight onto it zeroes
        # the room. Dirty display.update also drops every pixel outside the
        # rectangle, because that back buffer is not kept. Compose here, then
        # one opaque blit and a full flip.
        self._layers = [pygame.Surface((WIN_W, WIN_H), depth=24) for _ in range(2)]
        self.frame = self._layers[0]
        self._labels = {}
        self._hint = self._make_hint()

    # ---------------------------------------------------------------- input
    def read_input(self):
        k = pygame.key.get_pressed()
        turn = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
        move = (k[pygame.K_UP] or k[pygame.K_w]) - (k[pygame.K_DOWN] or k[pygame.K_s])
        if self.pad is not None:
            ax = self.pad.get_axis(0) if self.pad.get_numaxes() > 0 else 0
            ay = self.pad.get_axis(1) if self.pad.get_numaxes() > 1 else 0
            hx, hy = self.pad.get_hat(0) if self.pad.get_numhats() else (0, 0)
            turn = turn or (1 if ax > .5 or hx > 0 else -1 if ax < -.5 or hx < 0 else 0)
            move = move or (1 if ay < -.5 or hy > 0 else -1 if ay > .5 or hy < 0 else 0)
        return turn, move

    # ---------------------------------------------------------------- update
    def update(self, dt, turn, move):
        if self.trans:
            kind, t, *rest = self.trans
            t += dt / (SLIDE_S if kind == "slide" else FADE_S)
            self.trans = None if t >= 1 else (kind, t, *rest)
        self.turn_cd = max(0.0, self.turn_cd - dt)
        if turn and self.turn_cd <= 0:
            i = FACING_ORDER.index(self.facing)
            self.facing = FACING_ORDER[(i + turn) % 4]
            self.turn_cd = TURN_S
        if not turn:
            self.turn_cd = 0.0
        self.moving = False
        if move:
            dx, dy = DIRS[self.facing]
            if self.flipped:             # screen-up stays "away from the camera"
                dx, dy = -dx, -dy
            step = SPEED * dt * move
            ox, oy = self.x, self.y
            if self._slide(dx * step, dy * step):
                self.dist += math.hypot(self.x - ox, self.y - oy)
                self.moving = True
            cr = house.crossing(self.room, self.x, self.y)
            if cr:
                self.change_room(*cr)
            else:
                cr = house.stair_crossing(self.room, self.x, self.y)
                if cr:
                    self.change_room(*cr)
        v = house.view_for(self.room, self.x, self.view)
        if v != self.view:                                   # the beam: slide
            self.trans = ("slide", 0.0, None, self.view, v)
            self.view = v
            self.log.append((self.room, v[0]))

    def _slide(self, dx, dy):
        """Move by (dx, dy). If a corner is in the way, sidestep and carry on
        instead of sticking; a wall face still stops him."""
        room, x, y = self.room, self.x, self.y
        if house.free(room, x + dx, y + dy):
            self.x, self.y = x + dx, y + dy
            return True
        along_x = abs(dx) >= abs(dy)
        n = 0.025
        while n <= SLIDE_NUDGE + 1e-9:
            for s in (n, -n):
                ox = 0.0 if along_x else s
                oy = s if along_x else 0.0
                if house.free(room, x + ox, y + oy) and house.free(room, x + dx + ox, y + dy + oy):
                    self.x, self.y = x + dx + ox, y + dy + oy
                    return True
            n += 0.025
        lo, hi = 0.0, 1.0
        for _ in range(7):
            mid = (lo + hi) * 0.5
            if house.free(room, x + dx * mid, y + dy * mid):
                lo = mid
            else:
                hi = mid
        if lo > 0.05:
            self.x, self.y = x + dx * lo, y + dy * lo
            return True
        return False

    def change_room(self, room, x, y):
        snap = pygame.Surface((WIN_W, WIN_H), 0, 24)
        snap.blit(self.screen, (0, 0))
        old = self.view
        self.room, self.x, self.y = room, x, y
        self.view = house.view_for(room, x)
        self.trans = ("fade", 0.0, snap, old, self.view)
        self.log.append((room, self.view[0]))

    # ---------------------------------------------------------------- drawing
    def vid(self, view):
        return view[0] + ("_r" if self.flipped else "")

    def to_screen(self, view, x, y, z=0.0):
        m = self.views[self.vid(view)]
        lx = x - view[1]
        if m.get("flip"):
            lx, y = m["RW"] - lx, m["RD"] - y
        return m["OX"] + (lx - y) * HW, m["OY"] + (lx + y) * HH - z

    def _occlude(self, img, dest, view):
        """Punch the sprite where a closer solid covers it. `dest` is the
        sprite's top-left on the unshifted view."""
        depth = self.views[self.vid(view)].get("depth")
        flipped = self.views[self.vid(view)].get("flip")
        if depth is None:
            return img
        w, h = img.get_size()
        x0 = max(0, dest[0])
        y0 = max(0, dest[1])
        x1 = min(WIN_W, dest[0] + w)
        y1 = min(WIN_H, dest[1] + h)
        if x1 <= x0 or y1 <= y0:
            return img
        sub = depth[x0:x1, y0:y1]
        # Archie stands a fraction in front of his back foot so a surface he
        # is touching doesn't swallow him
        lx = self.x - view[1]
        thr = np.float16(lx + self.y - 0.04)
        # normal view: closer solids have a larger x+y. opposite view: smaller.
        if flipped:
            hide = (sub > 0) & (sub < thr)
            if not np.any(hide):
                return img
        elif np.max(sub) <= thr:
            return img
        else:
            hide = sub > thr
        out = img.copy()
        alpha = pygame.surfarray.pixels_alpha(out)
        sx, sy = x0 - dest[0], y0 - dest[1]
        region = alpha[sx:sx + (x1 - x0), sy:sy + (y1 - y0)]
        region[hide] = 0
        del alpha
        return out

    def draw_archie(self, surf, view):
        gx, gy = self.to_screen(view, self.x, self.y)
        k = SPRITE[self.facing]
        ax, ay = self.meta["facings"][k]["anchor"]
        if self.moving:
            n = self.meta["frames"]
            img = self.walk[k][int(self.dist / self.meta["cycle_tiles"] * n) % n]
        else:
            img = self.stand[k]
        body = (round(gx - ax), round(gy - ay))
        shade_at = (round(gx - 30), round(gy - 12))
        surf.blit(self._occlude(self.shadow, shade_at, view), shade_at)
        surf.blit(self._occlude(img, body, view), body)
        rect = pygame.Rect(body, img.get_size()).union(pygame.Rect(shade_at, self.shadow.get_size()))
        return rect.inflate(2, 2).clip(pygame.Rect(0, 0, WIN_W, WIN_H))

    def _blit_fg(self, surf, view, dest_rect=None):
        crop, fr = self._fg[self.vid(view)]
        if fr.w == 0:
            return
        if dest_rect is None:
            surf.blit(crop, fr.topleft)
            return
        hit = dest_rect.clip(fr)
        if hit.w == 0:
            return
        src = pygame.Rect(hit.x - fr.x, hit.y - fr.y, hit.w, hit.h)
        surf.blit(crop, hit.topleft, src)

    def _paint_view(self, target, view, player=True):
        """One room onto a 24-bit surface: background, Archie, ghost walls."""
        m = self.views[self.vid(view)]
        target.blit(m["bg"], (0, 0))
        if player:
            self.draw_archie(target, view)
        self._blit_fg(target, view)

    def _hud_on(self, target):
        name = house.label(self.room, self.view)
        way = "north-west" if self.flipped else "south-east"
        label = self._make_label(name + "  ·  " + way)
        target.blit(label, (16, 14))
        hint_at = (WIN_W - self._hint.get_width() - 16, WIN_H - self._hint.get_height() - 14)
        target.blit(self._hint, hint_at)

    def _flip(self):
        """Opaque copy of the finished frame. Never a per-pixel-alpha blit."""
        self._hud_on(self.frame)
        self.screen.blit(self.frame, (0, 0))
        pygame.display.flip()

    def _make_label(self, name):
        if name in self._labels:
            return self._labels[name]
        txt = self.font.render(name, True, (248, 240, 220))
        sh = self.font.render(name, True, (18, 12, 14))
        w = txt.get_width() + 36
        h = txt.get_height() + 20
        box = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(box, (18, 14, 16, 188), box.get_rect(), border_radius=9)
        pygame.draw.rect(box, (206, 168, 96, 220), pygame.Rect(12, h - 8, w - 24, 2))
        box.blit(sh, (19, 8))
        box.blit(txt, (18, 7))
        self._labels[name] = box
        return box

    def _make_hint(self):
        way = "north-west" if self.flipped else "south-east"
        text = f"Left / Right turn    Up / Down walk    V looking {way}    Esc quits"
        txt = self.small.render(text, True, (214, 204, 178))
        sh = self.small.render(text, True, (12, 10, 12))
        box = pygame.Surface((txt.get_width() + 4, txt.get_height() + 2), pygame.SRCALPHA)
        box.blit(sh, (2, 1))
        box.blit(txt, (0, 0))
        return box

    def toggle_view(self):
        """Look at every room from the opposite side. The choice sticks when
        Archie walks through a door, so the house doesn't spin under him."""
        if self.trans:
            return
        snap = pygame.Surface((WIN_W, WIN_H), 0, 24)
        snap.blit(self.screen, (0, 0))
        self.flipped = not self.flipped
        self._hint = self._make_hint()
        self.trans = ("fade", 0.0, snap, self.view, self.view)

    def draw_view(self, view, offset=(0, 0), alpha=255, player=True):
        """Paint one view into the 24-bit frame (used by the transition below)."""
        layer = self._layers[1]
        layer.set_alpha(None)
        layer.fill((8, 8, 9))
        self._paint_view(layer, view, player=player)
        layer.set_alpha(None if alpha >= 255 else alpha)
        self.frame.blit(layer, offset)
        if alpha < 255:
            layer.set_alpha(None)

    def draw(self):
        self.frame.set_alpha(None)
        self.frame.fill((8, 8, 9))
        if self.trans and self.trans[0] == "slide":
            _, t, _, a, b = self.trans
            e = t * t * (3 - 2 * t)
            # the same world point sits at different screen spots in the two halves
            pa, pb = self.to_screen(a, self.x, self.y), self.to_screen(b, self.x, self.y)
            d = (pb[0] - pa[0], pb[1] - pa[1])
            self.draw_view(a, offset=(round(-d[0] * e), round(-d[1] * e)), player=False)
            self.draw_view(b, offset=(round(d[0] * (1 - e)), round(d[1] * (1 - e))), alpha=int(255 * e))
        elif self.trans and self.trans[0] == "fade":
            _, t, snap, a, b = self.trans
            self._paint_view(self.frame, b)
            snap.set_alpha(int(255 * (1 - t)))
            self.frame.blit(snap, (0, 0))
            snap.set_alpha(None)
        else:
            self._paint_view(self.frame, self.view)
        self._flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Hide and Seek")
    g = Game(screen)
    clock = pygame.time.Clock()
    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_v:
                g.toggle_view()
        g.update(dt, *g.read_input())
        g.draw()


if __name__ == "__main__":
    main()
