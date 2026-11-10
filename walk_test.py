#!/usr/bin/env python3
"""Headless scripted walk through the downstairs, driven through the game's own
tank controls (turn, then walk forward), with a breadth-first path inside each
room. Checks every doorway pairing is reachable and passable both ways, and
saves a few screenshots.

    SDL_VIDEODRIVER=dummy python3 walk_test.py          # screenshots go to shots/
"""
import os
import sys
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

import house  # noqa: E402
import game  # noqa: E402

SHOTS = os.environ.get("HS_SHOTS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots"))
DT = 1 / 60
G = 0.1
FAIL = []


def step(g, turn=0, move=0):
    g.update(DT, turn, move)
    g.draw()


def settle(g):
    while g.trans:
        step(g)


def face(g, f):
    while g.facing != f:
        i, j = game.FACING_ORDER.index(g.facing), game.FACING_ORDER.index(f)
        step(g, 1 if (j - i) % 4 <= 2 else -1)
        step(g)                                  # release, so the next press turns again


def path(g, goal):
    """BFS over free grid spots from Archie's position to within G of goal."""
    room, sx, sy = g.room, g.x, g.y
    start = (0, 0)
    prev = {start: None}
    q = deque([start])
    best = None
    while q:
        c = q.popleft()
        x, y = sx + c[0] * G, sy + c[1] * G
        if abs(x - goal[0]) <= G / 2 + 1e-6 and abs(y - goal[1]) <= G / 2 + 1e-6:
            best = c
            break
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + d[0], c[1] + d[1])
            if n not in prev and house.free(room, sx + n[0] * G, sy + n[1] * G) and abs(n[0]) < 200 and abs(n[1]) < 120:
                prev[n] = c
                q.append(n)
    if best is None:
        return None
    cells = []
    while best is not None:
        cells.append(best)
        best = prev[best]
    cells.reverse()
    # compress into straight runs
    segs = []
    for a, b in zip(cells, cells[1:]):
        d = (b[0] - a[0], b[1] - a[1])
        if segs and segs[-1][0] == d:
            segs[-1][1] += 1
        else:
            segs.append([d, 1])
    return [(d, n * G) for d, n in segs]


def screen_facing(world_facing, flipped):
    """Facing stored on Archie is the way he faces on screen. In the opposite
    view that is the reverse of the world direction, so Up still walks into
    the picture."""
    if flipped:
        return {"E": "W", "W": "E", "S": "N", "N": "S"}[world_facing]
    return world_facing


def walk(g, segs, shot=None):
    for (dx, dy), L in segs:
        world = {(1, 0): "E", (-1, 0): "W", (0, 1): "S", (0, -1): "N"}[(dx, dy)]
        face(g, screen_facing(world, g.flipped))
        tx, ty = g.x + dx * L, g.y + dy * L
        for _ in range(int(L / (game.SPEED * DT)) + 3):
            rem = abs(tx - g.x) + abs(ty - g.y)
            if rem < game.SPEED * DT / 2:
                break
            step(g, 0, 1)
            if shot and g.trans and g.trans[0] == "slide" and g.trans[1] > .45:
                pygame.image.save(g.screen, shot)
                print("  saved", shot)
                shot = None
        step(g)
    return shot


def nearest_free(room, x, y):
    for r in range(0, 30):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if max(abs(dx), abs(dy)) == r and house.free(room, x + dx * .05, y + dy * .05):
                    return x + dx * .05, y + dy * .05
    return None


def go_to(g, x, y, shot=None):
    tgt = nearest_free(g.room, x, y)
    segs = path(g, tgt) if tgt else None
    if segs is None:
        FAIL.append(f"no path in {g.room} to {x:.2f},{y:.2f}")
        return False
    walk(g, segs, shot)
    return True


def through(g, to_room):
    """Walk from the current room through its doorway to to_room."""
    for wall, a, b, (troom, twall, ta, tb) in house.portals_of(g.room):
        if troom == to_room:
            break
    else:
        FAIL.append(f"no doorway {g.room} -> {to_room}")
        return False
    rm = house.ROOMS[g.room]
    u, inset = (a + b) / 2, .5
    x, y = {"S": (u, inset), "N": (u, rm["rd"] - inset), "E": (inset, u), "W": (rm["rw"] - inset, u)}[wall]
    frm = g.room
    if not go_to(g, x, y):
        return False
    face(g, screen_facing({"S": "N", "N": "S", "E": "W", "W": "E"}[wall], g.flipped))
    for _ in range(120):
        step(g, 0, 1)
        if g.room != frm:
            break
    for _ in range(8):
        step(g, 0, 1)
    step(g)
    settle(g)
    ok = g.room == to_room and house.free(g.room, g.x, g.y)
    print(f"  {frm:8s} -> {to_room:8s} via {wall} wall: {'OK' if ok else 'FAILED (now in ' + g.room + ')'}")
    if not ok:
        FAIL.append(f"{frm} -> {to_room}")
    return ok


def through_stairs(g, to_room):
    """Walk from the current room onto its stair link to to_room."""
    link = next((L for L in house.STAIR_LINKS if L["room"] == g.room and L["dest"] == to_room), None)
    if link is None:
        FAIL.append(f"no stair {g.room} -> {to_room}")
        return False
    frm = g.room
    # stand just outside the zone, then walk into it
    mx = (link["x0"] + link["x1"]) / 2
    if frm == "hall":
        ax, ay, world = mx, link["y0"] - 0.18, "S"   # face north, into the stairs
    else:
        ax, ay, world = mx, link["y1"] + 0.18, "N"   # face south, into the well
    if not go_to(g, ax, ay):
        return False
    face(g, screen_facing(world, g.flipped))
    for _ in range(160):
        step(g, 0, 1)
        if g.room != frm:
            break
    for _ in range(8):
        step(g, 0, 1)
    step(g)
    settle(g)
    ok = g.room == to_room and house.free(g.room, g.x, g.y)
    print(f"  {frm:8s} -> {to_room:8s} via stairs: {'OK' if ok else 'FAILED (now in ' + g.room + ')'}")
    if not ok:
        FAIL.append(f"stairs {frm} -> {to_room}")
    return ok


def snap(g, name):
    p = os.path.join(SHOTS, f"hs_walk_{name}.png")
    pygame.image.save(g.screen, p)
    print("  saved", p)


def run(g):
    step(g)
    print("walk:" if not g.flipped else "opposite view:")
    go_to(g, 2.4, 2.6)
    snap(g, "1_hall")
    through(g, "sitting")
    go_to(g, 3.0, 4.6)
    snap(g, "2_sitting_room")
    through(g, "hall")
    through(g, "drawing")
    go_to(g, 3.6, 4.4)
    snap(g, "3_drawing_room")
    through(g, "kd")
    go_to(g, 9.5, 2.5)
    go_to(g, 6.2, 2.5, shot=os.path.join(SHOTS, "hs_walk_4_kitchen_to_dining_slide.png"))
    settle(g)
    if g.view[0] != "dining":
        FAIL.append("kitchen -> dining slide")
    print(f"  kitchen  -> dining   across the beam: {'OK' if g.view[0] == 'dining' else 'FAILED'}")
    through(g, "boot")
    through(g, "utility")
    go_to(g, 1.8, 2.0)
    snap(g, "5_utility")
    through(g, "boot")
    through(g, "office")
    through(g, "boot")
    through(g, "wc")
    go_to(g, .7, 1.2)
    snap(g, "6_dragon_toilet")
    # the remaining pairings, both ways
    print("all doorways, both ways:")
    for (p, q) in house.PORTALS:
        for a, b in ((p, q), (q, p)):
            g.room, g.view = a[0], None
            rm = house.ROOMS[a[0]]
            if a[0] == "kd":
                sx, sy = 9.5, 2.5
            elif a[0] == "landing":
                sx, sy = 2.15, 2.20
            else:
                sx, sy = rm["rw"] / 2, rm["rd"] / 2
            g.x, g.y = nearest_free(a[0], sx, sy)
            g.view = house.view_for(g.room, g.x)
            through(g, b[0])
    print("stairs, both ways:")
    for link in house.STAIR_LINKS:
        g.room, g.view = link["room"], None
        if link["room"] == "hall":
            g.x, g.y = nearest_free("hall", 2.05, 2.40)
        else:
            g.x, g.y = nearest_free("landing", 2.15, 7.70)
        g.view = house.view_for(g.room, g.x)
        through_stairs(g, link["dest"])
def main():
    os.makedirs(SHOTS, exist_ok=True)
    pygame.init()
    screen = pygame.display.set_mode((game.WIN_W, game.WIN_H))
    g = game.Game(screen)
    run(g)
    g.flipped = True
    g._hint = g._make_hint()
    g.room, g.x, g.y, g.facing = "hall", 1.6, 1.2, "N"
    g.view = house.view_for(g.room, g.x)
    g.trans = None
    g.moving = False
    run(g)
    print("RESULT:", "all connections OK" if not FAIL else f"FAILURES: {FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
