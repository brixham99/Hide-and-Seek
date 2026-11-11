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
    check(app.choice == "archie", "Archie is chosen to begin with")
    shot_a = pygame.surfarray.array3d(app.surf).copy()
    run(app, 2, [btn(pad, pads.DPAD_RIGHT)])
    check(app.choice == "holly", "D-pad right on the title chooses Holly")
    run(app, 2, [btn(pad, pads.DPAD_RIGHT, False)])
    run(app, 2, [btn(pad, pads.DPAD_RIGHT)])
    check(app.choice == "holly", "right again stays on Holly (no wrap)")
    run(app, 2, [btn(pad, pads.DPAD_RIGHT, False), btn(pad, pads.DPAD_LEFT)])
    check(app.choice == "archie", "D-pad left chooses Archie")
    run(app, 2, [btn(pad, pads.DPAD_LEFT, False)])
    run(app, 10, [axis(pad, pads.AXIS_LEFTX, 32000)])
    check(app.choice == "holly", "stick right chooses Holly, one step for a held push")
    run(app, 2, [axis(pad, pads.AXIS_LEFTX, 0)])
    shot_h = pygame.surfarray.array3d(app.surf)
    diff = int((abs(shot_a.astype(int) - shot_h).sum(axis=2) > 40).sum())
    check(diff > 2000, f"the title shows who is chosen (highlight moves, {diff} px change)")
    pygame.image.save(app.surf, os.path.join(SHOTS, "zen_hs_title_holly.png"))
    run(app, 2, [btn(pad, pads.A)])
    check(app.mode == "play", "A on the title starts the game")
    g = app.game
    check(g.player == "holly" and g.npc.name == "archie", "starting with Holly chosen plays Holly; Archie wanders")
    run(app, 2, [btn(pad, pads.A, False)])
    x0, y0, f0 = g.x, g.y, g.facing
    run(app, 40, [axis(pad, pads.AXIS_LEFTY, -32000)])
    check((g.x, g.y) != (x0, y0), f"left stick up walks the player ({x0:.2f},{y0:.2f}) -> ({g.x:.2f},{g.y:.2f})")
    run(app, 2, [axis(pad, pads.AXIS_LEFTY, 0)])
    run(app, 2, [btn(pad, pads.DPAD_RIGHT)])
    check(g.facing != f0, f"D-pad right turns ({f0} -> {g.facing})")
    run(app, 2, [btn(pad, pads.DPAD_RIGHT, False)])
    run(app, 2, [btn(pad, pads.Y)])
    check(g.flipped, "Y looks from the other side (like V)")
    run(app, 30, [btn(pad, pads.Y, False)])
    run(app, 2, [btn(pad, pads.B)])
    check(app.mode == "title", "B goes back to the title")
    check(app.choice == "holly", "the choice is remembered back on the title")
    run(app, 2, [btn(pad, pads.B, False), btn(pad, pads.START)])
    check(app.mode == "play", "Start also starts")
    check(app.game is g and g.player == "holly", "same game, still Holly")
    run(app, 2, [btn(pad, pads.START, False)])
    run(app, 30, [btn(pad, pads.BACK)])
    check(app.running, "a short press of Back does not quit")
    run(app, 40)
    check(not app.running, "holding Back about a second quits (back to Zen Station)")

    app = make_app(None)
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)])
    check(app.choice == "holly", "Right arrow on the title chooses Holly")
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)])
    check(app.choice == "archie", "Left arrow chooses Archie")
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    check(app.mode == "play" and app.game.player == "archie", "Enter starts, as Archie")
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)])
    run(app, 1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)])
    check(app.mode == "play" and app.game.player == "holly" and app.game.npc.name == "archie",
          "back to the title, D then Space: now playing Holly, Archie wanders")
    src = open(os.path.join(HERE, "game.py")).read() + open(os.path.join(HERE, "zen.py")).read()
    check("V Looking {way}" in src and "Looking {way}" in src and " looking {way}" not in src
          and "Up / Down Walk" in src and "Hold {back} to Quit" in src, "bottom hints in Title Case")
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
    # Under the launcher SDL_VIDEODRIVER is unset; importing the game must not
    # set it to dummy (that opened an invisible window and the launcher hung).
    import subprocess
    env = {k: v for k, v in os.environ.items() if k not in ("SDL_VIDEODRIVER", "ZENSTATION")}
    out = subprocess.run([sys.executable, "-c",
                          "import os, game, zen, zenbuild; zenbuild.needed(); "
                          "print('DRIVER', os.environ.get('SDL_VIDEODRIVER'))"],
                         cwd=HERE, env=env, capture_output=True, text=True).stdout
    check("DRIVER None" in out, "importing game/zen/zenbuild leaves SDL_VIDEODRIVER unset")

    # zen.log: written under ZENSTATION=1 with versions, the modes tried and frames
    log = os.path.join(HERE, "zen.log")
    if os.path.exists(log):
        os.remove(log)
    env = dict(os.environ, ZENSTATION="1", SDL_VIDEODRIVER="dummy")
    p = subprocess.Popen([sys.executable, "game.py"], cwd=HERE, env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import time
    t0 = time.time()
    while time.time() - t0 < 20:
        if os.path.exists(log) and "running:" in open(log).read():
            break
        time.sleep(0.2)
    p.terminate()
    p.wait(timeout=10)
    text = open(log).read() if os.path.exists(log) else ""
    check("Hide and Seek started" in text and "SDL 2" in text and "set_mode" in text
          and "running:" in text, "ZENSTATION=1 writes zen.log (versions, set_mode, frames)")

    print("RESULT:", "all OK" if not FAIL else f"FAILURES: {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
