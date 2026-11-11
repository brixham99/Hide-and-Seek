"""Compose cache/<view>_bg + _fg into one image: python tools/compose_view.py out_dir view..."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init(); pygame.display.set_mode((1, 1))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for v in sys.argv[2:]:
    bg = pygame.image.load(os.path.join(HERE, "cache", f"{v}_bg.png")).convert_alpha()
    bg.blit(pygame.image.load(os.path.join(HERE, "cache", f"{v}_fg.png")).convert_alpha(), (0, 0))
    pygame.image.save(bg, os.path.join(out, f"{v}.png"))
