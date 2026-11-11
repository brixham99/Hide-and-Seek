"""Render the reported scenes: python tools/kd_shots.py out_dir prefix"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import view_shot as vs
SCENES = [  # name, room, x, y, dog
    ("boot", "boot", 3.2, 1.7, (2.3, 2.0)),
    ("kitchen", "kd", 12.0, 2.4, None),
    ("kitchen_b", "kd", 14.5, 6.2, None),
    ("dining", "kd", 4.8, 3.2, None),
    ("dining_b", "kd", 6.3, 1.4, None),
]
out, pre = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
g = None
for name, room, x, y, dog in SCENES:
    for flip in (False, True):
        g = vs.shot(os.path.join(out, f"{pre}_{name}_{'south' if flip else 'north'}.png"), room, x, y, flip, dog, g=g)
