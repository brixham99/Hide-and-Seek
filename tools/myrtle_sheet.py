#!/usr/bin/env python3
"""Contact sheet of Myrtle's sprites (all facings and poses), Archie for scale."""
import os
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import json  # noqa: E402
import pygame  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets")
out = sys.argv[1] if len(sys.argv) > 1 else "myrtle_sheet.png"
pygame.init()
pygame.display.set_mode((1, 1))
meta = json.load(open(os.path.join(A, "myrtle", "myrtle.json")))
fw, fh = meta["size"]
n = meta["frames"]
cols = 1 + n + 2 + 1                 # stand, walk frames, sit, lie, archie
W, H = cols * fw, 4 * fh + 40
sheet = pygame.Surface((W, H))
for r in range(4):
    sheet.fill((92, 66, 44) if r % 2 else (58, 44, 34), (0, 40 + r * fh, W, fh))   # light and dark boards
sheet.fill((24, 22, 24), (0, 0, W, 40))
f = pygame.font.Font(None, 26)
for i, t in enumerate(["stand"] + [f"walk {j + 1}" for j in range(n)] + ["sit", "lie", "Archie"]):
    sheet.blit(f.render(t, True, (236, 226, 200)), (i * fw + 10, 12))
for r, k in enumerate(meta["facings"]):
    y = 40 + r * fh
    imgs = [pygame.image.load(os.path.join(A, "myrtle", f"myrtle_{k}.png"))]
    s = pygame.image.load(os.path.join(A, "myrtle", f"myrtle_{k}_walk.png"))
    imgs += [s.subsurface((i * fw, 0, fw, fh)) for i in range(n)]
    imgs += [pygame.image.load(os.path.join(A, "myrtle", f"myrtle_{k}_{p}.png")) for p in ("sit", "lie")]
    for i, im in enumerate(imgs):
        sheet.blit(im, (i * fw, y))
    sheet.blit(f.render(k, True, (236, 226, 200)), (6, y + 6))
    ar = pygame.image.load(os.path.join(A, "characters", f"archie_{k}.png"))
    aw = json.load(open(os.path.join(A, "characters", "archie_walk.json")))["facings"][k]["anchor"]
    sheet.blit(ar, ((cols - 1) * fw + meta["anchor"][0] - aw[0], y + meta["anchor"][1] - aw[1]),
               )
pygame.image.save(sheet, out)
print(out)
