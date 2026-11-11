#!/usr/bin/env python3
"""Headless check of the other child (npc.py): they start in their own room,
wander the whole house (up and down the stairs, through the arch), stand
about in rooms, never get stuck and never stand inside furniture or a wall;
in the game they are drawn in both cameras, Myrtle can be woken by them,
Bunty goes up on the island for them, and swapping who you play puts each
child where the other was.

    python3 npc_test.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import house  # noqa: E402
import npc  # noqa: E402

DT = 1 / 30
FAIL = []


def check(ok, msg):
    print(("  ok    " if ok else "  FAIL  ") + msg)
    if not ok:
        FAIL.append(msg)


def main():
    print("wandering")
    for name in ("archie", "holly"):
        c = npc.Child(name, seed=1)
        check(c.room == npc.STARTS[name][0] and house.free(c.room, c.x, c.y),
              f"{name} starts in {c.room} on clear floor")
        for seed in (1, 7):
            c = npc.Child(name, seed=seed)
            rooms, bad, still, stuck, maxstep, last, paused = set(), [], 0.0, 0.0, 0.0, None, 0.0
            for _ in range(int(2400 / DT)):
                c.update(DT)
                rooms.add(c.room)
                pos = (c.room, c.x, c.y)
                still = still + DT if (c.state == "wander" and pos == last) else 0.0
                stuck = max(stuck, still)
                if last and last[0] == c.room:
                    maxstep = max(maxstep, math.hypot(c.x - last[1], c.y - last[2]))
                if c.state == "pause":
                    paused += DT
                if not house.free(c.room, c.x, c.y, house.R * 0.7):
                    bad.append((c.room, round(c.x, 2), round(c.y, 2)))
                last = pos
            up = {"landing", "corridor"} & rooms
            check(len(rooms) >= 14 and "hall" in rooms and bool(up),
                  f"{name} seed {seed}: up and downstairs, {len(rooms)} of {len(house.ROOMS)} rooms in 40 min")
            check(stuck < 2.0, f"{name} seed {seed}: never stuck (longest stall {stuck:.1f} s)")
            check(not bad, f"{name} seed {seed}: never inside furniture or a wall {bad[:3]}")
            check(maxstep <= npc.WALK * DT + 1e-6, f"{name} seed {seed}: walks at a child's pace, no jumps")
            check(0.2 < paused / 2400 < 0.8, f"{name} seed {seed}: stands about in rooms ({paused / 24:.0f}% of the time)")

    print("in the game")
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    import game
    g = game.Game(pygame.display.get_surface(), player="holly")
    check(g.player == "holly" and g.npc.name == "archie", "playing Holly: Archie is the one wandering")
    for flip in (False, True):
        g.flipped = flip
        g.room, g.x, g.y = "drawing", 3.4, 4.6
        g.view = house.view_for("drawing", 3.4)
        g.dog.room = g.cat.room = "nowhere"
        g.npc.room = "nowhere"
        g._paint_view(g.frame, g.view)
        a = pygame.surfarray.array3d(g.frame).copy()
        g.npc.room, g.npc.x, g.npc.y = "drawing", 2.6, 2.0
        g._paint_view(g.frame, g.view)
        n = int((abs(a.astype(int) - pygame.surfarray.array3d(g.frame)).sum(axis=2) > 30).sum())
        check(n > 2000, f"Archie drawn in the room, {'looking south' if flip else 'looking north'} ({n} px)")
    g.flipped = False
    # Myrtle asleep; Archie (not the player) walks into the Drawing Room
    import dog
    g.dog = dog.Dog(follow_p=1.0)
    g.room, g.x, g.y = "sitting", 3.0, 4.2
    g.npc.place("hall", 1.0, 1.2, "W")
    g.npc.stops = [("drawing", 3.6, 4.0)]
    g.npc._set("wander")
    woke = False
    for _ in range(int(20 / DT)):
        g.update(DT, 0, 0)
        if g.dog.state != "lie":
            woke = True
            break
    check(woke and g.dog.lead == 1, "Myrtle wakes when the other child comes into her room, and goes with them")
    # Bunty: the other child in the Kitchen fetches her up on the island
    import cat
    g.cat = cat.Cat(seed=4, spot="sofa")
    g.npc.place("kd", 11.0, 6.6, "S")
    g.npc.timer = 999
    for _ in range(int(40 / DT)):
        g.update(DT, 0, 0)
    check(g.cat.state == "island", f"Bunty hops on the island for the other child in the Kitchen ({g.cat.state})")
    # swapping who you play
    g = game.Game(pygame.display.get_surface(), player="archie")
    g.room, g.x, g.y, g.facing = "hall", 1.6, 1.2, "N"
    n0 = (g.npc.room, g.npc.x, g.npc.y)
    g.set_player("holly")
    check(g.player == "holly" and (g.room, g.x, g.y) == n0 and g.npc.name == "archie"
          and (g.npc.room, g.npc.x, g.npc.y) == ("hall", 1.6, 1.2),
          "choosing the other child swaps places: you carry on where they were")
    check(g.stand is g.kids["holly"][0], "and the player is drawn with Holly's sprites")

    print("RESULT: " + ("all OK" if not FAIL else f"{len(FAIL)} FAILED"))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
