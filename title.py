"""Title screen: the front of the house (assets/title/house.png, painted by
tools/make_title.py), with Archie, Holly and Myrtle on the lawn.

Left / Right (keys, D-pad or stick) chooses who you play, Archie or Holly; the
chosen one stands in a gold ring with a gold name tag. Press A / Cross /
Enter / Space to start. Esc (or holding Back / Share) quits.
While it shows, the room images can be building in the background; a small
bar at the bottom says how far that has got.
"""
import math
import os

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "assets", "title", "house.png")
CHARS = os.path.join(HERE, "assets", "characters")
MYRTLE = os.path.join(HERE, "assets", "myrtle")

TITLE = "Hide and Seek"
BRAND = "Anderson Family - Gaming Creations"
MADE = "\u00a9 2026 - Made in England"
CREAM = (250, 242, 222)
GOLD = (214, 172, 96)
INK = (22, 18, 24)
CHOICES = ("archie", "holly")                     # left to right, as on the lawn
NAMES = {"archie": "Archie", "holly": "Holly"}
FEET = {"archie": (186, 640), "holly": (288, 640)}   # where they stand on the lawn


def font(size, bold=False, italic=False):
    for name in ("liberation serif", "dejavuserif", "dejavu serif", "times new roman", "georgia", "freeserif",
                 "noto serif"):
        path = pygame.font.match_font(name, bold=bold, italic=italic)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size + 10)


def shadow_text(surf, f, text, pos, col=CREAM, shadow=INK, off=3, anchor="topleft"):
    img = f.render(text, True, col)
    sh = f.render(text, True, shadow)
    r = img.get_rect(**{anchor: pos})
    for dx, dy in ((off, off), (off - 1, off), (off, off - 1)):
        surf.blit(sh, r.move(dx, dy))
    surf.blit(img, r)
    return r


def panel(size, alpha=150, radius=14):
    p = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(p, (16, 14, 20, alpha), p.get_rect(), border_radius=radius)
    return p


class TitleScreen:
    def __init__(self, size=(1280, 720)):
        self.size = size
        art = pygame.image.load(ART)
        self.bg = pygame.transform.smoothscale(art, size).convert() if art.get_size() != size else art.convert()
        self.f_title = font(80, bold=True)
        self.f_beta = font(22, bold=True)
        self.f_brand = font(26, italic=True)
        self.f_prompt = font(30, bold=True)
        self.f_small = font(18)
        kids = {}
        for n in CHOICES:
            img = pygame.image.load(os.path.join(CHARS, f"{n}_sw.png")).convert_alpha()
            img = pygame.transform.smoothscale(img, (int(img.get_width() * 0.86), int(img.get_height() * 0.86)))
            dim = img.copy()
            dim.fill((150, 146, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)
            kids[n] = (img, dim)
        self.kids = kids
        archie = pygame.image.load(os.path.join(CHARS, "archie_sw.png")).convert_alpha()
        myrtle = pygame.image.load(os.path.join(MYRTLE, "myrtle_se_sit.png")).convert_alpha()
        self.archie = pygame.transform.smoothscale(archie, (int(archie.get_width() * 0.86), int(archie.get_height() * 0.86)))
        self.myrtle = pygame.transform.smoothscale(myrtle, (int(myrtle.get_width() * 0.86), int(myrtle.get_height() * 0.86)))
        self.shadow = pygame.Surface((70, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (20, 40, 10, 90), self.shadow.get_rect())
        self.f_name = font(24, bold=True)
        self._static = {}

    def scene(self, choice=None):
        """The painting with Archie, Holly and Myrtle on the lawn, no text (also
        the Zen Station tile). With `choice`, that child stands in a gold ring
        and the other is a little in shadow."""
        s = self.bg.copy()
        for n, (fx, fy) in FEET.items():
            img, dim = self.kids[n]
            if choice == n:
                ring = pygame.Surface((96, 34), pygame.SRCALPHA)
                pygame.draw.ellipse(ring, (*GOLD, 120), ring.get_rect())
                pygame.draw.ellipse(ring, (255, 226, 150, 235), ring.get_rect(), 3)
                s.blit(ring, (fx - 48, fy - 17))
            s.blit(self.shadow, (fx - 35, fy - 11))
            pic = dim if (choice is not None and choice != n) else img
            s.blit(pic, (fx - pic.get_width() // 2 - 4, fy - int(162 * 0.86)))
        mx, my = 380, 652
        s.blit(pygame.transform.smoothscale(self.shadow, (84, 24)), (mx - 42, my - 12))
        s.blit(self.myrtle, (mx - int(90 * 0.86), my - int(118 * 0.86)))
        return s

    def _compose(self, choice=None):
        s = self.scene(choice)
        # title block
        tw = self.f_title.size(TITLE)[0]
        s.blit(panel((tw + 92, 162), 128, 18), (34, 30))
        r = shadow_text(s, self.f_title, TITLE, (66, 46), off=4)
        pygame.draw.rect(s, GOLD, pygame.Rect(68, r.bottom + 2, tw - 4, 3))
        # the Beta tag, a small gold label on the end of the title
        bt = self.f_beta.render("BETA", True, INK)
        tag = pygame.Rect(0, 0, bt.get_width() + 20, bt.get_height() + 6)
        tag.midleft = (r.right + 8, r.top + 30)
        pygame.draw.rect(s, GOLD, tag, border_radius=8)
        pygame.draw.rect(s, (120, 90, 40), tag, 2, border_radius=8)
        s.blit(bt, bt.get_rect(center=tag.center))
        shadow_text(s, self.f_brand, BRAND, (68, r.bottom + 16), col=(240, 226, 196), off=2)
        # footer
        shadow_text(s, self.f_small, MADE, (24, 720 - 14), col=(240, 232, 214), off=2, anchor="bottomleft")
        return s

    def draw(self, surf, t, start_label="A", quit_label="Back", build=None, choice="archie"):
        """build: (done, total) while the rooms are being built, else None.
        choice: who you will play, "archie" or "holly"."""
        if choice not in self._static:
            self._static[choice] = self._compose(choice)
        surf.blit(self._static[choice], (0, 0))
        # name tags under the children, the chosen one in gold
        for n, (fx, fy) in FEET.items():
            name = NAMES[n]
            w, h = self.f_name.size(name)
            tag = pygame.Rect(0, 0, w + 26, h + 8)
            tag.midtop = (fx - 4, fy + 14)
            if n == choice:
                pygame.draw.rect(surf, GOLD, tag, border_radius=10)
                pygame.draw.rect(surf, (120, 90, 40), tag, 2, border_radius=10)
                img = self.f_name.render(name, True, INK)
                surf.blit(img, img.get_rect(center=tag.center))
            else:
                surf.blit(panel(tag.size, 140, 10), tag.topleft)
                img = self.f_name.render(name, True, (214, 204, 186))
                surf.blit(img, img.get_rect(center=tag.center))
        prompt = f"Press {start_label} or Enter to Start"
        pw, ph = self.f_prompt.size(prompt)
        cx, cy = 820, 640
        surf.blit(panel((pw + 60, ph + 24), 150, 16), (cx - pw // 2 - 30, cy - ph // 2 - 12))
        glow = 0.55 + 0.45 * math.sin(t * 3.2)
        col = tuple(int(c * (0.7 + 0.3 * glow)) for c in CREAM)
        shadow_text(surf, self.f_prompt, prompt, (cx, cy), col=col, off=2, anchor="center")
        shadow_text(surf, self.f_small, f"Left / Right to Choose  \u00b7  Playing as {NAMES[choice]}",
                    (cx, cy - ph // 2 - 22), col=(240, 232, 214), off=2, anchor="midbottom")
        shadow_text(surf, self.f_small, f"Esc or Hold {quit_label} to Quit", (1280 - 24, 720 - 14),
                    col=(240, 232, 214), off=2, anchor="bottomright")
        if build:
            done, total = build
            bw = 300
            x, y = cx - bw // 2, cy + ph // 2 + 22
            pygame.draw.rect(surf, (16, 14, 20), (x - 2, y - 2, bw + 4, 10), border_radius=5)
            pygame.draw.rect(surf, GOLD, (x, y, int(bw * done / max(1, total)), 6), border_radius=3)
            shadow_text(surf, self.f_small, f"Getting the house ready\u2026 {done} of {total} rooms",
                        (cx, y + 12), col=(236, 226, 204), off=2, anchor="midtop")


class BuildScreen:
    """Full-screen progress while the rooms build (first run after an update)."""

    def __init__(self, title_screen):
        self.ts = title_screen
        self.dim = pygame.Surface(title_screen.size, pygame.SRCALPHA)
        self.dim.fill((10, 8, 14, 165))

    def draw(self, surf, t, done, total, eta=None, quit_label="Back"):
        surf.blit(self.ts.bg, (0, 0))
        surf.blit(self.dim, (0, 0))
        ts = self.ts
        shadow_text(surf, ts.f_title, TITLE, (640, 170), off=4, anchor="center")
        shadow_text(surf, ts.f_brand, BRAND, (640, 240), col=(240, 226, 196), off=2, anchor="center")
        shadow_text(surf, ts.f_prompt, "Getting the house ready\u2026", (640, 350), off=2, anchor="center")
        bw, bh = 640, 26
        x, y = 640 - bw // 2, 400
        pygame.draw.rect(surf, (30, 26, 34), (x - 4, y - 4, bw + 8, bh + 8), border_radius=12)
        frac = done / max(1, total)
        pygame.draw.rect(surf, GOLD, (x, y, max(bh, int(bw * frac)), bh), border_radius=10)
        # a moving sheen so it never looks stuck between rooms
        sx = x + int((t * 220) % (bw + 120)) - 60
        sheen = pygame.Surface((60, bh), pygame.SRCALPHA)
        sheen.fill((255, 255, 255, 40))
        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(x, y, max(bh, int(bw * frac)), bh))
        surf.blit(sheen, (sx, y))
        surf.set_clip(clip)
        msg = f"{done} of {total} rooms painted"
        if eta is not None and done < total:
            msg += f"  \u00b7  about {max(1, int(round(eta)))} s to go"
        shadow_text(surf, ts.f_small, msg, (640, y + bh + 18), col=(236, 226, 204), off=2, anchor="midtop")
        shadow_text(surf, ts.f_small, "This only happens the first time after an update.", (640, y + bh + 46),
                    col=(206, 196, 176), off=2, anchor="midtop")
        shadow_text(surf, ts.f_small, MADE, (24, 720 - 14), col=(240, 232, 214), off=2, anchor="bottomleft")
        shadow_text(surf, ts.f_small, f"Esc or Hold {quit_label} to Quit", (1280 - 24, 720 - 14),
                    col=(240, 232, 214), off=2, anchor="bottomright")
