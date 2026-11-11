#!/usr/bin/env python3
"""Headless check of Myrtle's state machine: asleep until someone comes into
her room, the follow / stay coin toss, re-tosses while following, back to bed
and waiting again, the kitchen linger, nobody downstairs, and that she never
walks through furniture or goes upstairs.

    python3 dog_test.py
"""
import math
import sys

import dog
import house

DT = 1 / 30
FAIL = []


def check(ok, msg):
    print(("  ok    " if ok else "  FAIL  ") + msg)
    if not ok:
        FAIL.append(msg)


def run(d, secs, room, pts=None, moving=False):
    """Tick for `secs`. With pts, the player walks the waypoint loop at 3 tiles/s."""
    n = int(secs / DT)
    i, (x, y) = 0, (pts[0] if pts else (0, 0))
    for _ in range(n):
        if pts and moving:
            tx, ty = pts[(i + 1) % len(pts)]
            dx, dy = tx - x, ty - y
            dd = math.hypot(dx, dy)
            s = 3.0 * DT
            if dd <= s:
                x, y = tx, ty
                i += 1
            else:
                x, y = x + dx / dd * s, y + dy / dd * s
        d.update(DT, room, x, y, moving and bool(pts))
        assert d.room in dog.DOWNSTAIRS, d.room
        if not (house.free(d.room, d.x, d.y, dog.R * 0.6) or d.state == "lie"):
            FAIL.append(f"inside furniture/wall at {d.room} {d.x:.2f},{d.y:.2f}")
            print("  FAIL  inside furniture/wall", d.room, round(d.x, 2), round(d.y, 2))
            return x, y
    return x, y


class Script:
    """A stand-in for random.Random: random() plays back `tosses` (True =
    follow), then `then`; uniform() gives the low end, so tosses come
    every REROLL_S[0] seconds."""

    def __init__(self, tosses=(), then=True):
        self.tosses = list(tosses)
        self.then = then

    def random(self):
        ok = self.tosses.pop(0) if self.tosses else self.then
        return 0.0 if ok else 0.99

    def uniform(self, a, b):
        return a


def enter_drawing(d, x=2.0, y=1.2):
    """Walk from the Hall into the Drawing Room (one tick each side)."""
    run(d, 0.2, "hall", [(1.3, 1.0)], moving=True)
    return run(d, 0.2, "drawing", [(x, y)], moving=True)


def main():
    loop = [(4.5, 4.5), (5.6, 5.4), (4.0, 6.2), (3.2, 4.0)]
    hall = [(1.3, 1.0), (2.4, 1.6), (2.4, 2.4), (1.3, 1.0)]
    print("Myrtle:")
    d = dog.Dog(rng=Script(then=True))
    check(d.state == "lie" and d.room == "drawing", "starts lying on her bed in the Drawing Room")

    # inactive until someone comes into her room
    run(d, 0.1, "drawing", loop, moving=True)       # already in the room at the start: not an entry
    run(d, 6, "drawing", loop, moving=True)
    check(d.on_bed(), f"takes no notice of someone already in the room ({d.state})")
    run(d, 6, "hall", hall, moving=True)
    check(d.on_bed(), f"or of someone walking about in another room ({d.state})")

    # follow branch
    enter_drawing(d)
    px, py = run(d, 6, "drawing", loop, moving=True)
    check(d.state in ("follow", "wait"), f"on a 'follow' toss, gets up and follows ({d.state})")
    dist = math.hypot(d.x - px, d.y - py)
    check(dist < 2.4, f"keeps close behind ({dist:.2f} tiles)")
    run(d, 3, "drawing", [(px, py)], moving=False)
    check(d.state == "sit", f"sits when they stop ({d.state})")
    run(d, dog.IDLE_S + 1, "drawing", [(px, py)], moving=False)
    check(d.state in ("return", "lie"), f"heads back to bed after a while idle ({d.state})")
    run(d, 10, "drawing", [(px, py)], moving=False)
    check(d.on_bed(), "lies down on her bed again")
    run(d, 4, "drawing", loop, moving=True)
    check(d.on_bed(), "and waits there although they are still in the room")

    # follow the player out of the Drawing Room into the Hall, then the kitchen
    enter_drawing(d)
    run(d, 1, "drawing", [(2.0, 1.2)], moving=True)
    run(d, 12, "hall", hall, moving=True)
    check(d.room == "hall", f"follows through the doorway into the Hall ({d.room})")
    kd = [(9.0, 1.0), (9.5, 2.5), (8.8, 3.2), (9.0, 1.0)]
    px, py = run(d, 15, "kd", kd, moving=True)
    check(d.room == "kd", f"follows into the Kitchen ({d.room})")
    dist = math.hypot(d.x - px, d.y - py)
    check(dist < 2.0, f"stays closer in the Kitchen ({dist:.2f} tiles)")
    run(d, dog.IDLE_S + 5, "kd", [(px, py)], moving=False)
    check(d.state == "sit" and d.room == "kd", f"lingers, sitting hopefully, in the Kitchen ({d.state})")
    check("keep" in d.log, "tossed again while following, and kept following")
    run(d, dog.IDLE_S_KITCHEN - dog.IDLE_S, "kd", [(px, py)], moving=False)
    check(d.state in ("return", "lie"), f"eventually gives up and goes back ({d.state})")

    # stay branch
    d3 = dog.Dog(rng=Script([False]))
    run(d3, 0.2, "hall", [(1.3, 1.0)], moving=True)
    enter_drawing(d3)
    run(d3, 6, "drawing", loop, moving=True)
    check(d3.on_bed() and "stay" in d3.log, f"on a 'stay' toss, stays lying on her bed ({d3.state})")
    enter_drawing(d3)
    run(d3, 3, "drawing", loop, moving=True)
    check(d3.state in ("follow", "wait"), f"and tosses again the next time someone comes in ({d3.state})")

    # while following, a 'no' toss sends her back to bed; then she waits again
    d4 = dog.Dog(rng=Script([True, False], then=True))
    run(d4, 0.2, "hall", [(1.3, 1.0)], moving=True)
    enter_drawing(d4)
    run(d4, 1, "drawing", [(2.0, 1.2)], moving=True)
    run(d4, dog.REROLL_S[0] - 2, "hall", hall, moving=True)
    check(d4.state in ("follow", "wait", "sit") and d4.room == "hall", f"follows into the Hall ({d4.state}, {d4.room})")
    run(d4, 3, "hall", hall, moving=True)
    check(d4.state == "return", f"a 'no' toss while following: walks back to bed ({d4.state})")
    run(d4, 20, "hall", hall, moving=True)
    check(d4.on_bed(), "lies down on her bed")
    run(d4, 5, "hall", hall, moving=True)
    check(d4.on_bed(), "and stays there while they walk about elsewhere")
    enter_drawing(d4)
    run(d4, 3, "drawing", loop, moving=True)
    check(d4.state in ("follow", "wait"), f"until someone comes into her room again ({d4.state})")

    # roughly half the time, with a real (seeded) coin
    d5 = dog.Dog(seed=1)
    ups = sum(d5._toss() for _ in range(400))
    check(150 < ups < 250, f"follows about half the time ({ups}/400 tosses)")
    check(dog.Dog(seed=7)._toss() == dog.Dog(seed=7)._toss(), "seeded tosses repeat")

    # nobody downstairs: straight back to bed, and she never goes up
    d2 = dog.Dog(rng=Script(then=True))
    run(d2, 0.2, "hall", [(1.3, 1.0)], moving=True)
    enter_drawing(d2, 4.0, 4.0)
    run(d2, 1, "drawing", [(4.0, 4.0)], moving=True)
    run(d2, 8, "hall", hall, moving=True)
    run(d2, 1, "landing", [(2.0, 4.0)], moving=True)
    check(d2.state in ("return", "lie"), f"goes back to bed when everyone is upstairs ({d2.state})")
    run(d2, 25, "landing", [(2.0, 4.0)], moving=True)
    check(d2.on_bed(), "and is lying on her bed")
    known = {"wake", "follow", "wait", "sit", "return", "lie", "stay", "keep"}
    check(all(set(x.log) <= known for x in (d, d2, d3, d4)), "only known states")
    print("RESULT:", "all OK" if not FAIL else f"{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
