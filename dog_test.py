#!/usr/bin/env python3
"""Headless check of Myrtle's state machine: bed -> follow -> sit -> back to
bed, the kitchen linger, nobody downstairs, and that she never walks through
furniture or goes upstairs.

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


def main():
    d = dog.Dog()
    print("Myrtle:")
    check(d.state == "lie" and d.room == "drawing", "starts lying on her bed in the Drawing Room")

    loop = [(4.5, 4.5), (5.6, 5.4), (4.0, 6.2), (3.2, 4.0)]
    px, py = run(d, 6, "drawing", loop, moving=True)
    check(d.state in ("follow", "wait"), f"gets up and follows when someone walks about ({d.state})")
    dist = math.hypot(d.x - px, d.y - py)
    check(dist < 2.4, f"keeps close behind ({dist:.2f} tiles)")
    run(d, 3, "drawing", [(px, py)], moving=False)
    check(d.state == "sit", f"sits when they stop ({d.state})")
    run(d, dog.IDLE_S + 1, "drawing", [(px, py)], moving=False)
    check(d.state in ("return", "lie"), f"heads back to bed after a while idle ({d.state})")
    run(d, 10, "drawing", [(px, py)], moving=False)
    check(d.on_bed(), "lies down on her bed again")

    # follow the player out of the Drawing Room into the Hall
    run(d, 1, "drawing", [(2.0, 1.2)], moving=True)
    hall = [(1.3, 1.0), (2.4, 1.6), (2.4, 2.4), (1.3, 1.0)]
    run(d, 12, "hall", hall, moving=True)
    check(d.room == "hall", f"follows through the doorway into the Hall ({d.room})")

    # into the kitchen: she follows, then lingers
    kd = [(9.0, 1.0), (9.5, 2.5), (8.8, 3.2), (9.0, 1.0)]
    px, py = run(d, 15, "kd", kd, moving=True)
    check(d.room == "kd", f"follows into the Kitchen ({d.room})")
    dist = math.hypot(d.x - px, d.y - py)
    check(dist < 2.0, f"stays closer in the Kitchen ({dist:.2f} tiles)")
    run(d, dog.IDLE_S + 5, "kd", [(px, py)], moving=False)
    check(d.state == "sit" and d.room == "kd", f"lingers, sitting hopefully, in the Kitchen ({d.state})")
    run(d, dog.IDLE_S_KITCHEN - dog.IDLE_S, "kd", [(px, py)], moving=False)
    check(d.state in ("return", "lie"), f"eventually gives up and goes back ({d.state})")

    # nobody downstairs: straight back to bed, and she never goes up
    d2 = dog.Dog()
    run(d2, 1, "drawing", [(4.0, 4.0)], moving=True)
    run(d2, 8, "hall", hall, moving=True)
    run(d2, 1, "landing", [(2.0, 4.0)], moving=True)
    check(d2.state in ("return", "lie"), f"goes back to bed when everyone is upstairs ({d2.state})")
    run(d2, 25, "landing", [(2.0, 4.0)], moving=True)
    check(d2.on_bed(), "and is lying on her bed")
    check(set(d.log) <= {"wake", "follow", "wait", "sit", "return", "lie"}, "only known states")
    print("RESULT:", "all OK" if not FAIL else f"{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
