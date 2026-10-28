import sys, glob, numpy as np
from PIL import Image
from scipy import ndimage
for f in sorted(glob.glob(sys.argv[1] + '/*.png')):
    a = np.asarray(Image.open(f).convert('RGB')).astype(int)
    m = (a[:, :, 0] > 180) & (a[:, :, 2] > 180) & (a[:, :, 1] < 90)
    lab, n = ndimage.label(m)
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(xs) < 4: continue
        out.append('blob c=(%.0f,%.0f) w=%d h=%d px=%d' % (xs.mean(), ys.mean(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1, len(xs)))
    print(f.split('/')[-1], '; '.join(out))
