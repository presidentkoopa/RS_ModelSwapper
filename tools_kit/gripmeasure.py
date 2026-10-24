"""Measure the gripping region of one posed hand frame FROM THE HAND MESH ALONE.

Why this exists
---------------
`align.held_patch()` works out which face of Ermac's hand does the gripping by
reading ERMAC'S OWN GUN: it keeps the gun points within 3 cm of the hand and ICPs
that patch onto the target. The kit stages only his hands (`kit/kit/ermac/hand/`),
so on a fresh copy `align.fit()` cannot run at all.

But the gripping face is a fixed property of the POSE. It does not depend on the
target gun, and HAND_FITTING.md section 8 already measured one by hand (the fist's
curl slot, "F 25, L -1.5, U -5.2 in Ermac's frame"). This generalises that: it
measures the same thing for every pose, automatically, and stores it as data.

How it measures it
------------------
Ermac's hands are posed by eye and overlap the gun they hold by over a centimetre,
so there is no empty tunnel to find: an inscribed-sphere or enclosed-cavity search
lands in the palm hollow, 2-3 cm off the part actually held (measured; see
GRIP_REGIONS.md). What survives the overlap is the CHORD ACROSS THE CURL:

  * from each hand facet, march along the facet's own outward normal until it
    hits the hand again -- the far wall of the curl. That chord crosses whatever
    the hand is closed around.
  * the chord lengths have a clear mode at the held part's width (the fingers over
    the top and the palm under the bottom are a fixed distance apart). Keep the
    facets in that mode.
  * both ends of each kept chord are hand points in contact with the held part, so
    a cylinder fitted through them is the held part: axis, radius, axial extent.

Everything here reads `kit/kit/ermac/hand/hand.md3` and `hand2.md3` and nothing else.
Positions are the controller frame in cm, F forward, L left, U up -- the same frame
as every other number in `hands/`.

usage:
  python -B gripmeasure.py                 # measure every pose in POSES, write the json
  python -B gripmeasure.py hand2:15        # one pose, printed only
"""
import os, sys, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ermac, gunview, hudrender

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'gripregions.json')

# the poses this kit's packs use. mesh:frame -> what it holds (for the note only)
POSES = {
    'hand:19':  'pistol, two-handed  (gun hand)',
    'hand:6':   'pistol, one-handed  (gun hand)',
    'hand:30':  'shotgun             (gun hand)',
    'hand:106': 'plasma rifle        (gun hand)',
    'hand2:4':  'pistol support, cupped under the gun hand',
    'hand2:15': 'shotgun / rifle forend support',
    'hand2:91': 'fist on a vertical grip',
}

VOX = 0.22          # ray-march step and occupancy cell, cm
RAY = 14.0          # longest chord across a curl, cm
SKIN = 0.5          # start the ray this far off the facet, so it misses its own cell


def hand_item(mesh, frame):
    return dict(path=ermac.E + 'hand/%s.md3' % mesh, frame=frame, **ermac.PL)


def facets(mesh, frame):
    """triangle centroids, OUTWARD unit normals, areas (F/L/U cm)"""
    it = hand_item(mesh, frame)
    C, N, A = [], [], []
    for tris, raw in gunview.item_mesh(it):
        v = gunview.to_fl(hudrender.to_local(raw, it))
        a, b, c = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        n = np.cross(b - a, c - a)
        ar = np.linalg.norm(n, axis=1) / 2
        ok = ar > 1e-9
        C.append((a + b + c)[ok] / 3)
        N.append(n[ok] / np.linalg.norm(n[ok], axis=1)[:, None])
        A.append(ar[ok])
    C, N, A = np.concatenate(C), np.concatenate(N), np.concatenate(A)
    if ((C * N).sum(1) * A).sum() < 0:      # divergence theorem: 3V must be positive
        N = -N
    return C, N, A


def samples(mesh, frame, step=0.20):
    """dense surface samples, so a ray cannot slip between two vertices"""
    it = hand_item(mesh, frame)
    out = []
    for tris, raw in gunview.item_mesh(it):
        v = gunview.to_fl(hudrender.to_local(raw, it))
        a, b, c = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        e = np.maximum.reduce([np.linalg.norm(b - a, axis=1),
                               np.linalg.norm(c - b, axis=1),
                               np.linalg.norm(a - c, axis=1)])
        need = np.clip(np.ceil(e / step).astype(int), 1, 20)
        for n in range(1, 21):
            m = (need == n)
            if not m.any():
                continue
            aa, bb, cc = a[m], b[m], c[m]
            for i in range(n + 1):
                for j in range(n + 1 - i):
                    out.append((aa * i + bb * j + cc * (n - i - j)) / n)
    return np.concatenate(out)


def _occupancy(S):
    lo = S.min(0) - 2.0
    dim = np.ceil((S.max(0) + 2.0 - lo) / VOX).astype(int) + 1
    occ = np.zeros(dim, bool)
    i = np.clip(np.floor((S - lo) / VOX).astype(int), 0, dim - 1)
    occ[i[:, 0], i[:, 1], i[:, 2]] = True
    return lo, dim, occ


def chords(mesh, frame):
    """for every facet: the distance along its own outward normal to the far wall
    of the hand (inf if the ray leaves)"""
    C, N, A = facets(mesh, frame)
    lo, dim, occ = _occupancy(samples(mesh, frame))
    n = len(C)
    d = np.full(n, np.inf)
    p = C + N * SKIN
    t = np.full(n, SKIN)
    live = np.ones(n, bool)
    for _ in range(int(RAY / VOX)):
        p = p + N * VOX
        t = t + VOX
        idx = np.floor((p - lo) / VOX).astype(int)
        inb = ((idx >= 0) & (idx < dim)).all(1)
        hit = np.zeros(n, bool)
        sel = live & inb
        hit[sel] = occ[idx[sel, 0], idx[sel, 1], idx[sel, 2]]
        d[hit & live] = t[hit & live]
        live &= ~hit
        live &= inb
    return C, N, A, d


def chord_mode(d, A, lo=1.5, hi=12.0, bw=0.5):
    """the width the hand is closed around: the peak of the area-weighted chord
    length histogram"""
    e = np.arange(lo, hi + bw, bw)
    h = np.histogram(d, bins=e, weights=A)[0]
    k = np.array([1., 2, 3, 2, 1]); k /= k.sum()
    return float(e[np.convolve(h, k, 'same').argmax()] + bw / 2)


def _circle_at(pts, w, a):
    """least-squares circle through the contact points in the plane square to `a`"""
    a = a / np.linalg.norm(a)
    t = np.array([1., 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1., 0])
    e1 = np.cross(a, t); e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    c0 = np.average(pts, 0, weights=w)
    q = np.stack([(pts - c0) @ e1, (pts - c0) @ e2], 1)
    M = np.c_[q[:, 0], q[:, 1], np.ones(len(q))] * w[:, None]
    b = (q ** 2).sum(1) * w
    s = np.linalg.lstsq(M, b, rcond=None)[0]
    cc = np.array([s[0] / 2, s[1] / 2])
    r = float(np.sqrt(max(s[2] + cc @ cc, 1e-6)))
    return c0 + e1 * cc[0] + e2 * cc[1], r


def _cylinder(pts, w, a0, iters=8):
    """axis + radius through a ring of contact points, least squares, re-seating
    the axis each round"""
    a = a0 / np.linalg.norm(a0)
    c = np.average(pts, 0, weights=w)
    r = 1.0
    for _ in range(iters):
        t = np.array([1., 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1., 0])
        e1 = np.cross(a, t); e1 /= np.linalg.norm(e1)
        e2 = np.cross(a, e1)
        c0 = np.average(pts, 0, weights=w)
        q = np.stack([(pts - c0) @ e1, (pts - c0) @ e2], 1)
        M = np.c_[q[:, 0], q[:, 1], np.ones(len(q))] * w[:, None]
        b = (q ** 2).sum(1) * w
        s = np.linalg.lstsq(M, b, rcond=None)[0]
        cc = np.array([s[0] / 2, s[1] / 2])
        r = float(np.sqrt(max(s[2] + cc @ cc, 1e-6)))
        c = c0 + e1 * cc[0] + e2 * cc[1]
        X = pts - c
        ev, V = np.linalg.eigh((X * w[:, None]).T @ X / w.sum())
        na = V[:, -1]
        if na @ a < 0:
            na = -na
        if np.linalg.norm(na - a) < 1e-5:
            a = na
            break
        a = na
    return c, a, r


def measure(mesh, frame, band=(-1.1, 1.4)):
    C, N, A, d = chords(mesh, frame)
    fin = np.isfinite(d)
    C, N, A, d = C[fin], N[fin], A[fin], d[fin]
    md = chord_mode(d, A)
    keep = (d >= md + band[0]) & (d <= md + band[1])
    if keep.sum() < 20:
        raise SystemExit('%s:%d -- only %d facets in the chord mode' % (mesh, frame, keep.sum()))
    near = C[keep]
    far = C[keep] + N[keep] * d[keep][:, None]
    pts = np.concatenate([near, far])
    w = np.concatenate([A[keep], A[keep]])
    seed = pts - pts.mean(0)
    _, V = np.linalg.eigh(seed.T @ seed / len(seed))
    c, a, r = _cylinder(pts, w, V[:, -1])
    if a[0] < 0:                      # point the axis forward, so the data reads the same way
        a = -a
    # A second axis estimate, recorded but NOT used. Every facet on a cylinder has its
    # normal square to the axis, so the smallest eigenvector of the contact normals'
    # covariance is the textbook cylinder axis, and on hand2:15 it is 4 degrees off
    # Ermac's own pump where the point cloud's long axis is 12. But refitting the
    # centre in its plane moved the centre 0.4 cm FURTHER from the pump, and that
    # costs more in the final shift than the tilt does (measured end to end on the
    # m41a and m37a2: worst axis error 1.28 cm with it, 1.14 cm without). It is kept
    # here because it is the better number for anything that wants the direction --
    # a rotated hold, `minigun_fit.rot_hook` -- rather than the position.
    nn = N[keep]
    _, V2 = np.linalg.eigh((nn * A[keep][:, None]).T @ nn)
    an = V2[:, 0]
    if an @ a < 0:
        an = -an
    t = (pts - c) @ a
    th = (C - c) @ a                  # axial span of the whole hand
    # Two radii, and the difference matters. `fit_radius` is the least-squares circle
    # through the contact points; it runs large because the walls spread past the
    # tangent line. `radius` is half the chord mode -- the distance between the two
    # walls the hand closes on, halved -- which is the held part's own half-width and
    # the one the fitter wants, because a stand-in cylinder has to be about the size
    # of the real part for the ICP to seat the same way. Measured on hand2:15: half
    # chord 2.12, least squares 3.07, Ermac's pump 2.26.
    return dict(mesh=mesh, frame=int(frame),
                note=POSES.get('%s:%d' % (mesh, frame), ''),
                axis=[round(float(x), 4) for x in a],
                axis_normals=[round(float(x), 4) for x in an],
                point=[round(float(x), 3) for x in c],
                radius=round(float(md / 2), 3),
                fit_radius=round(float(r), 3),
                extent=[round(float(t.min()), 2), round(float(t.max()), 2)],
                hand_extent=[round(float(th.min()), 2), round(float(th.max()), 2)],
                chord_mode=round(md, 2),
                facets=int(keep.sum()),
                contact=[[round(float(x), 2) for x in p] for p in pts])


def main(argv):
    if argv:
        for key in argv:
            mesh, fr = key.split(':')
            r = measure(mesh, int(fr))
            r.pop('contact')
            print(key, json.dumps(r))
        return
    out = {}
    for key in POSES:
        mesh, fr = key.split(':')
        out[key] = measure(mesh, int(fr))
        q = dict(out[key]); q.pop('contact')
        print(key, json.dumps(q), flush=True)
    doc = {'_units': 'controller frame, cm: F forward, L left, U up '
                     '(gunview.to_fl / hudrender.to_local, vr_weaponScale 1.02)',
           '_frame': "Ermac's own placement, ermac.PL: Scale -1 1 1, Offset 0 -24 -10",
           '_method': 'gripmeasure.py -- chord across the curl; hand mesh only, no gun mesh',
           'poses': out}
    json.dump(doc, open(OUT, 'w'), indent=1)
    print('\nwrote', OUT)


if __name__ == '__main__':
    main(sys.argv[1:])
