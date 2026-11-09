#!/usr/bin/env python3
"""Pre-render every room view from the room drawing code in rooms/ into
cache/<view>_bg.png (floor, walls, furniture) and cache/<view>_fg.png (the ghost
near walls, drawn over Archie), plus cache/<view>.json (screen origin) and
cache/<view>_depth.npy (occluder depth, view-local x+y, 0 = empty).

Internal doors are removed on the fly (door leaves dropped, ghost door frames
dropped, closed internal doors on back walls replaced by open doorways); the room
scripts themselves still render the original mock-ups if run on their own.

Rooms are built in this process. Each room module binds its own size at import,
and build() pushes that size back into house_common before drawing, so they no
longer need a subprocess each.

    python build_rooms.py            # all views
    python build_rooms.py hall       # one view
"""
import importlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "rooms")
CACHE = os.path.join(HERE, "cache")
VIEWS = {"hall": "mock_hall", "sitting": "mock_sitting_room", "drawing": "mock_drawing_room",
         "kitchen": "mock_kitchen", "dining": "mock_dining", "boot": "mock_boot_room",
         "utility": "mock_utility", "office": "mock_office", "wc": "mock_wc"}

if MOCK not in sys.path:
    sys.path.insert(0, MOCK)


def build(view):
    sys.argv = [sys.argv[0], os.path.join(CACHE, "_unused.png")]   # non-empty ARGS: mocks skip their close-ups
    import pygame
    import house_common as hc
    mod = importlib.import_module(VIEWS[view])
    # the module captured RW/RD/OX/OY/screen at import; later rooms overwrite
    # house_common, so put this room's geometry back before drawing
    hc.init_room(mod.RW, mod.RD, ox=mod.OX, oy=mod.OY)
    mod.screen = hc.screen
    mod.OX, mod.OY, mod.RW, mod.RD = hc.OX, hc.OY, hc.RW, hc.RD

    saved = []

    def patch(obj, name, fn):
        saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, fn)

    fg = []

    def ghost(*a, **k):
        layer = pygame.Surface(hc.screen.get_size(), pygame.SRCALPHA)
        with hc.drawing_on(layer):
            saved_ghost(*a, **k)
        fg.append(layer)

    def finish(*a, **k):
        scaled = pygame.transform.smoothscale(hc.screen, (hc.WIN_W, hc.WIN_H))
        # smoothscale can come back with per-pixel alpha on macOS. The vignette
        # overlay is transparent in the middle; blitting it onto an alpha
        # surface stores that 0 and the floor is saved invisible.
        img = pygame.Surface((hc.WIN_W, hc.WIN_H), depth=24)
        img.blit(scaled, (0, 0))
        hc.vignette(img)
        pygame.image.save(img, os.path.join(CACHE, f"{view}_bg.png"))
        top = pygame.Surface((hc.WIN_W, hc.WIN_H), pygame.SRCALPHA)
        for layer in fg:
            top.blit(pygame.transform.smoothscale(layer, (hc.WIN_W, hc.WIN_H)), (0, 0))
        pygame.image.save(top, os.path.join(CACHE, f"{view}_fg.png"))
        depth = hc.raster_depth()
        np.save(os.path.join(CACHE, f"{view}_depth.npy"), np.clip(depth, 0, 1024).astype(np.float16))
        with open(os.path.join(CACHE, f"{view}.json"), "w") as f:
            json.dump({"OX": hc.OX, "OY": hc.OY, "RW": hc.RW, "RD": hc.RD}, f)
        print("built", view, f"({len(hc._occluders)} occluders)")
        return img

    def back_doorway(side, a, b, col):
        view_ = hc.exterior_layer({side: lambda s, rnd: hc.qz(0, -6, -4, 0, 12, col) if s == "W" else hc.qz(0, -4, -6, 12, 0, col)},
                                  haze=hc.shade(col, .6))
        hc.doorway_back(side, a, b, view_)

    saved_ghost = hc.ghost_near_walls
    try:
        patch(mod, "place_sprite", lambda *a, **k: None)
        patch(hc, "place_sprite", lambda *a, **k: None)
        patch(mod, "ghost_near_walls", ghost)
        patch(mod, "finish", finish)
        mod.CLOSE = os.path.join(CACHE, "_unused_closeup.png")   # never touch the mocks' own outputs
        if view != "dining":                       # the dining room's only near-wall door is the (external) French doors
            patch(hc.HMG, "door_frame_polys", lambda *a, **k: [])
            orig_pl = hc.HMG.polys_layer

            def polys_layer(polys):
                return orig_pl(polys) if polys else (pygame.Surface((1, 1), pygame.SRCALPHA), (0, 0))

            patch(hc.HMG, "polys_layer", polys_layer)
        if view == "boot":
            patch(mod, "kitchen_leaf", lambda *a, **k: None)
            patch(mod, "plank_door_face", lambda *a, **k: [])          # the WC door on the ghost wall
        elif view in ("office", "utility"):
            patch(mod, "door_leaf", lambda *a, **k: None)
        elif view == "wc":
            import glimpses
            patch(mod, "door", lambda: hc.back_opening("W", *mod.DOOR, glimpses.boot_from_wc))
        elif view == "hall":
            patch(mod, "drawing_door_polys", lambda: [])
        mod.main()
    finally:
        for obj, name, old in reversed(saved):
            setattr(obj, name, old)


def build_all(quiet=False):
    """Render every view in this process (room globals are restored per view)."""
    os.makedirs(CACHE, exist_ok=True)
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    for v in VIEWS:
        build(v)
    with open(os.path.join(CACHE, "REV"), "w") as f:
        f.write(CACHE_REV + "\n")


# Bump when saved room images must be rebuilt (macOS alpha-safe canvas).
CACHE_REV = "4"


def cache_ok():
    rev = os.path.join(CACHE, "REV")
    if not os.path.exists(rev) or open(rev).read().strip() != CACHE_REV:
        return False
    return all(os.path.exists(os.path.join(CACHE, f"{v}{ext}"))
               for v in VIEWS for ext in ("_bg.png", "_fg.png", ".json", "_depth.npy"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in VIEWS:
        os.makedirs(CACHE, exist_ok=True)
        build(sys.argv[1])
    else:
        build_all("-q" in sys.argv)
