"""Holly as the player with Archie wandering in the same room, both cameras,
and a sprite sheet of both children: python tools/holly_shots.py out_dir"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import view_shot as vs  # noqa: E402
import pygame  # noqa: E402
import game  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/holly"
os.makedirs(OUT, exist_ok=True)
g = game.Game(vs.scr, player="holly")
for flip in (False, True):
    # Holly in the Drawing Room, Archie walking past the coffee table, Myrtle on her bed
    g = vs.shot(os.path.join(OUT, f"drawing{'_r' if flip else ''}.png"), "drawing", 3.4, 4.6, flip,
                (dogx := 1.95, 5.1), "W" if not flip else "E", g, True, None, (5.5, 4.6, "W"))
    g.npc.moving = True
    g.npc.dist = 0.4
    g._paint_view(g.frame, g.view)
    g._hint = g._make_hint()
    g._hud_on(g.frame)
    pygame.image.save(g.frame, os.path.join(OUT, f"drawing{'_r' if flip else ''}.png"))
# sprite sheet: rows Archie, Holly; standing in each facing then the 8 walk frames (se)
S = 1
W, H = 96, 184
sheet = pygame.Surface((W * 12 + 120, H * 2 * 2 + 20))
sheet.fill((206, 190, 160))
f = pygame.font.Font(pygame.font.match_font("dejavusans", bold=True), 22)
for r, name in enumerate(game.CHILDREN):
    stand, walk, meta = g.kids[name]
    y0 = 10 + r * H * 2
    sheet.blit(f.render(game.NAMES[name], True, (40, 30, 20)), (10, y0 + 40))
    for c, k in enumerate(("se", "sw", "nw", "ne")):
        sheet.blit(stand[k], (120 + c * W, y0))
        sheet.blit(f.render(k.upper(), True, (40, 30, 20)), (120 + c * W + 30, y0 + H - 4))
    for c, k in enumerate(("se", "sw")):
        sheet.blit(f.render(f"Walk {k.upper()}", True, (40, 30, 20)), (10, y0 + c * H + 120))
        for i in range(8):
            sheet.blit(walk[k][i], (120 + (4 + i) * W, y0 + c * H))
pygame.image.save(sheet, os.path.join(OUT, "sheet.png"))
