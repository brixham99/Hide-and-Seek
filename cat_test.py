#!/usr/bin/env python3
"""Headless check of Bunty: asleep on a bed or the sofa at the start, naps
then slow wanders round the whole house (up and down the stairs), changes
her spot now and then, takes no notice of anyone, hops up onto the Kitchen
island while the player is in the Kitchen and down again when they leave,
never stands inside furniture, and is drawn in both cameras.

    python3 cat_test.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import cat  # noqa: E402
import house  # noqa: E402

DT = 1 / 30
FAIL = []
UPSTAIRS = ("landing", "corridor", "archie", "upoffice", "bathroom", "holly", "master", "dressing", "ensuite")


def check(ok, msg):
    print(("  ok    " if ok else "  FAIL  ") + msg)
    if not ok:
        FAIL.append(msg)


def run(c, secs, room, x, y, moving=False, each=None):
    for _ in range(int(secs / DT)):
        c.update(DT, room, x, y, moving)
        if each:
            each(c)


def main():
    print("start")
    starts = {cat.Cat(seed=s).spot for s in range(40)}
    check(starts == set(cat.SPOTS), f"starts on each of the spots over seeds: {sorted(starts)}")
    for name, sp in cat.SPOTS.items():
        c = cat.Cat(seed=1, spot=name)
        ok = c.room == sp["room"] and c.z > 0 and c.pose() == "sleep" and c.on_furniture()
        check(ok, f"asleep on {name} ({sp['room']}, z {c.z})")
        check(house.free(sp["room"], *sp["approach"], cat.R), f"{name}: hop-off point is clear floor")
    check(house.free("kd", *cat.ISLAND["approach"], cat.R), "island: hop-up point is clear floor")

    print("takes no notice of people (outside the kitchen)")
    c = cat.Cat(seed=3, spot="sofa")
    x0 = (c.x, c.y)
    pts = [(2.0, 3.0), (3.0, 5.0), (2.0, 3.0)]
    for i in range(int(15 / DT)):
        px, py = pts[(i // 60) % 3]
        c.update(DT, "drawing", px, py, True)
    check(c.state == "sleep" and (c.x, c.y) == x0, "the player walking about her room doesn't wake her")

    print("a long day (player out of the way in the Sitting Room)")
    for seed in (2, 5, 11):
        c = cat.Cat(seed=seed)
        stats = dict(t=0.0, sleep=0.0, bad=[], rooms=set(), maxstep=0.0, last=None, still=0.0, stuck=0.0)

        def each(c, st=stats):
            st["t"] += DT
            st["rooms"].add(c.room)
            if c.state == "sleep":
                st["sleep"] += DT
            if c.state != "hop" and c.z == 0 and not house.free(c.room, c.x, c.y, cat.R * 0.5):
                st["bad"].append((c.room, round(c.x, 2), round(c.y, 2), c.state))
            same = st["last"] == (c.room, c.x, c.y)
            st["still"] = st["still"] + DT if (same and c.state in ("wander", "return", "to_island")) else 0.0
            st["stuck"] = max(st["stuck"], st["still"])
            if st["last"] and st["last"][0] == c.room:
                st["maxstep"] = max(st["maxstep"], math.hypot(c.x - st["last"][1], c.y - st["last"][2]))
            st["last"] = (c.room, c.x, c.y)
        run(c, 3600, "sitting", 3.0, 4.2, False, each)
        frac = stats["sleep"] / stats["t"]
        spots = [e for e in c.log if isinstance(e, tuple) and e[0] == "spot"]
        up = any(r in UPSTAIRS for r in stats["rooms"])
        down = any(r not in UPSTAIRS for r in stats["rooms"])
        check(frac > 0.5, f"seed {seed}: mostly asleep ({frac:.0%} of an hour)")
        check(up and down and "hall" in stats["rooms"] and "landing" in stats["rooms"],
              f"seed {seed}: wanders up and down the stairs ({len(stats['rooms'])} rooms)")
        check(len(spots) >= 1, f"seed {seed}: changes spot now and then ({[s[1] for s in spots]})")
        check(not stats["bad"], f"seed {seed}: never inside furniture or a wall {stats['bad'][:3]}")
        check(stats["maxstep"] <= cat.TROT * DT + 0.05 or stats["maxstep"] < 1.2,
              f"seed {seed}: no jumps within a room (largest step {stats['maxstep']:.2f} tiles)")
        check(stats["stuck"] < 2.0, f"seed {seed}: never stuck on the way somewhere (longest stall {stats['stuck']:.1f} s)")
        check(c.log.count("sleep") >= 2, f"seed {seed}: goes back to sleep after wandering")

    print("the kitchen island")
    c = cat.Cat(seed=4, spot="sofa")
    hop = dict(zmax=0.0, n=0, poses=set())

    def watch(c, h=hop):
        if c.state == "hop":
            h["n"] += 1
            h["poses"].add(c.pose())
            h["zmax"] = max(h["zmax"], c.z)
    run(c, 40, "kd", 11.0, 6.6, False, watch)
    check(c.room == "kd" and c.state == "island" and c.z == cat.ISLAND["at"][2],
          f"player in the Kitchen: she goes from the sofa to the island ({c.room}, {c.state}, z {c.z})")
    check(c.pose() == "sit", "sits on the island")
    check(hop["poses"] == {"jump"} and hop["zmax"] > cat.ISLAND["at"][2],
          f"hops up with the jump pose and an arc (peak z {hop['zmax']:.0f})")
    check(abs(hop["n"] * DT - 2 * cat.HOP_S) < 0.2, f"two short hops (off the sofa, up the island), {hop['n'] * DT:.2f} s")
    run(c, 20, "kd", 14.0, 6.6, True)
    check(c.state == "island", "stays up while they're in the Kitchen")
    run(c, 4, "hall", 2.0, 2.0)
    check(c.z == 0 and c.state not in ("island", "hop"), f"jumps down after they leave ({c.state}, z {c.z})")
    run(c, 400, "hall", 2.0, 2.0)
    check(c.log.count("sleep") >= 1 and c.state in ("sleep", "wander", "pause", "return"), "then back to her nap")

    c = cat.Cat(seed=4, spot="holly")
    run(c, 15, "kd", 11.0, 6.6)
    check(c.state == "sleep" and c.room == "holly", "asleep upstairs: the Kitchen doesn't fetch her")

    print("drawn in the game, both cameras")
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    import game
    g = game.Game(pygame.display.get_surface())
    for flip in (False, True):
        g.flipped = flip
        g.room, g.x, g.y = "kd", 11.0, 6.6
        g.view = house.view_for("kd", 11.0)
        g.dog.room = "nowhere"
        g.cat.room = "nowhere"
        g._paint_view(g.frame, g.view)
        a = pygame.surfarray.array3d(g.frame).copy()
        g.cat.room, (g.cat.x, g.cat.y, g.cat.z), g.cat.state = "kd", cat.ISLAND["at"], "island"
        g._paint_view(g.frame, g.view)
        b = pygame.surfarray.array3d(g.frame)
        n = int((abs(a.astype(int) - b).sum(axis=2) > 30).sum())
        check(n > 150, f"on the island, {'looking south' if flip else 'looking north'}: {n} px of cat")
    def area(img):
        return int((pygame.surfarray.array_alpha(img) > 128).sum())
    sz = [area(g.cat_img["stand"]["se"][0]), area(g.dog_img["stand"]["se"][0])]
    check(sz[0] < 0.5 * sz[1], f"clearly smaller than Myrtle ({sz[0]} px of sprite vs {sz[1]} px)")
    for pose in ("stand", "walk", "sit", "sleep", "jump"):
        check(all(g.cat_img[pose][k] for k in ("se", "sw", "nw", "ne")), f"sprites: {pose} in all four directions")

    print("RESULT: " + ("all OK" if not FAIL else f"{len(FAIL)} FAILED"))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
