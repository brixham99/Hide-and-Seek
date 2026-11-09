#!/usr/bin/env python3
"""Hide and Seek - walkable prototype of the downstairs.

Archie walks the house with Haunted Mansion's tank controls: Left/Right (A/D)
turn a quarter turn, Up/Down (W/S) walk forward/back. A gamepad works too
(stick or d-pad). Esc quits. Rooms are the mock-up renders (build_rooms.py);
every internal doorway is open, and walking through one switches the view
(the Kitchen and Dining Room slide at the beam). The room images are built
into cache/ automatically on the first run.

    python3 game.py
"""
import json
import math
import os
import sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
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


def load_views():
    import build_rooms
    if not build_rooms.cache_ok():
        print("Building the room images (first run only, a few seconds)...")
        build_rooms.build_all(quiet=True)
    views = {}
    for v in ("hall", "sitting", "drawing", "kitchen", "dining", "boot", "utility", "office", "wc"):
        p = os.path.join(CACHE, f"{v}_bg.png")
        with open(os.path.join(CACHE, f"{v}.json")) as f:
            meta = json.load(f)
        views[v] = dict(bg=pygame.image.load(p).convert(),
                        fg=pygame.image.load(os.path.join(CACHE, f"{v}_fg.png")).convert_alpha(), **meta)
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


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.views = load_views()
        self.stand, self.walk, self.meta = load_archie()
        self.font = pygame.font.Font(None, 40)
        self.small = pygame.font.Font(None, 24)
        self.shadow = pygame.Surface((60, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (0, 0, 0, 70), self.shadow.get_rect())
        self.room, self.x, self.y, self.facing = "hall", 1.6, 1.2, "N"
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
        self.moving = bool(move)
        if move:
            dx, dy = DIRS[self.facing]
            step = SPEED * dt * move
            nx, ny = self.x + dx * step, self.y + dy * step
            if house.free(self.room, nx, ny):
                self.x, self.y = nx, ny
                self.dist += abs(step)
            cr = house.crossing(self.room, self.x, self.y)
            if cr:
                self.change_room(*cr)
        v = house.view_for(self.room, self.x, self.view)
        if v != self.view:                                   # the beam: slide
            self.trans = ("slide", 0.0, None, self.view, v)
            self.view = v
            self.log.append((self.room, v[0]))

    def change_room(self, room, x, y):
        snap = self.screen.copy()
        old = self.view
        self.room, self.x, self.y = room, x, y
        self.view = house.view_for(room, x)
        self.trans = ("fade", 0.0, snap, old, self.view)
        self.log.append((room, self.view[0]))

    # ---------------------------------------------------------------- drawing
    def to_screen(self, view, x, y, z=0.0):
        m = self.views[view[0]]
        lx = x - view[1]
        return m["OX"] + (lx - y) * HW, m["OY"] + (lx + y) * HH - z

    def draw_view(self, view, offset=(0, 0), alpha=255, player=True):
        m = self.views[view[0]]
        layer = pygame.Surface((WIN_W, WIN_H)).convert()
        layer.blit(m["bg"], (0, 0))
        if player:
            self.draw_archie(layer, view)
        layer.blit(m["fg"], (0, 0))
        layer.set_alpha(alpha)
        self.screen.blit(layer, offset)

    def draw_archie(self, surf, view):
        gx, gy = self.to_screen(view, self.x, self.y)
        k = SPRITE[self.facing]
        ax, ay = self.meta["facings"][k]["anchor"]
        if self.moving:
            n = self.meta["frames"]
            img = self.walk[k][int(self.dist / self.meta["cycle_tiles"] * n) % n]
        else:
            img = self.stand[k]
        surf.blit(self.shadow, (gx - 30, gy - 12))
        surf.blit(img, (round(gx - ax), round(gy - ay)))

    def draw(self):
        self.screen.fill((8, 8, 9))
        if self.trans and self.trans[0] == "slide":
            _, t, _, a, b = self.trans
            e = t * t * (3 - 2 * t)
            # the same world point sits at different screen spots in the two halves
            pa, pb = self.to_screen(a, self.x, self.y), self.to_screen(b, self.x, self.y)
            d = (pb[0] - pa[0], pb[1] - pa[1])
            self.draw_view(a, (round(-d[0] * e), round(-d[1] * e)), player=False)
            self.draw_view(b, (round(d[0] * (1 - e)), round(d[1] * (1 - e))), alpha=int(255 * e))
        elif self.trans and self.trans[0] == "fade":
            _, t, snap, a, b = self.trans
            self.draw_view(b)
            snap.set_alpha(int(255 * (1 - t)))
            self.screen.blit(snap, (0, 0))
        else:
            self.draw_view(self.view)
        name = house.label(self.room, self.view)
        txt = self.font.render(name, True, (240, 230, 205))
        box = pygame.Surface((txt.get_width() + 28, 46), pygame.SRCALPHA)
        box.fill((10, 8, 12, 170))
        self.screen.blit(box, (16, 14))
        self.screen.blit(txt, (30, 24))
        hint = self.small.render("Left/Right turn, Up/Down walk, Esc quits", True, (170, 160, 140))
        self.screen.blit(hint, (WIN_W - hint.get_width() - 18, WIN_H - 30))


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
        g.update(dt, *g.read_input())
        g.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
