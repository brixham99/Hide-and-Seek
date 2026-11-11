#!/usr/bin/env python3
"""Headless checks for the Zen Station front end (zen.py, title.py, zenbuild.py).

Drives the title screen, the game and the quit hold through a synthetic
gamepad and the keyboard, and saves screenshots.

    SDL_VIDEODRIVER=dummy python3 tools/zen_test.py [shots_dir]
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

import game  # noqa: E402
import house  # noqa: E402
import pads  # noqa: E402
import screenfit  # noqa: E402
import zen  # noqa: E402
import zenbuild  # noqa: E402

SHOTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "shots")
FAIL = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAIL.append(what)


def btn(pad, b, down=True):
    t = pygame.CONTROLLERBUTTONDOWN if down else pygame.CONTROLLERBUTTONUP
    return pygame.event.Event(t, instance_id=pad.instance_id, button=b)


def axis(pad, a, v):
    return pygame.event.Event(pygame.CONTROLLERAXISMOTION, instance_id=pad.instance_id, axis=a, value=v)


def run(app, n=1, events=()):
    app.frame(1 / 60, list(events))
    for _ in range(n - 1):
        app.frame(1 / 60, [])


def make_app(pad="xbox"):
    args = zen.parse_args(["--pad", pad] if pad else [])
    args.headless = True              # no real pads scanned, no background build
    view = screenfit.open_display((zen.WIN_W, zen.WIN_H), fullscreen=False, headless=True)
    return zen.App(game.Game, args, view)


def main():
    os.makedirs(SHOTS, exist_ok=True)
    check(screenfit.fullscreen_requested(False, "1"), "ZENSTATION=1 asks for full screen")
    check(not screenfit.fullscreen_requested(False, ""), "without ZENSTATION the game stays windowed")
    if zenbuild.needed():
        check(zenbuild.main([]) == 0, "room images build")
    check(not zenbuild.needed(), "room cache is current (CACHE_REV)")
    pygame.init()
    app = make_app("xbox")
    pad = app.pads.player(0)
    run(app, 2)
    check(app.mode == "title", "starts on the title screen")
    run(app, 2, [btn(pad, pads.A)])
    check(app.mode == "play", "A on the title starts the game")
    g = app.game
    run(app, 2, [btn(pad, pads.A, False)])
    x0, y0, f0 = g.x, g.y, g.facing
    run(app, 40, [axis(pad, pads.AXIS_LEFTY, -32000)])
    check((g.x, g.y) != (x0, y0), f"left stick up walks Archie ({x0:.2f},{y0:.2f}) -> ({g.x:.2f},{g.y:.2f})")
    run(app, 2, [axis(pad, pads.AXIS_LEFTY, 0)])
    run(app, 2, [btn(pad, pads.DPAD_RIGHT)])
    check(g.facing != f0, f"D-pad right turns ({f0} -> {g.facing})")
    run(app, 2, [btn(pad, pads.DPAD_RIGHT, False)])
    run(app, 2, [btn(pad, pads.Y)])
    check(g.flipped, "Y looks from the other side (like V)")
    run(app, 30, [btn(pad, pads.Y, False)])
    run(app, 2, [btn(pad, pads.B)])
    check(app.mode == "title", "B goes back to the title")
    run(app, 2, [btn(pad, pads.B, False), btn(pad, pads.START)])
    check(app.mode == "play", "Start also starts")
    run(app, 2, [btn(pad, pads.START, False)])
    run(app, 30, [btn(pad, pads.BACK)])
    check(app.running, "a short press of Back does not quit")
    run(app, 40)
    check(not app.running, "holding Back about a second quits (back to Zen Station)")

    app = make_app(None)
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    check(app.mode == "play", "Enter starts")
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    check(app.mode == "title" and app.running, "Esc in play goes to the title")
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    check(not app.running, "Esc on the title quits")

    # the Drawing Room with Myrtle on her bed, for the screenshot
    app = make_app("xbox")
    app.enter_play()
    g = app.game
    g.room, g.x, g.y, g.facing = "drawing", 3.6, 4.4, "W"
    g.view = house.view_for(g.room, g.x)
    g.trans = None
    run(app, 3)
    pygame.image.save(app.surf, os.path.join(SHOTS, "zen_hs_game_drawing.png"))
    print("RESULT:", "all OK" if not FAIL else f"FAILURES: {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
