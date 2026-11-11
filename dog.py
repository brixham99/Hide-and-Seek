"""Myrtle, the family's black Labrador.

She lies asleep on her teal bed in the Drawing Room and takes no notice of
anything until someone comes into the room she is in. Then it is a coin
toss (FOLLOW_P): either she gets up and follows a little way behind, finding
her way room to room through the open doorways (she never goes upstairs),
or she stays put on her bed. While she follows she tosses again every
20-40 s (REROLL_S); on a "no" she walks back to her bed and lies down, and
then waits for someone to come in again. So she follows about half the time.
In the Kitchen / Dining Room she keeps closer and hangs about longer,
sitting and looking up hopefully. When everyone stops she sits; after a
while idle, or when nobody is left downstairs, she goes back to bed.

She is simulated in every room all the time (no drawing) so she can appear
through a doorway; the game only draws her in the room on screen. She has
no collision with the player, so she can never trap or block anyone.

Positions are room-local tiles, like the player's (house.py).
"""
import math
import random
from collections import deque

import house

DOWNSTAIRS = ("hall", "sitting", "drawing", "kd", "boot", "utility", "office", "wc")
BED_ROOM = "drawing"
BED = (1.35, 4.55, 2.55, 5.65)            # the teal dog bed (rooms/mock_drawing_room.py), room-local tiles
BED_XY = ((BED[0] + BED[2]) / 2, (BED[1] + BED[3]) / 2)
BED_Z = 16                                # bed top, px
BED_FACING = "E"                          # lying with her nose towards +x (the room)
R = 0.18                                  # her footprint for the furniture checks (tiles)
GRID = 0.15                               # path grid
FOLLOW_D = 1.35                           # how far behind she stays (tiles)
FOLLOW_D_KITCHEN = 0.9
WALK = 2.5                                # tiles/s
TROT = 3.6                                # catching up
SIT_AFTER = 1.2                           # s after the player stops, before she sits
IDLE_S = 25.0                             # s of nobody moving before she goes back to bed
IDLE_S_KITCHEN = 50.0                     # she hangs about in the kitchen, hopefully
WAKE_S = 0.6                              # getting up off the bed
DOOR_CLEAR = 0.9                          # she won't sit this close to a doorway centre
REPATH_S = 0.35
FOLLOW_P = 0.5                            # chance she gets up / keeps following on each toss
REROLL_S = (20.0, 40.0)                   # seconds between tosses while she follows


def _portal_point(room, wall, a, b, depth=0.35):
    """Just through a doorway, on the far side of the wall line (room-local)."""
    rm = house.ROOMS[room]
    rw, rd = rm["rw"], rm["rd"]
    u = (a + b) / 2
    return {"S": (u, -depth), "N": (u, rd + depth), "E": (-depth, u), "W": (rw + depth, u)}[wall]


def _portal_mid(room, wall, a, b):
    return _portal_point(room, wall, a, b, 0.0)


class Grid:
    """A free/blocked grid over one room (and its doorway mouths)."""

    def __init__(self, room):
        rm = house.ROOMS[room]
        self.room = room
        self.x0, self.y0 = -0.6, -0.6
        self.nx = int((rm["rw"] + 1.2) / GRID) + 1
        self.ny = int((rm["rd"] + 1.2) / GRID) + 1
        self.ok = [[house.free(room, self.x0 + i * GRID, self.y0 + j * GRID, R) for j in range(self.ny)]
                   for i in range(self.nx)]

    def cell(self, x, y):
        return (min(self.nx - 1, max(0, round((x - self.x0) / GRID))),
                min(self.ny - 1, max(0, round((y - self.y0) / GRID))))

    def xy(self, c):
        return self.x0 + c[0] * GRID, self.y0 + c[1] * GRID

    def nearest_free(self, x, y, avoid=()):
        c0 = self.cell(x, y)
        best, bd = None, 1e9
        r = 0
        while best is None and r < max(self.nx, self.ny):
            for i in range(c0[0] - r, c0[0] + r + 1):
                for j in range(c0[1] - r, c0[1] + r + 1):
                    if 0 <= i < self.nx and 0 <= j < self.ny and self.ok[i][j]:
                        px, py = self.xy((i, j))
                        if any(math.hypot(px - ax, py - ay) < rad for ax, ay, rad in avoid):
                            continue
                        d = math.hypot(px - x, py - y)
                        if d < bd:
                            best, bd = (i, j), d
            r += 1
        return best

    def path(self, sx, sy, tx, ty):
        """8-way BFS from (sx, sy) to the free cell nearest (tx, ty): list of points."""
        start = self.cell(sx, sy)
        if not self.ok[start[0]][start[1]]:
            start = self.nearest_free(sx, sy) or start
        goal = self.nearest_free(tx, ty)
        if goal is None:
            return []
        prev = {start: None}
        q = deque([start])
        steps = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
        while q:
            c = q.popleft()
            if c == goal:
                break
            for dx, dy in steps:
                n = (c[0] + dx, c[1] + dy)
                if n in prev or not (0 <= n[0] < self.nx and 0 <= n[1] < self.ny) or not self.ok[n[0]][n[1]]:
                    continue
                if dx and dy and not (self.ok[c[0] + dx][c[1]] and self.ok[c[0]][c[1] + dy]):
                    continue                           # no corner cutting
                prev[n] = c
                q.append(n)
        if goal not in prev:
            return []
        out = []
        c = goal
        while c is not None:
            out.append(self.xy(c))
            c = prev[c]
        out.reverse()
        return self._smooth(out)

    def _clear(self, a, b):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(d / (GRID * 0.5)))
        for i in range(n + 1):
            t = i / n
            c = self.cell(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if not self.ok[c[0]][c[1]]:
                return False
        return True

    def _smooth(self, pts):
        if len(pts) <= 2:
            return pts[1:] if len(pts) == 2 else pts
        out = []
        i = 0
        while i < len(pts) - 1:
            j = len(pts) - 1
            while j > i + 1 and not self._clear(pts[i], pts[j]):
                j -= 1
            out.append(pts[j])
            i = j
        return out


def _room_graph():
    g = {r: [] for r in DOWNSTAIRS}
    for (ra, wa, a0, a1), (rb, wb, b0, b1) in house.PORTALS:
        if ra in g and rb in g:
            g[ra].append((rb, (wa, a0, a1)))
            g[rb].append((ra, (wb, b0, b1)))
    return g


class Dog:
    def __init__(self, seed=None, rng=None, follow_p=FOLLOW_P):
        """`seed` (or an `rng` with random() and uniform()) makes her coin
        tosses repeatable, for the tests."""
        self.rng = rng or random.Random(seed)
        self.follow_p = follow_p
        self.p_prev_room = None            # the player's room last tick, to see them come in
        self.reroll = 0.0                  # seconds to the next toss while following
        self.room = BED_ROOM
        self.x, self.y = BED_XY
        self.facing = BED_FACING           # engine direction: E (+x), S (+y), W (-x), N (-y)
        self.state = "lie"                 # lie, wake, follow, wait, sit, return
        self.t_state = 0.0
        self.idle = 0.0                    # seconds since anyone moved
        self.still = 0.0                   # seconds since the player last moved
        self.dist = 0.0                    # walked, for the walk cycle
        self.moving = False
        self.path = []
        self.path_key = None
        self.repath = 0.0
        self.sit_spot = None
        self.p_last = None                 # player's last spot and heading, to trail behind them
        self.p_head = (0.0, 1.0)
        self._grids = {}
        self._graph = _room_graph()
        self.log = []                      # state changes and tosses ("stay", "keep"), for the tests

    # ---------------------------------------------------------------- helpers
    def grid(self, room):
        if room not in self._grids:
            self._grids[room] = Grid(room)
        return self._grids[room]

    def _set(self, st):
        if st != self.state:
            self.state = st
            self.t_state = 0.0
            self.path = []
            self.path_key = None
            self.log.append(st)

    def on_bed(self):
        return self.state == "lie" and self.room == BED_ROOM

    def _next_hop(self, to_room):
        """The doorway (wall, a, b) out of this room on the way to `to_room`."""
        if self.room == to_room:
            return None
        prev = {self.room: None}
        q = deque([self.room])
        while q:
            r = q.popleft()
            if r == to_room:
                break
            for n, door in self._graph[r]:
                if n not in prev:
                    prev[n] = (r, door)
                    q.append(n)
        if to_room not in prev:
            return None
        r = to_room
        while prev[r][0] != self.room:
            r = prev[r][0]
        return prev[r][1]

    def _goal(self, room, x, y):
        """Where to head in this room for a goal (room, x, y): the goal itself,
        or just through the next doorway towards it."""
        if room == self.room:
            return x, y, True
        hop = self._next_hop(room)
        if hop is None:
            return self.x, self.y, True
        return (*_portal_point(self.room, *hop), False)

    def _walk_to(self, gx, gy, speed, dt, key):
        g = self.grid(self.room)
        self.repath -= dt
        if not self.path or self.repath <= 0 or key != self.path_key:
            self.path = g.path(self.x, self.y, gx, gy)
            self.path_key = key
            self.repath = REPATH_S
        if not self.path:
            return False
        tx, ty = self.path[0]
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        step = speed * dt
        if d <= step:
            self.x, self.y = tx, ty
            self.path.pop(0)
        else:
            self.x += dx / d * step
            self.y += dy / d * step
        moved = min(step, d)
        self.dist += moved
        self.moving = moved > 1e-4
        if d > 1e-4:
            self.facing = ("E" if dx > 0 else "W") if abs(dx) >= abs(dy) else ("S" if dy > 0 else "N")
        cr = house.crossing(self.room, self.x, self.y)
        if cr and cr[0] in DOWNSTAIRS:
            self.room, self.x, self.y = cr
            self.path = []
            self.path_key = None
        return True

    def _face_towards(self, x, y):
        dx, dy = x - self.x, y - self.y
        if abs(dx) + abs(dy) > 1e-3:
            self.facing = ("E" if dx > 0 else "W") if abs(dx) >= abs(dy) else ("S" if dy > 0 else "N")

    def _near_door(self, x, y):
        for wall, a, b, _ in house.portals_of(self.room):
            mx, my = _portal_mid(self.room, wall, a, b)
            if math.hypot(x - mx, y - my) < DOOR_CLEAR:
                return True
        return False

    def _toss(self):
        return self.rng.random() < self.follow_p

    def _next_toss(self):
        self.reroll = self.rng.uniform(*REROLL_S)

    # ---------------------------------------------------------------- update
    def update(self, dt, p_room, px, py, p_moving):
        """One tick. p_* is the player (whoever is walking about)."""
        entered = self.p_prev_room is not None and self.p_prev_room != p_room and p_room == self.room
        self.p_prev_room = p_room
        self.t_state += dt
        self.moving = False
        down = p_room in DOWNSTAIRS
        if p_moving:
            self.idle = 0.0
            self.still = 0.0
        else:
            self.idle += dt
            self.still += dt
        if self.p_last and self.p_last[0] == p_room:
            hx, hy = px - self.p_last[1], py - self.p_last[2]
            hd = math.hypot(hx, hy)
            if hd > 1e-3:
                self.p_head = (hx / hd, hy / hd)
        self.p_last = (p_room, px, py)
        kitchen = p_room == "kd" and self.room == "kd"
        near_d = FOLLOW_D_KITCHEN if kitchen else FOLLOW_D
        idle_s = IDLE_S_KITCHEN if kitchen else IDLE_S
        same = self.room == p_room
        dist = math.hypot(px - self.x, py - self.y) if same else 99.0

        if not down or (self.state in ("sit", "wait", "follow") and self.idle > idle_s):
            if self.state not in ("lie", "return"):
                self._set("return")
        if self.state in ("follow", "wait", "sit"):
            self.reroll -= dt
            if self.reroll <= 0:
                if self._toss():
                    self.log.append("keep")
                    self._next_toss()
                else:
                    self._set("return")          # had enough: back to bed
        if self.state == "lie":
            # asleep until someone comes into her room; then a coin toss
            if entered:
                if self._toss():
                    self._next_toss()
                    self._set("wake")
                else:
                    self.log.append("stay")
            return
        if self.state == "wake":
            if self.t_state >= WAKE_S:
                self._set("follow")
            return
        if self.state == "return":
            gx, gy, here = self._goal(BED_ROOM, *BED_XY)
            self._walk_to(gx, gy, WALK, dt, ("bed", self.room))
            if self.room == BED_ROOM and math.hypot(self.x - BED_XY[0], self.y - BED_XY[1]) < 0.12:
                self.x, self.y = BED_XY
                self.facing = BED_FACING
                self._set("lie")
            return
        if self.state == "follow":
            if same and dist <= near_d:
                self._set("wait")
                return
            # trail a little behind and to one side of them, not underfoot
            hx, hy = self.p_head
            tx, ty = px - hx * near_d * 0.8 - hy * 0.4, py - hy * near_d * 0.8 + hx * 0.4
            gx, gy, here = self._goal(p_room, tx, ty)
            speed = TROT if (not same or dist > 3.0 or kitchen) else WALK
            key = ("p", self.room, round(tx * 2), round(ty * 2)) if here else ("door", self.room, p_room)
            self._walk_to(gx, gy, speed, dt, key)
            return
        if self.state == "wait":
            self._face_towards(px, py) if same else None
            if not same or dist > near_d + 0.45:
                self._set("follow")
                return
            if self.still >= SIT_AFTER:
                # don't sit in a doorway: settle a little into the room first
                if self._near_door(self.x, self.y):
                    g = self.grid(self.room)
                    avoid = [(*_portal_mid(self.room, w, a, b), DOOR_CLEAR) for w, a, b, _ in house.portals_of(self.room)]
                    c = g.nearest_free(self.x, self.y, avoid)
                    self.sit_spot = g.xy(c) if c else None
                else:
                    self.sit_spot = None
                self._set("sit")
            return
        if self.state == "sit":
            if self.sit_spot is not None:
                sx, sy = self.sit_spot
                self._walk_to(sx, sy, WALK, dt, ("sit", sx, sy))
                if math.hypot(self.x - sx, self.y - sy) < 0.08:
                    self.sit_spot = None
                return
            if same:
                self._face_towards(px, py)        # looking up at them, hopefully
            if p_moving and (not same or dist > near_d + 0.45):
                self._set("follow")

    # ---------------------------------------------------------------- drawing
    def pose(self):
        """'lie', 'sit', 'walk' or 'stand' for the sprite."""
        if self.state == "lie":
            return "lie"
        if self.moving:
            return "walk"
        if self.state == "sit" and self.sit_spot is None:
            return "sit"
        return "stand"
