"""Contact sheet of every cached view: python tools/contact_sheet.py cache_dir out.png [views...]"""
import os, sys, json
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import build_rooms
cache, out = sys.argv[1], sys.argv[2]
views = sys.argv[3:] or [v + s for v in build_rooms.VIEWS for s in ("", "_r")]
tw, th = 480, 270
cols = 6
rows = (len(views) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (20, 20, 20))
d = ImageDraw.Draw(sheet)
for i, v in enumerate(views):
    bg = Image.open(os.path.join(cache, v + "_bg.png")).convert("RGBA")
    bg.alpha_composite(Image.open(os.path.join(cache, v + "_fg.png")).convert("RGBA"))
    x, y = (i % cols) * tw, (i // cols) * (th + 18)
    sheet.paste(bg.convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + 18))
    d.text((x + 4, y + 3), v.replace("_r", " (looking south)"), fill=(240, 230, 200))
sheet.save(out)
