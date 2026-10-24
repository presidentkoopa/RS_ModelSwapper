"""Put Ermac's posed hands (Force Unleashed: hand.md3 gun-hand frames, hand2.md3
support frames, drawn with his weapons at Scale -1 1 1 / Offset 0 -24 -10) onto
BD22's guns. Each hand keeps Ermac's pose exactly; only a translation is found:
the patch of Ermac's gun that the hand holds is fitted (ICP, translation only)
onto the matching part of the BD22 gun. Positions: controller frame, cm,
F forward, L left, U up.
"""
import sys, math
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, 'C:/Users/Command/Desktop/Quest_Weapons_Kit/kit/kit/melee')
import gunview, hudrender, guns, ermac

def surface_points(it, per_tri=True):
    pts = []
    for tris, raw in gunview.item_mesh(it):
        v = gunview.to_fl(hudrender.to_local(raw, it))
        pts.append(v)
        if per_tri:
            pts.append((v[tris[:, 0]] + v[tris[:, 1]] + v[tris[:, 2]]) / 3)
            # extra samples on long triangles (low-poly cylinders)
            for w in (0.25, 0.75):
                pts.append(v[tris[:, 0]] * w + v[tris[:, 1]] * (1 - w))
                pts.append(v[tris[:, 1]] * w + v[tris[:, 2]] * (1 - w))
                pts.append(v[tris[:, 2]] * w + v[tris[:, 0]] * (1 - w))
    return np.concatenate(pts)

def held_patch(gun_pts, hand_pts, r=3.0):
    t = cKDTree(hand_pts)
    d, _ = t.query(gun_pts)
    return gun_pts[d < r]

def icp_translate(src, dst, t0, iters=40, keep=0.8):
    tree = cKDTree(dst)
    t = np.array(t0, float)
    for _ in range(iters):
        d, idx = tree.query(src + t)
        k = np.argsort(d)[:max(10, int(len(d) * keep))]
        step = (dst[idx[k]] - (src[k] + t)).mean(0)
        t += step
        if np.linalg.norm(step) < 1e-3:
            break
    d, _ = tree.query(src + t)
    return t, float(np.median(d))

def box(pts, f=(-1e9, 1e9), l=(-1e9, 1e9), u=(-1e9, 1e9)):
    m = (pts[:, 0] >= f[0]) & (pts[:, 0] <= f[1]) & (pts[:, 1] >= l[0]) & (pts[:, 1] <= l[1]) & (pts[:, 2] >= u[0]) & (pts[:, 2] <= u[1])
    return pts[m]

def hook_from_shift(dflu):
    """translation in the controller frame (cm) -> ModifyBobLayer3D hook for a
    layer whose MODELDEF is Scale -1 1 1 (local x mirrored): local (x right,
    y up, z back) = (-L, U, -F); hook = S^-1 * local"""
    f, l, u = dflu
    return [round(float(l), 2), round(float(u), 2), round(float(-f), 2)]

def ermac_points(name, which):
    """(gun points, hand points) for Ermac's set; which: 1 gun hand, 2 support"""
    g, gf, h1, h2, _ = ermac.SETS[name]
    gi = dict(path=ermac.E + g, frame=gf, **ermac.PL)
    hi = dict(path=ermac.E + ('hand/hand.md3' if which == 1 else 'hand/hand2.md3'), frame=h1 if which == 1 else h2, **ermac.PL)
    return surface_points(gi), surface_points(hi, per_tri=False)

def fit(cls, ename, which, region, t0=(0, 0, 0), r=3.0):
    gE, hE = ermac_points(ename, which)
    patch = held_patch(gE, hE, r)
    gO = surface_points(guns.item(cls))
    dst = box(gO, **region)
    if len(dst) < 20 or len(patch) < 10:
        raise SystemExit('%s/%s: patch %d dst %d' % (cls, ename, len(patch), len(dst)))
    t, err = icp_translate(patch, dst, t0)
    return t, err, patch
