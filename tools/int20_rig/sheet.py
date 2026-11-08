"""TEST ONLY: contact sheet of held-gun frames. sheet.py <out.png> <cols> <png...>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
out, cols, fs = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
W = 320; ims = []
for f in fs:
    im = Image.open(f).convert('RGB'); im = im.resize((W, int(im.height * W / im.width)))
    d = ImageDraw.Draw(im); lab = os.path.basename(f)[:-4].split('_', 1)[1]
    d.rectangle([0, 0, W, 18], fill=(0, 0, 0)); d.text((4, 3), lab, fill=(255, 255, 0))
    ims.append(im)
H = max(i.height for i in ims); rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (cols * W, rows * H), (20, 20, 20))
for k, im in enumerate(ims): sh.paste(im, ((k % cols) * W, (k // cols) * H))
sh.save(out); print(out, sh.size)
