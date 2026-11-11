"""Bunty, the family's small tabby cat.

She mostly sleeps: curled up on one of the beds upstairs (Archie's, Holly's,
the Master Bedroom's) or on the Drawing Room sofa. She picks a spot at the
start and now and then changes her mind when she goes back to bed. Between
naps she wanders slowly round the whole house, up and down the stairs,
stopping to sit in a room or two, then goes back to her spot.

She takes no notice of anyone, with one exception: when the player is in the
Kitchen and she is in it or next door (Hall, Drawing Room, Boot Room), she
trots over, hops up onto the Kitchen island and sits there watching them.
When they leave the Kitchen she hops down and goes back to her nap.

Like Myrtle she is simulated in every room all the time and the game only
draws her in the room on screen. No collision with the player. Positions are
room-local tiles (house.py); `z` is her height off the floor in px, as the
rooms are drawn (sofa seat 44, beds 53-54, island 96).
"""
import math
import random
from collections import deque

import dog as dogmod
import house

R = 0.14                                  # her footprint, tiles (smaller than Myrtle)
WALK = 1.05                               # tiles/s: an unhurried wander
TROT = 1.9                                # on her way to the island (there's food about)
HOP_S = 0.45                              # one hop up or down
HOP_ARC = 40                              # px above the straight line, mid-hop
SLEEP_S = (90.0, 240.0)                   # a nap
FIRST_NAP_S = (20.0, 90.0)
PAUSE_S = (4.0, 10.0)                     # sitting about while she wanders
STOPS = (1, 3)                            # rooms she stops in on one wander
NEW_SPOT_P = 0.3                          # chance she picks a new bed when she goes back
KITCHEN_NEAR = ("kd", "hall", "drawing", "boot")
REACT_S = (1.0, 2.5)                      # before she notices the player in the kitchen
LEAVE_S = 1.5                             # player gone from the kitchen this long: she hops down
REPATH_S = 0.5

# name: room, spot (x, y, z px), approach (floor point she hops from), the
# furniture's footprint (for drawing her on top of it), how she lies
SPOTS = {
    "sofa":   dict(room="drawing", at=(4.6, 1.0, 44), approach=(4.6, 1.75), box=(3.45, 0.0, 7.3, 1.55), facing="W"),
    "archie": dict(room="archie", at=(5.45, 4.3, 53), approach=(4.4, 4.3), box=(4.60, 2.35, 6.35, 5.95), facing="S"),
    "holly":  dict(room="holly", at=(4.4, 4.35, 54), approach=(4.4, 3.35), box=(3.38, 3.58, 6.78, 5.14), facing="W"),
    "master": dict(room="master", at=(3.4, 5.2, 54), approach=(4.65, 5.2), box=(1.70, 4.18, 4.44, 7.62), facing="N"),
}
ISLAND = dict(room="kd", at=(12.7, 4.7, 96), approach=(12.7, 5.7), box=(10.1, 3.8, 13.5, 5.4), facing="S")


class Grid(dogmod.Grid):
    """Myrtle's path grid with Bunty's smaller footprint (or `r`, for the
    children)."""
    def __init__(self, room, r=R):
        rm = house.ROOMS[room]
        self.room = room
        self.r = r
        self.x0, self.y0 = -0.6, -0.6
        self.nx = int((rm["rw"] + 1.2) / dogmod.GRID) + 1
        self.ny = int((rm["rd"] + 1.2) / dogmod.GRID) + 1
        self.ok = [[house.free(room, self.x0 + i * dogmod.GRID, self.y0 + j * dogmod.GRID, r) for j in range(self.ny)]
                   for i in range(self.nx)]

    def path(self, sx, sy, tx, ty):
        """Myrtle's path, but if the straight run from where she actually is
        to its first point would clip furniture, go via her own cell first."""
        out = super().path(sx, sy, tx, ty)
        if out and not self._clear((sx, sy), out[0]):
            c = self.cell(sx, sy)
            if not self.ok[c[0]][c[1]]:
                c = self.nearest_free(sx, sy) or c
            out.insert(0, self.xy(c))
        return out

    def _clear(self, a, b):
        """A straight run is clear only if her whole footprint stays off the
        furniture all the way (no shaving table corners)."""
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(d / 0.05))
        for i in range(n + 1):
            t = i / n
            if not house.free(self.room, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, self.r * 0.9):
                return False
        return True


def _link_centre(link, r=R):
    """A point inside a stair / arch zone that she (footprint r) can stand on."""
    x = (link["x0"] + link["x1"]) / 2
    room = link["room"]
    for y in [link["y0"] + (link["y1"] - link["y0"]) * t for t in (0.5, 0.3, 0.7, 0.15, 0.85)]:
        if house.free(room, x, y, r):
            return x, y
    return x, (link["y0"] + link["y1"]) / 2


def _house_graph():
    """Every room, joined by its doorways, the stairs and the landing arch."""
    g = {r: [] for r in house.ROOMS}
    for (ra, wa, a0, a1), (rb, wb, b0, b1) in house.PORTALS:
        g[ra].append((rb, ("door", wa, a0, a1)))
        g[rb].append((ra, ("door", wb, b0, b1)))
    for link in list(house.STAIR_LINKS) + list(house.ARCH_LINKS):
        g[link["room"]].append((link["dest"], ("link", link)))
    return g


def _facing(dx, dy):
    return ("E" if dx > 0 else "W") if abs(dx) >= abs(dy) else ("S" if dy > 0 else "N")


class Cat:
    r = R                                  # footprint for paths (the children use theirs)
    def __init__(self, seed=None, rng=None, spot=None):
        """`seed` / `rng` make her choices repeatable (tests); `spot` picks
        where she starts asleep (default: a random one of SPOTS)."""
        self.rng = rng or random.Random(seed)
        self.spot = spot or self.rng.choice(sorted(SPOTS))
        sp = SPOTS[self.spot]
        self.room = sp["room"]
        self.x, self.y, self.z = sp["at"]
        self.facing = sp["facing"]
        self.state = "sleep"               # sleep, wander, pause, return, to_island, island, hop
        self.t_state = 0.0
        self.timer = self.rng.uniform(*FIRST_NAP_S)
        self.dist = 0.0
        self.moving = False
        self.perch = sp                    # the furniture she is on (None on the floor)
        self.path = []
        self.path_key = None
        self.repath = 0.0
        self.stops = []                    # wander: [(room, x, y)]
        self.hop = None                    # (from xyz, to xyz, then-state, perch after)
        self.kitchen_seen = 0.0            # how long the player has been in the kitchen near her
        self.kitchen_gone = 0.0
        self._react_s = REACT_S[1]
        self._grids = {}
        self._graph = _house_graph()
        self.log = []                      # state changes, spot changes, room changes (tests)

    # ---------------------------------------------------------------- helpers
    def grid(self, room):
        if room not in self._grids:
            self._grids[room] = Grid(room, self.r)
        return self._grids[room]

    def _set(self, st):
        if st != self.state:
            self.state = st
            self.t_state = 0.0
            self.path = []
            self.path_key = None
            self.log.append(st)

    def on_furniture(self):
        return self.z > 0.5

    def _next_hop(self, to_room):
        if self.room == to_room:
            return None
        prev = {self.room: None}
        q = deque([self.room])
        while q:
            r = q.popleft()
            if r == to_room:
                break
            for n, edge in self._graph[r]:
                if n not in prev:
                    prev[n] = (r, edge)
                    q.append(n)
        if to_room not in prev:
            return None
        r = to_room
        while prev[r][0] != self.room:
            r = prev[r][0]
        return prev[r][1]

    def _go(self, room, x, y, speed, dt):
        """A step towards (room, x, y) through doors and up / down stairs.
        True when she is there."""
        if room == self.room:
            if math.hypot(self.x - x, self.y - y) < 0.1:
                return True
            self._walk_to(x, y, speed, dt, ("here", room, round(x, 2), round(y, 2)))
            if not self.path:
                return True                          # as near as she can get (or a spot she can't reach)
            return False
        edge = self._next_hop(room)
        if edge is None:
            return True
        if edge[0] == "door":
            gx, gy = dogmod._portal_point(self.room, *edge[1:])
            self._walk_to(gx, gy, speed, dt, ("door", self.room, edge[1:]))
            return False
        link = edge[1]
        cx, cy = _link_centre(link, self.r)
        self._walk_to(cx, cy, speed, dt, ("link", self.room, link["dest"]))
        if math.hypot(self.x - cx, self.y - cy) < 0.2:
            dest = house.stair_crossing(self.room, cx, cy)
            if dest:
                self._move_to_room(*dest)
        return False

    def _move_to_room(self, room, x, y):
        self.room, self.x, self.y = room, x, y
        self.path = []
        self.path_key = None
        self.log.append(("room", room))

    def _walk_to(self, gx, gy, speed, dt, key):
        g = self.grid(self.room)
        self.repath -= dt
        if not self.path or self.repath <= 0 or key != self.path_key:
            self.path = g.path(self.x, self.y, gx, gy)
            self.path_key = key
            self.repath = REPATH_S
        if not self.path:
            return
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
            self.facing = _facing(dx, dy)
        cr = house.crossing(self.room, self.x, self.y)
        if cr:
            self._move_to_room(*cr)

    def _start_hop(self, to, then, perch):
        frm = (self.x, self.y, self.z)
        self.facing = _facing(to[0] - frm[0], to[1] - frm[1])
        self.hop = (frm, to, then, perch)
        self._set("hop")

    def _random_point(self, room):
        """A free spot in `room` that is joined to its doorways (not a pocket
        behind the bed)."""
        g = self.grid(room)
        free = self._reachable(room)
        rm = house.ROOMS[room]
        inside = [c for c in free if 0.3 < g.xy(c)[0] < rm["rw"] - 0.3 and 0.3 < g.xy(c)[1] < rm["rd"] - 0.3]
        c = self.rng.choice(inside or free)
        return g.xy(c)

    def _reachable(self, room):
        if not hasattr(self, "_reach"):
            self._reach = {}
        if room not in self._reach:
            g = self.grid(room)
            seeds = [dogmod._portal_point(room, w, a, b, -0.4) for w, a, b, _ in house.portals_of(room)]
            seeds += [_link_centre(lk, self.r) for lk in list(house.STAIR_LINKS) + list(house.ARCH_LINKS) if lk["room"] == room]
            seen = set()
            q = deque()
            for sx, sy in seeds:
                c = g.nearest_free(sx, sy)
                if c and c not in seen:
                    seen.add(c)
                    q.append(c)
            while q:
                c = q.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (c[0] + dx, c[1] + dy)
                    if 0 <= n[0] < g.nx and 0 <= n[1] < g.ny and g.ok[n[0]][n[1]] and n not in seen:
                        seen.add(n)
                        q.append(n)
            self._reach[room] = sorted(seen)
        return self._reach[room]

    def _plan_wander(self):
        rooms = sorted(r for r in house.ROOMS if r != self.room)
        n = self.rng.randint(*STOPS)
        self.stops = []
        for _ in range(n):
            r = self.rng.choice(rooms)
            self.stops.append((r, *self._random_point(r)))

    # ---------------------------------------------------------------- update
    def update(self, dt, p_room, px, py, p_moving=False):
        self.t_state += dt
        self.moving = False
        near_kitchen = p_room == "kd" and self.room in KITCHEN_NEAR
        if near_kitchen:
            if self.kitchen_seen == 0.0:             # a moment before she notices them
                self._react_s = self.rng.uniform(*REACT_S)
            self.kitchen_seen += dt
        else:
            self.kitchen_seen = 0.0
        self.kitchen_gone = 0.0 if p_room == "kd" else self.kitchen_gone + dt

        if self.state == "hop":
            frm, to, then, perch = self.hop
            s = min(1.0, self.t_state / HOP_S)
            self.x = frm[0] + (to[0] - frm[0]) * s
            self.y = frm[1] + (to[1] - frm[1]) * s
            self.z = frm[2] + (to[2] - frm[2]) * s + HOP_ARC * 4 * s * (1 - s)
            if s >= 1.0:
                self.x, self.y, self.z = to
                self.perch = perch
                self.hop = None
                self._set(then)
                if then == "sleep":
                    self.timer = self.rng.uniform(*SLEEP_S)
                    self.facing = SPOTS[self.spot]["facing"]
            return

        # the kitchen: up onto the island while they're in there
        if (near_kitchen and self.kitchen_seen >= self._react_s
                and self.state not in ("to_island", "island")):
            if self.on_furniture():
                ax, ay = self.perch["approach"]
                self._start_hop((ax, ay, 0), "to_island", None)
            else:
                self._set("to_island")
            return
        if self.state == "to_island":
            if p_room != "kd":
                self._set("return")
                return
            ax, ay = ISLAND["approach"]
            if self._go(ISLAND["room"], ax, ay, TROT, dt):
                self.x, self.y = ax, ay
                self._start_hop(ISLAND["at"], "island", ISLAND)
            return
        if self.state == "island":
            if p_room == "kd":
                self.facing = _facing(px - self.x, py - self.y)
            if self.kitchen_gone >= LEAVE_S:
                ax, ay = ISLAND["approach"]
                self._start_hop((ax, ay, 0), "return", None)
            return

        if self.state == "sleep":
            self.timer -= dt
            if self.timer <= 0:
                self._plan_wander()
                if self.on_furniture():
                    ax, ay = self.perch["approach"]
                    self._start_hop((ax, ay, 0), "wander", None)
                else:
                    self._set("wander")
            return
        if self.state == "wander":
            if not self.stops:
                self._set("return")
                return
            r, x, y = self.stops[0]
            if self._go(r, x, y, WALK, dt):
                self.stops.pop(0)
                self.timer = self.rng.uniform(*PAUSE_S)
                self._set("pause")
            return
        if self.state == "pause":
            self.timer -= dt
            if self.timer <= 0:
                self._set("wander")
            return
        if self.state == "return":
            if self.t_state < dt * 1.5 and self.rng.random() < NEW_SPOT_P:
                new = self.rng.choice(sorted(SPOTS))
                if new != self.spot:
                    self.spot = new
                    self.log.append(("spot", new))
            sp = SPOTS[self.spot]
            ax, ay = sp["approach"]
            if self._go(sp["room"], ax, ay, WALK, dt):
                self.x, self.y = ax, ay
                self._start_hop(sp["at"], "sleep", sp)

    # ---------------------------------------------------------------- drawing
    def pose(self):
        """'sleep', 'sit', 'walk', 'stand' or 'jump' for the sprite."""
        if self.state == "hop":
            return "jump"
        if self.state == "sleep":
            return "sleep"
        if self.moving:
            return "walk"
        if self.state in ("island", "pause"):
            return "sit"
        return "stand"
