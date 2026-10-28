"""TEST ONLY (2.0 final): contact sheet of the held frames. f20sheet.py <dir with held_<Gun>.png> <out.png> <title>"""
import sys, glob, os
from PIL import Image, ImageDraw
d, out, title = sys.argv[1:4]
fs = sorted(glob.glob(d + '/held_*.png'), key=lambda f: f.lower()); T = 320; n = 6; rows = (len(fs) + n - 1) // n
sh = Image.new('RGB', (n * T, 30 + rows * (T + 18)), (20, 20, 20)); dr = ImageDraw.Draw(sh); dr.text((6, 8), title, fill=(255, 255, 255))
for k, f in enumerate(fs):
    x, y = (k % n) * T, 30 + (k // n) * (T + 18)
    dr.text((x + 4, y + 2), os.path.basename(f)[5:-4], fill=(255, 220, 120)); sh.paste(Image.open(f).resize((T, T)), (x, y + 16))
sh.save(out); print(out, len(fs))
