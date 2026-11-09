"""What you see through an open doorway: the neighbouring room, in its own
tiles, shifted onto this room's canvas (house_common.placed) and clipped to
the opening.

Origins match house.py. Closed doors (front door, boot-room back door, French
doors) are not drawn here.
"""
import house_common as hc

# house-grid origin of each room's (east wall, south wall) corner
HALL = (6.55, -8.25)
SITTING = (-0.75, -8.25)
DRAWING = (9.95, -8.0)
KD = (0.0, 0.0)             # kitchen + dining, world tiles
KITCHEN_VIEW = (8.2, 0.0)   # the kitchen picture's local origin (world x of the beam)
BOOT = (16.6, -0.65)
UTILITY = (16.6, 2.65)
OFFICE = (20.85, 2.65)
WC = (23.2, -0.65)

PINE = ((196, 116, 56), (178, 100, 46))
DARK = ((96, 62, 40), (78, 50, 32))
SLATE = ((196, 160, 84), (176, 104, 60), (118, 124, 98), (96, 98, 88), (208, 178, 104), (150, 128, 76))
FLAGS = ((128, 118, 104), (112, 104, 94), (138, 126, 108), (104, 98, 90))
TERR = (176, 84, 56)
LILAC = (196, 190, 204)
BLUE = (170, 184, 194)
GREEN = (46, 82, 72)
NAVY = (52, 64, 88)
CREAM = (232, 228, 216)
TEAL = (22, 88, 98)


def _at(here, there):
    return hc.placed(here[0] - there[0], here[1] - there[1])


def _floor(kind, x0, y0, x1, y1, seed=4):
    import paint
    w, h = max(0.4, x1 - x0), max(0.4, y1 - y0)
    if kind == "slate":
        tex = paint.slate(w, h, seed, SLATE)
    elif kind == "flags":
        tex = paint.flagstones(w, h, seed, FLAGS)
    elif kind == "quarry":
        tex = paint.quarry(w, h, seed, TERR)
    elif kind == "dark":
        tex = paint.timber(w, h, seed, DARK[0], DARK[1], along="y", plank=0.27)
    else:
        tex = paint.timber(w, h, seed, PINE[0], PINE[1], along="x", plank=0.27)
    paint.stamp(tex, x0, y0, x1, y1, 0)


def _wall_y(y, x0, x1, col, z1=None):
    hc.qy(y, x0, x1, 0, hc.WALL_H if z1 is None else z1, hc.shade(col, hc.KY))


def _wall_x(x, y0, y1, col, z1=None):
    hc.qx(x, y0, y1, 0, hc.WALL_H if z1 is None else z1, hc.shade(col, hc.KX))


# ---------------------------------------------------------------- rooms
def kitchen_zone(x0, y0, x1, y1):
    """Slate floor, cream walls and the island, in kitchen world tiles."""
    _floor("slate", x0, y0, x1, y1, seed=8)
    _wall_y(8.4, max(0, x0), min(16.4, x1), CREAM)          # garden wall, far side of this view
    # island: chunky pine top on a pale base (only the part that falls in the opening shows)
    hc.box(10.15, 3.85, 13.45, 5.35, 8, 84, (204, 206, 202))
    hc.box(10.02, 3.72, 13.58, 5.48, 84, 96, (200, 156, 100))
    for sx, sy in ((10.8, 3.25), (11.8, 3.25), (12.8, 3.25)):
        hc.cyl(sx, sy, 0.22, 0, 68, (176, 122, 70))
    # west-end run the boot door looks onto: bins and the end of the units
    hc.cyl(15.55, 7.5, 0.27, 0, 70, (178, 182, 186))
    hc.box(14.6, 6.9, 16.3, 8.25, 0, 90, (240, 238, 232))
    hc.box(14.5, 6.85, 16.35, 8.3, 90, 96, (58, 60, 66))


def hall_zone(east_wall=True):
    """Dark boards, lilac walls, the runner and the stair, in hall tiles.
    east_wall is the one the sitting room looks through, so that view skips it."""
    _floor("dark", 0, 0, 3.2, 8.05, seed=14)
    import paint
    paint.stamp(paint.rug(1.2, 7.3, "hall", 4), 1.72, 0.45, 2.92, 7.75, 0.6)
    if east_wall:
        _wall_x(0, 0, 8.05, LILAC)
    _wall_y(0, 0, 3.2, LILAC)
    # front door, shut, at the far end
    hc.qx(0.01, 1.0, 2.2, 0, 154, hc.shade((244, 242, 236), hc.KX))
    # carpeted stair against the east wall
    hc.box(0.0, 3.0, 1.62, 8.0, 0, 120, (198, 188, 172))
    hc.box(1.5, 3.0, 1.7, 8.0, 0, 160, (240, 238, 232))


def sitting_zone():
    """Honey boards, blue-grey south wall, navy sofa and the bookcase."""
    _floor("honey", 0, 0, 7.1, 6.6, seed=4)
    _wall_y(0, 0, 7.1, BLUE)
    _wall_x(0, 0, 6.6, BLUE)
    hc.box(0.35, 0.2, 4.7, 1.55, 0, 52, NAVY)                 # sofa along the south wall
    hc.box(5.4, 0.05, 6.95, 0.6, 0, 92, (84, 56, 38))         # bookcase by the hall door
    import paint
    paint.stamp(paint.rug(3.8, 3.5, "sitting", 31), 1.7, 1.5, 5.5, 5.0, 0.6)


def drawing_zone(east_wall=True):
    """Snug: green walls, boards, the red rug, sofa and piano.
    The hall looks through the east wall, so that view skips it."""
    _floor("honey", 0, 0, 7.3, 7.8, seed=4)
    _wall_y(0, 0, 7.3, GREEN)
    if east_wall:
        _wall_x(0, 0, 7.8, GREEN)
    import paint
    paint.stamp(paint.rug(4.8, 5.5, "drawing", 12), 1.25, 1.05, 6.05, 6.55, 0.6)
    hc.box(0.35, 2.0, 2.1, 6.4, 0, 52, (196, 194, 184))       # sofa
    hc.box(5.6, 0.15, 7.15, 1.7, 0, 100, (92, 52, 36))        # piano against the south wall


def boot_zone(east_wall=True):
    """Flagstones, painted brick, the settle under the window.
    The kitchen looks through the east wall."""
    _floor("flags", 0, 0, 6.4, 3.1, seed=5)
    _wall_y(0, 0, 6.4, (232, 228, 218))
    if east_wall:
        _wall_x(0, 0, 3.1, (232, 228, 218))
    hc.box(1.85, 0.08, 4.05, 0.78, 0, 50, (168, 132, 86))     # settle
    hc.box(0.15, 0.02, 1.4, 0.16, 12, 74, (238, 238, 234))    # radiator


def utility_zone():
    """Terracotta floor, white machines and the sink run."""
    _floor("quarry", 0, 0, 3.6, 5.8, seed=9)
    _wall_x(0, 0, 5.8, (244, 244, 242))
    hc.box(0.04, 2.6, 0.92, 3.55, 4, 86, (244, 244, 242))     # washer
    hc.box(0.04, 3.55, 0.92, 4.85, 4, 86, (244, 244, 242))
    hc.box(0.9, 4.85, 3.5, 5.7, 0, 90, (244, 244, 242))       # north run
    hc.box(0.85, 4.8, 3.55, 5.75, 90, 96, (176, 128, 80))


def office_zone():
    """Terracotta floor, white panelling, the grey desk and the tan chair."""
    _floor("quarry", 0, 0, 3.6, 6.0, seed=6)
    _wall_x(0, 0, 6.0, (214, 214, 210))
    hc.box(0.1, 3.8, 1.2, 5.9, 0, 74, (120, 124, 130))        # desk
    hc.box(2.2, 0.25, 3.3, 1.35, 0, 72, (178, 118, 70))       # tan armchair
    hc.box(0.05, 1.65, 0.55, 3.5, 20, 120, (34, 34, 36))      # shelving


def wc_zone():
    """Teal above a white tiled dado, basin and toilet."""
    _floor("flags", 0, 0, 1.65, 3.1, seed=21)
    # south wall only; the boot room looks through the east wall
    hc.qy(0, 0, 1.65, 0, 100, (240, 240, 236))
    hc.qy(0.01, 0, 1.65, 100, hc.WALL_H, hc.shade(TEAL, hc.KY))
    hc.box(0.95, 0.08, 1.55, 0.55, 48, 78, (248, 248, 246))   # basin
    hc.box(0.5, 2.15, 1.15, 3.0, 0, 42, (248, 248, 246))      # toilet


# ---------------------------------------------------------------- one callable per directed opening
def _open(here, there, draw):
    def go():
        with _at(here, there):
            draw()
    return go


kitchen_from_hall = _open(HALL, KD, lambda: kitchen_zone(6.2, 0.0, 13.8, 6.5))
kitchen_from_boot = _open(BOOT, KD, lambda: kitchen_zone(9.8, 0.0, 16.4, 8.2))
kitchen_from_drawing = _open(DRAWING, KD, lambda: kitchen_zone(11.5, 0.0, 16.4, 5.5))
hall_from_kitchen = _open(KITCHEN_VIEW, HALL, hall_zone)
hall_from_sitting = _open(SITTING, HALL, lambda: hall_zone(east_wall=False))
hall_from_drawing = _open(DRAWING, HALL, hall_zone)
sitting_from_hall = _open(HALL, SITTING, sitting_zone)
drawing_from_hall = _open(HALL, DRAWING, lambda: drawing_zone(east_wall=False))
drawing_from_kitchen = _open(KITCHEN_VIEW, DRAWING, drawing_zone)
boot_from_kitchen = _open(KITCHEN_VIEW, BOOT, lambda: boot_zone(east_wall=False))
boot_from_utility = _open(UTILITY, BOOT, boot_zone)
boot_from_office = _open(OFFICE, BOOT, boot_zone)
boot_from_wc = _open(WC, BOOT, boot_zone)
utility_from_boot = _open(BOOT, UTILITY, utility_zone)
office_from_boot = _open(BOOT, OFFICE, office_zone)
wc_from_boot = _open(BOOT, WC, wc_zone)
