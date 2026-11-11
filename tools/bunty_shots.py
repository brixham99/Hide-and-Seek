"""Bunty screenshots: python tools/bunty_shots.py out_dir
asleep on the sofa and an upstairs bed, on the island with Archie in the
Kitchen (both cameras), with Myrtle; crops around her, 2x."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import view_shot as vs  # noqa: E402
import pygame  # noqa: E402
import cat as catmod  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bunty"
os.makedirs(OUT, exist_ok=True)
g = None


def sp(name):
    s = catmod.SPOTS.get(name, catmod.ISLAND)
    return (*s["at"], "sleep", s["facing"])


SCENES = [
    ("sofa", "drawing", 2.6, 3.2, False, None, sp("sofa")),
    ("sofa_r", "drawing", 2.6, 3.2, True, None, sp("sofa")),
    ("holly", "holly", 2.6, 2.0, False, None, sp("holly")),
    ("holly_r", "holly", 2.6, 2.0, True, None, sp("holly")),
    ("archie_bed", "archie", 2.8, 3.6, False, None, sp("archie")),
    ("master", "master", 4.9, 2.2, False, None, sp("master")),
    ("master_r", "master", 4.9, 2.2, True, None, sp("master")),
    ("island", "kd", 11.0, 6.5, False, None, (12.7, 4.7, 96, "island", "S")),
    ("island_r", "kd", 11.0, 6.5, True, None, (12.7, 4.7, 96, "island", "N")),
    ("myrtle", "drawing", 4.4, 4.6, False, (2.0, 5.1), (3.4, 5.0, 0, "pause", "W")),
    ("myrtle_r", "drawing", 4.4, 4.6, True, (2.0, 5.1), (3.4, 5.0, 0, "pause", "E")),
    ("walk", "hall", 2.4, 5.0, False, None, (2.4, 6.4, 0, "wander", "N")),
]
for name, room, x, y, flip, dog, cat in SCENES:
    g = vs.shot(os.path.join(OUT, f"scene_{name}.png"), room, x, y, flip, dog, "S" if not flip else "N", g, True, cat)
    c = g.cat
    cx, cy = g.to_screen(g.view, c.x, c.y, c.z)
    full = pygame.image.load(os.path.join(OUT, f"scene_{name}.png"))
    r = pygame.Rect(0, 0, 360, 240)
    if name.startswith("myrtle"):          # Myrtle and Archie in the frame too
        dx, dy = g.to_screen(g.view, g.dog.x, g.dog.y)
        cx, cy = (cx + dx) / 2, (cy + dy) / 2
    r.center = (round(cx), round(cy) - 20)
    r.clamp_ip(full.get_rect())
    pygame.image.save(pygame.transform.scale(full.subsurface(r), (720, 480)), os.path.join(OUT, f"crop_{name}.png"))
    print(name, flush=True)
