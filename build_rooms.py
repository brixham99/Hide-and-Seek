#!/usr/bin/env python3
"""Pre-render every room view from the room drawing code in rooms/ into
cache/<view>_bg.png (floor, walls, furniture) and cache/<view>_fg.png (the ghost
near walls, drawn over Archie), plus cache/<view>.json (screen origin).

Internal doors are removed on the fly (door leaves dropped, ghost door frames
dropped, closed internal doors on back walls replaced by open doorways); the room
scripts themselves still render the original mock-ups if run on their own.

    python build_rooms.py            # all views (one subprocess each)
    python build_rooms.py hall       # one view
"""
import importlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "rooms")
CACHE = os.path.join(HERE, "cache")
VIEWS = {"hall": "mock_hall", "sitting": "mock_sitting_room", "drawing": "mock_drawing_room",
         "kitchen": "mock_kitchen", "dining": "mock_dining", "boot": "mock_boot_room",
         "utility": "mock_utility", "office": "mock_office", "wc": "mock_wc"}


def build(view):
    sys.path.insert(0, MOCK)
    sys.argv = [sys.argv[0], os.path.join(CACHE, "_unused.png")]   # non-empty ARGS: mocks skip their close-ups
    import pygame
    import house_common as hc
    mod = importlib.import_module(VIEWS[view])
    noop = lambda *a, **k: None
    fg = []

    def ghost(*a, **k):
        layer = pygame.Surface(hc.screen.get_size(), pygame.SRCALPHA)
        with hc.drawing_on(layer):
            orig_ghost(*a, **k)
        fg.append(layer)

    def finish(*a, **k):
        img = pygame.transform.smoothscale(hc.screen, (hc.WIN_W, hc.WIN_H))
        hc.vignette(img)
        pygame.image.save(img, os.path.join(CACHE, f"{view}_bg.png"))
        top = pygame.Surface((hc.WIN_W, hc.WIN_H), pygame.SRCALPHA)
        for layer in fg:
            top.blit(pygame.transform.smoothscale(layer, (hc.WIN_W, hc.WIN_H)), (0, 0))
        pygame.image.save(top, os.path.join(CACHE, f"{view}_fg.png"))
        with open(os.path.join(CACHE, f"{view}.json"), "w") as f:
            json.dump({"OX": hc.OX, "OY": hc.OY, "RW": hc.RW, "RD": hc.RD}, f)
        print("built", view)
        return img

    def back_doorway(side, a, b, col):
        view_ = hc.exterior_layer({side: lambda s, rnd: hc.qz(0, -6, -4, 0, 12, col) if s == "W" else hc.qz(0, -4, -6, 12, 0, col)},
                                  haze=hc.shade(col, .6))
        hc.doorway_back(side, a, b, view_)

    orig_ghost = hc.ghost_near_walls
    mod.place_sprite = hc.place_sprite = noop
    mod.ghost_near_walls = ghost
    mod.finish = finish
    mod.CLOSE = os.path.join(CACHE, "_unused_closeup.png")   # never touch the mocks' own outputs
    if view != "dining":                       # the dining room's only near-wall door is the (external) French doors
        hc.HMG.door_frame_polys = lambda *a, **k: []
        orig_pl = hc.HMG.polys_layer
        hc.HMG.polys_layer = lambda polys: orig_pl(polys) if polys else (pygame.Surface((1, 1), pygame.SRCALPHA), (0, 0))
    if view == "drawing":                      # its east-wall door to the hall: an open doorway
        mod.panel_door_W = lambda a, b: back_doorway("W", a, b, (84, 54, 36))
    elif view == "boot":
        mod.kitchen_leaf = noop
        mod.plank_door_face = lambda *a, **k: []          # the WC door on the ghost wall
    elif view in ("office", "utility"):
        mod.door_leaf = noop
    elif view == "wc":
        mod.door = lambda: back_doorway("W", *mod.DOOR, (120, 112, 100))
    elif view == "hall":
        mod.drawing_door_polys = lambda: []
    mod.main()


def build_all(quiet=False):
    """Render every view, each in its own process (the room modules set up globals at import)."""
    os.makedirs(CACHE, exist_ok=True)
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    for v in VIEWS:
        subprocess.run([sys.executable, os.path.abspath(__file__), v], check=True, env=env, cwd=MOCK,
                       stdout=subprocess.DEVNULL if quiet else None)


def cache_ok():
    return all(os.path.exists(os.path.join(CACHE, f"{v}{ext}")) for v in VIEWS for ext in ("_bg.png", "_fg.png", ".json"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in VIEWS:
        os.makedirs(CACHE, exist_ok=True)
        build(sys.argv[1])
    else:
        build_all("-q" in sys.argv)
