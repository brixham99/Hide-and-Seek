"""Headless in-game shot: python tools/view_shot.py out.png room x y [flip] [dogx dogy]
Draws the room the way the game does (bg, Archie, Myrtle, ghost walls)."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); os.chdir(HERE)
import pygame
pygame.init(); scr = pygame.display.set_mode((1280, 720))
import game, house


def shot(out, room, x, y, flip=False, dog=None, facing="N", g=None, hud=False, cat=None, npc=None):
    """`cat` = (x, y, z, state, facing) puts Bunty in the room; `npc` = (x, y, facing)
    the other child; by default both are out of shot."""
    g = g or game.Game(scr)
    g.room, g.x, g.y, g.facing, g.flipped = room, x, y, facing, flip
    g.view = house.view_for(room, x)
    if dog:
        g.dog.room, g.dog.x, g.dog.y = room, dog[0], dog[1]
    else:
        g.dog.room = "nowhere"
    if cat:
        c = g.cat
        c.room, c.x, c.y, c.z, c.state, c.facing = room, *cat
        c.moving = False
    else:
        g.cat.room = "nowhere"
    if npc:
        g.npc.room, g.npc.x, g.npc.y, g.npc.facing = room, *npc
        g.npc.moving = False
    else:
        g.npc.room = "nowhere"
    g._paint_view(g.frame, g.view)
    if hud:
        g._hint = g._make_hint()
        g._hud_on(g.frame)
    pygame.image.save(g.frame, out)
    return g


if __name__ == "__main__":
    a = [v for v in sys.argv[1:] if v != "--hud"]
    flip = len(a) > 4 and a[4] in ("1", "flip", "s")
    dog = (float(a[5]), float(a[6])) if len(a) > 6 else None
    shot(a[0], a[1], float(a[2]), float(a[3]), flip, dog, hud="--hud" in sys.argv)
