"""The other child: whichever of Archie and Holly you are not playing.

They wander the whole house on their own, up and downstairs, at a child's
walking pace: pick a room, walk there through the doorways, the stairs and
the landing arch, stand about for a bit, pick another. Pathing is Bunty's
(cat.py), on a child's footprint (house.R, the same as the player's), so
they keep clear of furniture and walls exactly as the player must. No
collision with the player, like Myrtle and Bunty.

Positions are room-local tiles (house.py).
"""
import random

import cat
import house

WALK = 2.0                     # tiles/s (the player walks at 3)
PAUSE_S = (4.0, 14.0)          # standing about in a room
STARTS = {                     # where each child is when the game starts
    "archie": ("archie", 2.4, 4.6, "S"),       # in his room, by the desk
    "holly": ("holly", 2.6, 2.0, "S"),         # in hers, by the desk
}


class Child(cat.Cat):
    r = house.R

    def __init__(self, name, seed=None, rng=None, start=None):
        self.name = name
        self.rng = rng or random.Random(seed)
        self.room, self.x, self.y, self.facing = start or STARTS[name]
        self.z = 0
        self.state = "pause"            # pause, wander
        self.t_state = 0.0
        self.timer = self.rng.uniform(1.0, 4.0)
        self.dist = 0.0
        self.moving = False
        self.perch = None
        self.path = []
        self.path_key = None
        self.repath = 0.0
        self.stops = []
        self._grids = {}
        self._graph = cat._house_graph()
        self.log = []

    def place(self, room, x, y, facing):
        """Put them somewhere (when the player swaps who they are)."""
        self.room, self.x, self.y, self.facing = room, x, y, facing
        self.path = []
        self.path_key = None
        self.stops = []
        self.timer = self.rng.uniform(*PAUSE_S)
        self._set("pause")

    def update(self, dt, *_):
        self.t_state += dt
        self.moving = False
        if self.state == "pause":
            self.timer -= dt
            if self.timer <= 0:
                r = self.rng.choice(sorted(rm for rm in house.ROOMS if rm != self.room))
                self.stops = [(r, *self._random_point(r))]
                self._set("wander")
            return
        if self.state == "wander":
            if not self.stops:
                self._set("pause")
                return
            r, x, y = self.stops[0]
            if self._go(r, x, y, WALK, dt):
                self.stops.pop(0)
                self.timer = self.rng.uniform(*PAUSE_S)
                self._set("pause")

    def pose(self):
        return "walk" if self.moving else "stand"
