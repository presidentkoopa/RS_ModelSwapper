import sys, glob, os
from PIL import Image
d = sys.argv[1]
for f in sorted(glob.glob(d + '/*.ppm')):
    Image.open(f).save(f[:-4] + '.png'); os.remove(f)
fs = sorted(glob.glob(d + '/*.png'))
th = [Image.open(f).resize((160, 160)) for f in fs]
n = 8; rows = (len(th) + n - 1) // n
sheet = Image.new('RGB', (160 * n, 160 * rows))
for k, t in enumerate(th): sheet.paste(t, ((k % n) * 160, (k // n) * 160))
sheet.save(d + '_contact.png'); print(len(fs), fs[0], fs[-1])
