"""Pixel diff between two folders of composed views: python tools/diff_views.py A B OUT"""
import os, sys
import numpy as np
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
A, B, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
for f in sorted(os.listdir(A)):
    if not os.path.exists(os.path.join(B, f)):
        continue
    a = pygame.surfarray.array3d(pygame.image.load(os.path.join(A, f))).astype(int)
    b = pygame.surfarray.array3d(pygame.image.load(os.path.join(B, f))).astype(int)
    d = np.abs(a - b).sum(2) > 40
    print(f"{f:20s} {int(d.sum()):7d} px changed")
    if d.any():
        img = b.copy(); img[d] = (img[d] * 0.3 + np.array([255, 0, 255]) * 0.7)
        pygame.image.save(pygame.surfarray.make_surface(img.astype(np.uint8)), os.path.join(OUT, f))
