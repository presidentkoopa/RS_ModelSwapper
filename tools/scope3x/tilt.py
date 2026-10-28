import sys, numpy as np
from PIL import Image
from scipy import ndimage
def tilt(f, cx_max=520):
    a = np.asarray(Image.open(f).convert('RGB')).astype(int)
    m = (a[:, :, 0] > 180) & (a[:, :, 2] > 180) & (a[:, :, 1] < 90)
    lab, n = ndimage.label(m); best = max(range(1, n + 1), key=lambda k: (lab == k).sum())
    b = lab == best; ys, xs = np.nonzero(b)
    y0, y1 = ys.min(), ys.max(); x0, x1 = xs.min(), xs.max()
    rows = range(y0 + 4, y1 - 3); cols = range(x0 + 4, x1 - 3)
    L = np.array([(y, np.nonzero(b[y])[0].min()) for y in rows]); R = np.array([(y, np.nonzero(b[y])[0].max()) for y in rows])
    T = np.array([(x, np.nonzero(b[:, x])[0].min()) for x in cols]); B = np.array([(x, np.nonzero(b[:, x])[0].max()) for x in cols])
    sl = lambda P: np.degrees(np.arctan(np.polyfit(P[:, 0], P[:, 1], 1)[0]))
    # left/right edges: dx/dy (positive = bottom to the right); top/bottom: dy/dx (positive = right side lower)
    return dict(left=sl(L), right=sl(R), top=sl(T), bottom=sl(B), w=x1 - x0 + 1, h=y1 - y0 + 1, px=int(b.sum()))
for f in sys.argv[1:]:
    print(f, {k: round(v, 2) if isinstance(v, float) else v for k, v in tilt(f).items()})
