"""The fit, without Ermac's gun meshes: `stored_patch()` in place of `held_patch()`.

`align.fit()` needs TWO meshes it does not own -- Ermac's hand AND Ermac's gun --
because `held_patch()` decides which face of the hand grips by keeping the gun
points within 3 cm of the hand. The kit stages the hands only, so on a fresh copy
`align.fit()` dies on a missing `ermac/<set>/<gun>.md3`.

The gripping face does not depend on the target gun. `gripmeasure.py` measures it
once per pose from the hand mesh alone and stores it in `gripregions.json`; this
module turns a stored record back into a point cloud shaped like the part the hand
holds, and runs the SAME ICP (`align.icp_translate`) against the target gun. The
old path is untouched and still works exactly as it did -- this is a second way in,
beside it, the way `fit_pack.py` is a second way in beside `fitall.py`.

The stand-in cloud is built the way `held_patch()` built the real one: the surface
of the measured grip cylinder, kept where it is within 3 cm of the hand. The only
difference is that the 3 cm is measured against the hand instead of against a gun.

Positions: controller frame, cm, F forward, L left, U up.
"""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import guns                      # before align: align re-points sys.path at kit/melee
import align, ermac, gunview, hudrender

REGIONS = os.path.join(HERE, 'gripregions.json')
_data = None


def regions():
    global _data
    if _data is None:
        _data = json.load(open(REGIONS))['poses']
    return _data


def record(key):
    r = regions().get(key)
    if r is None:
        raise SystemExit('%s is not measured. gripregions.json holds %s -- add the pose to '
                         'gripmeasure.POSES and re-run `python -B gripmeasure.py`, rather than '
                         'guessing from a neighbouring frame.' % (key, ', '.join(sorted(regions()))))
    return r


def pose_key(ename, which):
    """Ermac set + which hand -> the stored pose key, from ermac.SETS.
    which: 1 gun hand (two-handed frame), 2 support hand, 0 gun hand one-handed."""
    g, gf, h1, h2, h1one = ermac.SETS[ename]
    if which == 2:
        return 'hand2:%d' % h2
    if which == 0:
        return 'hand:%d' % h1one
    return 'hand:%d' % h1


def hand_points(key):
    rec = record(key)
    it = dict(path=ermac.E + 'hand/%s.md3' % rec['mesh'], frame=rec['frame'], **ermac.PL)
    return align.surface_points(it, per_tri=False)


def grip_frame(key):
    """(point on the axis, unit axis, radius) of the stored grip cylinder"""
    rec = record(key)
    return np.array(rec['point'], float), np.array(rec['axis'], float), float(rec['radius'])


def contact_patch(key):
    """the measured gripping FACE itself: the hand points that touch the held part,
    both walls of every chord across the curl.

    For a grip -- which is not a tube -- this is the better stand-in: measured
    against Ermac's own staged guns it lies 0.65 / 0.74 / 1.54 cm from his gun
    surface on hand:19 / hand:30 / hand:106, where the cylinder stand-in below is
    2.76 / 1.95 / 2.78 cm out. For a forend it is the other way round (hand2:15:
    contact 1.65, cylinder 1.19), because a forend really is a tube and the cylinder
    closes the circle the fingers leave open."""
    return np.array(record(key)['contact'], float)


def stored_patch(key, r=3.0, pad=4.0, nang=48, step=0.4):
    """the point cloud that stands in for `align.held_patch()`: the surface of the
    measured grip cylinder, trimmed to within `r` cm of the hand -- the same 3 cm
    rule `held_patch()` uses, measured against the hand instead of against a gun."""
    rec = record(key)
    c, a, rad = grip_frame(key)
    t = np.array([1., 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1., 0])
    e1 = np.cross(a, t); e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    t0, t1 = rec['extent']
    ts = np.arange(t0 - pad, t1 + pad + 1e-9, step)
    th = np.arange(nang) * (2 * np.pi / nang)
    ring = np.outer(np.cos(th), e1) * rad + np.outer(np.sin(th), e2) * rad
    pts = (c + np.einsum('i,j->ij', ts, a)[:, None, :] + ring[None, :, :]).reshape(-1, 3)
    d, _ = cKDTree(hand_points(key)).query(pts)
    return pts[d < r]


def patch_for(key, kind='cylinder', r=3.0):
    return contact_patch(key) if kind == 'contact' else stored_patch(key, r)


def fit(cls, ename, which, region, t0=(0, 0, 0), r=3.0, key=None, kind='cylinder'):
    """`align.fit()` with the stored region in place of `held_patch()`.
    Same arguments, same return: (shift F/L/U cm, ICP residual cm, the patch).
    `kind`: 'cylinder' (a tube -- forends, pumps) or 'contact' (a grip)."""
    key = key or pose_key(ename, which)
    patch = patch_for(key, kind, r)
    gO = align.surface_points(guns.item(cls))
    dst = align.box(gO, **region)
    if len(dst) < 20 or len(patch) < 10:
        raise SystemExit('%s/%s: patch %d dst %d' % (cls, key, len(patch), len(dst)))
    t, err = align.icp_translate(patch, dst, t0)
    return t, err, patch


if __name__ == '__main__':
    for k, rec in sorted(regions().items()):
        p = stored_patch(k)
        print('%-10s frame %-4d r %.2f  axis %s  point %s  stand-in cloud %d pts  bbox F %.1f..%.1f L %.1f..%.1f U %.1f..%.1f'
              % (k, rec['frame'], rec['radius'], rec['axis'], rec['point'], len(p),
                 p[:, 0].min(), p[:, 0].max(), p[:, 1].min(), p[:, 1].max(), p[:, 2].min(), p[:, 2].max()))
