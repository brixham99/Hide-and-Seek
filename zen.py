"""Zen Station / TV front end for Hide and Seek.

game.py's main() hands over to this. It adds what the Raspberry Pi console
needs, kept out of game.py so the room work there merges cleanly:

* full screen when ZENSTATION=1 (or --fullscreen), via Haunted Mansion's
  screenfit.py: the 1280x720 picture scaled to the TV;
* gamepads via Haunted Mansion's pads.py (Xbox and PlayStation): left stick or
  D-pad for the tank controls, right trigger walks forwards, Y / Triangle (or X /
  Square) looks from the other side like V, B / Circle goes back to the title,
  and holding Back / Share for a second quits back to the launcher;
* the title screen (title.py);
* the room images built in parallel with a progress screen (zenbuild.py),
  started straight away so they are often ready by the time you press start.

    python3 game.py [--windowed | --fullscreen]
    python3 zen.py --scene title --screenshot shots/title.png [--pad xbox]
"""
import argparse
import os
import sys
import time

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

import pads  # noqa: E402
import screenfit  # noqa: E402
import title as titlemod  # noqa: E402
import zenbuild  # noqa: E402

WIN_W, WIN_H = 1280, 720


def make_game_class(Game):
    class ZenGame(Game):
        """The game, read from the pads as well as the keyboard, shown through screenfit."""
        pads = None
        present = None

        def read_input(self):
            k = pygame.key.get_pressed()
            turn = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
            move = (k[pygame.K_UP] or k[pygame.K_w]) - (k[pygame.K_DOWN] or k[pygame.K_s])
            p0 = self.pads.player(0) if self.pads else None
            if p0 is not None and not turn and not move:
                turn, move = p0.digital_move()
            return turn, move

        def _make_hint(self):
            if not (self.pads and self.pads.connected):
                way = "south" if self.flipped else "north"
                text = f"Left / Right turn    Up / Down walk    V looking {way}    Esc title"
            else:
                way = "south" if self.flipped else "north"
                y, back = self.pads.label("Y"), self.pads.label("BACK")
                b = self.pads.label("B")
                text = f"Stick turn / walk    {y} looking {way}    {b} title    hold {back} to quit"
            txt = self.small.render(text, True, (214, 204, 178))
            sh = self.small.render(text, True, (12, 10, 12))
            box = pygame.Surface((txt.get_width() + 4, txt.get_height() + 2), pygame.SRCALPHA)
            box.blit(sh, (2, 1))
            box.blit(txt, (0, 0))
            return box

        def _flip(self):
            self._hud_on(self.frame)
            self.screen.blit(self.frame, (0, 0))
            if self.present:
                self.present()
            else:
                pygame.display.flip()

    return ZenGame


class App:
    def __init__(self, Game, args, view):
        self.Game = make_game_class(Game)
        self.args = args
        self.view = view
        self.surf = view.surface
        self.pads = pads.Pads()
        if not args.headless:
            self.pads.scan()
        if args.pad:
            self.pads.attach_synthetic(pads.PAD_NAMES[args.pad])
        self.title = titlemod.TitleScreen((WIN_W, WIN_H))
        self.buildscr = titlemod.BuildScreen(self.title)
        self.mode = "title"
        self.t = 0.0
        self.game = None
        self.build = None
        self.build_t0 = time.time()
        self.running = True
        if not args.headless and zenbuild.needed():
            self.build = zenbuild.Build()

    # ------------------------------------------------------------ helpers
    def labels(self):
        if self.pads.connected:
            return self.pads.label("A"), self.pads.label("BACK")
        return "A", "Back"

    def build_progress(self):
        if self.build is None:
            return None
        done, total, fin = self.build.step()
        if fin:
            if self.build.error:
                print("Hide and Seek: room build failed:", self.build.error, file=sys.stderr)
            self.build = None
            return None
        return done, total

    def start(self):
        if self.build is not None or zenbuild.needed():
            if self.build is None:
                self.build = zenbuild.Build()
            self.mode = "build"
            return
        self.enter_play()

    def enter_play(self):
        if self.game is None:
            self.game = self.Game(self.surf)
            self.game.pads = self.pads
            self.game.present = self.view.present
            self.game._hint = self.game._make_hint()
        self.mode = "play"

    def to_title(self):
        self.mode = "title"

    def quit(self):
        if self.build is not None:
            self.build.cancel()
            self.build = None
        self.running = False

    # ------------------------------------------------------------ one frame
    def on_key(self, key):
        if self.mode == "title":
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.start()
            elif key == pygame.K_ESCAPE:
                self.quit()
        elif self.mode == "build":
            if key == pygame.K_ESCAPE:
                self.quit()
        elif self.mode == "play":
            if key == pygame.K_ESCAPE:
                self.to_title()
            elif key == pygame.K_v:
                self.game.toggle_view()

    def on_pad(self, button):
        if self.mode == "title" and button in (pads.A, pads.START):
            self.start()
        elif self.mode == "play":
            if button in (pads.Y, pads.X):
                self.game.toggle_view()
            elif button in (pads.B, pads.START):
                self.to_title()

    def frame(self, dt, events):
        self.t += dt
        self.pads.begin_frame()
        had_pads = self.pads.connected
        for ev in events:
            if ev.type == pygame.QUIT:
                self.quit()
                return
            if self.pads.handle_event(ev):
                continue
            if ev.type == pygame.KEYDOWN:
                self.on_key(ev.key)
                if not self.running:
                    return
        self.pads.poll()
        self.pads.finish()
        if self.game is not None and had_pads != self.pads.connected:
            self.game._hint = self.game._make_hint()
        if self.pads.consume_quit(dt):
            self.quit()
            return
        p0 = self.pads.player(0)
        if p0 is not None:
            for b in sorted(p0.pressed):
                self.on_pad(b)
        a_label, back_label = self.labels()
        if self.mode == "title":
            self.title.draw(self.surf, self.t, a_label, back_label, self.build_progress())
            self.view.present()
        elif self.mode == "build":
            prog = self.build_progress()
            if prog is None:
                self.enter_play()
                return
            done, total = prog
            el = time.time() - self.build.t0
            eta = el / done * (total - done) if done >= 3 else None
            self.buildscr.draw(self.surf, self.t, done, total, eta, back_label)
            self.view.present()
        elif self.mode == "play":
            self.game.update(dt, *self.game.read_input())
            self.game.draw()


def parse_args(argv):
    p = argparse.ArgumentParser(description="Hide and Seek")
    p.add_argument("--fullscreen", action="store_true", help="fill the screen (also on when ZENSTATION=1)")
    p.add_argument("--windowed", action="store_true", help="stay in a window even under Zen Station")
    p.add_argument("--pad", choices=tuple(pads.PAD_NAMES), default=None,
                   help="treat this controller as connected (hints, screenshots, tests)")
    p.add_argument("--scene", choices=("title", "build", "play"), default=None, help="headless: draw a scene")
    p.add_argument("--screenshot", default=None, help="headless: save the scene here and exit")
    p.add_argument("--sim", type=float, default=0.5, help="headless: seconds to run before the shot")
    return p.parse_args(argv)


def main(Game, argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    args.headless = args.scene is not None
    pygame.init()
    pygame.display.set_caption("Hide and Seek")
    fullscreen = (not args.headless and not args.windowed
                  and screenfit.fullscreen_requested(args.fullscreen)
                  and os.environ.get("SDL_VIDEODRIVER") != "dummy")
    view = screenfit.open_display((WIN_W, WIN_H), fullscreen=fullscreen, headless=args.headless)
    app = App(Game, args, view)
    if args.headless:
        return _scene(app, args)
    clock = pygame.time.Clock()
    while app.running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        app.frame(dt, pygame.event.get())
    pygame.quit()
    return 0


def _scene(app, args):
    if args.scene == "build":
        a, back = app.labels()
        app.buildscr.draw(app.surf, 1.3, 14, 36, 23, back)
    elif args.scene == "title":
        a, back = app.labels()
        app.title.draw(app.surf, 0.5, a, back, None)
    else:
        if zenbuild.needed():
            zenbuild.main([])
        app.enter_play()
        for _ in range(int(args.sim * 60)):
            app.frame(1 / 60, [])
    if args.screenshot:
        os.makedirs(os.path.dirname(os.path.abspath(args.screenshot)), exist_ok=True)
        pygame.image.save(app.surf, args.screenshot)
    pygame.quit()
    return 0


if __name__ == "__main__":
    import game
    sys.exit(main(game.Game))
